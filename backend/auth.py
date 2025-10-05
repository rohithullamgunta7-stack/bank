from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Optional
from models import UserSignup, AdminSignup, Token, UserInfo, RoleUpdateRequest
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, ADMIN_SECRET_KEY
from database import users_collection, messages_collection, mongo_connected

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Rate limiting storage (in production, use Redis)
login_attempts = defaultdict(list)
signup_attempts = defaultdict(list)

def hash_password(password: str):
    """Hash password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(password: str, hashed_pw: str):
    """Verify password against hash"""
    return pwd_context.verify(password, hashed_pw)

def create_access_token(data: dict):
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    """Verify JWT token and return user data"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {
            "email": payload["sub"], 
            "name": payload.get("name"),
            "role": payload.get("role", "user")
        }
    except JWTError:
        return None

def check_rate_limit(identifier: str, attempts_dict: dict, max_attempts: int = 5, window_minutes: int = 15):
    """
    Rate limiting to prevent brute force attacks
    In production, use Redis for distributed rate limiting
    """
    now = datetime.utcnow()
    cutoff = now - timedelta(minutes=window_minutes)
    
    # Clean old attempts
    attempts_dict[identifier] = [
        attempt for attempt in attempts_dict[identifier] 
        if attempt > cutoff
    ]
    
    # Check if limit exceeded
    if len(attempts_dict[identifier]) >= max_attempts:
        return False, f"Too many attempts. Please try again in {window_minutes} minutes."
    
    # Record this attempt
    attempts_dict[identifier].append(now)
    return True, None

def sanitize_email(email: str) -> str:
    """Sanitize and normalize email"""
    return email.lower().strip()

def get_current_user(authorization: Optional[str] = Header(None)):
    """Dependency to get current user from Authorization header"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401, 
            detail="Authorization header required. Please login."
        )
    
    token = authorization.split(" ")[1]
    user_data = verify_token(token)
    
    if not user_data:
        raise HTTPException(
            status_code=401, 
            detail="Invalid or expired token. Please login again."
        )
    
    return user_data

def require_admin(current_user: dict = Depends(get_current_user)):
    """Dependency to require admin role"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

def require_support_or_admin(current_user: dict = Depends(get_current_user)):
    """Dependency to require customer support agent or admin role"""
    if current_user.get("role") not in ["customer_support_agent", "admin"]:
        raise HTTPException(
            status_code=403, 
            detail="Customer support or admin access required"
        )
    return current_user

@router.post("/signup", response_model=Token)
def signup(user: UserSignup):
    """Regular user signup - only allows 'user' role"""
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable. Please try again later.")
    
    # Rate limiting
    email = sanitize_email(user.email)
    allowed, error_msg = check_rate_limit(email, signup_attempts, max_attempts=3, window_minutes=60)
    if not allowed:
        raise HTTPException(status_code=429, detail=error_msg)
    
    # Check if user exists
    if users_collection.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Force role to be 'user' for regular signup
    if user.role != "user":
        raise HTTPException(status_code=400, detail="Regular signup only allows user role")
    
    try:
        hashed_pw = hash_password(user.password)
        
        # Create user document
        user_id = f"user_{int(datetime.utcnow().timestamp())}"
        user_doc = {
            "user_id": user_id,
            "email": email, 
            "password": hashed_pw, 
            "name": user.name.strip(),
            "role": "user",
            "created_at": datetime.utcnow().isoformat(),
            "last_login": datetime.utcnow().isoformat()
        }
        users_collection.insert_one(user_doc)
        
        # Create token
        token = create_access_token({
            "sub": email, 
            "name": user.name,
            "role": "user"
        })
        
        return {"access_token": token, "token_type": "bearer"}
    
    except Exception as e:
        print(f"Signup error: {e}")
        raise HTTPException(status_code=500, detail="Signup failed. Please try again.")

@router.post("/admin-signup", response_model=Token)
def admin_signup(user: AdminSignup):
    """Admin/Support agent signup with secret key"""
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable. Please try again later.")
    
    # Verify admin secret key
    if user.admin_secret != ADMIN_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Invalid admin secret key")
    
    # Rate limiting
    email = sanitize_email(user.email)
    allowed, error_msg = check_rate_limit(email, signup_attempts, max_attempts=3, window_minutes=60)
    if not allowed:
        raise HTTPException(status_code=429, detail=error_msg)
    
    if users_collection.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="User already exists")
    
    try:
        hashed_pw = hash_password(user.password)
        
        # Create user document
        user_id = f"{user.role}_{int(datetime.utcnow().timestamp())}"
        user_doc = {
            "user_id": user_id,
            "email": email, 
            "password": hashed_pw, 
            "name": user.name.strip(),
            "role": user.role,
            "created_at": datetime.utcnow().isoformat(),
            "last_login": datetime.utcnow().isoformat()
        }
        users_collection.insert_one(user_doc)
        
        # Create token
        token = create_access_token({
            "sub": email, 
            "name": user.name,
            "role": user.role
        })
        
        return {"access_token": token, "token_type": "bearer"}
    
    except Exception as e:
        print(f"Admin signup error: {e}")
        raise HTTPException(status_code=500, detail="Signup failed. Please try again.")

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint with rate limiting"""
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable. Please try again later.")
    
    # Rate limiting
    email = sanitize_email(form_data.username)
    allowed, error_msg = check_rate_limit(email, login_attempts)
    if not allowed:
        raise HTTPException(status_code=429, detail=error_msg)
    
    # Find user
    db_user = users_collection.find_one({"email": email})
    if not db_user or not verify_password(form_data.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Ensure user has user_id and role (for existing users)
    updates = {}
    if "user_id" not in db_user:
        user_id = f"user_{int(datetime.utcnow().timestamp())}"
        updates["user_id"] = user_id
        db_user["user_id"] = user_id
    
    if "role" not in db_user:
        updates["role"] = "user"
        db_user["role"] = "user"
    
    # Update last login
    updates["last_login"] = datetime.utcnow().isoformat()
    
    # Apply updates
    if updates:
        users_collection.update_one({"email": email}, {"$set": updates})
    
    # Create token
    token = create_access_token({
        "sub": db_user["email"], 
        "name": db_user["name"],
        "role": db_user["role"]
    })
    
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserInfo)
def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    db_user = users_collection.find_one({"email": current_user["email"]})
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": db_user["user_id"],
        "email": db_user["email"],
        "name": db_user["name"],
        "role": db_user["role"],
        "created_at": db_user.get("created_at")
    }

@router.put("/update-role", response_model=dict)
def update_user_role(request: RoleUpdateRequest, admin_user: dict = Depends(require_admin)):
    """Admin endpoint to update user roles"""
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    # Find user by user_id
    target_user = users_collection.find_one({"user_id": request.user_id})
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent self-demotion for admins
    if target_user["email"] == admin_user["email"] and request.new_role != "admin":
        raise HTTPException(
            status_code=400, 
            detail="Cannot change your own admin role. Ask another admin."
        )
    
    # Update role
    users_collection.update_one(
        {"user_id": request.user_id},
        {"$set": {
            "role": request.new_role, 
            "updated_at": datetime.utcnow().isoformat()
        }}
    )
    
    return {
        "message": f"User {target_user['name']} role updated to {request.new_role}",
        "user_id": request.user_id,
        "new_role": request.new_role
    }

@router.get("/users", response_model=list)
def get_all_users(admin_user: dict = Depends(require_admin)):
    """Admin endpoint to get all users"""
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    users = list(users_collection.find({}, {"password": 0}))
    return users

@router.get("/stats")
def get_system_stats(current_user: dict = Depends(require_support_or_admin)):
    """Get system statistics for dashboard"""
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        total_users = users_collection.count_documents({"role": "user"})
        total_agents = users_collection.count_documents({"role": "customer_support_agent"})
        total_admins = users_collection.count_documents({"role": "admin"})
        total_messages = messages_collection.count_documents({})
        
        # Get recent activity (last 10 messages)
        recent_messages = list(messages_collection.find({}).sort("timestamp", -1).limit(10))
        
        return {
            "total_users": total_users,
            "total_agents": total_agents,
            "total_admins": total_admins,
            "total_messages": total_messages,
            "recent_activity": recent_messages
        }
    except Exception as e:
        print(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch statistics")

@router.post("/logout")
def logout(current_user: dict = Depends(get_current_user)):
    """Logout endpoint (client-side token removal)"""
    # In a production app with token blacklisting, add token to blacklist here
    return {"message": "Logged out successfully"}