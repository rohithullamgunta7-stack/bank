
# from fastapi import FastAPI, Depends, HTTPException, Request
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse
# from .models import MessageRequest, MessageResponse
# from .chat import get_bot_reply
# from .database import (
#     get_or_create_user, get_user_conversations, get_all_users, 
#     get_conversation_summaries, get_user_conversation_history, 
#     messages_collection
# )
# from .config import orders_col, refunds_col, mongo_connected, gemini_initialized
# from .auth import router as auth_router, get_current_user, require_admin, require_support_or_admin
# from .escalation import router as escalation_router
# from .faq import router as faq_router
# from .faq_learning import router as faq_learning_router
# from .feedback import router as feedback_router
# import time
# from datetime import datetime, timedelta

# app = FastAPI(
#     title="FoodHub Support API",
#     description="AI-Powered Food Delivery Customer Support System",
#     version="2.0.0"
# )

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Allow all origins for development
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Include routers
# app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
# app.include_router(escalation_router, prefix="/escalation", tags=["Escalation"])
# app.include_router(faq_router, prefix="/faq", tags=["FAQ Management"])
# app.include_router(faq_learning_router, prefix="/faq/learning", tags=["FAQ Learning"])
# app.include_router(feedback_router, prefix="/feedback", tags=["Feedback"])

# # Global exception handler
# @app.exception_handler(Exception)
# async def global_exception_handler(request: Request, exc: Exception):
#     """Handle uncaught exceptions gracefully"""
#     print(f"Unhandled exception: {exc}")
#     return JSONResponse(
#         status_code=500,
#         content={"detail": "Internal server error. Please try again later."}
#     )

# # ==================== SYSTEM ENDPOINTS ====================

# @app.get("/", tags=["System"])
# def root():
#     """API root endpoint"""
#     return {
#         "message": "FoodHub Support API - AI-Powered Food Delivery Chatbot",
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

# # ==================== USER ENDPOINTS ====================

# @app.post("/chat", response_model=MessageResponse, tags=["Chat"])
# def chat_endpoint(req: MessageRequest, current_user: dict = Depends(get_current_user)):
#     """Chat endpoint for food delivery support"""
#     if not mongo_connected:
#         raise HTTPException(status_code=503, detail="Database unavailable. Please try again later.")
    
#     if not gemini_initialized:
#         raise HTTPException(status_code=503, detail="AI service unavailable. Please try again later.")
    
#     try:
#         user = get_or_create_user(
#             current_user["email"], 
#             current_user.get("name"),
#             current_user.get("role", "user")
#         )
        
#         if not user or "user_id" not in user:
#             raise HTTPException(status_code=500, detail="User creation failed")
        
#         reply = get_bot_reply(
#             user["user_id"], 
#             req.message, 
#             current_user.get("role", "user")
#         )
        
#         if reply == "ORDER_LIST":
#             from .chat import get_order_list
#             orders_data, _ = get_order_list(user["user_id"])
            
#             return {
#                 "reply": "ORDER_LIST",
#                 "orders": orders_data if orders_data else []
#             }
        
#         return {"reply": reply}
    
#     except HTTPException:
#         raise
#     except Exception as e:
#         print(f"Chat endpoint error: {e}")
#         import traceback
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail="Failed to process message. Please try again.")

# @app.get("/my-orders", tags=["User"])
# def get_my_orders(current_user: dict = Depends(get_current_user)):
#     """Get current user's orders"""
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
        
#         orders = list(orders_col.find({"user_id": user["user_id"]}).sort("order_date", -1))
#         for order in orders:
#             order['_id'] = str(order['_id'])
        
#         return {"orders": orders}
#     except Exception as e:
#         print(f"My orders error: {e}")
#         raise HTTPException(status_code=500, detail="Failed to fetch orders")

# @app.get("/my-refunds", tags=["User"])
# def get_my_refunds(current_user: dict = Depends(get_current_user)):
#     """Get current user's refund requests"""
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
        
#         refunds = list(refunds_col.find({"user_id": user["user_id"]}).sort("request_time", -1))
        
#         for refund in refunds:
#             refund['_id'] = str(refund['_id'])
#             if 'request_time' in refund:
#                 try:
#                     if hasattr(refund['request_time'], 'isoformat'):
#                         refund['request_time'] = refund['request_time'].isoformat()
#                 except:
#                     pass
        
#         return {"refunds": refunds, "total": len(refunds)}
#     except Exception as e:
#         print(f"My refunds error: {e}")
#         raise HTTPException(status_code=500, detail="Failed to fetch refunds")

# @app.get("/my-conversations", tags=["User"])
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
#         return {"conversations": conversations}
    
#     except Exception as e:
#         print(f"My conversations error: {e}")
#         raise HTTPException(status_code=500, detail="Failed to fetch conversations")

# # ==================== DASHBOARD ENDPOINT ====================

# @app.get("/dashboard", tags=["Dashboard"])
# def get_dashboard_data(current_user: dict = Depends(get_current_user)):
#     """Get role-specific dashboard data"""
#     if not mongo_connected:
#         raise HTTPException(status_code=503, detail="Database unavailable")
    
#     try:
#         role = current_user.get("role", "user")
        
#         if role == "admin":
#             all_users = get_all_users()
#             summaries = get_conversation_summaries("admin", 10)
#             total_orders = orders_col.count_documents({})
#             total_refunds = refunds_col.count_documents({})
            
#             return {
#                 "role": role,
#                 "total_users": len(all_users),
#                 "total_orders": total_orders,
#                 "total_refunds": total_refunds,
#                 "conversation_summaries": summaries,
#                 "user_roles_count": {
#                     "user": len([u for u in all_users if u.get("role") == "user"]),
#                     "customer_support_agent": len([u for u in all_users if u.get("role") == "customer_support_agent"]),
#                     "admin": len([u for u in all_users if u.get("role") == "admin"])
#                 }
#             }
        
#         elif role == "customer_support_agent":
#             summaries = get_conversation_summaries("customer_support_agent", 20)
#             pending_refunds = refunds_col.count_documents({"status": "Pending"})
#             active_orders = orders_col.count_documents({"status": {"$in": ["Processing", "Preparing", "Out for Delivery"]}})
            
#             yesterday = datetime.utcnow() - timedelta(hours=24)
#             active_conversations = len(set([
#                 msg["user_id"] for msg in messages_collection.find(
#                     {"timestamp": {"$gte": yesterday}},
#                     {"user_id": 1}
#                 )
#             ]))
            
#             return {
#                 "role": role,
#                 "active_conversations": active_conversations,
#                 "active_orders": active_orders,
#                 "pending_refunds": pending_refunds,
#                 "conversation_summaries": summaries,
#                 "message": "Customer Support Dashboard"
#             }
        
#         else:
#             user = get_or_create_user(
#                 current_user["email"], 
#                 current_user.get("name"),
#                 role
#             )
            
#             my_conversations = get_user_conversations(role, user["user_id"])
#             my_orders_count = orders_col.count_documents({"user_id": user["user_id"]})
            
#             return {
#                 "role": role,
#                 "my_conversations_count": len(my_conversations),
#                 "my_orders_count": my_orders_count,
#                 "recent_conversations": my_conversations[:10],
#                 "message": "Welcome to FoodHub Support"
#             }
    
#     except Exception as e:
#         print(f"Dashboard error: {e}")
#         import traceback
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail="Failed to fetch dashboard data")

# # ==================== SUPPORT AGENT ENDPOINTS ====================

# @app.get("/support/conversations", tags=["Support"])
# def get_support_conversations(support_user: dict = Depends(require_support_or_admin)):
#     """Support agent endpoint to view user conversations"""
#     if not mongo_connected:
#         raise HTTPException(status_code=503, detail="Database unavailable")
    
#     try:
#         conversations = get_user_conversations("customer_support_agent")
#         return {"conversations": conversations, "total": len(conversations)}
#     except Exception as e:
#         print(f"Support conversations error: {e}")
#         raise HTTPException(status_code=500, detail="Failed to fetch conversations")

# @app.get("/support/conversation-summaries", tags=["Support"])
# def get_support_conversation_summaries(support_user: dict = Depends(require_support_or_admin)):
#     """Support agent endpoint to get conversation summaries"""
#     if not mongo_connected:
#         raise HTTPException(status_code=503, detail="Database unavailable")
    
#     try:
#         summaries = get_conversation_summaries("customer_support_agent")
#         return {"summaries": summaries, "total": len(summaries)}
#     except Exception as e:
#         print(f"Support conversation summaries error: {e}")
#         import traceback
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail="Failed to fetch conversation summaries")

# @app.get("/support/orders", tags=["Support"])
# def get_support_orders(support_user: dict = Depends(require_support_or_admin)):
#     """Support agent endpoint to view recent orders"""
#     if not mongo_connected:
#         raise HTTPException(status_code=503, detail="Database unavailable")
    
#     try:
#         orders = list(orders_col.find().sort("order_date", -1).limit(50))
#         for order in orders:
#             order['_id'] = str(order['_id'])
#         return {"orders": orders, "total": len(orders)}
#     except Exception as e:
#         print(f"Support orders error: {e}")
#         raise HTTPException(status_code=500, detail="Failed to fetch orders")

# @app.get("/support/refunds", tags=["Support"])
# def get_support_refunds(support_user: dict = Depends(require_support_or_admin)):
#     """Support agent endpoint to view refund requests"""
#     if not mongo_connected:
#         raise HTTPException(status_code=503, detail="Database unavailable")
    
#     try:
#         refunds = list(refunds_col.find().sort("request_time", -1).limit(50))
#         for refund in refunds:
#             refund['_id'] = str(refund['_id'])
#         return {"refunds": refunds, "total": len(refunds)}
#     except Exception as e:
#         print(f"Support refunds error: {e}")
#         raise HTTPException(status_code=500, detail="Failed to fetch refunds")

# # ==================== ADMIN ENDPOINTS ====================

# @app.get("/admin/orders", tags=["Admin"])
# def get_all_orders(admin_user: dict = Depends(require_admin)):
#     """Admin endpoint to view all orders"""
#     if not mongo_connected:
#         raise HTTPException(status_code=503, detail="Database unavailable")
    
#     try:
#         orders = list(orders_col.find().sort("order_date", -1).limit(100))
#         for order in orders:
#             order['_id'] = str(order['_id'])
#         return {"orders": orders, "total": len(orders)}
#     except Exception as e:
#         print(f"Admin orders error: {e}")
#         raise HTTPException(status_code=500, detail="Failed to fetch orders")

# @app.get("/admin/refunds", tags=["Admin"])
# def get_all_refunds(admin_user: dict = Depends(require_admin)):
#     """Admin endpoint to view all refunds"""
#     if not mongo_connected:
#         raise HTTPException(status_code=503, detail="Database unavailable")
    
#     try:
#         refunds = list(refunds_col.find().sort("request_time", -1).limit(100))
#         for refund in refunds:
#             refund['_id'] = str(refund['_id'])
#         return {"refunds": refunds, "total": len(refunds)}
#     except Exception as e:
#         print(f"Admin refunds error: {e}")
#         raise HTTPException(status_code=500, detail="Failed to fetch refunds")

# @app.get("/admin/conversations", tags=["Admin"])
# def get_all_conversations(admin_user: dict = Depends(require_admin)):
#     """Admin endpoint to view all conversations"""
#     if not mongo_connected:
#         raise HTTPException(status_code=503, detail="Database unavailable")
    
#     try:
#         conversations = get_user_conversations("admin")
#         return {"conversations": conversations, "total": len(conversations)}
#     except Exception as e:
#         print(f"Admin conversations error: {e}")
#         raise HTTPException(status_code=500, detail="Failed to fetch conversations")

# @app.get("/admin/conversation-summaries", tags=["Admin"])
# def get_admin_conversation_summaries(admin_user: dict = Depends(require_admin)):
#     """Admin endpoint to get conversation summaries"""
#     if not mongo_connected:
#         raise HTTPException(status_code=503, detail="Database unavailable")
    
#     try:
#         summaries = get_conversation_summaries("admin")
#         return {"summaries": summaries, "total": len(summaries)}
#     except Exception as e:
#         print(f"Admin conversation summaries error: {e}")
#         raise HTTPException(status_code=500, detail="Failed to fetch conversation summaries")

# # ==================== SHARED ENDPOINTS ====================

# @app.get("/conversation/{user_id}", tags=["Conversations"])
# def get_user_conversation(user_id: str, current_user: dict = Depends(require_support_or_admin)):
#     """Get full conversation history for a specific user"""
#     if not mongo_connected:
#         raise HTTPException(status_code=503, detail="Database unavailable")
    
#     try:
#         conversation = get_user_conversation_history(user_id)
#         return {"user_id": user_id, "conversation": conversation, "total_messages": len(conversation)}
#     except Exception as e:
#         print(f"User conversation error: {e}")
#         raise HTTPException(status_code=500, detail="Failed to fetch user conversation")

# # ==================== STARTUP ====================

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)


# main.py

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .models import MessageRequest, MessageResponse
from .chat import get_bot_reply
from .database import (
    get_or_create_user, get_user_conversations, get_all_users, 
    get_conversation_summaries, get_user_conversation_history, 
    messages_collection
)
from .config import orders_col, refunds_col, mongo_connected, gemini_initialized
from .auth import router as auth_router, get_current_user, require_admin, require_support_or_admin
from .escalation import router as escalation_router
from .faq import router as faq_router
from .faq_learning import router as faq_learning_router
from .feedback import router as feedback_router
import time
from datetime import datetime, timedelta

app = FastAPI(
    title="FoodHub Support API",
    description="AI-Powered Food Delivery Customer Support System",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(escalation_router, prefix="/escalation", tags=["Escalation"])
app.include_router(faq_router, prefix="/faq", tags=["FAQ Management"])
app.include_router(faq_learning_router, prefix="/faq/learning", tags=["FAQ Learning"])
app.include_router(feedback_router, prefix="/feedback", tags=["Feedback"])

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions gracefully"""
    print(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."}
    )

# ==================== SYSTEM ENDPOINTS ====================

@app.get("/", tags=["System"])
def root():
    """API root endpoint"""
    return {
        "message": "FoodHub Support API - AI-Powered Food Delivery Chatbot",
        "version": "2.0.0",
        "status": "operational",
        "documentation": "/docs"
    }

@app.get("/health", tags=["System"])
def health_check():
    """Check system health status"""
    return {
        "status": "healthy" if mongo_connected and gemini_initialized else "degraded",
        "database": "connected" if mongo_connected else "disconnected",
        "ai_service": "ready" if gemini_initialized else "unavailable",
        "timestamp": time.time()
    }

# ==================== USER ENDPOINTS ====================

@app.post("/chat", tags=["Chat"])  # Remove response_model restriction
def chat_endpoint(req: MessageRequest, current_user: dict = Depends(get_current_user)):
    """Chat endpoint for food delivery support"""
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable. Please try again later.")
    
    if not gemini_initialized:
        raise HTTPException(status_code=503, detail="AI service unavailable. Please try again later.")
    
    try:
        user = get_or_create_user(
            current_user["email"], 
            current_user.get("name"),
            current_user.get("role", "user")
        )
        
        if not user or "user_id" not in user:
            raise HTTPException(status_code=500, detail="User creation failed")
        
        reply = get_bot_reply(
            user["user_id"], 
            req.message, 
            current_user.get("role", "user")
        )
        
        # ✅ FIX: Check if reply is a dictionary (order list response)
        if isinstance(reply, dict):
            print(f"✅ Returning dictionary response: {reply}")
            return reply  # FastAPI will auto-convert to JSON
        
        # Regular string response
        print(f"✅ Returning text response: {reply[:100]}...")
        return {"reply": reply}
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Chat endpoint error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to process message. Please try again.")

@app.get("/my-orders", tags=["User"])
def get_my_orders(current_user: dict = Depends(get_current_user)):
    """Get current user's orders"""
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
        
        orders = list(orders_col.find({"user_id": user["user_id"]}).sort("order_date", -1))
        for order in orders:
            order['_id'] = str(order['_id'])
        
        return {"orders": orders}
    except Exception as e:
        print(f"My orders error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch orders")

@app.get("/my-refunds", tags=["User"])
def get_my_refunds(current_user: dict = Depends(get_current_user)):
    """Get current user's refund requests"""
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
        
        refunds = list(refunds_col.find({"user_id": user["user_id"]}).sort("request_time", -1))
        
        for refund in refunds:
            refund['_id'] = str(refund['_id'])
            if 'request_time' in refund:
                try:
                    if hasattr(refund['request_time'], 'isoformat'):
                        refund['request_time'] = refund['request_time'].isoformat()
                except:
                    pass
        
        return {"refunds": refunds, "total": len(refunds)}
    except Exception as e:
        print(f"My refunds error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch refunds")

@app.get("/my-conversations", tags=["User"])
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
        return {"conversations": conversations}
    
    except Exception as e:
        print(f"My conversations error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch conversations")

# ==================== DASHBOARD ENDPOINT ====================

@app.get("/dashboard", tags=["Dashboard"])
def get_dashboard_data(current_user: dict = Depends(get_current_user)):
    """Get role-specific dashboard data"""
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        role = current_user.get("role", "user")
        
        if role == "admin":
            all_users = get_all_users()
            # FIX: Added 'or []' to prevent TypeError if no summaries are returned
            summaries = get_conversation_summaries("admin", 10) or []
            total_orders = orders_col.count_documents({})
            total_refunds = refunds_col.count_documents({})
            
            return {
                "role": role,
                "total_users": len(all_users),
                "total_orders": total_orders,
                "total_refunds": total_refunds,
                "conversation_summaries": summaries,
                "user_roles_count": {
                    "user": len([u for u in all_users if u.get("role") == "user"]),
                    "customer_support_agent": len([u for u in all_users if u.get("role") == "customer_support_agent"]),
                    "admin": len([u for u in all_users if u.get("role") == "admin"])
                }
            }
        
        elif role == "customer_support_agent":
            # FIX: Added 'or []' to prevent TypeError if no summaries are returned
            summaries = get_conversation_summaries("customer_support_agent", 20) or []
            pending_refunds = refunds_col.count_documents({"status": "Pending"})
            active_orders = orders_col.count_documents({"status": {"$in": ["Processing", "Preparing", "Out for Delivery"]}})
            
            yesterday = datetime.utcnow() - timedelta(hours=24)
            active_conversations = len(set([
                msg["user_id"] for msg in messages_collection.find(
                    {"timestamp": {"$gte": yesterday}},
                    {"user_id": 1}
                )
            ]))
            
            return {
                "role": role,
                "active_conversations": active_conversations,
                "active_orders": active_orders,
                "pending_refunds": pending_refunds,
                "conversation_summaries": summaries,
                "message": "Customer Support Dashboard"
            }
        
        else:
            user = get_or_create_user(
                current_user["email"], 
                current_user.get("name"),
                role
            )
            
            my_conversations = get_user_conversations(role, user["user_id"])
            my_orders_count = orders_col.count_documents({"user_id": user["user_id"]})
            
            return {
                "role": role,
                "my_conversations_count": len(my_conversations),
                "my_orders_count": my_orders_count,
                "recent_conversations": my_conversations[:10],
                "message": "Welcome to FoodHub Support"
            }
    
    except Exception as e:
        print(f"Dashboard error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to fetch dashboard data")

# ==================== SUPPORT AGENT ENDPOINTS ====================

@app.get("/support/conversations", tags=["Support"])
def get_support_conversations(support_user: dict = Depends(require_support_or_admin)):
    """Support agent endpoint to view user conversations"""
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        conversations = get_user_conversations("customer_support_agent")
        return {"conversations": conversations, "total": len(conversations)}
    except Exception as e:
        print(f"Support conversations error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch conversations")

@app.get("/support/conversation-summaries", tags=["Support"])
def get_support_conversation_summaries(support_user: dict = Depends(require_support_or_admin)):
    """Support agent endpoint to get conversation summaries"""
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        # FIX: Added 'or []' to prevent TypeError if no summaries are returned
        summaries = get_conversation_summaries("customer_support_agent") or []
        return {"summaries": summaries, "total": len(summaries)}
    except Exception as e:
        print(f"Support conversation summaries error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to fetch conversation summaries")

@app.get("/support/orders", tags=["Support"])
def get_support_orders(support_user: dict = Depends(require_support_or_admin)):
    """Support agent endpoint to view recent orders"""
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        orders = list(orders_col.find().sort("order_date", -1).limit(50))
        for order in orders:
            order['_id'] = str(order['_id'])
        return {"orders": orders, "total": len(orders)}
    except Exception as e:
        print(f"Support orders error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch orders")

@app.get("/support/refunds", tags=["Support"])
def get_support_refunds(support_user: dict = Depends(require_support_or_admin)):
    """Support agent endpoint to view refund requests"""
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        refunds = list(refunds_col.find().sort("request_time", -1).limit(50))
        for refund in refunds:
            refund['_id'] = str(refund['_id'])
        return {"refunds": refunds, "total": len(refunds)}
    except Exception as e:
        print(f"Support refunds error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch refunds")

# ==================== ADMIN ENDPOINTS ====================

@app.get("/admin/orders", tags=["Admin"])
def get_all_orders(admin_user: dict = Depends(require_admin)):
    """Admin endpoint to view all orders"""
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        orders = list(orders_col.find().sort("order_date", -1).limit(100))
        for order in orders:
            order['_id'] = str(order['_id'])
        return {"orders": orders, "total": len(orders)}
    except Exception as e:
        print(f"Admin orders error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch orders")

@app.get("/admin/refunds", tags=["Admin"])
def get_all_refunds(admin_user: dict = Depends(require_admin)):
    """Admin endpoint to view all refunds"""
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        refunds = list(refunds_col.find().sort("request_time", -1).limit(100))
        for refund in refunds:
            refund['_id'] = str(refund['_id'])
        return {"refunds": refunds, "total": len(refunds)}
    except Exception as e:
        print(f"Admin refunds error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch refunds")

@app.get("/admin/conversations", tags=["Admin"])
def get_all_conversations(admin_user: dict = Depends(require_admin)):
    """Admin endpoint to view all conversations"""
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        conversations = get_user_conversations("admin")
        return {"conversations": conversations, "total": len(conversations)}
    except Exception as e:
        print(f"Admin conversations error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch conversations")

@app.get("/admin/conversation-summaries", tags=["Admin"])
def get_admin_conversation_summaries(admin_user: dict = Depends(require_admin)):
    """Admin endpoint to get conversation summaries"""
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        # FIX: Added 'or []' to prevent TypeError if no summaries are returned
        summaries = get_conversation_summaries("admin") or []
        return {"summaries": summaries, "total": len(summaries)}
    except Exception as e:
        print(f"Admin conversation summaries error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch conversation summaries")

# ==================== SHARED ENDPOINTS ====================

@app.get("/conversation/{user_id}", tags=["Conversations"])
def get_user_conversation(user_id: str, current_user: dict = Depends(require_support_or_admin)):
    """Get full conversation history for a specific user"""
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        conversation = get_user_conversation_history(user_id)
        return {"user_id": user_id, "conversation": conversation, "total_messages": len(conversation)}
    except Exception as e:
        print(f"User conversation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user conversation")

# ==================== STARTUP ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)