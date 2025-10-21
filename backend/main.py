
# from fastapi import FastAPI, Depends, HTTPException, Request
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse
# from models import MessageRequest, MessageResponse
# from chat import get_bot_reply
# from database import (
#     get_or_create_user, get_user_conversations, get_all_users, 
#     get_conversation_summaries, get_user_conversation_history,
#     get_customer_by_email, get_customer_all_accounts,
#     save_feedback, get_user_feedback, get_system_statistics
# )
# from config import mongo_connected, gemini_initialized
# from config import accounts_col, transactions_col, users_collection, messages_collection  # Import for statistics
# from auth import router as auth_router, get_current_user, require_admin, require_support_or_admin
# from escalation import router as escalation_router
# from faq import router as faq_router
# from cards import router as cards_router
# import time
# from datetime import datetime, timezone, timedelta

# app = FastAPI(
#     title="Banking Support API",
#     description="AI-Powered Banking Customer Support System",
#     version="2.0.0"
# )

# # CORS Configuration
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ==================== ROUTER INCLUSION ====================

# app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
# app.include_router(escalation_router, prefix="/escalation", tags=["Escalation"])
# app.include_router(faq_router, prefix="/faq", tags=["FAQ Management"])
# app.include_router(cards_router, prefix="/cards", tags=["Card Management"])

# # ==================== EXCEPTION HANDLERS ====================

# @app.exception_handler(Exception)
# async def global_exception_handler(request: Request, exc: Exception):
#     """Handle uncaught exceptions gracefully"""
#     print(f"Unhandled exception: {type(exc).__name__}: {exc}")
#     import traceback
#     traceback.print_exc()
#     return JSONResponse(
#         status_code=500,
#         content={"detail": "Internal server error. Please try again later."}
#     )

# @app.exception_handler(HTTPException)
# async def http_exception_handler(request: Request, exc: HTTPException):
#     """Handle HTTP exceptions"""
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={"detail": exc.detail}
#     )

# # ==================== SYSTEM ENDPOINTS ====================

# @app.get("/", tags=["System"])
# def root():
#     """API root endpoint"""
#     return {
#         "message": "Banking Support API - AI-Powered Customer Support",
#         "version": "2.0.0",
#         "status": "operational",
#         "documentation": "/docs"
#     }

# @app.get("/health", tags=["System"])
# def health_check():
#     """Check system health status"""
#     return {
#         "status": "healthy" if mongo_connected and gemini_initialized else "degraded",
#         "database": "connected" if mongo_connected else "disconnected",
#         "ai_service": "ready" if gemini_initialized else "unavailable",
#         "timestamp": time.time()
#     }

# # ==================== CHAT ENDPOINTS ====================

# @app.post("/chat", tags=["Chat"])
# def chat_endpoint(req: MessageRequest, current_user: dict = Depends(get_current_user)):
#     """Chat endpoint for banking support"""
#     if not mongo_connected:
#         raise HTTPException(status_code=503, detail="Database unavailable. Please try again later.")
    
#     if not gemini_initialized:
#         raise HTTPException(status_code=503, detail="AI service unavailable. Please try again later.")
    
#     try:
#         # Create or retrieve user
#         user = get_or_create_user(
#             current_user["email"],
#             current_user.get("name"),
#             current_user.get("role", "user")
#         )
        
#         if not user or "user_id" not in user:
#             raise HTTPException(status_code=500, detail="User creation failed")
        
#         # Get bot reply
#         reply = get_bot_reply(
#             user["user_id"],
#             req.message,
#             current_user.get("role", "user")
#         )
        
#         # Handle different response types
#         if isinstance(reply, dict):
#             print(f"✅ Returning dict response with keys: {reply.keys()}")
#             return reply
#         else:
#             return {"reply": reply}
    
#     except HTTPException:
#         raise
#     except Exception as e:
#         print(f"❌ Chat endpoint error: {type(e).__name__}: {e}")
#         import traceback
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail="Failed to process message.")

# # ==================== USER ACCOUNT ENDPOINTS ====================

# @app.get("/accounts", tags=["User"])
# def get_my_accounts(current_user: dict = Depends(get_current_user)):
#     """Get current user's bank accounts"""
#     if not mongo_connected:
#         raise HTTPException(status_code=503, detail="Database unavailable")
    
#     try:
#         user = get_or_create_user(
#             current_user["email"],
#             current_user.get("name"),
#             current_user.get("role", "user")
#         )
        
#         if not user or "user_id" not in user:
#             raise HTTPException(status_code=500, detail="User not found")
        
#         # Get customer and their accounts
#         customer = get_customer_by_email(current_user["email"])
#         if not customer:
#             return {"accounts": [], "message": "No customer profile found"}
        
#         accounts = get_customer_all_accounts(str(customer["_id"]))
#         return {"accounts": accounts, "total": len(accounts)}
    
#     except Exception as e:
#         print(f"Get accounts error: {e}")
#         raise HTTPException(status_code=500, detail="Failed to fetch accounts")

# @app.get("/conversations", tags=["User"])
# def get_my_conversations(current_user: dict = Depends(get_current_user)):
#     """Get current user's conversation history"""
#     if not mongo_connected:
#         raise HTTPException(status_code=503, detail="Database unavailable")
    
#     try:
#         user = get_or_create_user(
#             current_user["email"],
#             current_user.get("name"),
#             current_user.get("role", "user")
#         )
        
#         if not user or "user_id" not in user:
#             raise HTTPException(status_code=500, detail="User not found")
        
#         conversations = get_user_conversations(
#             current_user.get("role", "user"),
#             user["user_id"]
#         )
#         return {"conversations": conversations, "total": len(conversations)}
    
#     except Exception as e:
#         print(f"Get conversations error: {e}")
#         raise HTTPException(status_code=500, detail="Failed to fetch conversations")



# # ==================== DASHBOARD ENDPOINTS (FIXED) ====================

# @app.get("/dashboard", tags=["Dashboard"])
# def get_dashboard_data(current_user: dict = Depends(get_current_user)):
#     """Get role-specific dashboard data with banking statistics"""
#     if not mongo_connected:
#         raise HTTPException(status_code=503, detail="Database unavailable")
    
#     try:
#         role = current_user.get("role", "user")
        
#         if role == "admin":
#             print(f"📊 Admin dashboard requested by {current_user['email']}")
            
#             # Get all users
#             all_users = get_all_users()
            
#             # Get conversation summaries
#             summaries = get_conversation_summaries("admin", 20) or []
            
#             # Get banking statistics - COUNT FROM DATABASE
#             total_accounts = 0
#             total_transactions = 0
            
#             try:
#                 if accounts_col is not None:
#                     total_accounts = accounts_col.count_documents({})
#                     print(f"✅ Total accounts counted: {total_accounts}")
#                 else:
#                     print("⚠️ accounts_col is None")
                    
#                 if transactions_col is not None:
#                     total_transactions = transactions_col.count_documents({})
#                     print(f"✅ Total transactions counted: {total_transactions}")
#                 else:
#                     print("⚠️ transactions_col is None")
                    
#             except Exception as e:
#                 print(f"❌ Error fetching banking stats: {e}")
#                 import traceback
#                 traceback.print_exc()
            
#             # Get user role breakdown
#             user_roles_count = {
#                 "support_agents": len([u for u in all_users if u.get("role") == "customer_support_agent"]),
#                 "admins": len([u for u in all_users if u.get("role") == "admin"]),
#                 "regular_users": len([u for u in all_users if u.get("role") == "user"])
#             }
            
#             dashboard_response = {
#                 "total_users": len(all_users),
#                 "total_agents": user_roles_count["support_agents"],
#                 "total_admins": user_roles_count["admins"],
#                 "total_accounts": total_accounts,
#                 "total_transactions": total_transactions,
#                 "active_conversations": len(summaries),
#                 "user_roles_count": user_roles_count,
#                 "conversation_summaries": summaries,
#                 "timestamp": datetime.now(timezone.utc).isoformat()
#             }
            
#             print(f"✅ Dashboard response: Accounts={total_accounts}, Transactions={total_transactions}")
#             return dashboard_response
        
#         elif role == "customer_support_agent":
#             # Support agent dashboard
#             summaries = get_conversation_summaries("customer_support_agent", 20) or []
            
#             return {
#                 "role": role,
#                 "conversation_summaries": summaries,
#                 "total_conversations": len(summaries),
#                 "message": "Support Agent Dashboard",
#                 "timestamp": datetime.now(timezone.utc).isoformat()
#             }
        
#         else:
#             # Regular user dashboard
#             user = get_or_create_user(
#                 current_user["email"],
#                 current_user.get("name"),
#                 role
#             )
            
#             my_conversations = get_user_conversations(role, user["user_id"])
#             customer = get_customer_by_email(current_user["email"])
#             accounts_count = 0
            
#             if customer:
#                 accounts = get_customer_all_accounts(str(customer["_id"]))
#                 accounts_count = len(accounts)
            
#             return {
#                 "role": role,
#                 "conversations_count": len(my_conversations),
#                 "accounts_count": accounts_count,
#                 "recent_conversations": my_conversations[:5],
#                 "message": "Welcome to Banking Support",
#                 "timestamp": datetime.now(timezone.utc).isoformat()
#             }
    
#     except Exception as e:
#         print(f"❌ Dashboard error: {e}")
#         import traceback
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail="Failed to fetch dashboard data")

# # ==================== SUPPORT AGENT ENDPOINTS ====================

# @app.get("/support/conversations", tags=["Support"])
# def get_support_conversations(support_user: dict = Depends(require_support_or_admin)):
#     """Support agent: view all user conversations"""
#     if not mongo_connected:
#         raise HTTPException(status_code=503, detail="Database unavailable")
    
#     try:
#         conversations = get_user_conversations("customer_support_agent") or []
#         return {"conversations": conversations, "total": len(conversations)}
#     except Exception as e:
#         print(f"Support conversations error: {e}")
#         raise HTTPException(status_code=500, detail="Failed to fetch conversations")

# @app.get("/support/conversation-summaries", tags=["Support"])
# def get_support_summaries(support_user: dict = Depends(require_support_or_admin)):
#     """Support agent: get conversation summaries"""
#     if not mongo_connected:
#         raise HTTPException(status_code=503, detail="Database unavailable")
    
#     try:
#         summaries = get_conversation_summaries("customer_support_agent") or []
#         return {"summaries": summaries, "total": len(summaries)}
#     except Exception as e:
#         print(f"Support summaries error: {e}")
#         import traceback
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail="Failed to fetch summaries")

# # ==================== ADMIN ENDPOINTS ====================

# @app.get("/admin/all-users", tags=["Admin"])
# def get_admin_all_users(admin_user: dict = Depends(require_admin)):
#     """Admin: view all users"""
#     if not mongo_connected:
#         raise HTTPException(status_code=503, detail="Database unavailable")
    
#     try:
#         all_users = get_all_users()
#         return {"users": all_users, "total": len(all_users)}
#     except Exception as e:
#         print(f"Admin users error: {e}")
#         raise HTTPException(status_code=500, detail="Failed to fetch users")

# @app.get("/admin/conversations", tags=["Admin"])
# def get_admin_conversations(admin_user: dict = Depends(require_admin)):
#     """Admin: view all conversations"""
#     if not mongo_connected:
#         raise HTTPException(status_code=503, detail="Database unavailable")
    
#     try:
#         conversations = get_user_conversations("admin") or []
#         return {"conversations": conversations, "total": len(conversations)}
#     except Exception as e:
#         print(f"Admin conversations error: {e}")
#         raise HTTPException(status_code=500, detail="Failed to fetch conversations")

# @app.get("/admin/conversation-summaries", tags=["Admin"])
# def get_admin_summaries(admin_user: dict = Depends(require_admin)):
#     """Admin: get all conversation summaries"""
#     if not mongo_connected:
#         raise HTTPException(status_code=503, detail="Database unavailable")
    
#     try:
#         summaries = get_conversation_summaries("admin") or []
#         return {"summaries": summaries, "total": len(summaries)}
#     except Exception as e:
#         print(f"Admin summaries error: {e}")
#         import traceback
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail="Failed to fetch summaries")

# @app.get("/admin/statistics", tags=["Admin"])
# def get_admin_statistics(admin_user: dict = Depends(require_admin)):
#     """Admin: Get detailed system statistics"""
#     if not mongo_connected:
#         raise HTTPException(status_code=503, detail="Database unavailable")
    
#     try:
#         all_users = get_all_users()
        
#         # Banking statistics
#         total_accounts = 0
#         total_transactions = 0
#         active_accounts = 0
        
#         try:
#             if accounts_col:
#                 total_accounts = accounts_col.count_documents({})
#                 active_accounts = accounts_col.count_documents({"status": "active"})
#             if transactions_col:
#                 total_transactions = transactions_col.count_documents({})
#         except Exception as e:
#             print(f"Error fetching statistics: {e}")
        
#         return {
#             "users": {
#                 "total": len(all_users),
#                 "regular_users": len([u for u in all_users if u.get("role") == "user"]),
#                 "support_agents": len([u for u in all_users if u.get("role") == "customer_support_agent"]),
#                 "admins": len([u for u in all_users if u.get("role") == "admin"])
#             },
#             "banking": {
#                 "total_accounts": total_accounts,
#                 "active_accounts": active_accounts,
#                 "total_transactions": total_transactions
#             },
#             "timestamp": datetime.now(timezone.utc).isoformat()
#         }
    
#     except Exception as e:
#         print(f"Statistics error: {e}")
#         raise HTTPException(status_code=500, detail="Failed to fetch statistics")

# # ==================== SHARED ENDPOINTS ====================

# @app.get("/conversation/{user_id}", tags=["Conversations"])
# def get_user_conversation_endpoint(user_id: str, current_user: dict = Depends(require_support_or_admin)):
#     """Get full conversation history for a specific user"""
#     if not mongo_connected:
#         raise HTTPException(status_code=503, detail="Database unavailable")
    
#     try:
#         conversation = get_user_conversation_history(user_id)
#         return {
#             "user_id": user_id,
#             "conversation": conversation,
#             "total_messages": len(conversation)
#         }
#     except Exception as e:
#         print(f"User conversation error: {e}")
#         raise HTTPException(status_code=500, detail="Failed to fetch conversation")

# # ==================== STARTUP ====================

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)




# import os
# import time
# import traceback
# from datetime import datetime, timezone, timedelta
# from fastapi import FastAPI, Depends, HTTPException, Request
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse

# # Corrected relative imports
# from .models import MessageRequest, MessageResponse
# from .chat import get_bot_reply
# from .database import (
#     get_or_create_user, get_user_conversations, get_all_users, 
#     get_conversation_summaries, get_user_conversation_history,
#     get_customer_by_email, get_customer_all_accounts,
#     save_feedback, get_user_feedback, get_system_statistics
# )
# from .config import mongo_connected, gemini_initialized
# from .config import accounts_col, transactions_col, users_collection, messages_collection
# from .auth import router as auth_router, get_current_user, require_admin, require_support_or_admin
# from .escalation import router as escalation_router
# from .faq import router as faq_router
# from .cards import router as cards_router

# app = FastAPI(
#     title="Banking Support API",
#     description="AI-Powered Banking Customer Support System",
#     version="2.0.0",
#     docs_url="/docs",  # Explicitly set docs URL
#     redoc_url="/redoc" # Explicitly set redoc URL
# )

# # --- Production-Ready CORS Configuration ---
# # Load allowed origins from an environment variable
# # On Render, set ALLOWED_ORIGINS="https://your-frontend.onrender.com"
# # For multiple domains: "https://domain1.com,https://domain2.com"
# # Defaulting to "*" is insecure but fine for initial testing.
# ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "*").split(",")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=ALLOWED_ORIGINS, # Use the dynamic list
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ==================== ROUTER INCLUSION ====================

# app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
# app.include_router(escalation_router, prefix="/escalation", tags=["Escalation"])
# app.include_router(faq_router, prefix="/faq", tags=["FAQ Management"])
# app.include_router(cards_router, prefix="/cards", tags=["Card Management"])

# # ==================== EXCEPTION HANDLERS ====================

# @app.exception_handler(Exception)
# async def global_exception_handler(request: Request, exc: Exception):
#     """Handle uncaught exceptions gracefully"""
#     print(f"Unhandled exception: {type(exc).__name__}: {exc}")
#     traceback.print_exc()
#     return JSONResponse(
#         status_code=500,
#         content={"detail": "Internal server error. Please try again later."}
#     )

# @app.exception_handler(HTTPException)
# async def http_exception_handler(request: Request, exc: HTTPException):
#     """Handle HTTP exceptions"""
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={"detail": exc.detail}
#     )

# # ==================== SYSTEM ENDPOINTS ====================

# @app.get("/", tags=["System"])
# def root():
#     """API root endpoint"""
#     return {
#         "message": "Banking Support API - AI-Powered Customer Support",
#         "version": "2.0.0",
#         "status": "operational",
#         "documentation": "/docs"
#     }

# @app.get("/health", tags=["System"])
# def health_check():
#     """Check system health status"""
#     return {
#         "status": "healthy" if mongo_connected and gemini_initialized else "degraded",
#         "database": "connected" if mongo_connected else "disconnected",
#         "ai_service": "ready" if gemini_initialized else "unavailable",
#         "timestamp": datetime.now(timezone.utc).isoformat()
#     }

# # ==================== CHAT ENDPOINTS ====================

# @app.post("/chat", tags=["Chat"])
# def chat_endpoint(req: MessageRequest, current_user: dict = Depends(get_current_user)):
#     """Chat endpoint for banking support"""
#     if not mongo_connected:
#         raise HTTPException(status_code=503, detail="Database unavailable. Please try again later.")
    
#     if not gemini_initialized:
#         raise HTTPException(status_code=503, detail="AI service unavailable. Please try again later.")
    
#     try:
#         # Create or retrieve user
#         user = get_or_create_user(
#             current_user["email"],
#             current_user.get("name"),
#             current_user.get("role", "user")
#         )
        
#         if not user or "user_id" not in user:
#             raise HTTPException(status_code=500, detail="User creation failed")
        
#         # Get bot reply
#         reply = get_bot_reply(
#             user["user_id"],
#             req.message,
#             current_user.get("role", "user")
#         )
        
#         # Handle different response types
#         if isinstance(reply, dict):
#             print(f"✅ Returning dict response with keys: {reply.keys()}")
#             return reply
#         else:
#             return {"reply": reply}
    
#     except HTTPException:
#         raise
#     except Exception as e:
#         print(f"❌ Chat endpoint error: {type(e).__name__}: {e}")
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail="Failed to process message.")

# # ==================== USER ACCOUNT ENDPOINTS ====================

# @app.get("/accounts", tags=["User"])
# def get_my_accounts(current_user: dict = Depends(get_current_user)):
#     """Get current user's bank accounts"""
#     if not mongo_connected:
#         raise HTTPException(status_code=503, detail="Database unavailable")
    
#     try:
#         user = get_or_create_user(
#             current_user["email"],
#             current_user.get("name"),
#             current_user.get("role", "user")
#         )
        
#         if not user or "user_id" not in user:
#             raise HTTPException(status_code=500, detail="User not found")
        
#         # Get customer and their accounts
#         customer = get_customer_by_email(current_user["email"])
#         if not customer:
#             return {"accounts": [], "message": "No customer profile found"}
        
#         accounts = get_customer_all_accounts(str(customer["_id"]))
#         return {"accounts": accounts, "total": len(accounts)}
    
#     except Exception as e:
#         print(f"Get accounts error: {e}")
#         raise HTTPException(status_code=500, detail="Failed to fetch accounts")

# @app.get("/conversations", tags=["User"])
# def get_my_conversations(current_user: dict = Depends(get_current_user)):
#     """Get current user's conversation history"""
#     if not mongo_connected:
#         raise HTTPException(status_code=503, detail="Database unavailable")
    
#     try:
#         user = get_or_create_user(
#             current_user["email"],
#             current_user.get("name"),
#             current_user.get("role", "user")
#         )
        
#         if not user or "user_id" not in user:
#             raise HTTPException(status_code=500, detail="User not found")
        
#         conversations = get_user_conversations(
#             current_user.get("role", "user"),
#             user["user_id"]
#         )
#         return {"conversations": conversations, "total": len(conversations)}
    
#     except Exception as e:
#         print(f"Get conversations error: {e}")
#         raise HTTPException(status_code=500, detail="Failed to fetch conversations")



# # ==================== DASHBOARD ENDPOINTS (FIXED) ====================

# @app.get("/dashboard", tags=["Dashboard"])
# def get_dashboard_data(current_user: dict = Depends(get_current_user)):
#     """Get role-specific dashboard data with banking statistics"""
#     if not mongo_connected:
#         raise HTTPException(status_code=503, detail="Database unavailable")
    
#     try:
#         role = current_user.get("role", "user")
        
#         if role == "admin":
#             print(f"📊 Admin dashboard requested by {current_user['email']}")
            
#             # Get all users
#             all_users = get_all_users()
            
#             # Get conversation summaries
#             summaries = get_conversation_summaries("admin", 20) or []
            
#             # Get banking statistics - COUNT FROM DATABASE
#             total_accounts = 0
#             total_transactions = 0
            
#             try:
#                 if accounts_col is not None:
#                     total_accounts = accounts_col.count_documents({})
#                     print(f"✅ Total accounts counted: {total_accounts}")
#                 else:
#                     print("⚠️ accounts_col is None")
                    
#                 if transactions_col is not None:
#                     total_transactions = transactions_col.count_documents({})
#                     print(f"✅ Total transactions counted: {total_transactions}")
#                 else:
#                     print("⚠️ transactions_col is None")
                    
#             except Exception as e:
#                 print(f"❌ Error fetching banking stats: {e}")
#                 traceback.print_exc()
            
#             # Get user role breakdown
#             user_roles_count = {
#                 "support_agents": len([u for u in all_users if u.get("role") == "customer_support_agent"]),
#                 "admins": len([u for u in all_users if u.get("role") == "admin"]),
#                 "regular_users": len([u for u in all_users if u.get("role") == "user"])
#             }
            
#             dashboard_response = {
#                 "total_users": len(all_users),
#                 "total_agents": user_roles_count["support_agents"],
#                 "total_admins": user_roles_count["admins"],
#                 "total_accounts": total_accounts,
#                 "total_transactions": total_transactions,
#                 "active_conversations": len(summaries),
#                 "user_roles_count": user_roles_count,
#                 "conversation_summaries": summaries,
#                 "timestamp": datetime.now(timezone.utc).isoformat()
#             }
            
#             print(f"✅ Dashboard response: Accounts={total_accounts}, Transactions={total_transactions}")
#             return dashboard_response
        
#         elif role == "customer_support_agent":
#             # Support agent dashboard
#             summaries = get_conversation_summaries("customer_support_agent", 20) or []
            
#             return {
#                 "role": role,
#                 "conversation_summaries": summaries,
#                 "total_conversations": len(summaries),
#                 "message": "Support Agent Dashboard",
#                 "timestamp": datetime.now(timezone.utc).isoformat()
#             }
        
#         else:
#             # Regular user dashboard
#             user = get_or_create_user(
#                 current_user["email"],
#                 current_user.get("name"),
#                 role
#             )
            
#             my_conversations = get_user_conversations(role, user["user_id"])
#             customer = get_customer_by_email(current_user["email"])
#             accounts_count = 0
            
#             if customer:
#                 accounts = get_customer_all_accounts(str(customer["_id"]))
#                 accounts_count = len(accounts)
            
#             return {
#                 "role": role,
#                 "conversations_count": len(my_conversations),
#                 "accounts_count": accounts_count,
#                 "recent_conversations": my_conversations[:5],
#                 "message": "Welcome to Banking Support",
#                 "timestamp": datetime.now(timezone.utc).isoformat()
#             }
    
#     except Exception as e:
#         print(f"❌ Dashboard error: {e}")
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail="Failed to fetch dashboard data")

# # ==================== SUPPORT AGENT ENDPOINTS ====================

# @app.get("/support/conversations", tags=["Support"])
# def get_support_conversations(support_user: dict = Depends(require_support_or_admin)):
#     """Support agent: view all user conversations"""
#     if not mongo_connected:
#         raise HTTPException(status_code=503, detail="Database unavailable")
    
#     try:
#         conversations = get_user_conversations("customer_support_agent") or []
#         return {"conversations": conversations, "total": len(conversations)}
#     except Exception as e:
#         print(f"Support conversations error: {e}")
#         raise HTTPException(status_code=500, detail="Failed to fetch conversations")

# @app.get("/support/conversation-summaries", tags=["Support"])
# def get_support_summaries(support_user: dict = Depends(require_support_or_admin)):
#     """Support agent: get conversation summaries"""
#     if not mongo_connected:
#         raise HTTPException(status_code=503, detail="Database unavailable")
    
#     try:
#         summaries = get_conversation_summaries("customer_support_agent") or []
#         return {"summaries": summaries, "total": len(summaries)}
#     except Exception as e:
#         print(f"Support summaries error: {e}")
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail="Failed to fetch summaries")

# # ==================== ADMIN ENDPOINTS ====================

# @app.get("/admin/all-users", tags=["Admin"])
# def get_admin_all_users(admin_user: dict = Depends(require_admin)):
#     """Admin: view all users"""
#     if not mongo_connected:
#         raise HTTPException(status_code=503, detail="Database unavailable")
    
#     try:
#         all_users = get_all_users()
#         return {"users": all_users, "total": len(all_users)}
#     except Exception as e:
#         print(f"Admin users error: {e}")
#         raise HTTPException(status_code=500, detail="Failed to fetch users")

# @app.get("/admin/conversations", tags=["Admin"])
# def get_admin_conversations(admin_user: dict = Depends(require_admin)):
#     """Admin: view all conversations"""
#     if not mongo_connected:
#         raise HTTPException(status_code=503, detail="Database unavailable")
    
#     try:
#         conversations = get_user_conversations("admin") or []
#         return {"conversations": conversations, "total": len(conversations)}
#     except Exception as e:
#         print(f"Admin conversations error: {e}")
#         raise HTTPException(status_code=500, detail="Failed to fetch conversations")

# @app.get("/admin/conversation-summaries", tags=["Admin"])
# def get_admin_summaries(admin_user: dict = Depends(require_admin)):
#     """Admin: get all conversation summaries"""
#     if not mongo_connected:
#         raise HTTPException(status_code=503, detail="Database unavailable")
    
#     try:
#         summaries = get_conversation_summaries("admin") or []
#         return {"summaries": summaries, "total": len(summaries)}
#     except Exception as e:
#         print(f"Admin summaries error: {e}")
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail="Failed to fetch summaries")

# @app.get("/admin/statistics", tags=["Admin"])
# def get_admin_statistics(admin_user: dict = Depends(require_admin)):
#     """Admin: Get detailed system statistics"""
#     if not mongo_connected:
#         raise HTTPException(status_code=503, detail="Database unavailable")
    
#     try:
#         all_users = get_all_users()
        
#         # Banking statistics
#         total_accounts = 0
#         total_transactions = 0
#         active_accounts = 0
        
#         try:
#             if accounts_col:
#                 total_accounts = accounts_col.count_documents({})
#                 active_accounts = accounts_col.count_documents({"status": "active"})
#             if transactions_col:
#                 total_transactions = transactions_col.count_documents({})
#         except Exception as e:
#             print(f"Error fetching statistics: {e}")
        
#         return {
#             "users": {
#                 "total": len(all_users),
#                 "regular_users": len([u for u in all_users if u.get("role") == "user"]),
#                 "support_agents": len([u for u in all_users if u.get("role") == "customer_support_agent"]),
#                 "admins": len([u for u in all_users if u.get("role") == "admin"])
#             },
#             "banking": {
#                 "total_accounts": total_accounts,
#                 "active_accounts": active_accounts,
#                 "total_transactions": total_transactions
#             },
#             "timestamp": datetime.now(timezone.utc).isoformat()
#         }
    
#     except Exception as e:
#         print(f"Statistics error: {e}")
#         raise HTTPException(status_code=500, detail="Failed to fetch statistics")

# # ==================== SHARED ENDPOINTS ====================

# @app.get("/conversation/{user_id}", tags=["Conversations"])
# def get_user_conversation_endpoint(user_id: str, current_user: dict = Depends(require_support_or_admin)):
#     """Get full conversation history for a specific user"""
#     if not mongo_connected:
#         raise HTTPException(status_code=503, detail="Database unavailable")
    
#     try:
#         conversation = get_user_conversation_history(user_id)
#         return {
#             "user_id": user_id,
#             "conversation": conversation,
#             "total_messages": len(conversation)
#         }
#     except Exception as e:
#         print(f"User conversation error: {e}")
#         raise HTTPException(status_code=500, detail="Failed to fetch conversation")

# # ==================== STARTUP ====================

# if __name__ == "__main__":
#     import uvicorn
#     # This block is for LOCAL DEVELOPMENT only.
#     # Render uses the 'gunicorn' command from your Build Command.
#     print("🚀 Starting local development server...")
#     port = int(os.environ.get("PORT", 8000))
#     # Run with "main:app" string to enable reload
#     uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)










import os
import time
import traceback
from datetime import datetime, timezone, timedelta
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Corrected relative imports
from .models import MessageRequest, MessageResponse
from .chat import get_bot_reply
from .database import (
    get_or_create_user, get_user_conversations, get_all_users, 
    get_conversation_summaries, get_user_conversation_history,
    get_customer_by_email, get_customer_all_accounts,
    save_feedback, get_user_feedback, get_system_statistics
)
from .config import mongo_connected, gemini_initialized
from .config import accounts_col, transactions_col, users_collection, messages_collection
from .auth import router as auth_router, get_current_user, require_admin, require_support_or_admin
from .escalation import router as escalation_router
from .faq import router as faq_router
from .cards import router as cards_router

app = FastAPI(
    title="Banking Support API",
    description="AI-Powered Banking Customer Support System",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# --- FIXED CORS Configuration ---
# Load allowed origins from environment variable
# Format: "https://domain1.com,https://domain2.com,http://localhost:3000"
allowed_origins_env = os.environ.get("ALLOWED_ORIGINS", "")

if allowed_origins_env:
    # Parse comma-separated origins from environment variable
    ALLOWED_ORIGINS = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]
else:
    ALLOWED_ORIGINS = ["*"]
    # Default development origins
    # ALLOWED_ORIGINS = [
    #     "http://localhost:3000",
    #     "http://127.0.0.1:3000",
    #     "https://bank-lime-rho.vercel.app",  # Your production frontend
    # ]

print(f"🌐 CORS Allowed Origins: {ALLOWED_ORIGINS}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Specific origins (NOT "*")
    allow_credentials=True,         # Required for authentication
    allow_methods=["*"],            # Allow all HTTP methods
    allow_headers=["*"],            # Allow all headers
    expose_headers=["*"],           # Expose headers to frontend
)

# ==================== ROUTER INCLUSION ====================

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(escalation_router, prefix="/escalation", tags=["Escalation"])
app.include_router(faq_router, prefix="/faq", tags=["FAQ Management"])
app.include_router(cards_router, prefix="/cards", tags=["Card Management"])

# ==================== EXCEPTION HANDLERS ====================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions gracefully"""
    print(f"Unhandled exception: {type(exc).__name__}: {exc}")
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# ==================== SYSTEM ENDPOINTS ====================

@app.get("/", tags=["System"])
def root():
    """API root endpoint"""
    return {
        "message": "Banking Support API - AI-Powered Customer Support",
        "version": "2.0.0",
        "status": "operational",
        "documentation": "/docs",
        "cors_enabled": True,
        "allowed_origins": len(ALLOWED_ORIGINS)
    }

@app.get("/health", tags=["System"])
def health_check():
    """Check system health status"""
    return {
        "status": "healthy" if mongo_connected and gemini_initialized else "degraded",
        "database": "connected" if mongo_connected else "disconnected",
        "ai_service": "ready" if gemini_initialized else "unavailable",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# ==================== CHAT ENDPOINTS ====================

@app.post("/chat", tags=["Chat"])
def chat_endpoint(req: MessageRequest, current_user: dict = Depends(get_current_user)):
    """Chat endpoint for banking support"""
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable. Please try again later.")
    
    if not gemini_initialized:
        raise HTTPException(status_code=503, detail="AI service unavailable. Please try again later.")
    
    try:
        # Create or retrieve user
        user = get_or_create_user(
            current_user["email"],
            current_user.get("name"),
            current_user.get("role", "user")
        )
        
        if not user or "user_id" not in user:
            raise HTTPException(status_code=500, detail="User creation failed")
        
        # Get bot reply
        reply = get_bot_reply(
            user["user_id"],
            req.message,
            current_user.get("role", "user")
        )
        
        # Handle different response types
        if isinstance(reply, dict):
            print(f"✅ Returning dict response with keys: {reply.keys()}")
            return reply
        else:
            return {"reply": reply}
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Chat endpoint error: {type(e).__name__}: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to process message.")

# ==================== USER ACCOUNT ENDPOINTS ====================

@app.get("/accounts", tags=["User"])
def get_my_accounts(current_user: dict = Depends(get_current_user)):
    """Get current user's bank accounts"""
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        user = get_or_create_user(
            current_user["email"],
            current_user.get("name"),
            current_user.get("role", "user")
        )
        
        if not user or "user_id" not in user:
            raise HTTPException(status_code=500, detail="User not found")
        
        # Get customer and their accounts
        customer = get_customer_by_email(current_user["email"])
        if not customer:
            return {"accounts": [], "message": "No customer profile found"}
        
        accounts = get_customer_all_accounts(str(customer["_id"]))
        return {"accounts": accounts, "total": len(accounts)}
    
    except Exception as e:
        print(f"Get accounts error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch accounts")

@app.get("/conversations", tags=["User"])
def get_my_conversations(current_user: dict = Depends(get_current_user)):
    """Get current user's conversation history"""
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        user = get_or_create_user(
            current_user["email"],
            current_user.get("name"),
            current_user.get("role", "user")
        )
        
        if not user or "user_id" not in user:
            raise HTTPException(status_code=500, detail="User not found")
        
        conversations = get_user_conversations(
            current_user.get("role", "user"),
            user["user_id"]
        )
        return {"conversations": conversations, "total": len(conversations)}
    
    except Exception as e:
        print(f"Get conversations error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch conversations")

# ==================== DASHBOARD ENDPOINTS ====================

@app.get("/dashboard", tags=["Dashboard"])
def get_dashboard_data(current_user: dict = Depends(get_current_user)):
    """Get role-specific dashboard data with banking statistics"""
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        role = current_user.get("role", "user")
        
        if role == "admin":
            print(f"📊 Admin dashboard requested by {current_user['email']}")
            
            # Get all users
            all_users = get_all_users()
            
            # Get conversation summaries
            summaries = get_conversation_summaries("admin", 20) or []
            
            # Get banking statistics
            total_accounts = 0
            total_transactions = 0
            
            try:
                if accounts_col is not None:
                    total_accounts = accounts_col.count_documents({})
                    print(f"✅ Total accounts counted: {total_accounts}")
                else:
                    print("⚠️ accounts_col is None")
                    
                if transactions_col is not None:
                    total_transactions = transactions_col.count_documents({})
                    print(f"✅ Total transactions counted: {total_transactions}")
                else:
                    print("⚠️ transactions_col is None")
                    
            except Exception as e:
                print(f"❌ Error fetching banking stats: {e}")
                traceback.print_exc()
            
            # Get user role breakdown
            user_roles_count = {
                "support_agents": len([u for u in all_users if u.get("role") == "customer_support_agent"]),
                "admins": len([u for u in all_users if u.get("role") == "admin"]),
                "regular_users": len([u for u in all_users if u.get("role") == "user"])
            }
            
            dashboard_response = {
                "total_users": len(all_users),
                "total_agents": user_roles_count["support_agents"],
                "total_admins": user_roles_count["admins"],
                "total_accounts": total_accounts,
                "total_transactions": total_transactions,
                "active_conversations": len(summaries),
                "user_roles_count": user_roles_count,
                "conversation_summaries": summaries,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            print(f"✅ Dashboard response: Accounts={total_accounts}, Transactions={total_transactions}")
            return dashboard_response
        
        elif role == "customer_support_agent":
            # Support agent dashboard
            summaries = get_conversation_summaries("customer_support_agent", 20) or []
            
            return {
                "role": role,
                "conversation_summaries": summaries,
                "total_conversations": len(summaries),
                "message": "Support Agent Dashboard",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        else:
            # Regular user dashboard
            user = get_or_create_user(
                current_user["email"],
                current_user.get("name"),
                role
            )
            
            my_conversations = get_user_conversations(role, user["user_id"])
            customer = get_customer_by_email(current_user["email"])
            accounts_count = 0
            
            if customer:
                accounts = get_customer_all_accounts(str(customer["_id"]))
                accounts_count = len(accounts)
            
            return {
                "role": role,
                "conversations_count": len(my_conversations),
                "accounts_count": accounts_count,
                "recent_conversations": my_conversations[:5],
                "message": "Welcome to Banking Support",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to fetch dashboard data")

# ==================== SUPPORT AGENT ENDPOINTS ====================

@app.get("/support/conversations", tags=["Support"])
def get_support_conversations(support_user: dict = Depends(require_support_or_admin)):
    """Support agent: view all user conversations"""
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        conversations = get_user_conversations("customer_support_agent") or []
        return {"conversations": conversations, "total": len(conversations)}
    except Exception as e:
        print(f"Support conversations error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch conversations")

@app.get("/support/conversation-summaries", tags=["Support"])
def get_support_summaries(support_user: dict = Depends(require_support_or_admin)):
    """Support agent: get conversation summaries"""
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        summaries = get_conversation_summaries("customer_support_agent") or []
        return {"summaries": summaries, "total": len(summaries)}
    except Exception as e:
        print(f"Support summaries error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to fetch summaries")

# ==================== ADMIN ENDPOINTS ====================

@app.get("/admin/all-users", tags=["Admin"])
def get_admin_all_users(admin_user: dict = Depends(require_admin)):
    """Admin: view all users"""
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        all_users = get_all_users()
        return {"users": all_users, "total": len(all_users)}
    except Exception as e:
        print(f"Admin users error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch users")

@app.get("/admin/conversations", tags=["Admin"])
def get_admin_conversations(admin_user: dict = Depends(require_admin)):
    """Admin: view all conversations"""
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        conversations = get_user_conversations("admin") or []
        return {"conversations": conversations, "total": len(conversations)}
    except Exception as e:
        print(f"Admin conversations error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch conversations")

@app.get("/admin/conversation-summaries", tags=["Admin"])
def get_admin_summaries(admin_user: dict = Depends(require_admin)):
    """Admin: get all conversation summaries"""
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        summaries = get_conversation_summaries("admin") or []
        return {"summaries": summaries, "total": len(summaries)}
    except Exception as e:
        print(f"Admin summaries error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to fetch summaries")

@app.get("/admin/statistics", tags=["Admin"])
def get_admin_statistics(admin_user: dict = Depends(require_admin)):
    """Admin: Get detailed system statistics"""
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        all_users = get_all_users()
        
        # Banking statistics
        total_accounts = 0
        total_transactions = 0
        active_accounts = 0
        
        try:
            if accounts_col:
                total_accounts = accounts_col.count_documents({})
                active_accounts = accounts_col.count_documents({"status": "active"})
            if transactions_col:
                total_transactions = transactions_col.count_documents({})
        except Exception as e:
            print(f"Error fetching statistics: {e}")
        
        return {
            "users": {
                "total": len(all_users),
                "regular_users": len([u for u in all_users if u.get("role") == "user"]),
                "support_agents": len([u for u in all_users if u.get("role") == "customer_support_agent"]),
                "admins": len([u for u in all_users if u.get("role") == "admin"])
            },
            "banking": {
                "total_accounts": total_accounts,
                "active_accounts": active_accounts,
                "total_transactions": total_transactions
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    except Exception as e:
        print(f"Statistics error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch statistics")

# ==================== SHARED ENDPOINTS ====================

@app.get("/conversation/{user_id}", tags=["Conversations"])
def get_user_conversation_endpoint(user_id: str, current_user: dict = Depends(require_support_or_admin)):
    """Get full conversation history for a specific user"""
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        conversation = get_user_conversation_history(user_id)
        return {
            "user_id": user_id,
            "conversation": conversation,
            "total_messages": len(conversation)
        }
    except Exception as e:
        print(f"User conversation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch conversation")

# ==================== STARTUP ====================

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting local development server...")
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
