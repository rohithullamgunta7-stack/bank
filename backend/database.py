
# from config import users_collection, messages_collection, mongo_connected
# from config import accounts_col, transactions_col, customers_col, feedback_collection
# from config import chat_sessions_collection, faq_collection, escalations_collection
# from datetime import datetime, timezone, timedelta
# from bson import ObjectId

# # ==================== USER OPERATIONS ====================

# def get_or_create_user(email, name=None, role="user"):
#     """Get existing user or create new one with role support"""
#     if not mongo_connected or users_collection is None:
#         return {"user_id": "local_user", "name": "Guest", "email": "guest@example.com", "role": "user"}

#     user = users_collection.find_one({"email": email})
#     if not user:
#         user_id = f"user_{int(datetime.now(timezone.utc).timestamp())}"
#         user_doc = {
#             "user_id": user_id,
#             "name": name or "Guest",
#             "email": email,
#             "role": role,
#             "created_at": datetime.now(timezone.utc).isoformat()
#         }
#         users_collection.insert_one(user_doc)
#         return user_doc
#     else:
#         updates = {}
#         if "user_id" not in user or not user.get("user_id"):
#             updates["user_id"] = f"user_{int(datetime.now(timezone.utc).timestamp())}"
#             user["user_id"] = updates["user_id"]
#         if user.get("role") not in ["user", "customer_support_agent", "admin"]:
#             updates["role"] = "user"
#             user["role"] = "user"
#         if "created_at" not in user:
#             updates["created_at"] = datetime.now(timezone.utc).isoformat()

#         if updates:
#             users_collection.update_one({"email": email}, {"$set": updates})
#             user.update(updates)

#         return user


# def get_user_by_id(user_id):
#     """Retrieve user by user_id and ensure data integrity."""
#     if not mongo_connected or users_collection is None:
#         return {"user_id": "local_user", "name": "Guest", "email": "guest@example.com", "role": "user"}

#     user = users_collection.find_one({"user_id": user_id})

#     if user:
#         updates = {}
#         if "user_id" not in user or not user.get("user_id"):
#             new_user_id = f"user_{int(datetime.now(timezone.utc).timestamp())}"
#             updates["user_id"] = new_user_id
#             user["user_id"] = new_user_id
        
#         if user.get("role") not in ["user", "customer_support_agent", "admin"]:
#             updates["role"] = "user"
#             user["role"] = "user"
        
#         # ✅ FIX: Convert ALL datetime objects to strings
#         if "created_at" in user:
#             if isinstance(user["created_at"], datetime):
#                 user["created_at"] = user["created_at"].isoformat()
#             elif user["created_at"] is None:
#                 user["created_at"] = datetime.now(timezone.utc).isoformat()
#         else:
#             user["created_at"] = datetime.now(timezone.utc).isoformat()
#             updates["created_at"] = user["created_at"]
        
#         # Convert any other datetime fields
#         for key, value in user.items():
#             if isinstance(value, datetime):
#                 user[key] = value.isoformat()
        
#         if updates:
#             users_collection.update_one({"_id": user["_id"]}, {"$set": updates})

#     return user


# # ✅ NEW: Get customer details with verification info
# def get_customer_by_user_id(user_id):
#     """Get customer with verification details"""
#     if not mongo_connected or users_collection is None:
#         return None
        
#     try:
#         user = users_collection.find_one({"user_id": user_id})
#         if not user:
#             return None
                
#         # Get customer profile with phone and address
#         customer = customers_col.find_one({"email": user.get('email')})
                
#         if customer:
#             # Extract nested contact details
#             contact_details = customer.get('contact_details', {})
            
#             # Merge user and customer data
#             return {
#                 "user_id": user_id,
#                 "name": user.get('name', customer.get('full_name')),
#                 "email": user.get('email'),
#                 "phone_number": contact_details.get('mobile', 'Not Available'),
#                 "address": contact_details.get('address', 'Not Available'),
#                 "date_of_birth": customer.get('date_of_birth', 'Not Available'),
#                 "customer_id": str(customer.get('_id')),
#                 "kyc_status": customer.get('kyc_status', 'Unknown'),
#                 "customer_tier": customer.get('customer_tier', 'Unknown')
#             }
                
#         return user
#     except Exception as e:
#         print(f"Error getting customer: {e}")
#         return None


# def get_user_by_email(email):
#     """Retrieve user by email and ensure data integrity."""
#     if not mongo_connected or users_collection is None:
#         return {"user_id": "local_user", "name": "Guest", "email": "guest@example.com", "role": "user"}

#     user = users_collection.find_one({"email": email})

#     if user:
#         updates = {}
#         if "user_id" not in user or not user.get("user_id"):
#             new_user_id = f"user_{int(datetime.now(timezone.utc).timestamp())}"
#             updates["user_id"] = new_user_id
#             user["user_id"] = new_user_id
        
#         if user.get("role") not in ["user", "customer_support_agent", "admin"]:
#             updates["role"] = "user"
#             user["role"] = "user"
        
#         # ✅ FIX: Convert ALL datetime objects to strings
#         if "created_at" in user:
#             if isinstance(user["created_at"], datetime):
#                 user["created_at"] = user["created_at"].isoformat()
#             elif user["created_at"] is None:
#                 user["created_at"] = datetime.now(timezone.utc).isoformat()
#         else:
#             user["created_at"] = datetime.now(timezone.utc).isoformat()
#             updates["created_at"] = user["created_at"]
        
#         # Convert any other datetime fields
#         for key, value in user.items():
#             if isinstance(value, datetime):
#                 user[key] = value.isoformat()

#         if updates:
#             users_collection.update_one({"email": email}, {"$set": updates})
            
#     return user


# def update_user_role(user_id, new_role):
#     """Update user role (user, customer_support_agent, admin)"""
#     if not mongo_connected or users_collection is None:
#         return False
#     if new_role not in ["user", "customer_support_agent", "admin"]:
#         return False
#     result = users_collection.update_one(
#         {"user_id": user_id},
#         {"$set": {"role": new_role, "updated_at": datetime.now(timezone.utc).isoformat()}}
#     )
#     return result.modified_count > 0


# def get_users_by_role(role):
#     """Get all users with specific role"""
#     if not mongo_connected or users_collection is None:
#         return []
#     return list(users_collection.find({"role": role}, {"password": 0}))


# def get_all_users(include_password=False):
#     """Get all users"""
#     if not mongo_connected or users_collection is None:
#         return []
#     projection = {} if include_password else {"password": 0}
#     return list(users_collection.find({}, projection))


# # ==================== CUSTOMER OPERATIONS ====================

# def get_customer_by_email(email):
#     """Get customer profile by email"""
#     if not mongo_connected or customers_col is None:
#         return None
#     return customers_col.find_one({"email": email})


# def get_customer_accounts(customer_id):
#     """Get all accounts for a customer"""
#     if not mongo_connected or accounts_col is None:
#         return []
#     return list(accounts_col.find({"customer_id": ObjectId(customer_id)}))


# # ==================== ACCOUNT OPERATIONS ====================

# def get_account_by_id(account_id):
#     """Get account details by account ID"""
#     if not mongo_connected or accounts_col is None:
#         return None
#     try:
#         return accounts_col.find_one({"_id": ObjectId(account_id)})
#     except Exception as e:
#         print(f"Error fetching account: {e}")
#         return None


# def get_customer_all_accounts(customer_id):
#     """Get all accounts for a customer with formatted data"""
#     if not mongo_connected or accounts_col is None:
#         return []
#     try:
#         accounts = list(accounts_col.find({"customer_id": ObjectId(customer_id)}))
#         formatted_accounts = []
        
#         for acc in accounts:
#             account_info = {
#                 "account_id": str(acc["_id"]),
#                 "account_number": acc.get("account_number", "N/A"),
#                 "account_type": acc.get("account_type", "Unknown"),
#                 "balance": acc.get("balance", 0),
#                 "currency": acc.get("currency", "INR"),
#                 "status": acc.get("status", "Unknown"),
#                 "created_at": acc.get("created_at").strftime("%b %d, %Y") if acc.get("created_at") else "Unknown"
#             }
            
#             if acc.get("account_type") == "Credit Card":
#                 account_info["total_limit"] = acc.get("total_limit", 0)
#                 account_info["available_credit"] = acc.get("available_credit", 0)
#             elif acc.get("account_type") == "Home Loan":
#                 account_info["principal_amount"] = acc.get("principal_amount", 0)
#                 account_info["interest_rate"] = acc.get("interest_rate", 0)
#                 account_info["emi_amount"] = acc.get("emi_amount", 0)
#                 account_info["next_emi_due"] = acc.get("next_emi_due").strftime("%b %d, %Y") if acc.get("next_emi_due") else "N/A"
            
#             formatted_accounts.append(account_info)
        
#         return formatted_accounts
#     except Exception as e:
#         print(f"Error fetching accounts: {e}")
#         return []


# # ==================== TRANSACTION OPERATIONS ====================

# def get_account_transactions(account_id, limit=20):
#     """Get transactions for an account"""
#     if not mongo_connected or transactions_col is None:
#         return []
#     try:
#         return list(transactions_col.find(
#             {"account_id": ObjectId(account_id)}
#         ).sort("date", -1).limit(limit))
#     except Exception as e:
#         print(f"Error fetching transactions: {e}")
#         return []


# # ==================== MESSAGE OPERATIONS ====================

# def save_message(user_id, user_msg, bot_msg, agent_id=None, escalation_id=None):
#     """Save chat message to database"""
#     if not mongo_connected or messages_collection is None:
#         return False
#     try:
#         message_doc = {
#             "user_id": user_id,
#             "user": user_msg,
#             "bot": bot_msg,
#             "timestamp": datetime.now(timezone.utc),
#             "agent_id": agent_id,
#             "escalation_id": escalation_id
#         }
#         messages_collection.insert_one(message_doc)

#         try:
#             from chat import invalidate_cache
#             invalidate_cache(user_id)
#         except ImportError:
#             pass
#         return True
#     except Exception as e:
#         print(f"Error saving message: {e}")
#         return False


# def load_chat_history(user_id, limit=None):
#     """Load chat history for user"""
#     if not mongo_connected or messages_collection is None:
#         return []
#     try:
#         query = messages_collection.find({"user_id": user_id}).sort("timestamp", 1)
#         if limit:
#             query = query.limit(limit * 2)
#         docs = list(query)
#         history = []
#         for doc in docs:
#             user_content = doc.get("user", "")
#             bot_content = doc.get("bot", "")
#             timestamp = doc.get("timestamp", datetime.now(timezone.utc))
#             if user_content:
#                 history.append({"role": "user", "content": user_content, "timestamp": timestamp})
#             if bot_content:
#                 history.append({"role": "assistant", "content": bot_content, "timestamp": timestamp})
#         return history
#     except Exception as e:
#         print(f"Error loading chat history: {e}")
#         return []


# # ==================== CARD OPERATIONS ====================

# def block_card_temporary(account_id):
#     """Temporarily block card associated with account"""
#     if not mongo_connected or accounts_col is None:
#         return False, "Database unavailable"
    
#     try:
#         from bson import ObjectId
        
#         result = accounts_col.update_one(
#             {"_id": ObjectId(account_id)},
#             {
#                 "$set": {
#                     "card_status": "blocked_temporary",
#                     "card_blocked_at": datetime.now(timezone.utc),
#                     "card_blocked_reason": "User requested temporary block"
#                 }
#             }
#         )
        
#         if result.modified_count > 0:
#             return True, "Card temporarily blocked successfully"
#         else:
#             return False, "Failed to block card - account not found"
    
#     except Exception as e:
#         print(f"Error blocking card: {e}")
#         import traceback
#         traceback.print_exc()
#         return False, f"Error: {str(e)}"


# def unblock_card(account_id):
#     """Unblock a temporarily blocked card"""
#     if not mongo_connected or accounts_col is None:
#         return False, "Database unavailable"
    
#     try:
#         from bson import ObjectId
        
#         # Check if card is temporarily blocked
#         account = accounts_col.find_one({"_id": ObjectId(account_id)})
#         if not account:
#             return False, "Account not found"
        
#         if account.get("card_status") == "blocked_permanent":
#             return False, "Cannot unblock permanently cancelled card. Please contact support for a new card."
        
#         result = accounts_col.update_one(
#             {"_id": ObjectId(account_id)},
#             {
#                 "$set": {
#                     "card_status": "active",
#                     "card_unblocked_at": datetime.now(timezone.utc)
#                 }
#             }
#         )
        
#         if result.modified_count > 0:
#             return True, "Card unblocked successfully"
#         else:
#             return False, "Failed to unblock card"
    
#     except Exception as e:
#         print(f"Error unblocking card: {e}")
#         return False, f"Error: {str(e)}"


# def get_card_status(account_id):
#     """Get current card status for account"""
#     if not mongo_connected or accounts_col is None:
#         return None
    
#     try:
#         from bson import ObjectId
#         account = accounts_col.find_one({"_id": ObjectId(account_id)})
        
#         if not account:
#             return None
        
#         return {
#             "card_status": account.get("card_status", "active"),
#             "account_type": account.get("account_type"),
#             "account_number": account.get("account_number"),
#             "blocked_at": account.get("card_blocked_at"),
#             "blocked_reason": account.get("card_blocked_reason")
#         }
    
#     except Exception as e:
#         print(f"Error getting card status: {e}")
#         return None


# def block_card_permanent(account_id, agent_id, reason):
#     """Permanently block/cancel card (Agent only)"""
#     if not mongo_connected or accounts_col is None:
#         return False, "Database unavailable"
    
#     try:
#         from bson import ObjectId
        
#         result = accounts_col.update_one(
#             {"_id": ObjectId(account_id)},
#             {
#                 "$set": {
#                     "card_status": "blocked_permanent",
#                     "card_cancelled_at": datetime.now(timezone.utc),
#                     "card_cancelled_by": agent_id,
#                     "card_cancelled_reason": reason,
#                     "requires_new_card": True
#                 }
#             }
#         )
        
#         if result.modified_count > 0:
#             return True, "Card permanently cancelled"
#         else:
#             return False, "Failed to cancel card"
    
#     except Exception as e:
#         print(f"Error permanently blocking card: {e}")
#         return False, f"Error: {str(e)}"


# # ==================== CONVERSATION & OTHER OPERATIONS ====================
# # (Keep all other existing functions as they were)

# def get_user_conversations(user_role, user_id=None):
#     """Get conversations based on user role"""
#     if not mongo_connected or messages_collection is None:
#         return []
#     try:
#         if user_role == "admin":
#             return list(messages_collection.find({}).sort("timestamp", -1))
#         elif user_role == "customer_support_agent":
#             user_ids = [u["user_id"] for u in get_users_by_role("user")]
#             if not user_ids:
#                 return []
#             return list(messages_collection.find({"user_id": {"$in": user_ids}}).sort("timestamp", -1))
#         else:
#             if user_id:
#                 return list(messages_collection.find({"user_id": user_id}).sort("timestamp", -1))
#             return []
#     except Exception as e:
#         print(f"Error getting user conversations: {e}")
#         return []


# def get_conversation_summaries(user_role, limit=None):
#     """Get conversation summaries aggregated by user"""
#     if not mongo_connected or messages_collection is None:
#         return []
#     try:
#         if user_role == "admin":
#             user_filter = {}
#         elif user_role == "customer_support_agent":
#             user_ids_list = [u["user_id"] for u in get_users_by_role("user")]
#             if not user_ids_list:
#                 return []
#             user_filter = {"user_id": {"$in": user_ids_list}}
#         else:
#             return []

#         pipeline = [
#             {"$match": user_filter},
#             {"$sort": {"timestamp": -1}},
#             {"$group": {
#                 "_id": "$user_id",
#                 "message_count": {"$sum": 1},
#                 "last_message": {"$first": "$user"},
#                 "last_timestamp": {"$first": "$timestamp"},
#                 "first_timestamp": {"$last": "$timestamp"}
#             }}
#         ]
#         if limit:
#             pipeline.append({"$limit": limit})
        
#         summaries = list(messages_collection.aggregate(pipeline))
#         enriched_summaries = []
        
#         for summary in summaries:
#             user = get_user_by_id(summary["_id"])
#             if user:
#                 enriched_summaries.append({
#                     "user_id": user.get("user_id"),
#                     "user_name": user.get("name", "Unknown"),
#                     "user_email": user.get("email", "unknown@example.com"),
#                     "message_count": summary.get("message_count", 0),
#                     "last_message": (summary.get("last_message", "")[:100] + "...") if len(summary.get("last_message", "")) > 100 else summary.get("last_message", ""),
#                     "last_timestamp": summary["last_timestamp"].isoformat() if hasattr(summary.get("last_timestamp"), 'isoformat') else str(summary.get("last_timestamp", "")),
#                     "first_timestamp": summary["first_timestamp"].isoformat() if hasattr(summary.get("first_timestamp"), 'isoformat') else str(summary.get("first_timestamp", ""))
#                 })
        
#         enriched_summaries.sort(key=lambda x: x.get("last_timestamp", ""), reverse=True)
#         return enriched_summaries
#     except Exception as e:
#         print(f"Error getting conversation summaries: {e}")
#         return []


# def get_user_conversation_history(user_id):
#     """Get formatted conversation history for user"""
#     if not mongo_connected or messages_collection is None:
#         return []
#     try:
#         messages = list(messages_collection.find({"user_id": user_id}).sort("timestamp", 1))
#         conversation = []
#         for msg in messages:
#             conversation.append({
#                 "role": "user",
#                 "content": msg.get("user", ""),
#                 "timestamp": msg.get("timestamp", datetime.now(timezone.utc)).isoformat() if hasattr(msg.get("timestamp"), 'isoformat') else str(msg.get("timestamp"))
#             })
#             conversation.append({
#                 "role": "assistant",
#                 "content": msg.get("bot", ""),
#                 "timestamp": msg.get("timestamp", datetime.now(timezone.utc)).isoformat() if hasattr(msg.get("timestamp"), 'isoformat') else str(msg.get("timestamp"))
#             })
#         return conversation
#     except Exception as e:
#         print(f"Error getting user conversation history: {e}")
#         return []


# def get_active_conversations_count():
#     """Get count of active conversations in last 24 hours"""
#     if not mongo_connected or messages_collection is None:
#         return 0
#     try:
#         yesterday = datetime.now(timezone.utc) - timedelta(hours=24)
#         pipeline = [
#             {"$match": {"timestamp": {"$gte": yesterday}}},
#             {"$group": {"_id": "$user_id"}},
#             {"$count": "active_conversations"}
#         ]
#         result = list(messages_collection.aggregate(pipeline))
#         return result[0]["active_conversations"] if result else 0
#     except Exception as e:
#         print(f"Error getting active conversations count: {e}")
#         return 0


# def get_system_statistics():
#     """Get overall system statistics"""
#     if not mongo_connected or users_collection is None or messages_collection is None:
#         return {}
#     try:
#         stats = {
#             "total_users": users_collection.count_documents({"role": "user"}),
#             "total_agents": users_collection.count_documents({"role": "customer_support_agent"}),
#             "total_admins": users_collection.count_documents({"role": "admin"}),
#             "total_messages": messages_collection.count_documents({}),
#             "active_conversations": get_active_conversations_count()
#         }
#         return stats
#     except Exception as e:
#         print(f"Error getting system statistics: {e}")
#         return {}


# def cleanup_old_messages(days=30):
#     """Delete messages older than specified days"""
#     if not mongo_connected or messages_collection is None:
#         return 0
#     try:
#         cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
#         result = messages_collection.delete_many({"timestamp": {"$lt": cutoff_date}})
#         return result.deleted_count
#     except Exception as e:
#         print(f"Error cleaning up old messages: {e}")
#         return 0


# def search_conversations(query, user_role, limit=50):
#     """Search conversations by message content"""
#     if not mongo_connected or messages_collection is None:
#         return []
#     try:
#         search_filter = {
#             "$or": [
#                 {"user": {"$regex": query, "$options": "i"}},
#                 {"bot": {"$regex": query, "$options": "i"}}
#             ]
#         }
#         if user_role == "customer_support_agent":
#             user_ids = [u["user_id"] for u in get_users_by_role("user")]
#             search_filter["user_id"] = {"$in": user_ids}
#         elif user_role not in ["admin", "customer_support_agent"]:
#             return []
        
#         results = list(messages_collection.find(search_filter).sort("timestamp", -1).limit(limit))
#         enriched_results = []
        
#         for msg in results:
#             user = get_user_by_id(msg.get("user_id"))
#             if user:
#                 enriched_results.append({
#                     "user_id": user.get("user_id"),
#                     "user_name": user.get("name", "Unknown"),
#                     "user_email": user.get("email", "unknown@example.com"),
#                     "user_message": msg.get("user", ""),
#                     "bot_response": msg.get("bot", ""),
#                     "timestamp": msg.get("timestamp").isoformat() if hasattr(msg.get("timestamp"), 'isoformat') else str(msg.get("timestamp"))
#                 })
#         return enriched_results
#     except Exception as e:
#         print(f"Error searching conversations: {e}")
#         return []


# def save_feedback(user_id, rating, comment, session_id, issue_resolved):
#     """Save user feedback"""
#     if not mongo_connected or feedback_collection is None:
#         return False
#     try:
#         feedback_doc = {
#             "feedback_id": f"FB_{int(datetime.now(timezone.utc).timestamp())}",
#             "user_id": user_id,
#             "rating": rating,
#             "comment": comment,
#             "session_id": session_id,
#             "issue_resolved": issue_resolved,
#             "submitted_at": datetime.now(timezone.utc)
#         }
#         feedback_collection.insert_one(feedback_doc)
#         return True
#     except Exception as e:
#         print(f"Error saving feedback: {e}")
#         return False


# def get_user_feedback(user_id):
#     """Get all feedback submitted by user"""
#     if not mongo_connected or feedback_collection is None:
#         return []
#     try:
#         return list(feedback_collection.find({"user_id": user_id}).sort("submitted_at", -1))
#     except Exception as e:
#         print(f"Error fetching feedback: {e}")
#         return []


# def get_escalations_by_user(user_id):
#     """Get escalations for a user"""
#     if not mongo_connected or escalations_collection is None:
#         return []
#     try:
#         return list(escalations_collection.find({"user_id": user_id}).sort("created_at", -1))
#     except Exception as e:
#         print(f"Error fetching escalations: {e}")
#         return []


# def get_escalation_by_id(escalation_id):
#     """Get specific escalation"""
#     if not mongo_connected or escalations_collection is None:
#         return None
#     try:
#         return escalations_collection.find_one({"escalation_id": escalation_id})
#     except Exception as e:
#         print(f"Error fetching escalation: {e}")
#         return None





from datetime import datetime, timezone, timedelta
from bson import ObjectId
import traceback

# Corrected relative imports for your project files
from .config import users_collection, messages_collection, mongo_connected
from .config import accounts_col, transactions_col, customers_col, feedback_collection
from .config import chat_sessions_collection, faq_collection, escalations_collection


# ==================== USER OPERATIONS ====================

def get_or_create_user(email, name=None, role="user"):
    """Get existing user or create new one with role support"""
    if not mongo_connected or users_collection is None:
        return {"user_id": "local_user", "name": "Guest", "email": "guest@example.com", "role": "user"}

    user = users_collection.find_one({"email": email})
    if not user:
        user_id = f"user_{int(datetime.now(timezone.utc).timestamp())}"
        user_doc = {
            "user_id": user_id,
            "name": name or "Guest",
            "email": email,
            "role": role,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        users_collection.insert_one(user_doc)
        return user_doc
    else:
        updates = {}
        if "user_id" not in user or not user.get("user_id"):
            updates["user_id"] = f"user_{int(datetime.now(timezone.utc).timestamp())}"
            user["user_id"] = updates["user_id"]
        if user.get("role") not in ["user", "customer_support_agent", "admin"]:
            updates["role"] = "user"
            user["role"] = "user"
        if "created_at" not in user:
            updates["created_at"] = datetime.now(timezone.utc).isoformat()

        if updates:
            users_collection.update_one({"email": email}, {"$set": updates})
            user.update(updates)

        return user


def get_user_by_id(user_id):
    """Retrieve user by user_id and ensure data integrity."""
    if not mongo_connected or users_collection is None:
        return {"user_id": "local_user", "name": "Guest", "email": "guest@example.com", "role": "user"}

    user = users_collection.find_one({"user_id": user_id})

    if user:
        updates = {}
        if "user_id" not in user or not user.get("user_id"):
            new_user_id = f"user_{int(datetime.now(timezone.utc).timestamp())}"
            updates["user_id"] = new_user_id
            user["user_id"] = new_user_id
        
        if user.get("role") not in ["user", "customer_support_agent", "admin"]:
            updates["role"] = "user"
            user["role"] = "user"
        
        # ✅ FIX: Convert ALL datetime objects to strings
        if "created_at" in user:
            if isinstance(user["created_at"], datetime):
                user["created_at"] = user["created_at"].isoformat()
            elif user["created_at"] is None:
                user["created_at"] = datetime.now(timezone.utc).isoformat()
        else:
            user["created_at"] = datetime.now(timezone.utc).isoformat()
            updates["created_at"] = user["created_at"]
        
        # Convert any other datetime fields
        for key, value in user.items():
            if isinstance(value, datetime):
                user[key] = value.isoformat()
        
        if updates:
            users_collection.update_one({"_id": user["_id"]}, {"$set": updates})

    return user


# ✅ NEW: Get customer details with verification info
def get_customer_by_user_id(user_id):
    """Get customer with verification details"""
    if not mongo_connected or users_collection is None:
        return None
        
    try:
        user = users_collection.find_one({"user_id": user_id})
        if not user:
            return None
                
        # Get customer profile with phone and address
        customer = customers_col.find_one({"email": user.get('email')})
                
        if customer:
            # Extract nested contact details
            contact_details = customer.get('contact_details', {})
            
            # Merge user and customer data
            return {
                "user_id": user_id,
                "name": user.get('name', customer.get('full_name')),
                "email": user.get('email'),
                "phone_number": contact_details.get('mobile', 'Not Available'),
                "address": contact_details.get('address', 'Not Available'),
                "date_of_birth": customer.get('date_of_birth', 'Not Available'),
                "customer_id": str(customer.get('_id')),
                "kyc_status": customer.get('kyc_status', 'Unknown'),
                "customer_tier": customer.get('customer_tier', 'Unknown')
            }
                
        return user
    except Exception as e:
        print(f"Error getting customer: {e}")
        return None


def get_user_by_email(email):
    """Retrieve user by email and ensure data integrity."""
    if not mongo_connected or users_collection is None:
        return {"user_id": "local_user", "name": "Guest", "email": "guest@example.com", "role": "user"}

    user = users_collection.find_one({"email": email})

    if user:
        updates = {}
        if "user_id" not in user or not user.get("user_id"):
            new_user_id = f"user_{int(datetime.now(timezone.utc).timestamp())}"
            updates["user_id"] = new_user_id
            user["user_id"] = new_user_id
        
        if user.get("role") not in ["user", "customer_support_agent", "admin"]:
            updates["role"] = "user"
            user["role"] = "user"
        
        # ✅ FIX: Convert ALL datetime objects to strings
        if "created_at" in user:
            if isinstance(user["created_at"], datetime):
                user["created_at"] = user["created_at"].isoformat()
            elif user["created_at"] is None:
                user["created_at"] = datetime.now(timezone.utc).isoformat()
        else:
            user["created_at"] = datetime.now(timezone.utc).isoformat()
            updates["created_at"] = user["created_at"]
        
        # Convert any other datetime fields
        for key, value in user.items():
            if isinstance(value, datetime):
                user[key] = value.isoformat()

        if updates:
            users_collection.update_one({"email": email}, {"$set": updates})
            
    return user


def update_user_role(user_id, new_role):
    """Update user role (user, customer_support_agent, admin)"""
    if not mongo_connected or users_collection is None:
        return False
    if new_role not in ["user", "customer_support_agent", "admin"]:
        return False
    result = users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"role": new_role, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    return result.modified_count > 0


def get_users_by_role(role):
    """Get all users with specific role"""
    if not mongo_connected or users_collection is None:
        return []
    return list(users_collection.find({"role": role}, {"password": 0}))


def get_all_users(include_password=False):
    """Get all users"""
    if not mongo_connected or users_collection is None:
        return []
    projection = {} if include_password else {"password": 0}
    return list(users_collection.find({}, projection))


# ==================== CUSTOMER OPERATIONS ====================

def get_customer_by_email(email):
    """Get customer profile by email"""
    if not mongo_connected or customers_col is None:
        return None
    return customers_col.find_one({"email": email})


def get_customer_accounts(customer_id):
    """Get all accounts for a customer"""
    if not mongo_connected or accounts_col is None:
        return []
    return list(accounts_col.find({"customer_id": ObjectId(customer_id)}))


# ==================== ACCOUNT OPERATIONS ====================

def get_account_by_id(account_id):
    """Get account details by account ID"""
    if not mongo_connected or accounts_col is None:
        return None
    try:
        return accounts_col.find_one({"_id": ObjectId(account_id)})
    except Exception as e:
        print(f"Error fetching account: {e}")
        return None


def get_customer_all_accounts(customer_id):
    """Get all accounts for a customer with formatted data"""
    if not mongo_connected or accounts_col is None:
        return []
    try:
        accounts = list(accounts_col.find({"customer_id": ObjectId(customer_id)}))
        formatted_accounts = []
        
        for acc in accounts:
            account_info = {
                "account_id": str(acc["_id"]),
                "account_number": acc.get("account_number", "N/A"),
                "account_type": acc.get("account_type", "Unknown"),
                "balance": acc.get("balance", 0),
                "currency": acc.get("currency", "INR"),
                "status": acc.get("status", "Unknown"),
                "created_at": acc.get("created_at").strftime("%b %d, %Y") if acc.get("created_at") else "Unknown"
            }
            
            if acc.get("account_type") == "Credit Card":
                account_info["total_limit"] = acc.get("total_limit", 0)
                account_info["available_credit"] = acc.get("available_credit", 0)
            elif acc.get("account_type") == "Home Loan":
                account_info["principal_amount"] = acc.get("principal_amount", 0)
                account_info["interest_rate"] = acc.get("interest_rate", 0)
                account_info["emi_amount"] = acc.get("emi_amount", 0)
                account_info["next_emi_due"] = acc.get("next_emi_due").strftime("%b %d, %Y") if acc.get("next_emi_due") else "N/A"
            
            formatted_accounts.append(account_info)
        
        return formatted_accounts
    except Exception as e:
        print(f"Error fetching accounts: {e}")
        return []


# ==================== TRANSACTION OPERATIONS ====================

def get_account_transactions(account_id, limit=20):
    """Get transactions for an account"""
    if not mongo_connected or transactions_col is None:
        return []
    try:
        return list(transactions_col.find(
            {"account_id": ObjectId(account_id)}
        ).sort("date", -1).limit(limit))
    except Exception as e:
        print(f"Error fetching transactions: {e}")
        return []


# ==================== MESSAGE OPERATIONS ====================

def save_message(user_id, user_msg, bot_msg, agent_id=None, escalation_id=None):
    """Save chat message to database"""
    if not mongo_connected or messages_collection is None:
        return False
    try:
        message_doc = {
            "user_id": user_id,
            "user": user_msg,
            "bot": bot_msg,
            "timestamp": datetime.now(timezone.utc),
            "agent_id": agent_id,
            "escalation_id": escalation_id
        }
        messages_collection.insert_one(message_doc)
        
        #
        # ⚠️ CRITICAL FIX: Removed call to invalidate_cache() to prevent circular import
        #
        
        return True
    except Exception as e:
        print(f"Error saving message: {e}")
        return False


def load_chat_history(user_id, limit=None):
    """Load chat history for user"""
    if not mongo_connected or messages_collection is None:
        return []
    try:
        query = messages_collection.find({"user_id": user_id}).sort("timestamp", 1)
        if limit:
            # Fetch more to ensure we get user/bot pairs
            query = query.limit(limit * 2) 
        docs = list(query)
        history = []
        for doc in docs:
            user_content = doc.get("user", "")
            bot_content = doc.get("bot", "")
            timestamp = doc.get("timestamp", datetime.now(timezone.utc))
            if user_content:
                history.append({"role": "user", "content": user_content, "timestamp": timestamp})
            if bot_content:
                history.append({"role": "assistant", "content": bot_content, "timestamp": timestamp})
        
        # Return only the most recent 'limit' messages
        if limit:
            return history[-limit:]
        return history
    except Exception as e:
        print(f"Error loading chat history: {e}")
        return []


# ==================== CARD OPERATIONS ====================

def block_card_temporary(account_id):
    """Temporarily block card associated with account"""
    if not mongo_connected or accounts_col is None:
        return False, "Database unavailable"
    
    try:
        from bson import ObjectId
        
        result = accounts_col.update_one(
            {"_id": ObjectId(account_id)},
            {
                "$set": {
                    "card_status": "blocked_temporary",
                    "card_blocked_at": datetime.now(timezone.utc),
                    "card_blocked_reason": "User requested temporary block"
                }
            }
        )
        
        if result.modified_count > 0:
            return True, "Card temporarily blocked successfully"
        else:
            return False, "Failed to block card - account not found"
    
    except Exception as e:
        print(f"Error blocking card: {e}")
        traceback.print_exc()
        return False, f"Error: {str(e)}"


def unblock_card(account_id):
    """Unblock a temporarily blocked card"""
    if not mongo_connected or accounts_col is None:
        return False, "Database unavailable"
    
    try:
        from bson import ObjectId
        
        # Check if card is temporarily blocked
        account = accounts_col.find_one({"_id": ObjectId(account_id)})
        if not account:
            return False, "Account not found"
        
        if account.get("card_status") == "blocked_permanent":
            return False, "Cannot unblock permanently cancelled card. Please contact support for a new card."
        
        result = accounts_col.update_one(
            {"_id": ObjectId(account_id)},
            {
                "$set": {
                    "card_status": "active",
                    "card_unblocked_at": datetime.now(timezone.utc)
                }
            }
        )
        
        if result.modified_count > 0:
            return True, "Card unblocked successfully"
        else:
            return False, "Failed to unblock card"
    
    except Exception as e:
        print(f"Error unblocking card: {e}")
        return False, f"Error: {str(e)}"


def get_card_status(account_id):
    """Get current card status for account"""
    if not mongo_connected or accounts_col is None:
        return None
    
    try:
        from bson import ObjectId
        account = accounts_col.find_one({"_id": ObjectId(account_id)})
        
        if not account:
            return None
        
        return {
            "card_status": account.get("card_status", "active"),
            "account_type": account.get("account_type"),
            "account_number": account.get("account_number"),
            "blocked_at": account.get("card_blocked_at"),
            "blocked_reason": account.get("card_blocked_reason")
        }
    
    except Exception as e:
        print(f"Error getting card status: {e}")
        return None


def block_card_permanent(account_id, agent_id, reason):
    """Permanently block/cancel card (Agent only)"""
    if not mongo_connected or accounts_col is None:
        return False, "Database unavailable"
    
    try:
        from bson import ObjectId
        
        result = accounts_col.update_one(
            {"_id": ObjectId(account_id)},
            {
                "$set": {
                    "card_status": "blocked_permanent",
                    "card_cancelled_at": datetime.now(timezone.utc),
                    "card_cancelled_by": agent_id,
                    "card_cancelled_reason": reason,
                    "requires_new_card": True
                }
            }
        )
        
        if result.modified_count > 0:
            return True, "Card permanently cancelled"
        else:
            return False, "Failed to cancel card"
    
    except Exception as e:
        print(f"Error permanently blocking card: {e}")
        return False, f"Error: {str(e)}"


# ==================== CONVERSATION & OTHER OPERATIONS ====================

def get_user_conversations(user_role, user_id=None):
    """Get conversations based on user role"""
    if not mongo_connected or messages_collection is None:
        return []
    try:
        if user_role == "admin":
            return list(messages_collection.find({}).sort("timestamp", -1))
        elif user_role == "customer_support_agent":
            user_ids = [u["user_id"] for u in get_users_by_role("user")]
            if not user_ids:
                return []
            return list(messages_collection.find({"user_id": {"$in": user_ids}}).sort("timestamp", -1))
        else:
            if user_id:
                return list(messages_collection.find({"user_id": user_id}).sort("timestamp", -1))
            return []
    except Exception as e:
        print(f"Error getting user conversations: {e}")
        return []


def get_conversation_summaries(user_role, limit=None):
    """Get conversation summaries aggregated by user"""
    if not mongo_connected or messages_collection is None:
        return []
    try:
        if user_role == "admin":
            user_filter = {}
        elif user_role == "customer_support_agent":
            user_ids_list = [u["user_id"] for u in get_users_by_role("user")]
            if not user_ids_list:
                return []
            user_filter = {"user_id": {"$in": user_ids_list}}
        else:
            return []

        pipeline = [
            {"$match": user_filter},
            {"$sort": {"timestamp": -1}},
            {"$group": {
                "_id": "$user_id",
                "message_count": {"$sum": 1},
                "last_message": {"$first": "$user"},
                "last_timestamp": {"$first": "$timestamp"},
                "first_timestamp": {"$last": "$timestamp"}
            }}
        ]
        if limit:
            pipeline.append({"$limit": limit})
        
        summaries = list(messages_collection.aggregate(pipeline))
        enriched_summaries = []
        
        for summary in summaries:
            user = get_user_by_id(summary["_id"])
            if user:
                enriched_summaries.append({
                    "user_id": user.get("user_id"),
                    "user_name": user.get("name", "Unknown"),
                    "user_email": user.get("email", "unknown@example.com"),
                    "message_count": summary.get("message_count", 0),
                    "last_message": (summary.get("last_message", "")[:100] + "...") if len(summary.get("last_message", "")) > 100 else summary.get("last_message", ""),
                    "last_timestamp": summary["last_timestamp"].isoformat() if hasattr(summary.get("last_timestamp"), 'isoformat') else str(summary.get("last_timestamp", "")),
                    "first_timestamp": summary["first_timestamp"].isoformat() if hasattr(summary.get("first_timestamp"), 'isoformat') else str(summary.get("first_timestamp", ""))
                })
        
        enriched_summaries.sort(key=lambda x: x.get("last_timestamp", ""), reverse=True)
        return enriched_summaries
    except Exception as e:
        print(f"Error getting conversation summaries: {e}")
        return []


def get_user_conversation_history(user_id):
    """Get formatted conversation history for user"""
    if not mongo_connected or messages_collection is None:
        return []
    try:
        messages = list(messages_collection.find({"user_id": user_id}).sort("timestamp", 1))
        conversation = []
        for msg in messages:
            conversation.append({
                "role": "user",
                "content": msg.get("user", ""),
                "timestamp": msg.get("timestamp", datetime.now(timezone.utc)).isoformat() if hasattr(msg.get("timestamp"), 'isoformat') else str(msg.get("timestamp"))
            })
            conversation.append({
                "role": "assistant",
                "content": msg.get("bot", ""),
                "timestamp": msg.get("timestamp", datetime.now(timezone.utc)).isoformat() if hasattr(msg.get("timestamp"), 'isoformat') else str(msg.get("timestamp"))
            })
        return conversation
    except Exception as e:
        print(f"Error getting user conversation history: {e}")
        return []


def get_active_conversations_count():
    """Get count of active conversations in last 24 hours"""
    if not mongo_connected or messages_collection is None:
        return 0
    try:
        yesterday = datetime.now(timezone.utc) - timedelta(hours=24)
        pipeline = [
            {"$match": {"timestamp": {"$gte": yesterday}}},
            {"$group": {"_id": "$user_id"}},
            {"$count": "active_conversations"}
        ]
        result = list(messages_collection.aggregate(pipeline))
        return result[0]["active_conversations"] if result else 0
    except Exception as e:
        print(f"Error getting active conversations count: {e}")
        return 0


def get_system_statistics():
    """Get overall system statistics"""
    if not mongo_connected or users_collection is None or messages_collection is None:
        return {}
    try:
        stats = {
            "total_users": users_collection.count_documents({"role": "user"}),
            "total_agents": users_collection.count_documents({"role": "customer_support_agent"}),
            "total_admins": users_collection.count_documents({"role": "admin"}),
            "total_messages": messages_collection.count_documents({}),
            "active_conversations": get_active_conversations_count()
        }
        return stats
    except Exception as e:
        print(f"Error getting system statistics: {e}")
        return {}


def cleanup_old_messages(days=30):
    """Delete messages older than specified days"""
    if not mongo_connected or messages_collection is None:
        return 0
    try:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        result = messages_collection.delete_many({"timestamp": {"$lt": cutoff_date}})
        return result.deleted_count
    except Exception as e:
        print(f"Error cleaning up old messages: {e}")
        return 0


def search_conversations(query, user_role, limit=50):
    """Search conversations by message content"""
    if not mongo_connected or messages_collection is None:
        return []
    try:
        search_filter = {
            "$or": [
                {"user": {"$regex": query, "$options": "i"}},
                {"bot": {"$regex": query, "$options": "i"}}
            ]
        }
        if user_role == "customer_support_agent":
            user_ids = [u["user_id"] for u in get_users_by_role("user")]
            search_filter["user_id"] = {"$in": user_ids}
        elif user_role not in ["admin", "customer_support_agent"]:
            return []
        
        results = list(messages_collection.find(search_filter).sort("timestamp", -1).limit(limit))
        enriched_results = []
        
        for msg in results:
            user = get_user_by_id(msg.get("user_id"))
            if user:
                enriched_results.append({
                    "user_id": user.get("user_id"),
                    "user_name": user.get("name", "Unknown"),
                    "user_email": user.get("email", "unknown@example.com"),
                    "user_message": msg.get("user", ""),
                    "bot_response": msg.get("bot", ""),
                    "timestamp": msg.get("timestamp").isoformat() if hasattr(msg.get("timestamp"), 'isoformat') else str(msg.get("timestamp"))
                })
        return enriched_results
    except Exception as e:
        print(f"Error searching conversations: {e}")
        return []


def save_feedback(user_id, rating, comment, session_id, issue_resolved):
    """Save user feedback"""
    if not mongo_connected or feedback_collection is None:
        return False
    try:
        feedback_doc = {
            "feedback_id": f"FB_{int(datetime.now(timezone.utc).timestamp())}",
            "user_id": user_id,
            "rating": rating,
            "comment": comment,
            "session_id": session_id,
            "issue_resolved": issue_resolved,
            "submitted_at": datetime.now(timezone.utc)
        }
        feedback_collection.insert_one(feedback_doc)
        return True
    except Exception as e:
        print(f"Error saving feedback: {e}")
        return False


def get_user_feedback(user_id):
    """Get all feedback submitted by user"""
    if not mongo_connected or feedback_collection is None:
        return []
    try:
        return list(feedback_collection.find({"user_id": user_id}).sort("submitted_at", -1))
    except Exception as e:
        print(f"Error fetching feedback: {e}")
        return []


def get_escalations_by_user(user_id):
    """Get escalations for a user"""
    if not mongo_connected or escalations_collection is None:
        return []
    try:
        return list(escalations_collection.find({"user_id": user_id}).sort("created_at", -1))
    except Exception as e:
        print(f"Error fetching escalations: {e}")
        return []


def get_escalation_by_id(escalation_id):
    """Get specific escalation"""
    if not mongo_connected or escalations_collection is None:
        return None
    try:
        return escalations_collection.find_one({"escalation_id": escalation_id})
    except Exception as e:
        print(f"Error fetching escalation: {e}")
        return None