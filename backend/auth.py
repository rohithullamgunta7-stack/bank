from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Optional
import hashlib
import bcrypt as bcrypt_lib
from .models import UserSignup, AdminSignup, Token, UserInfo, RoleUpdateRequest
from .config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, ADMIN_SECRET_KEY
from .database import users_collection, messages_collection, mongo_connected

router = APIRouter()

# Use ONLY Argon2 for new passwords
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

# Rate limiting storage (in production, use Redis)
login_attempts = defaultdict(list)
signup_attempts = defaultdict(list)

# ---------------- Password Utilities ---------------- #

def hash_password(password: str) -> str:
    """Hash password using Argon2 (new default - no byte limit)"""
    return pwd_context.hash(password)

def verify_bcrypt_directly(password: str, hashed_pw: str) -> bool:
    """
    Verify bcrypt password directly using bcrypt library.
    Handles 72-byte limitation by preprocessing with SHA256.
    """
    # ... (This function is correct, no changes needed)
    try:
        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        hashed_bytes = hashed_pw.encode('utf-8')
        password_bytes = password_hash.encode('utf-8')
        if bcrypt_lib.checkpw(password_bytes, hashed_bytes):
            return True
    except Exception:
        pass
    try:
        password_truncated = password.encode('utf-8')[:72]
        hashed_bytes = hashed_pw.encode('utf-8')
        if bcrypt_lib.checkpw(password_truncated, hashed_bytes):
            return True
    except Exception:
        pass
    try:
        password_bytes = password.encode('utf-8')
        hashed_bytes = hashed_pw.encode('utf-8')
        return bcrypt_lib.checkpw(password_bytes, hashed_bytes)
    except Exception:
        pass
    return False

def verify_password(password: str, hashed_pw) -> bool:
    """
    Verify password against hash. Handles both string and bytes hash formats.
    """
    if isinstance(hashed_pw, bytes):
        try:
            hashed_pw = hashed_pw.decode('utf-8')
        except UnicodeDecodeError:
            return False
    
    if hashed_pw.startswith("$argon2"):
        try:
            return pwd_context.verify(password, hashed_pw)
        except Exception:
            return False
    
    if hashed_pw.startswith(("$2a$", "$2b$", "$2y$")):
        return verify_bcrypt_directly(password, hashed_pw)
    
    return False

def needs_rehash(hashed_pw) -> bool:
    """Check if password needs to be rehashed (bcrypt -> argon2)"""
    if isinstance(hashed_pw, bytes):
        try:
            hashed_pw = hashed_pw.decode('utf-8')
        except UnicodeDecodeError:
            return False
    if isinstance(hashed_pw, str):
        return hashed_pw.startswith(("$2a$", "$2b$", "$2y$"))
    return False

# ---------------- JWT Utilities ---------------- #

def create_access_token(data: dict) -> str:
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

# ---------------- Rate Limiting ---------------- #

def check_rate_limit(identifier: str, attempts_dict: dict, max_attempts: int = 5, window_minutes: int = 15):
    """Rate limiting to prevent brute force attacks"""
    now = datetime.utcnow()
    cutoff = now - timedelta(minutes=window_minutes)
    attempts_dict[identifier] = [attempt for attempt in attempts_dict[identifier] if attempt > cutoff]
    if len(attempts_dict[identifier]) >= max_attempts:
        return False, f"Too many attempts. Please try again in {window_minutes} minutes."
    attempts_dict[identifier].append(now)
    return True, None

# ---------------- Helpers ---------------- #

def sanitize_email(email: str) -> str:
    """Sanitize and normalize email"""
    return email.lower().strip()

def get_current_user(authorization: Optional[str] = Header(None)):
    """Dependency to get current user from Authorization header"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header required. Please login.")
    token = authorization.split(" ")[1]
    user_data = verify_token(token)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token. Please login again.")
    return user_data

def require_admin(current_user: dict = Depends(get_current_user)):
    """Dependency to require admin role"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

def require_support_or_admin(current_user: dict = Depends(get_current_user)):
    """Dependency to require customer support agent or admin role"""
    if current_user.get("role") not in ["customer_support_agent", "admin"]:
        raise HTTPException(status_code=403, detail="Customer support or admin access required")
    return current_user

# ---------------- Routes ---------------- #

@router.post("/signup", response_model=Token)
def signup(user: UserSignup):
    """Regular user signup - only allows 'user' role"""
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable. Please try again later.")
    
    email = sanitize_email(user.email)
    allowed, error_msg = check_rate_limit(email, signup_attempts, max_attempts=3, window_minutes=60)
    if not allowed:
        raise HTTPException(status_code=429, detail=error_msg)
    
    if users_collection.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="User already exists")
    
    if user.role != "user":
        raise HTTPException(status_code=400, detail="Regular signup only allows user role")
    
    try:
        hashed_pw = hash_password(user.password)
        user_id = f"user_{int(datetime.utcnow().timestamp())}"
        
        # FIX: Save name as 'full_name' for consistency
        user_doc = {
            "user_id": user_id,
            "email": email, 
            "password": hashed_pw, 
            "full_name": user.name.strip(),
            "role": "user",
            "created_at": datetime.utcnow().isoformat(),
            "last_login": datetime.utcnow().isoformat()
        }
        users_collection.insert_one(user_doc)
        
        token = create_access_token({"sub": email, "name": user.name.strip(), "role": "user"})
        return {"access_token": token, "token_type": "bearer"}
    
    except Exception as e:
        print(f"Signup error: {e}")
        raise HTTPException(status_code=500, detail="Signup failed. Please try again.")

@router.post("/admin-signup", response_model=Token)
def admin_signup(user: AdminSignup):
    """Admin/Support agent signup with secret key"""
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable. Please try again later.")
    
    if user.admin_secret != ADMIN_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Invalid admin secret key")
    
    email = sanitize_email(user.email)
    allowed, error_msg = check_rate_limit(email, signup_attempts, max_attempts=3, window_minutes=60)
    if not allowed:
        raise HTTPException(status_code=429, detail=error_msg)
    
    if users_collection.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="User already exists")
    
    try:
        hashed_pw = hash_password(user.password)
        user_id = f"{user.role.replace(' ', '_')}_{int(datetime.utcnow().timestamp())}"
        
        # FIX: Save name as 'full_name' for consistency
        user_doc = {
            "user_id": user_id,
            "email": email, 
            "password": hashed_pw, 
            "full_name": user.name.strip(),
            "role": user.role,
            "created_at": datetime.utcnow().isoformat(),
            "last_login": datetime.utcnow().isoformat()
        }
        users_collection.insert_one(user_doc)
        
        token = create_access_token({"sub": email, "name": user.name.strip(), "role": user.role})
        return {"access_token": token, "token_type": "bearer"}
    
    except Exception as e:
        print(f"Admin signup error: {e}")
        raise HTTPException(status_code=500, detail="Signup failed. Please try again.")

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint with rate limiting and automatic password rehashing"""
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable. Please try again later.")
    
    email = sanitize_email(form_data.username)
    allowed, error_msg = check_rate_limit(email, login_attempts)
    if not allowed:
        raise HTTPException(status_code=429, detail=error_msg)
    
    db_user = users_collection.find_one({"email": email})
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    password_valid = verify_password(form_data.password, db_user["password"])
    if not password_valid:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    print("✅ PASSWORD VERIFICATION SUCCESSFUL!")
    
    updates = {}
    if needs_rehash(db_user["password"]):
        updates["password"] = hash_password(form_data.password)
    
    updates["last_login"] = datetime.utcnow().isoformat()
    if updates:
        users_collection.update_one({"email": email}, {"$set": updates})
    
    # FIX: Check for 'full_name' first, then fall back to 'name'
    user_name = db_user.get("full_name") or db_user.get("name", "User")

    token = create_access_token({
        "sub": db_user["email"], 
        "name": user_name,
        "role": db_user.get("role", "user")
    })
    
    return {"access_token": token, "token_type": "bearer"}

@router.put("/update-role", response_model=dict)
def update_user_role(request: RoleUpdateRequest, admin_user: dict = Depends(require_admin)):
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    target_user = users_collection.find_one({"user_id": request.user_id})
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if target_user["email"] == admin_user["email"] and request.new_role != "admin":
        raise HTTPException(status_code=400, detail="Cannot change your own admin role. Ask another admin.")
    
    users_collection.update_one(
        {"user_id": request.user_id},
        {"$set": {"role": request.new_role, "updated_at": datetime.utcnow().isoformat()}}
    )
    
    return {
        "message": f"User {target_user.get('full_name')} role updated to {request.new_role}",
        "user_id": request.user_id,
        "new_role": request.new_role
    }

@router.get("/users", response_model=list)
def get_all_users(admin_user: dict = Depends(require_admin)):
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    users = list(users_collection.find({}, {"password": 0}))
    for user in users:
        user["_id"] = str(user["_id"])
    return users

@router.get("/stats")
def get_system_stats(current_user: dict = Depends(require_support_or_admin)):
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        total_users = users_collection.count_documents({"role": "user"})
        total_agents = users_collection.count_documents({"role": "customer_support_agent"})
        total_admins = users_collection.count_documents({"role": "admin"})
        total_messages = messages_collection.count_documents({})
        
        return {
            "total_users": total_users,
            "total_agents": total_agents,
            "total_admins": total_admins,
            "total_messages": total_messages
        }
    except Exception as e:
        print(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch statistics")

@router.post("/logout")
def logout(current_user: dict = Depends(get_current_user)):
    return {"message": "Logged out successfully"}
@router.get("/me", response_model=UserInfo)
def get_current_user_info(current_user: dict = Depends(get_current_user)):
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    db_user = users_collection.find_one({"email": current_user["email"]})
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check for 'full_name' first, then fall back to 'name'
    user_name = db_user.get("full_name") or db_user.get("name", "User")

    # --- THIS IS THE FIX ---
    # Convert the datetime object to an ISO string
    created_at_dt = db_user.get("created_at")
    created_at_str = None
    if isinstance(created_at_dt, datetime):
        created_at_str = created_at_dt.isoformat()
    elif isinstance(created_at_dt, str):
         created_at_str = created_at_dt # It's already a string

    return {
        "user_id": db_user.get("user_id"),
        "email": db_user["email"],
        "name": user_name,
        "role": db_user.get("role"),
        "created_at": created_at_str  # Pass the converted string
    }