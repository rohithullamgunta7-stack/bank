
import os
import secrets
import time
from pymongo import MongoClient
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def get_secret_key(env_var_name, default_length=32):
    key = os.getenv(env_var_name)
    if not key:
        key = secrets.token_urlsafe(default_length)
    return key

SECRET_KEY = get_secret_key("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

ADMIN_SECRET_KEY = os.getenv("ADMIN_SECRET_KEY")
if not ADMIN_SECRET_KEY:
    ADMIN_SECRET_KEY = "CHANGE_THIS_IN_PRODUCTION_IMMEDIATELY"

MONGO_URI = os.getenv("MONGO_URI")
MAX_RETRIES = 3

mongo_connected = False
db = None

users_collection = None
messages_collection = None
orders_col = None
refunds_col = None
feedback_collection = None
chat_sessions_collection = None

def connect_mongodb(retry_count=0):
    global mongo_connected, db
    global users_collection, messages_collection, orders_col, refunds_col
    global feedback_collection, chat_sessions_collection

    if not MONGO_URI:
        return False

    try:
        client = MongoClient(
            MONGO_URI,
            tls=True,
            tlsAllowInvalidCertificates=True,
            tlsAllowInvalidHostnames=True,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000
        )
        client.admin.command("ping")

        db = client.get_database()
        users_collection = db["users"]
        messages_collection = db["messages"]
        orders_col = db["orders"]
        refunds_col = db["refunds"]
        feedback_collection = db["feedback"]
        chat_sessions_collection = db["chat_sessions"]

        mongo_connected = True
        create_indexes()
        return True

    except Exception as e:
        if retry_count < MAX_RETRIES - 1:
            time.sleep(2)
            return connect_mongodb(retry_count + 1)
        mongo_connected = False
        return False

def create_indexes():
    if not mongo_connected:
        return
    try:
        users_collection.create_index("email", unique=True)
        users_collection.create_index("user_id", unique=True)
        users_collection.create_index("role")

        messages_collection.create_index([("user_id", 1), ("timestamp", -1)])
        messages_collection.create_index("timestamp")

        orders_col.create_index([("user_id", 1), ("order_date", -1)])
        orders_col.create_index("order_id", unique=True)
        orders_col.create_index("status")

        refunds_col.create_index([("user_id", 1), ("request_time", -1)])
        refunds_col.create_index("refund_id", unique=True)
        refunds_col.create_index("status")

        feedback_collection.create_index([("user_id", 1), ("submitted_at", -1)])
        feedback_collection.create_index("feedback_id", unique=True)
        feedback_collection.create_index("sentiment")
        feedback_collection.create_index("rating")
        feedback_collection.create_index("submitted_at")

        chat_sessions_collection.create_index([("user_id", 1), ("start_time", -1)])
        chat_sessions_collection.create_index("session_id", unique=True)
        chat_sessions_collection.create_index("feedback_submitted")

    except Exception:
        pass

connect_mongodb()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
model = None

def initialize_gemini():
    global model
    if not GEMINI_API_KEY:
        return False
    try:
        genai.configure(api_key=GEMINI_API_KEY, transport="rest")
        model = genai.GenerativeModel("models/gemini-flash-latest")
        return True
    except Exception:
        return False

gemini_initialized = initialize_gemini()

APP_CONFIG = {
    "max_message_length": 1000,
    "max_messages_per_minute": 20,
    "session_timeout_minutes": 60,
    "max_login_attempts": 5,
    "login_lockout_minutes": 15,
}

def check_environment():
    required_vars = ["MONGO_URI", "GEMINI_API_KEY", "SECRET_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        return False
    return True
# Add these to the global variables section in config.py

faq_collection = None
conversation_patterns_collection = None

# Update the connect_mongodb function to include:
def connect_mongodb(retry_count=0):
    global mongo_connected, db
    global users_collection, messages_collection, orders_col, refunds_col
    global feedback_collection, chat_sessions_collection
    global faq_collection, conversation_patterns_collection  # ADD THIS LINE

    if not MONGO_URI:
        return False

    try:
        client = MongoClient(
            MONGO_URI,
            tls=True,
            tlsAllowInvalidCertificates=True,
            tlsAllowInvalidHostnames=True,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000
        )
        client.admin.command("ping")

        db = client.get_database()
        users_collection = db["users"]
        messages_collection = db["messages"]
        orders_col = db["orders"]
        refunds_col = db["refunds"]
        feedback_collection = db["feedback"]
        chat_sessions_collection = db["chat_sessions"]
        faq_collection = db["faqs"]  # ADD THIS LINE
        conversation_patterns_collection = db["conversation_patterns"]  # ADD THIS LINE

        mongo_connected = True
        create_indexes()
        return True

    except Exception as e:
        if retry_count < MAX_RETRIES - 1:
            time.sleep(2)
            return connect_mongodb(retry_count + 1)
        mongo_connected = False
        return False

# Update the create_indexes function to add:
def create_indexes():
    if not mongo_connected:
        return
    try:
        # ... existing indexes ...
        
        # FAQ indexes
        faq_collection.create_index("faq_id", unique=True)
        faq_collection.create_index("category")
        faq_collection.create_index("tags")
        faq_collection.create_index("is_active")
        faq_collection.create_index("usage_count")
        faq_collection.create_index([("question", "text"), ("answer", "text")])
        
        # Conversation patterns indexes
        conversation_patterns_collection.create_index("pattern_id", unique=True)
        conversation_patterns_collection.create_index("approved")
        conversation_patterns_collection.create_index("occurrence_count")

    except Exception:
        pass
check_environment()
