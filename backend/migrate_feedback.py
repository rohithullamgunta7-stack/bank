from .config import db, mongo_connected
from datetime import datetime, timezone

def migrate_feedback_schema():
    print("🔄 Starting feedback system migration...")

    if not mongo_connected or db is None:
        print("❌ MongoDB not connected")
        return
    
    try:
        if "feedback" not in db.list_collection_names():
            db.create_collection("feedback")
            print("✅ Created 'feedback' collection")
        
        if "chat_sessions" not in db.list_collection_names():
            db.create_collection("chat_sessions")
            print("✅ Created 'chat_sessions' collection")
        
        feedback_col = db["feedback"]
        sessions_col = db["chat_sessions"]
        
        feedback_col.create_index([("user_id", 1), ("submitted_at", -1)])
        feedback_col.create_index("feedback_id", unique=True)
        feedback_col.create_index("sentiment")
        feedback_col.create_index("rating")
        feedback_col.create_index("submitted_at")
        print("✅ Created feedback indexes")
        
        sessions_col.create_index([("user_id", 1), ("start_time", -1)])
        sessions_col.create_index("session_id", unique=True)
        sessions_col.create_index("feedback_submitted")
        print("✅ Created chat_sessions indexes")
        
        sample_feedback = {
            "feedback_id": f"FBK_{int(datetime.now(timezone.utc).timestamp())}",
            "user_id": "sample_user",
            "rating": 5,
            "comment": "Great service, very helpful!",
            "issue_resolved": True,
            "feedback_type": "bot_chat",
            "sentiment": "positive",
            "topics": ["service_quality", "helpfulness"],
            "key_phrases": ["great service", "very helpful"],
            "submitted_at": datetime.now(timezone.utc),
            "user_name": "Test User",
            "user_email": "test@example.com"
        }
        
        # feedback_col.insert_one(sample_feedback)
        # print("✅ Inserted sample feedback")
        
        print("\n🎉 Feedback system migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    migrate_feedback_schema()
