
from config import users_collection, messages_collection, mongo_connected
from datetime import datetime, timezone, timedelta

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
        # Ensure required fields exist
        updates = {}
        if "user_id" not in user:
            updates["user_id"] = f"user_{int(datetime.now(timezone.utc).timestamp())}"
            user["user_id"] = updates["user_id"]
        if "role" not in user:
            updates["role"] = "user"
            user["role"] = "user"
        if "created_at" not in user:
            updates["created_at"] = datetime.now(timezone.utc).isoformat()

        if updates:
            users_collection.update_one({"email": email}, {"$set": updates})
            user.update(updates)

        return user

def get_user_by_id(user_id):
    if not mongo_connected or users_collection is None:
        return {"user_id": "local_user", "name": "Guest", "email": "guest@example.com", "role": "user"}
    user = users_collection.find_one({"user_id": user_id})
    if user and "role" not in user:
        users_collection.update_one({"user_id": user_id}, {"$set": {"role": "user"}})
        user["role"] = "user"
    return user

def get_user_by_email(email):
    if not mongo_connected or users_collection is None:
        return {"user_id": "local_user", "name": "Guest", "email": "guest@example.com", "role": "user"}
    user = users_collection.find_one({"email": email})
    if user and "role" not in user:
        users_collection.update_one({"email": email}, {"$set": {"role": "user"}})
        user["role"] = "user"
    return user

def update_user_role(user_id, new_role):
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
    if not mongo_connected or users_collection is None:
        return []
    return list(users_collection.find({"role": role}, {"password": 0}))

def get_all_users(include_password=False):
    if not mongo_connected or users_collection is None:
        return []
    projection = {} if include_password else {"password": 0}
    return list(users_collection.find({}, projection))

def save_message(user_id, user_msg, bot_msg, agent_id=None, escalation_id=None):
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

        try:
            from chat import invalidate_cache
            invalidate_cache(user_id)
        except ImportError:
            pass
        return True
    except Exception as e:
        print(f"Error saving message: {e}")
        return False

def load_chat_history(user_id, limit=None):
    if not mongo_connected or messages_collection is None:
        return []
    try:
        query = messages_collection.find({"user_id": user_id}).sort("timestamp", 1)
        if limit:
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
        return history
    except Exception as e:
        print(f"Error loading chat history: {e}")
        return []

def get_user_conversations(user_role, user_id=None):
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
                    "user_id": summary["_id"],
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
    if not mongo_connected or users_collection is None or messages_collection is None:
        return {
            "total_users": 0,
            "total_agents": 0,
            "total_admins": 0,
            "total_messages": 0,
            "active_conversations": 0
        }
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
        return {
            "total_users": 0,
            "total_agents": 0,
            "total_admins": 0,
            "total_messages": 0,
            "active_conversations": 0
        }

def cleanup_old_messages(days=30):
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
                    "user_id": msg.get("user_id"),
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
