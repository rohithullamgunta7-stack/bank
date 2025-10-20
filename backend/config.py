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
MAX_RETRIES = 5

# Global variables
mongo_connected = False
db = None
mongo_client = None

users_collection = None
messages_collection = None
accounts_col = None
transactions_col = None
customers_col = None
feedback_collection = None
chat_sessions_collection = None
faq_collection = None
conversation_patterns_collection = None
escalations_collection = None
orders_col = None
refunds_col = None

def connect_mongodb(retry_count=0):
    global mongo_connected, db, mongo_client
    global users_collection, messages_collection, accounts_col, transactions_col
    global customers_col, feedback_collection, chat_sessions_collection
    global faq_collection, conversation_patterns_collection, escalations_collection
    global orders_col, refunds_col

    if not MONGO_URI:
        print("❌ ERROR: MONGO_URI environment variable not set!")
        return False

    try:
        print(f"🔄 Attempting MongoDB connection (attempt {retry_count + 1}/{MAX_RETRIES})...")
        
        mongo_client = MongoClient(
            MONGO_URI,
            tls=True,
            tlsAllowInvalidCertificates=True,
            tlsAllowInvalidHostnames=True,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=20000,
            socketTimeoutMS=20000,
            retryWrites=True,
            retryReads=True,
            maxPoolSize=10,
            minPoolSize=1
        )
        
        # Test the connection
        mongo_client.admin.command("ping")
        print("✅ MongoDB ping successful!")

        # Get database
        db = mongo_client.get_database()
        print(f"📦 Connected to database: {db.name}")
        
        # Initialize collections
        users_collection = db["users"]
        messages_collection = db["messages"]
        accounts_col = db["accounts"]
        transactions_col = db["transactions"]
        customers_col = db["customers"]
        feedback_collection = db["feedback"]
        chat_sessions_collection = db["chat_sessions"]
        faq_collection = db["faqs"]
        conversation_patterns_collection = db["conversation_patterns"]
        escalations_collection = db["escalations"]
        orders_col = db["orders"]
        refunds_col = db["refunds"]

        mongo_connected = True
        print("✅ All collections initialized successfully!")
        
        # Create indexes
        create_indexes()
        
        print("🎉 MongoDB connection fully established!")
        return True

    except Exception as e:
        print(f"❌ MongoDB connection failed: {type(e).__name__}: {str(e)}")
        
        if retry_count < MAX_RETRIES - 1:
            wait_time = 2 * (retry_count + 1)
            print(f"⏳ Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
            return connect_mongodb(retry_count + 1)
        
        print(f"❌ FATAL: Failed to connect to MongoDB after {MAX_RETRIES} attempts")
        mongo_connected = False
        return False

def create_indexes():
    if not mongo_connected:
        print("⚠️ Skipping index creation - MongoDB not connected")
        return
    
    try:
        print("🔐 Creating database indexes...")
        
        # Users indexes
        users_collection.create_index("email", unique=True)
        users_collection.create_index("user_id", unique=True, sparse=True) # Sparse index to avoid null conflicts
        users_collection.create_index("role")

        # Messages indexes
        messages_collection.create_index([("user_id", 1), ("timestamp", -1)])
        messages_collection.create_index("timestamp")

        # Accounts indexes
        accounts_col.create_index([("customer_id", 1)])
        accounts_col.create_index("account_number", unique=True)
        accounts_col.create_index("account_type")
        accounts_col.create_index("status")

        # Transactions indexes
        transactions_col.create_index([("account_id", 1), ("date", -1)])
        transactions_col.create_index("transaction_id", unique=True)
        transactions_col.create_index("status")
        transactions_col.create_index("type")

        # Customers indexes
        customers_col.create_index("email", unique=True)
        customers_col.create_index("kyc_status")
        customers_col.create_index("customer_tier")

        # Feedback indexes
        feedback_collection.create_index([("user_id", 1), ("submitted_at", -1)])
        feedback_collection.create_index("feedback_id", unique=True)
        feedback_collection.create_index("sentiment")
        feedback_collection.create_index("rating")
        feedback_collection.create_index("submitted_at")

        # Chat sessions indexes
        chat_sessions_collection.create_index([("user_id", 1), ("start_time", -1)])
        chat_sessions_collection.create_index("session_id", unique=True)
        chat_sessions_collection.create_index("feedback_submitted")

        # FAQ indexes
        # ✅ FIXED: Added sparse=True to ignore documents where faq_id is null
        faq_collection.create_index("faq_id", unique=True, sparse=True)
        faq_collection.create_index("category")
        faq_collection.create_index("tags")
        faq_collection.create_index("is_active")
        faq_collection.create_index("usage_count")
        faq_collection.create_index([("question", "text"), ("answer", "text")])
        
        # Conversation patterns indexes
        conversation_patterns_collection.create_index("pattern_id", unique=True)
        conversation_patterns_collection.create_index("approved")
        conversation_patterns_collection.create_index("occurrence_count")

        # Escalations indexes
        escalations_collection.create_index("escalation_id", unique=True)
        escalations_collection.create_index([("user_id", 1), ("created_at", -1)])
        escalations_collection.create_index("status")
        escalations_collection.create_index("assigned_to")

        print("✅ Database indexes created successfully!")

    except Exception as e:
        print(f"⚠️ Warning: Index creation failed: {str(e)}")
        pass
def ensure_mongodb_connection():
    """Helper function to ensure MongoDB is connected before operations"""
    global mongo_connected
    
    if not mongo_connected:
        print("⚠️ MongoDB not connected, attempting reconnection...")
        return connect_mongodb()
    
    # Test if connection is still alive
    try:
        mongo_client.admin.command("ping")
        return True
    except Exception as e:
        print(f"⚠️ MongoDB connection lost: {str(e)}, reconnecting...")
        mongo_connected = False
        return connect_mongodb()

# Initialize MongoDB connection
print("\n" + "="*60)
print("🚀 Initializing Banking Support System")
print("="*60)
connection_result = connect_mongodb()
if connection_result:
    print("="*60)
    print("✅ System initialization complete!")
    print("="*60 + "\n")
else:
    print("="*60)
    print("❌ WARNING: System started without MongoDB connection!")
    print("="*60 + "\n")

# Gemini AI Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
model = None

def initialize_gemini():
    global model
    if not GEMINI_API_KEY:
        print("⚠️ GEMINI_API_KEY not set")
        return False
    try:
        print("🤖 Initializing Gemini AI...")
        genai.configure(api_key=GEMINI_API_KEY, transport="rest")
        model = genai.GenerativeModel("models/gemini-flash-latest")
        print("✅ Gemini AI initialized successfully!")
        return True
    except Exception as e:
        print(f"❌ Gemini AI initialization failed: {str(e)}")
        return False

gemini_initialized = initialize_gemini()

# Application Configuration
APP_CONFIG = {
    "max_message_length": 1000,
    "max_messages_per_minute": 20,
    "session_timeout_minutes": 60,
    "max_login_attempts": 5,
    "login_lockout_minutes": 15,
}

def check_environment():
    """Check if all required environment variables are set"""
    required_vars = ["MONGO_URI", "GEMINI_API_KEY", "SECRET_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ All required environment variables are set")
    return True

check_environment()



