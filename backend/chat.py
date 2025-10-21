
# import time
# import re
# from datetime import datetime, timezone, timedelta
# from database import load_chat_history, save_message, get_user_by_id, messages_collection
# from config import db, model
# from escalation import should_escalate, create_escalation
# from faq_context import get_faq_context

# # In-memory session cache with context tracking
# session_cache = {}
# user_context = {}  # Track user's current context
# CACHE_DURATION = timedelta(minutes=15)
# CONTEXT_DURATION = timedelta(minutes=10)

# # Initialize collections
# chat_sessions_collection = db["chat_sessions"] if db is not None else None
# accounts_col = db["accounts"] if db is not None else None
# transactions_col = db["transactions"] if db is not None else None
# customers_col = db["customers"] if db is not None else None


# # ==================== CONTEXT MANAGEMENT ====================

# def set_user_context(user_id, context_type, context_data):
#     """Store user's current context (e.g., selected account)"""
#     user_context[user_id] = {
#         "type": context_type,
#         "data": context_data,
#         "timestamp": datetime.now(timezone.utc)
#     }


# def get_user_context(user_id):
#     """Retrieve user's current context if not expired"""
#     if user_id not in user_context:
#         return None
    
#     context = user_context[user_id]
#     if datetime.now(timezone.utc) - context["timestamp"] > CONTEXT_DURATION:
#         del user_context[user_id]
#         return None
    
#     return context


# def clear_user_context(user_id):
#     """Clear user's context"""
#     if user_id in user_context:
#         del user_context[user_id]


# # ==================== TRANSACTION HISTORY ====================

# def format_transaction_history(transactions, account_info):
#     """Format transactions for display"""
#     if not transactions:
#         return "No transactions found for this account."
    
#     account_type = account_info.get('account_type', 'Account')
#     account_number = account_info.get('account_number', 'N/A')
    
#     response = f"TRANSACTION HISTORY\n"
#     response += f"═══════════════════════════════\n"
#     response += f"{account_type}: {account_number}\n"
#     response += f"═══════════════════════════════\n\n"
    
#     for txn in transactions[:20]:  # Limit to 20 transactions
#         date = txn.get('date')
#         if isinstance(date, datetime):
#             date_str = date.strftime("%b %d, %Y %H:%M")
#         else:
#             date_str = str(date)[:16] if date else "Unknown"
        
#         description = txn.get('description', 'N/A')
#         amount = txn.get('amount', 0)
#         txn_type = txn.get('type', 'N/A')
#         status = txn.get('status', 'N/A')
#         merchant = txn.get('merchant_name', '')
        
#         # Format amount with +/- based on type
#         amount_str = f"+{amount:,.2f}" if txn_type == "Credit" else f"-{amount:,.2f}"
        
#         response += f"📅 {date_str}\n"
#         response += f"💳 {description}"
#         if merchant:
#             response += f" ({merchant})"
#         response += f"\n💰 INR {amount_str} | {status}\n"
#         response += f"─────────────────────────────\n"
    
#     if len(transactions) > 20:
#         response += f"\nShowing 20 of {len(transactions)} transactions.\n"
    
#     response += f"\n═══════════════════════════════"
#     return response


# def get_transaction_history(account_id, user_id):
#     """Fetch and format transaction history"""
#     if transactions_col is None or accounts_col is None:
#         return "System error: Database unavailable."
    
#     try:
#         from bson import ObjectId
        
#         # Verify account belongs to user
#         user_info = get_user_by_id(user_id)
#         customer = customers_col.find_one({"email": user_info.get('email')})
        
#         if not customer:
#             return "Customer profile not found."
        
#         account = accounts_col.find_one({
#             "_id": ObjectId(account_id),
#             "customer_id": customer["_id"]
#         })
        
#         if not account:
#             return "Account not found or you don't have access."
        
#         # Fetch transactions
#         transactions = list(transactions_col.find({
#             "account_id": ObjectId(account_id)
#         }).sort("date", -1))
        
#         return format_transaction_history(transactions, account)
        
#     except Exception as e:
#         print(f"Error fetching transaction history: {e}")
#         import traceback
#         traceback.print_exc()
#         return "Error fetching transaction history. Please try again."


# # ==================== EXISTING FUNCTIONS ====================

# def get_cached_history(user_id, limit=30):
#     """Retrieve recent conversation history from cache or database."""
#     now = datetime.now(timezone.utc)
#     if user_id in session_cache:
#         cached_data, timestamp = session_cache[user_id]
#         if now - timestamp < CACHE_DURATION:
#             return cached_data[:limit]

#     history = load_chat_history(user_id, limit=limit)
#     session_cache[user_id] = (history, now)
#     cleanup_cache()
#     return history


# def cleanup_cache():
#     """Remove expired cache entries."""
#     now = datetime.now(timezone.utc)
#     expired = [uid for uid, (_, ts) in session_cache.items() if now - ts > CACHE_DURATION]
#     for uid in expired:
#         del session_cache[uid]


# def invalidate_cache(user_id):
#     """Clear cache when new message is saved."""
#     if user_id in session_cache:
#         del session_cache[user_id]


# def get_or_create_session(user_id: str) -> str:
#     """Get current session or create new one"""
#     if chat_sessions_collection is None:
#         return f"SESSION_{int(datetime.now(timezone.utc).timestamp())}"
    
#     cutoff = datetime.now(timezone.utc) - timedelta(minutes=30)
#     active_session = chat_sessions_collection.find_one({
#         "user_id": user_id,
#         "end_time": None,
#         "start_time": {"$gte": cutoff}
#     })
    
#     if active_session:
#         return active_session["session_id"]
    
#     session_id = f"SESSION_{int(datetime.now(timezone.utc).timestamp())}"
#     session_doc = {
#         "session_id": session_id,
#         "user_id": user_id,
#         "start_time": datetime.now(timezone.utc),
#         "end_time": None,
#         "message_count": 0,
#         "escalated": False,
#         "feedback_submitted": False
#     }
#     chat_sessions_collection.insert_one(session_doc)
#     return session_id


# def update_session_message_count(session_id: str):
#     """Increment message count for session"""
#     if chat_sessions_collection is None:
#         return
    
#     chat_sessions_collection.update_one(
#         {"session_id": session_id},
#         {"$inc": {"message_count": 1}}
#     )


# def classify_user_intent(user_msg, history, user_name="there"):
#     """Use AI to classify user intent with smart goodbye detection"""
    
#     msg_lower = user_msg.lower().strip()
#     msg_words = msg_lower.split()
    
#     goodbye_exact = ['bye', 'goodbye', 'thanks', 'thank you', 'thankyou', 'done', 'ok', 'okay']
#     goodbye_starts = ['thanks for', 'thank you for', "that's all", 'all set', 'got it', 
#                       "i'm good", "im good", 'nothing else', "that's it", "thats it"]
    
#     # Check for UNBLOCK keywords FIRST (before block keywords)
#     unblock_keywords = ['unblock', 'unlock', 'enable card', 'activate card', 'unfreeze', 'reactivate']
#     if any(keyword in msg_lower for keyword in unblock_keywords):
#         return "CARD_UNBLOCK"
    
#     # Check for card blocking keywords (after unblock check)
#     block_keywords = ['block card', 'freeze card', 'disable card', 'deactivate card', 'lock card', 
#                       'suspend card', 'stop card', 'lost card', 'stolen card', 'block my card',
#                       'freeze my card', 'lost my card', 'stolen my card']
#     # Also check for standalone "block" or "freeze" but NOT if "unblock" was already checked
#     if any(keyword in msg_lower for keyword in block_keywords) or (
#         ('block' in msg_lower or 'freeze' in msg_lower or 'lost' in msg_lower or 'stolen' in msg_lower) 
#         and 'unblock' not in msg_lower
#     ):
#         return "CARD_BLOCK"
    
#     # Check for escalation/agent keywords
#     agent_keywords = ['agent', 'human', 'representative', 'support agent', 'talk to someone',
#                       'speak to', 'customer service', 'help me', 'need help', 'supervisor']
#     if any(keyword in msg_lower for keyword in agent_keywords):
#         return "ESCALATE_TO_AGENT"
    
#     # Check for transaction-related keywords
#     transaction_keywords = ['transaction', 'history', 'statement', 'transactions', 'purchases', 'payments']
#     if any(keyword in msg_lower for keyword in transaction_keywords):
#         return "TRANSACTION_HISTORY"
    
#     if '?' in user_msg:
#         pass
#     elif len(msg_words) <= 3:
#         if msg_lower in goodbye_exact:
#             return "CONVERSATION_END"
#     elif len(msg_words) <= 6:
#         for phrase in goodbye_starts:
#             if msg_lower.startswith(phrase):
#                 return "CONVERSATION_END"
    
#     last_bot_msg = ""
#     if history and len(history) > 0:
#         last_bot_msg = history[-1].get("content", "")[:200]
    
#     classification_prompt = f"""You are analyzing a user's message in a banking support chat.

# User message: "{user_msg}"
# Last assistant message: "{last_bot_msg}"

# Classify the user's PRIMARY INTENT into ONE category:

# GREETING - Starting conversation
# ACCOUNT_BALANCE - Wants to check account balance
# ACCOUNT_SELECTION - Selecting specific account
# TRANSACTION_HISTORY - Wants transaction history/statement
# ACCOUNT_DETAILS - Wants detailed account information
# CARD_BLOCK - Wants to block/freeze card (temporary or permanent)
# CARD_UNBLOCK - Wants to unblock/activate card
# ESCALATE_TO_AGENT - Wants to talk to human agent/support
# CARD_MANAGEMENT - Card-related questions
# LOAN_INFO - Loan questions
# PROFILE_INFO - Profile/personal details
# CONVERSATION_END - Ending conversation
# OTHER - Anything else

# Respond with ONLY the category name in uppercase."""

#     try:
#         response = model.generate_content(classification_prompt)
#         intent = response.text.strip().upper().replace(" ", "_")
#         print(f"[Intent] '{user_msg[:40]}...' -> {intent}")
#         return intent
#     except Exception as e:
#         print(f"Intent classification error: {e}")
#         return "OTHER"


# def parse_selection_number(user_msg, max_items=5):
#     """Parse selection number from various formats"""
#     msg = user_msg.lower().strip()
    
#     if msg.isdigit():
#         num = int(msg)
#         if 1 <= num <= max_items:
#             return num - 1
    
#     match = re.search(r'\b(\d+)\b', msg)
#     if match:
#         num = int(match.group(1))
#         if 1 <= num <= max_items:
#             return num - 1
    
#     words = {'first':0,'second':1,'third':2,'fourth':3,'fifth':4,'one':0,'two':1,'three':2,'four':3,'five':4}
#     for word, idx in words.items():
#         if word in msg and idx < max_items:
#             return idx
    
#     return None


# def get_account_list(user_id):
#     """Get account list formatted for frontend"""
#     if accounts_col is None:
#         return None, "System error: Database unavailable."

#     try:
#         user_info = get_user_by_id(user_id)
#         customer = customers_col.find_one({"email": user_info.get('email')})
        
#         if not customer:
#             return None, "Customer profile not found."
        
#         accounts = list(accounts_col.find({"customer_id": customer["_id"]}))
        
#         if not accounts:
#             return None, "You don't have any accounts yet."

#         accounts_data = []
#         for acc in accounts:
#             account_type = acc.get('account_type', 'Unknown')
            
#             account_info = {
#                 "account_id": str(acc['_id']),
#                 "account_number": acc.get('account_number', 'N/A'),
#                 "account_type": account_type,
#                 "balance": acc.get('balance', 0),
#                 "currency": acc.get('currency', 'INR'),
#                 "status": acc.get('status', 'Unknown'),
#                 "created_at": acc.get('created_at').strftime("%b %d, %Y") if acc.get('created_at') else "Unknown"
#             }
            
#             if account_type == "Credit Card":
#                 account_info["total_limit"] = acc.get('total_limit', 0)
#                 account_info["available_credit"] = acc.get('available_credit', 0)
#             elif account_type == "Home Loan":
#                 account_info["principal_amount"] = acc.get('principal_amount', 0)
#                 account_info["interest_rate"] = acc.get('interest_rate', 0)
#                 account_info["emi_amount"] = acc.get('emi_amount', 0)
#                 account_info["next_emi_due"] = acc.get('next_emi_due').strftime("%b %d, %Y") if acc.get('next_emi_due') else "N/A"
            
#             accounts_data.append(account_info)
        
#         return accounts_data, "ACCOUNT_LIST"
    
#     except Exception as e:
#         print(f"Error fetching accounts: {e}")
#         return None, "Error fetching accounts."


# def get_specific_account_details(account_id, user_id):
#     """Get detailed account information and store in context"""
#     if accounts_col is None:
#         return "System error: Database unavailable."

#     try:
#         from bson import ObjectId
        
#         user_info = get_user_by_id(user_id)
#         customer = customers_col.find_one({"email": user_info.get('email')})
        
#         if not customer:
#             return "Customer profile not found."
        
#         account = accounts_col.find_one({"_id": ObjectId(account_id), "customer_id": customer["_id"]})
        
#         if not account:
#             return "Account not found."

#         # Store account in context for future reference
#         set_user_context(user_id, "selected_account", {
#             "account_id": account_id,
#             "account_type": account.get('account_type'),
#             "account_number": account.get('account_number')
#         })

#         account_type = account.get('account_type', 'Unknown')
#         account_number = account.get('account_number', 'N/A')
#         balance = account.get('balance', 0)
#         currency = account.get('currency', 'INR')
#         status = account.get('status', 'Unknown')
#         created_date = account.get('created_at').strftime("%b %d, %Y") if account.get('created_at') else "Unknown"
        
#         response = f"""ACCOUNT DETAILS
# ═══════════════════════════════

# Account Number: {account_number}
# Account Type: {account_type}
# Status: {status}
# Opened On: {created_date}

# """
        
#         if account_type in ["Savings", "Checking"]:
#             response += f"Current Balance: {currency} {balance:,.2f}\n"
        
#         elif account_type == "Credit Card":
#             total_limit = account.get('total_limit', 0)
#             available_credit = account.get('available_credit', 0)
#             outstanding = account.get('balance', 0)
            
#             response += f"Total Limit: {currency} {total_limit:,.2f}\n"
#             response += f"Available Credit: {currency} {available_credit:,.2f}\n"
#             response += f"Outstanding: {currency} {outstanding:,.2f}\n"
        
#         elif account_type == "Home Loan":
#             principal = account.get('principal_amount', 0)
#             outstanding = account.get('balance', 0)
#             interest_rate = account.get('interest_rate', 0)
#             emi = account.get('emi_amount', 0)
#             next_due = account.get('next_emi_due').strftime("%b %d, %Y") if account.get('next_emi_due') else "N/A"
            
#             response += f"Principal: {currency} {principal:,.2f}\n"
#             response += f"Outstanding: {currency} {outstanding:,.2f}\n"
#             response += f"Interest Rate: {interest_rate}%\n"
#             response += f"EMI: {currency} {emi:,.2f}\n"
#             response += f"Next Due: {next_due}\n"
        
#         response += f"\n═══════════════════════════════"
#         response += f"\n\nWhat else would you like to know about this account?"
        
#         return response
    
#     except Exception as e:
#         print(f"Error fetching account details: {e}")
#         return "Error fetching account details."


# def get_bot_reply(user_id, user_msg, current_user_role="user", retry_count=0):
#     """Generate bot reply with context awareness"""
#     max_retries = 2
#     history = get_cached_history(user_id, limit=30)
#     user_info = get_user_by_id(user_id)
#     user_name = user_info.get("name","there") if user_info else "there"

#     try:
#         session_id = get_or_create_session(user_id)
#         update_session_message_count(session_id)
#     except Exception as e:
#         print(f"Session tracking error: {e}")

#     # Get current context
#     context = get_user_context(user_id)
    
#     # ==================== PRIORITY: Handle numeric selections in context ====================
#     # If user is in a selection context and sends a number, handle it immediately
#     if context and user_msg.strip().isdigit():
#         if context["type"] == "account_balance_selection":
#             try:
#                 from bson import ObjectId
                
#                 user_info_data = get_user_by_id(user_id)
#                 customer = customers_col.find_one({"email": user_info_data.get('email')})
                
#                 if customer:
#                     accounts = list(accounts_col.find({"customer_id": customer["_id"]}))
#                     idx = parse_selection_number(user_msg, len(accounts))
                    
#                     if idx is not None and idx < len(accounts):
#                         account_id = str(accounts[idx]['_id'])
#                         bot_msg = get_specific_account_details(account_id, user_id)
#                         # DON'T clear context - keep it for follow-up actions like transaction history
#                         save_message(user_id, user_msg, bot_msg)
#                         return bot_msg
#             except Exception as e:
#                 print(f"Error handling account selection: {e}")
#                 import traceback
#                 traceback.print_exc()
        
#         elif context["type"] == "transaction_history_selection":
#             try:
#                 from bson import ObjectId
                
#                 user_info_data = get_user_by_id(user_id)
#                 customer = customers_col.find_one({"email": user_info_data.get('email')})
                
#                 if customer:
#                     accounts = list(accounts_col.find({"customer_id": customer["_id"]}))
#                     idx = parse_selection_number(user_msg, len(accounts))
                    
#                     if idx is not None and idx < len(accounts):
#                         account_id = str(accounts[idx]['_id'])
                        
#                         # Set context for future transaction requests
#                         set_user_context(user_id, "selected_account", {
#                             "account_id": account_id,
#                             "account_type": accounts[idx].get('account_type'),
#                             "account_number": accounts[idx].get('account_number')
#                         })
                        
#                         bot_msg = get_transaction_history(account_id, user_id)
#                         save_message(user_id, user_msg, bot_msg)
#                         return bot_msg
#             except Exception as e:
#                 print(f"Error handling transaction history selection: {e}")
#                 import traceback
#                 traceback.print_exc()
    
#     # Classify intent
#     intent = classify_user_intent(user_msg, history, user_name)
    
#     # ==================== CONTEXT-SPECIFIC FLOWS ====================
    
#     # Handle card block account selection (ONLY if explicitly in card block flow)
#     if context and context["type"] == "card_block_account_selection":
#         try:
#             user_info_data = get_user_by_id(user_id)
#             customer = customers_col.find_one({"email": user_info_data.get('email')})
            
#             if customer:
#                 all_accounts = list(accounts_col.find({"customer_id": customer["_id"]}))
#                 card_accounts = [
#                     acc for acc in all_accounts 
#                     if acc.get('account_type') in ['Credit Card', 'Savings', 'Checking']
#                 ]
                
#                 idx = parse_selection_number(user_msg, len(card_accounts))
#                 if idx is not None and idx < len(card_accounts):
#                     account = card_accounts[idx]
#                     account_id = str(account['_id'])
#                     account_number = account.get('account_number', 'N/A')
#                     account_type = account.get('account_type', 'Account')
                    
#                     if account_type == 'Credit Card':
#                         card_type = "Credit Card"
#                     elif account_type in ['Savings', 'Checking']:
#                         card_type = "Debit Card"
#                     else:
#                         card_type = "Card"
                    
#                     set_user_context(user_id, "card_block_pending", {
#                         "account_id": account_id,
#                         "account_number": account_number,
#                         "account_type": account_type,
#                         "card_type": card_type
#                     })
                    
#                     bot_msg = (
#                         f"You selected: {card_type} (Account: {account_number})\n\n"
#                         f"Please choose:\n"
#                         f"1️⃣ Temporary Block (you can unblock later)\n"
#                         f"2️⃣ Permanent Block (card will be cancelled)\n"
#                         f"3️⃣ Talk to Support Agent\n\n"
#                         f"Reply with 1, 2, or 3."
#                     )
#                     save_message(user_id, user_msg, bot_msg)
#                     return bot_msg
#         except Exception as e:
#             print(f"Error in card block selection: {e}")
#             import traceback
#             traceback.print_exc()

#     # Handle card block confirmation
#     elif context and context["type"] == "card_block_pending":
#         if user_msg.strip() in ["1", "2", "3", "temporary", "permanent", "agent"]:
#             card_type = context['data'].get('card_type', 'Card')
#             account_number = context['data']['account_number']
#             account_id = context['data']['account_id']
            
#             if user_msg.strip() in ["1", "temporary"]:
#                 from database import block_card_temporary
                
#                 success, message = block_card_temporary(account_id)
                
#                 if success:
#                     bot_msg = (
#                         f"🔒 **CARD TEMPORARILY BLOCKED**\n\n"
#                         f"Your {card_type} (Account: {account_number}) is now blocked.\n\n"
#                         f"**What this means:**\n"
#                         f"❌ Cannot make purchases or withdrawals\n"
#                         f"❌ ATM transactions disabled\n"
#                         f"✅ Account balance is SAFE\n"
#                         f"✅ You can still receive deposits\n"
#                         f"✅ Can be unblocked anytime by YOU\n\n"
#                         f"**To unblock:**\n"
#                         f"• Tell me 'unblock my card'\n"
#                         f"• Use mobile app\n"
#                         f"• Call: 1-800-BANK-HELP\n"
#                         f"• Visit any branch\n\n"
#                         f"Is there anything else I can help you with?"
#                     )
#                 else:
#                     bot_msg = f"Sorry, I couldn't block the card. Error: {message}\n\nPlease try again or contact support."
                
#                 clear_user_context(user_id)
#                 save_message(user_id, user_msg, bot_msg)
#                 return bot_msg
            
#             elif user_msg.strip() in ["2", "permanent"]:
#                 # ✅ Get full account and customer details for verification
#                 from bson import ObjectId
#                 from database import get_customer_by_user_id

#                 # Get account details
#                 account = accounts_col.find_one({"_id": ObjectId(account_id)})

#                 # Get customer verification details
#                 user_details = get_customer_by_user_id(user_id)
#                 if not user_details:
#                     user_details = user_info  # Fallback to basic user info

#                 # Format account creation date
#                 account_created_at = "N/A"
#                 if account and account.get('created_at'):
#                     try:
#                         if isinstance(account.get('created_at'), datetime):
#                             account_created_at = account.get('created_at').strftime("%b %d, %Y")
#                         else:
#                             account_created_at = str(account.get('created_at'))[:16]
#                     except:
#                         account_created_at = "N/A"

#                 # Create escalation with full verification details
#                 escalation_id = create_escalation(
#                     user_id,
#                     f"URGENT: User requested PERMANENT card cancellation - {card_type} - Account {account_number}",
#                     {
#                         "account_id": account_id,
#                         "account_number": account_number,
#                         "account_type": context['data']['account_type'],
#                         "card_type": card_type,
#                         "block_type": "permanent",
#                         "priority": "high",
#                         "requires_verification": True,
#                         "action_required": "Verify identity and permanently cancel card",
#                         # ✅ CUSTOMER VERIFICATION DETAILS
#                         "user_name": user_details.get('name', user_name),
#                         "user_email": user_details.get('email', 'N/A'),
#                         "phone_number": user_details.get('phone_number', 'Not Available'),
#                         "address": user_details.get('address', 'Not Available'),
#                         "customer_id": user_details.get('customer_id', user_id),
#                         "account_created_at": account_created_at,
#                         # Additional verification info (if available)
#                         "kyc_status": user_details.get('kyc_status', 'Unknown'),
#                         "customer_tier": user_details.get('customer_tier', 'Unknown'),
#                         "date_of_birth": user_details.get('date_of_birth', 'Not Available')
#                     }
#                 )

#                 bot_msg = (
#                     f"⚠️ **PERMANENT CARD CANCELLATION REQUEST**\n\n"
#                     f"**IMPORTANT - This action requires agent verification:**\n\n"
#                     f"**Temporary vs Permanent:**\n"
#                     f"🔄 **Temporary Block:**\n"
#                     f"   • YOU can unblock anytime\n"
#                     f"   • Same card number\n"
#                     f"   • Instant process\n\n"
#                     f"🚫 **Permanent Cancellation:**\n"
#                     f"   • Card is DESTROYED\n"
#                     f"   • Cannot be unblocked EVER\n"
#                     f"   • New card with NEW number needed\n"
#                     f"   • Requires agent verification\n"
#                     f"   • Takes 7-10 business days for new card\n\n"
#                     f"**Why agent verification?**\n"
#                     f"Security protection - prevents unauthorized cancellation\n\n"
#                     f"Case ID: {escalation_id[:12]} (Priority: HIGH)\n\n"
#                     f"👉 Click 'Talk to Human Agent' button above NOW.\n"
#                     f"An agent will verify your identity and complete the cancellation."
#                 )

#                 clear_user_context(user_id)
#                 save_message(user_id, user_msg, bot_msg)
#                 return {
#                     "reply": bot_msg,
#                     "escalation_id": escalation_id,
#                     "escalated": True
#                 }
            
#             elif user_msg.strip() in ["3", "agent"]:
#                 escalation_id = create_escalation(
#                     user_id,
#                     f"User requested agent help for {card_type} blocking - Account {account_number}",
#                     {
#                         "account_id": account_id,
#                         "account_number": account_number,
#                         "account_type": context['data']['account_type'],
#                         "card_type": card_type
#                     }
#                 )
                
#                 bot_msg = (
#                     f"I've connected you with a support agent.\n\n"
#                     f"They can help you with:\n"
#                     f"• Card blocking questions\n"
#                     f"• Report lost/stolen card\n"
#                     f"• Dispute transactions\n"
#                     f"• Order new card\n\n"
#                     f"Case ID: {escalation_id[:12]}\n\n"
#                     f"👉 Click 'Talk to Human Agent' button above."
#                 )
                
#                 clear_user_context(user_id)
#                 save_message(user_id, user_msg, bot_msg)
#                 return {
#                     "reply": bot_msg,
#                     "escalation_id": escalation_id,
#                     "escalated": True
#                 }

#     # Handle card unblock selection
#     elif context and context["type"] == "card_unblock_selection":
#         try:
#             accounts = context['data']['accounts']
#             idx = parse_selection_number(user_msg, len(accounts))
            
#             if idx is not None and idx < len(accounts):
#                 from database import unblock_card
#                 from bson import ObjectId
#                 account_id = accounts[idx]
                
#                 success, message = unblock_card(account_id)
                
#                 if success:
#                     account = accounts_col.find_one({"_id": ObjectId(account_id)})
#                     bot_msg = (
#                         f"✅ **CARD UNBLOCKED**\n\n"
#                         f"Your {account.get('account_type')} card (Account: {account.get('account_number')}) "
#                         f"is now ACTIVE.\n\n"
#                         f"You can now:\n"
#                         f"✅ Make purchases\n"
#                         f"✅ Withdraw cash from ATMs\n"
#                         f"✅ Use online transactions\n\n"
#                         f"Stay safe! If you didn't request this, contact us immediately."
#                     )
#                 else:
#                     bot_msg = f"Failed to unblock card: {message}"
                
#                 clear_user_context(user_id)
#                 save_message(user_id, user_msg, bot_msg)
#                 return bot_msg
#         except Exception as e:
#             print(f"Error unblocking card: {e}")
#             import traceback
#             traceback.print_exc()

#     # ==================== INTENT-BASED FLOWS ====================
    
#     if intent == "CARD_UNBLOCK":
#         try:
#             from database import unblock_card
#             from bson import ObjectId
#             user_info_data = get_user_by_id(user_id)
#             customer = customers_col.find_one({"email": user_info_data.get('email')})
            
#             if customer:
#                 accounts = list(accounts_col.find({
#                     "customer_id": customer["_id"],
#                     "card_status": "blocked_temporary"
#                 }))
                
#                 if not accounts:
#                     bot_msg = (
#                         "You don't have any temporarily blocked cards.\n\n"
#                         "If you need to unblock a permanently cancelled card, "
#                         "you'll need to apply for a new card. Would you like help with that?"
#                     )
#                     save_message(user_id, user_msg, bot_msg)
#                     return bot_msg
                
#                 if len(accounts) == 1:
#                     account = accounts[0]
#                     success, message = unblock_card(str(account['_id']))
                    
#                     if success:
#                         bot_msg = (
#                             f"✅ **CARD UNBLOCKED**\n\n"
#                             f"Your {account.get('account_type')} card (Account: {account.get('account_number')}) "
#                             f"is now ACTIVE.\n\n"
#                             f"You can now:\n"
#                             f"✅ Make purchases\n"
#                             f"✅ Withdraw cash from ATMs\n"
#                             f"✅ Use online transactions\n\n"
#                             f"Stay safe! If you didn't request this, contact us immediately."
#                         )
#                     else:
#                         bot_msg = f"Failed to unblock card: {message}"
                    
#                     save_message(user_id, user_msg, bot_msg)
#                     return bot_msg
#                 else:
#                     bot_msg = "You have multiple blocked cards. Which one would you like to unblock?\n\n"
#                     for idx, acc in enumerate(accounts, 1):
#                         bot_msg += f"{idx}. {acc.get('account_type')} - {acc.get('account_number')}\n"
#                     bot_msg += "\nReply with the number."
                    
#                     set_user_context(user_id, "card_unblock_selection", {
#                         "accounts": [str(acc['_id']) for acc in accounts]
#                     })
                    
#                     save_message(user_id, user_msg, bot_msg)
#                     return bot_msg
            
#         except Exception as e:
#             print(f"Error unblocking card: {e}")
#             import traceback
#             traceback.print_exc()
#             bot_msg = "Error unblocking card. Please contact support."
#             save_message(user_id, user_msg, bot_msg)
#             return bot_msg
    
#     elif intent == "ESCALATE_TO_AGENT":
#         try:
#             escalation_id = create_escalation(
#                 user_id, 
#                 "User requested to speak with support agent",
#                 {"recent_messages": history[-10:], "user_name": user_name}
#             )
            
#             bot_msg = (
#                 f"I understand you'd like to speak with a support agent. "
#                 f"I've created a support case for you (Case ID: {escalation_id[:12]}).\n\n"
#                 f"Please click the 'Talk to Human Agent' button above to connect with our support team. "
#                 f"An agent will be with you shortly!"
#             )
#             save_message(user_id, user_msg, bot_msg)
#             return {
#                 "reply": bot_msg,
#                 "escalation_id": escalation_id,
#                 "escalated": True
#             }
#         except Exception as e:
#             print(f"Escalation error: {e}")
#             bot_msg = "I'm having trouble connecting you to an agent. Please try again in a moment."
#             save_message(user_id, user_msg, bot_msg)
#             return bot_msg
    
#     elif intent == "CARD_BLOCK":
#         try:
#             accounts_data, msg = get_account_list(user_id)
#             if accounts_data:
#                 card_accounts = [
#                     acc for acc in accounts_data 
#                     if acc["account_type"] in ["Credit Card", "Savings", "Checking"]
#                 ]
                
#                 if card_accounts:
#                     for acc in card_accounts:
#                         if acc["account_type"] == "Credit Card":
#                             acc["display_name"] = "Credit Card"
#                         elif acc["account_type"] in ["Savings", "Checking"]:
#                             acc["display_name"] = f"{acc['account_type']} (Debit Card)"
                    
#                     bot_msg = (
#                         "I can help you block a card. Please select the account:\n\n"
#                         "💳 This will block the card linked to the selected account.\n"
#                         "Note: Blocking the card will NOT affect your account balance."
#                     )
                    
#                     set_user_context(user_id, "card_block_account_selection", {
#                         "action": "card_block"
#                     })
                    
#                     save_message(user_id, user_msg, "Displaying card accounts for blocking")
#                     return {
#                         "reply": "ACCOUNT_LIST",
#                         "accounts": card_accounts,
#                         "action": "card_block"
#                     }
#                 else:
#                     bot_msg = (
#                         "You don't have any active cards.\n\n"
#                         "Would you like to:\n"
#                         "1️⃣ Apply for a new card\n"
#                         "2️⃣ Talk to a support agent\n\n"
#                         "Reply with 1 or 2."
#                     )
#             else:
#                 bot_msg = msg
#         except Exception as e:
#             print(f"Error fetching accounts for card block: {e}")
#             import traceback
#             traceback.print_exc()
#             bot_msg = "I'm having trouble accessing your accounts. Please try again or contact support."
        
#         save_message(user_id, user_msg, bot_msg)
#         return bot_msg
    
#     elif intent == "GREETING":
#         bot_msg = (
#             f"Hello {user_name}! I'm your banking support assistant. 🏦\n\n"
#             f"I can help with:\n"
#             f"• Check account balance\n"
#             f"• View transaction history\n"
#             f"• Block/manage cards\n"
#             f"• Loan information\n"
#             f"• General banking queries\n\n"
#             f"What would you like help with?"
#         )
#         save_message(user_id, user_msg, bot_msg)
#         return bot_msg
    
#     elif intent == "CONVERSATION_END":
#         clear_user_context(user_id)
#         bot_msg = f"You're welcome, {user_name}! Have a great day! 😊"
#         save_message(user_id, user_msg, bot_msg)
        
#         try:
#             if chat_sessions_collection is not None:
#                 chat_sessions_collection.update_one(
#                     {"user_id": user_id, "end_time": None},
#                     {"$set": {"end_time": datetime.now(timezone.utc)}}
#                 )
#         except Exception as e:
#             print(f"Error marking session end: {e}")
        
#         return bot_msg
    
#     elif intent == "ACCOUNT_BALANCE":
#         try:
#             accounts_data, msg = get_account_list(user_id)
            
#             if accounts_data is None:
#                 save_message(user_id, user_msg, msg)
#                 return msg
#             else:
#                 # Set context to indicate we're showing accounts for balance checking
#                 set_user_context(user_id, "account_balance_selection", {
#                     "action": "view_balance"
#                 })
                
#                 save_message(user_id, user_msg, "Displaying user accounts")
#                 return {
#                     "reply": "ACCOUNT_LIST",
#                     "accounts": accounts_data
#                 }
#         except Exception as e:
#             print(f"Account balance error: {e}")
#             bot_msg = "I couldn't access your accounts. Please try again."
#             save_message(user_id, user_msg, bot_msg)
#             return bot_msg
    
#     elif intent == "ACCOUNT_SELECTION" or intent == "ACCOUNT_DETAILS":
#         # Check if user is in account balance selection context
#         if context and context["type"] == "account_balance_selection":
#             try:
#                 from bson import ObjectId
                
#                 user_info_data = get_user_by_id(user_id)
#                 customer = customers_col.find_one({"email": user_info_data.get('email')})
                
#                 if not customer:
#                     bot_msg = "Customer profile not found."
#                     save_message(user_id, user_msg, bot_msg)
#                     return bot_msg
                
#                 accounts = list(accounts_col.find({"customer_id": customer["_id"]}))
#                 if not accounts:
#                     bot_msg = "You don't have any accounts."
#                     save_message(user_id, user_msg, bot_msg)
#                     return bot_msg
                
#                 idx = parse_selection_number(user_msg, len(accounts))
#                 if idx is not None and idx < len(accounts):
#                     account_id = str(accounts[idx]['_id'])
#                     bot_msg = get_specific_account_details(account_id, user_id)
#                     # DON'T clear context - keep it for follow-up actions
#                     save_message(user_id, user_msg, bot_msg)
#                     return bot_msg
                
#                 bot_msg = "Which account would you like to see the details for? You can tell me the number (like '1' or 'the first one') or the type (like 'Savings')."
#                 save_message(user_id, user_msg, bot_msg)
#                 return bot_msg
                
#             except Exception as e:
#                 print(f"Account selection error: {e}")
#                 import traceback
#                 traceback.print_exc()
#                 bot_msg = "I had trouble processing your selection."
#                 save_message(user_id, user_msg, bot_msg)
#                 return bot_msg
#         else:
#             # User wants account details but hasn't selected from list yet
#             bot_msg = "Which account would you like to see details for? Please ask to check your account balance first to see all your accounts."
#             save_message(user_id, user_msg, bot_msg)
#             return bot_msg
    
#     elif intent == "TRANSACTION_HISTORY":
#         context = get_user_context(user_id)
        
#         # Check if user already has a selected account in context
#         if context and context["type"] in ["selected_account"]:
#             # User already selected an account earlier, use it directly
#             account_id = context["data"]["account_id"]
#             bot_msg = get_transaction_history(account_id, user_id)
#             save_message(user_id, user_msg, bot_msg)
#             return bot_msg
#         else:
#             # No account selected yet - show account cards for first-time selection
#             bot_msg = (
#                 "I can show you transaction history! First, let me show you your accounts.\n\n"
#                 "Which account would you like to view transactions for?"
#             )
#             save_message(user_id, user_msg, bot_msg)
            
#             # Automatically fetch and show accounts as cards
#             try:
#                 accounts_data, msg = get_account_list(user_id)
                
#                 if accounts_data is None:
#                     return msg
#                 else:
#                     # Set context specifically for transaction history selection
#                     set_user_context(user_id, "transaction_history_selection", {
#                         "action": "view_transactions"
#                     })
                    
#                     return {
#                         "reply": "ACCOUNT_LIST",
#                         "accounts": accounts_data
#                     }
#             except Exception as e:
#                 print(f"Error fetching accounts for transaction history: {e}")
#                 return "Please check your account balance first, then I can show you transaction history for a specific account."
    
#     # Fallback to AI
#     try:
#         faq_knowledge = get_faq_context()
        
#         system_prompt = (
#             f"You are a professional banking support assistant helping {user_name}. "
#             f"Be helpful, empathetic, and concise.\n\n"
#             f"{faq_knowledge}\n\n"
#             f"Keep responses brief (2-4 sentences)."
#         )
        
#         context_text = system_prompt + "\n\nRecent conversation:\n"
#         for m in history[-4:]:
#             role = "User" if m['role']=="user" else "Assistant"
#             context_text += f"{role}: {m['content'][:150]}\n"
#         context_text += f"User: {user_msg}\nAssistant:"

#         response = model.generate_content(context_text)
#         bot_msg = response.text.strip() if response.text else f"Hi {user_name}! How can I help?"

#     except Exception as e:
#         if retry_count < max_retries:
#             time.sleep(1)
#             return get_bot_reply(user_id, user_msg, current_user_role, retry_count+1)
#         bot_msg = f"Hi {user_name}! I'm experiencing technical difficulties."

#     save_message(user_id, user_msg, bot_msg)
#     return bot_msg














import time
import re
import traceback
from datetime import datetime, timezone, timedelta

# Corrected relative imports
from .database import load_chat_history, save_message, get_user_by_id, messages_collection
from .config import db, model
from .escalation import should_escalate, create_escalation
from .faq_context import get_faq_context

# In-memory session cache with context tracking
session_cache = {}
user_context = {}  # Track user's current context
CACHE_DURATION = timedelta(minutes=15)
CONTEXT_DURATION = timedelta(minutes=10)

# Initialize collections
chat_sessions_collection = db["chat_sessions"] if db is not None else None
accounts_col = db["accounts"] if db is not None else None
transactions_col = db["transactions"] if db is not None else None
customers_col = db["customers"] if db is not None else None


# ==================== CONTEXT MANAGEMENT ====================

def set_user_context(user_id, context_type, context_data):
    """Store user's current context (e.g., selected account)"""
    user_context[user_id] = {
        "type": context_type,
        "data": context_data,
        "timestamp": datetime.now(timezone.utc)
    }


def get_user_context(user_id):
    """Retrieve user's current context if not expired"""
    if user_id not in user_context:
        return None
    
    context = user_context[user_id]
    if datetime.now(timezone.utc) - context["timestamp"] > CONTEXT_DURATION:
        del user_context[user_id]
        return None
    
    return context


def clear_user_context(user_id):
    """Clear user's context"""
    if user_id in user_context:
        del user_context[user_id]


# ==================== TRANSACTION HISTORY ====================

def format_transaction_history(transactions, account_info):
    """Format transactions for display"""
    if not transactions:
        return "No transactions found for this account."
    
    account_type = account_info.get('account_type', 'Account')
    account_number = account_info.get('account_number', 'N/A')
    
    response = f"TRANSACTION HISTORY\n"
    response += f"═══════════════════════════════\n"
    response += f"{account_type}: {account_number}\n"
    response += f"═══════════════════════════════\n\n"
    
    for txn in transactions[:20]:  # Limit to 20 transactions
        date = txn.get('date')
        if isinstance(date, datetime):
            date_str = date.strftime("%b %d, %Y %H:%M")
        else:
            date_str = str(date)[:16] if date else "Unknown"
        
        description = txn.get('description', 'N/A')
        amount = txn.get('amount', 0)
        txn_type = txn.get('type', 'N/A')
        status = txn.get('status', 'N/A')
        merchant = txn.get('merchant_name', '')
        
        # Format amount with +/- based on type
        amount_str = f"+{amount:,.2f}" if txn_type == "Credit" else f"-{amount:,.2f}"
        
        response += f"📅 {date_str}\n"
        response += f"💳 {description}"
        if merchant:
            response += f" ({merchant})"
        response += f"\n💰 INR {amount_str} | {status}\n"
        response += f"─────────────────────────────\n"
    
    if len(transactions) > 20:
        response += f"\nShowing 20 of {len(transactions)} transactions.\n"
    
    response += f"\n═══════════════════════════════"
    return response


def get_transaction_history(account_id, user_id):
    """Fetch and format transaction history"""
    if transactions_col is None or accounts_col is None:
        return "System error: Database unavailable."
    
    try:
        from bson import ObjectId
        
        # Verify account belongs to user
        user_info = get_user_by_id(user_id)
        customer = customers_col.find_one({"email": user_info.get('email')})
        
        if not customer:
            return "Customer profile not found."
        
        account = accounts_col.find_one({
            "_id": ObjectId(account_id),
            "customer_id": customer["_id"]
        })
        
        if not account:
            return "Account not found or you don't have access."
        
        # Fetch transactions
        transactions = list(transactions_col.find({
            "account_id": ObjectId(account_id)
        }).sort("date", -1))
        
        return format_transaction_history(transactions, account)
        
    except Exception as e:
        print(f"Error fetching transaction history: {e}")
        traceback.print_exc()
        return "Error fetching transaction history. Please try again."


# ==================== EXISTING FUNCTIONS ====================

def get_cached_history(user_id, limit=30):
    """Retrieve recent conversation history from cache or database."""
    now = datetime.now(timezone.utc)
    if user_id in session_cache:
        cached_data, timestamp = session_cache[user_id]
        if now - timestamp < CACHE_DURATION:
            return cached_data[:limit]

    history = load_chat_history(user_id, limit=limit)
    session_cache[user_id] = (history, now)
    cleanup_cache()
    return history


def cleanup_cache():
    """Remove expired cache entries."""
    now = datetime.now(timezone.utc)
    expired = [uid for uid, (_, ts) in session_cache.items() if now - ts > CACHE_DURATION]
    for uid in expired:
        del session_cache[uid]


def invalidate_cache(user_id):
    """Clear cache when new message is saved."""
    if user_id in session_cache:
        del session_cache[user_id]
        print(f"✅ Cache invalidated for user: {user_id}")


def get_or_create_session(user_id: str) -> str:
    """Get current session or create new one"""
    if chat_sessions_collection is None:
        return f"SESSION_{int(datetime.now(timezone.utc).timestamp())}"
    
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=30)
    active_session = chat_sessions_collection.find_one({
        "user_id": user_id,
        "end_time": None,
        "start_time": {"$gte": cutoff}
    })
    
    if active_session:
        return active_session["session_id"]
    
    session_id = f"SESSION_{int(datetime.now(timezone.utc).timestamp())}"
    session_doc = {
        "session_id": session_id,
        "user_id": user_id,
        "start_time": datetime.now(timezone.utc),
        "end_time": None,
        "message_count": 0,
        "escalated": False,
        "feedback_submitted": False
    }
    chat_sessions_collection.insert_one(session_doc)
    return session_id


def update_session_message_count(session_id: str):
    """Increment message count for session"""
    if chat_sessions_collection is None:
        return
    
    chat_sessions_collection.update_one(
        {"session_id": session_id},
        {"$inc": {"message_count": 1}}
    )


def classify_user_intent(user_msg, history, user_name="there"):
    """Use AI to classify user intent with smart goodbye detection"""
    
    msg_lower = user_msg.lower().strip()
    msg_words = msg_lower.split()
    
    goodbye_exact = ['bye', 'goodbye', 'thanks', 'thank you', 'thankyou', 'done', 'ok', 'okay']
    goodbye_starts = ['thanks for', 'thank you for', "that's all", 'all set', 'got it', 
                      "i'm good", "im good", 'nothing else', "that's it", "thats it"]
    
    # Check for UNBLOCK keywords FIRST (before block keywords)
    unblock_keywords = ['unblock', 'unlock', 'enable card', 'activate card', 'unfreeze', 'reactivate']
    if any(keyword in msg_lower for keyword in unblock_keywords):
        return "CARD_UNBLOCK"
    
    # Check for card blocking keywords (after unblock check)
    block_keywords = ['block card', 'freeze card', 'disable card', 'deactivate card', 'lock card', 
                      'suspend card', 'stop card', 'lost card', 'stolen card', 'block my card',
                      'freeze my card', 'lost my card', 'stolen my card']
    # Also check for standalone "block" or "freeze" but NOT if "unblock" was already checked
    if any(keyword in msg_lower for keyword in block_keywords) or (
        ('block' in msg_lower or 'freeze' in msg_lower or 'lost' in msg_lower or 'stolen' in msg_lower) 
        and 'unblock' not in msg_lower
    ):
        return "CARD_BLOCK"
    
    # Check for escalation/agent keywords
    agent_keywords = ['agent', 'human', 'representative', 'support agent', 'talk to someone',
                      'speak to', 'customer service', 'help me', 'need help', 'supervisor']
    if any(keyword in msg_lower for keyword in agent_keywords):
        return "ESCALATE_TO_AGENT"
    
    # Check for transaction-related keywords
    transaction_keywords = ['transaction', 'history', 'statement', 'transactions', 'purchases', 'payments']
    if any(keyword in msg_lower for keyword in transaction_keywords):
        return "TRANSACTION_HISTORY"
    
    if '?' in user_msg:
        pass
    elif len(msg_words) <= 3:
        if msg_lower in goodbye_exact:
            return "CONVERSATION_END"
    elif len(msg_words) <= 6:
        for phrase in goodbye_starts:
            if msg_lower.startswith(phrase):
                return "CONVERSATION_END"
    
    last_bot_msg = ""
    if history and len(history) > 0:
        last_bot_msg = history[-1].get("content", "")[:200]
    
    classification_prompt = f"""You are analyzing a user's message in a banking support chat.

User message: "{user_msg}"
Last assistant message: "{last_bot_msg}"

Classify the user's PRIMARY INTENT into ONE category:

GREETING - Starting conversation
ACCOUNT_BALANCE - Wants to check account balance
ACCOUNT_SELECTION - Selecting specific account
TRANSACTION_HISTORY - Wants transaction history/statement
ACCOUNT_DETAILS - Wants detailed account information
CARD_BLOCK - Wants to block/freeze card (temporary or permanent)
CARD_UNBLOCK - Wants to unblock/activate card
ESCALATE_TO_AGENT - Wants to talk to human agent/support
CARD_MANAGEMENT - Card-related questions
LOAN_INFO - Loan questions
PROFILE_INFO - Profile/personal details
CONVERSATION_END - Ending conversation
OTHER - Anything else

Respond with ONLY the category name in uppercase."""

    try:
        response = model.generate_content(classification_prompt)
        intent = response.text.strip().upper().replace(" ", "_")
        print(f"[Intent] '{user_msg[:40]}...' -> {intent}")
        return intent
    except Exception as e:
        print(f"Intent classification error: {e}")
        return "OTHER"


def parse_selection_number(user_msg, max_items=5):
    """Parse selection number from various formats"""
    msg = user_msg.lower().strip()
    
    if msg.isdigit():
        num = int(msg)
        if 1 <= num <= max_items:
            return num - 1
    
    match = re.search(r'\b(\d+)\b', msg)
    if match:
        num = int(match.group(1))
        if 1 <= num <= max_items:
            return num - 1
    
    words = {'first':0,'second':1,'third':2,'fourth':3,'fifth':4,'one':0,'two':1,'three':2,'four':3,'five':4}
    for word, idx in words.items():
        if word in msg and idx < max_items:
            return idx
    
    return None


def get_account_list(user_id):
    """Get account list formatted for frontend"""
    if accounts_col is None:
        return None, "System error: Database unavailable."

    try:
        user_info = get_user_by_id(user_id)
        customer = customers_col.find_one({"email": user_info.get('email')})
        
        if not customer:
            return None, "Customer profile not found."
        
        accounts = list(accounts_col.find({"customer_id": customer["_id"]}))
        
        if not accounts:
            return None, "You don't have any accounts yet."

        accounts_data = []
        for acc in accounts:
            account_type = acc.get('account_type', 'Unknown')
            
            account_info = {
                "account_id": str(acc['_id']),
                "account_number": acc.get('account_number', 'N/A'),
                "account_type": account_type,
                "balance": acc.get('balance', 0),
                "currency": acc.get('currency', 'INR'),
                "status": acc.get('status', 'Unknown'),
                "created_at": acc.get('created_at').strftime("%b %d, %Y") if acc.get('created_at') else "Unknown"
            }
            
            if account_type == "Credit Card":
                account_info["total_limit"] = acc.get('total_limit', 0)
                account_info["available_credit"] = acc.get('available_credit', 0)
            elif account_type == "Home Loan":
                account_info["principal_amount"] = acc.get('principal_amount', 0)
                account_info["interest_rate"] = acc.get('interest_rate', 0)
                account_info["emi_amount"] = acc.get('emi_amount', 0)
                account_info["next_emi_due"] = acc.get('next_emi_due').strftime("%b %d, %Y") if acc.get('next_emi_due') else "N/A"
            
            accounts_data.append(account_info)
        
        return accounts_data, "ACCOUNT_LIST"
    
    except Exception as e:
        print(f"Error fetching accounts: {e}")
        return None, "Error fetching accounts."


def get_specific_account_details(account_id, user_id):
    """Get detailed account information and store in context"""
    if accounts_col is None:
        return "System error: Database unavailable."

    try:
        from bson import ObjectId
        
        user_info = get_user_by_id(user_id)
        customer = customers_col.find_one({"email": user_info.get('email')})
        
        if not customer:
            return "Customer profile not found."
        
        account = accounts_col.find_one({"_id": ObjectId(account_id), "customer_id": customer["_id"]})
        
        if not account:
            return "Account not found."

        # Store account in context for future reference
        set_user_context(user_id, "selected_account", {
            "account_id": account_id,
            "account_type": account.get('account_type'),
            "account_number": account.get('account_number')
        })

        account_type = account.get('account_type', 'Unknown')
        account_number = account.get('account_number', 'N/A')
        balance = account.get('balance', 0)
        currency = account.get('currency', 'INR')
        status = account.get('status', 'Unknown')
        created_date = account.get('created_at').strftime("%b %d, %Y") if account.get('created_at') else "Unknown"
        
        response = f"""ACCOUNT DETAILS
═══════════════════════════════

Account Number: {account_number}
Account Type: {account_type}
Status: {status}
Opened On: {created_date}

"""
        
        if account_type in ["Savings", "Checking"]:
            response += f"Current Balance: {currency} {balance:,.2f}\n"
        
        elif account_type == "Credit Card":
            total_limit = account.get('total_limit', 0)
            available_credit = account.get('available_credit', 0)
            outstanding = account.get('balance', 0)
            
            response += f"Total Limit: {currency} {total_limit:,.2f}\n"
            response += f"Available Credit: {currency} {available_credit:,.2f}\n"
            response += f"Outstanding: {currency} {outstanding:,.2f}\n"
        
        elif account_type == "Home Loan":
            principal = account.get('principal_amount', 0)
            outstanding = account.get('balance', 0)
            interest_rate = account.get('interest_rate', 0)
            emi = account.get('emi_amount', 0)
            next_due = account.get('next_emi_due').strftime("%b %d, %Y") if account.get('next_emi_due') else "N/A"
            
            response += f"Principal: {currency} {principal:,.2f}\n"
            response += f"Outstanding: {currency} {outstanding:,.2f}\n"
            response += f"Interest Rate: {interest_rate}%\n"
            response += f"EMI: {currency} {emi:,.2f}\n"
            response += f"Next Due: {next_due}\n"
        
        response += f"\n═══════════════════════════════"
        response += f"\n\nWhat else would you like to know about this account?"
        
        return response
    
    except Exception as e:
        print(f"Error fetching account details: {e}")
        return "Error fetching account details."


def get_bot_reply(user_id, user_msg, current_user_role="user", retry_count=0):
    """Generate bot reply with context awareness"""
    max_retries = 2
    history = get_cached_history(user_id, limit=30)
    user_info = get_user_by_id(user_id)
    user_name = user_info.get("name","there") if user_info else "there"

    try:
        session_id = get_or_create_session(user_id)
        update_session_message_count(session_id)
    except Exception as e:
        print(f"Session tracking error: {e}")

    # Get current context
    context = get_user_context(user_id)
    
    # ==================== PRIORITY: Handle numeric selections in context ====================
    # If user is in a selection context and sends a number, handle it immediately
    if context and user_msg.strip().isdigit():
        if context["type"] == "account_balance_selection":
            try:
                from bson import ObjectId
                
                user_info_data = get_user_by_id(user_id)
                customer = customers_col.find_one({"email": user_info_data.get('email')})
                
                if customer:
                    accounts = list(accounts_col.find({"customer_id": customer["_id"]}))
                    idx = parse_selection_number(user_msg, len(accounts))
                    
                    if idx is not None and idx < len(accounts):
                        account_id = str(accounts[idx]['_id'])
                        bot_msg = get_specific_account_details(account_id, user_id)
                        # DON'T clear context - keep it for follow-up actions like transaction history
                        save_message(user_id, user_msg, bot_msg)
                        invalidate_cache(user_id)  # <-- ✅ FIX ADDED
                        return bot_msg
            except Exception as e:
                print(f"Error handling account selection: {e}")
                traceback.print_exc()
        
        elif context["type"] == "transaction_history_selection":
            try:
                from bson import ObjectId
                
                user_info_data = get_user_by_id(user_id)
                customer = customers_col.find_one({"email": user_info_data.get('email')})
                
                if customer:
                    accounts = list(accounts_col.find({"customer_id": customer["_id"]}))
                    idx = parse_selection_number(user_msg, len(accounts))
                    
                    if idx is not None and idx < len(accounts):
                        account_id = str(accounts[idx]['_id'])
                        
                        # Set context for future transaction requests
                        set_user_context(user_id, "selected_account", {
                            "account_id": account_id,
                            "account_type": accounts[idx].get('account_type'),
                            "account_number": accounts[idx].get('account_number')
                        })
                        
                        bot_msg = get_transaction_history(account_id, user_id)
                        save_message(user_id, user_msg, bot_msg)
                        invalidate_cache(user_id)  # <-- ✅ FIX ADDED
                        return bot_msg
            except Exception as e:
                print(f"Error handling transaction history selection: {e}")
                traceback.print_exc()
    
    # Classify intent
    intent = classify_user_intent(user_msg, history, user_name)
    
    # ==================== CONTEXT-SPECIFIC FLOWS ====================
    
    # Handle card block account selection (ONLY if explicitly in card block flow)
    if context and context["type"] == "card_block_account_selection":
        try:
            user_info_data = get_user_by_id(user_id)
            customer = customers_col.find_one({"email": user_info_data.get('email')})
            
            if customer:
                all_accounts = list(accounts_col.find({"customer_id": customer["_id"]}))
                card_accounts = [
                    acc for acc in all_accounts 
                    if acc.get('account_type') in ['Credit Card', 'Savings', 'Checking']
                ]
                
                idx = parse_selection_number(user_msg, len(card_accounts))
                if idx is not None and idx < len(card_accounts):
                    account = card_accounts[idx]
                    account_id = str(account['_id'])
                    account_number = account.get('account_number', 'N/A')
                    account_type = account.get('account_type', 'Account')
                    
                    if account_type == 'Credit Card':
                        card_type = "Credit Card"
                    elif account_type in ['Savings', 'Checking']:
                        card_type = "Debit Card"
                    else:
                        card_type = "Card"
                    
                    set_user_context(user_id, "card_block_pending", {
                        "account_id": account_id,
                        "account_number": account_number,
                        "account_type": account_type,
                        "card_type": card_type
                    })
                    
                    bot_msg = (
                        f"You selected: {card_type} (Account: {account_number})\n\n"
                        f"Please choose:\n"
                        f"1️⃣ Temporary Block (you can unblock later)\n"
                        f"2️⃣ Permanent Block (card will be cancelled)\n"
                        f"3️⃣ Talk to Support Agent\n\n"
                        f"Reply with 1, 2, or 3."
                    )
                    save_message(user_id, user_msg, bot_msg)
                    invalidate_cache(user_id)  # <-- ✅ FIX ADDED
                    return bot_msg
        except Exception as e:
            print(f"Error in card block selection: {e}")
            traceback.print_exc()

    # Handle card block confirmation
    elif context and context["type"] == "card_block_pending":
        if user_msg.strip() in ["1", "2", "3", "temporary", "permanent", "agent"]:
            card_type = context['data'].get('card_type', 'Card')
            account_number = context['data']['account_number']
            account_id = context['data']['account_id']
            
            if user_msg.strip() in ["1", "temporary"]:
                from .database import block_card_temporary
                
                success, message = block_card_temporary(account_id)
                
                if success:
                    bot_msg = (
                        f"🔒 **CARD TEMPORARILY BLOCKED**\n\n"
                        f"Your {card_type} (Account: {account_number}) is now blocked.\n\n"
                        f"**What this means:**\n"
                        f"❌ Cannot make purchases or withdrawals\n"
                        f"❌ ATM transactions disabled\n"
                        f"✅ Account balance is SAFE\n"
                        f"✅ You can still receive deposits\n"
                        f"✅ Can be unblocked anytime by YOU\n\n"
                        f"**To unblock:**\n"
                        f"• Tell me 'unblock my card'\n"
                        f"• Use mobile app\n"
                        f"• Call: 1-800-BANK-HELP\n"
                        f"• Visit any branch\n\n"
                        f"Is there anything else I can help you with?"
                    )
                else:
                    bot_msg = f"Sorry, I couldn't block the card. Error: {message}\n\nPlease try again or contact support."
                
                clear_user_context(user_id)
                save_message(user_id, user_msg, bot_msg)
                invalidate_cache(user_id)  # <-- ✅ FIX ADDED
                return bot_msg
            
            elif user_msg.strip() in ["2", "permanent"]:
                # ✅ Get full account and customer details for verification
                from bson import ObjectId
                from .database import get_customer_by_user_id

                # Get account details
                account = accounts_col.find_one({"_id": ObjectId(account_id)})

                # Get customer verification details
                user_details = get_customer_by_user_id(user_id)
                if not user_details:
                    user_details = user_info  # Fallback to basic user info

                # Format account creation date
                account_created_at = "N/A"
                if account and account.get('created_at'):
                    try:
                        if isinstance(account.get('created_at'), datetime):
                            account_created_at = account.get('created_at').strftime("%b %d, %Y")
                        else:
                            account_created_at = str(account.get('created_at'))[:16]
                    except:
                        account_created_at = "N/A"

                # Create escalation with full verification details
                escalation_id = create_escalation(
                    user_id,
                    f"URGENT: User requested PERMANENT card cancellation - {card_type} - Account {account_number}",
                    {
                        "account_id": account_id,
                        "account_number": account_number,
                        "account_type": context['data']['account_type'],
                        "card_type": card_type,
                        "block_type": "permanent",
                        "priority": "high",
                        "requires_verification": True,
                        "action_required": "Verify identity and permanently cancel card",
                        # ✅ CUSTOMER VERIFICATION DETAILS
                        "user_name": user_details.get('name', user_name),
                        "user_email": user_details.get('email', 'N/A'),
                        "phone_number": user_details.get('phone_number', 'Not Available'),
                        "address": user_details.get('address', 'Not Available'),
                        "customer_id": user_details.get('customer_id', user_id),
                        "account_created_at": account_created_at,
                        # Additional verification info (if available)
                        "kyc_status": user_details.get('kyc_status', 'Unknown'),
                        "customer_tier": user_details.get('customer_tier', 'Unknown'),
                        "date_of_birth": user_details.get('date_of_birth', 'Not Available')
                    }
                )

                bot_msg = (
                    f"⚠️ **PERMANENT CARD CANCELLATION REQUEST**\n\n"
                    f"**IMPORTANT - This action requires agent verification:**\n\n"
                    f"**Temporary vs Permanent:**\n"
                    f"🔄 **Temporary Block:**\n"
                    f"   • YOU can unblock anytime\n"
                    f"   • Same card number\n"
                    f"   • Instant process\n\n"
                    f"🚫 **Permanent Cancellation:**\n"
                    f"   • Card is DESTROYED\n"
                    f"   • Cannot be unblocked EVER\n"
                    f"   • New card with NEW number needed\n"
                    f"   • Requires agent verification\n"
                    f"   • Takes 7-10 business days for new card\n\n"
                    f"**Why agent verification?**\n"
                    f"Security protection - prevents unauthorized cancellation\n\n"
                    f"Case ID: {escalation_id[:12]} (Priority: HIGH)\n\n"
                    f"👉 Click 'Talk to Human Agent' button above NOW.\n"
                    f"An agent will verify your identity and complete the cancellation."
                )

                clear_user_context(user_id)
                save_message(user_id, user_msg, bot_msg)
                invalidate_cache(user_id)  # <-- ✅ FIX ADDED
                return {
                    "reply": bot_msg,
                    "escalation_id": escalation_id,
                    "escalated": True
                }
            
            elif user_msg.strip() in ["3", "agent"]:
                escalation_id = create_escalation(
                    user_id,
                    f"User requested agent help for {card_type} blocking - Account {account_number}",
                    {
                        "account_id": account_id,
                        "account_number": account_number,
                        "account_type": context['data']['account_type'],
                        "card_type": card_type
                    }
                )
                
                bot_msg = (
                    f"I've connected you with a support agent.\n\n"
                    f"They can help you with:\n"
                    f"• Card blocking questions\n"
                    f"• Report lost/stolen card\n"
                    f"• Dispute transactions\n"
                    f"• Order new card\n\n"
                    f"Case ID: {escalation_id[:12]}\n\n"
                    f"👉 Click 'Talk to Human Agent' button above."
                )
                
                clear_user_context(user_id)
                save_message(user_id, user_msg, bot_msg)
                invalidate_cache(user_id)  # <-- ✅ FIX ADDED
                return {
                    "reply": bot_msg,
                    "escalation_id": escalation_id,
                    "escalated": True
                }

    # Handle card unblock selection
    elif context and context["type"] == "card_unblock_selection":
        try:
            accounts = context['data']['accounts']
            idx = parse_selection_number(user_msg, len(accounts))
            
            if idx is not None and idx < len(accounts):
                from .database import unblock_card
                from bson import ObjectId
                account_id = accounts[idx]
                
                success, message = unblock_card(account_id)
                
                if success:
                    account = accounts_col.find_one({"_id": ObjectId(account_id)})
                    bot_msg = (
                        f"✅ **CARD UNBLOCKED**\n\n"
                        f"Your {account.get('account_type')} card (Account: {account.get('account_number')}) "
                        f"is now ACTIVE.\n\n"
                        f"You can now:\n"
                        f"✅ Make purchases\n"
                        f"✅ Withdraw cash from ATMs\n"
                        f"✅ Use online transactions\n\n"
                        f"Stay safe! If you didn't request this, contact us immediately."
                    )
                else:
                    bot_msg = f"Failed to unblock card: {message}"
                
                clear_user_context(user_id)
                save_message(user_id, user_msg, bot_msg)
                invalidate_cache(user_id)  # <-- ✅ FIX ADDED
                return bot_msg
        except Exception as e:
            print(f"Error unblocking card: {e}")
            traceback.print_exc()

    # ==================== INTENT-BASED FLOWS ====================
    
    if intent == "CARD_UNBLOCK":
        try:
            from .database import unblock_card
            from bson import ObjectId
            user_info_data = get_user_by_id(user_id)
            customer = customers_col.find_one({"email": user_info_data.get('email')})
            
            if customer:
                accounts = list(accounts_col.find({
                    "customer_id": customer["_id"],
                    "card_status": "blocked_temporary"
                }))
                
                if not accounts:
                    bot_msg = (
                        "You don't have any temporarily blocked cards.\n\n"
                        "If you need to unblock a permanently cancelled card, "
                        "you'll need to apply for a new card. Would you like help with that?"
                    )
                    save_message(user_id, user_msg, bot_msg)
                    invalidate_cache(user_id)  # <-- ✅ FIX ADDED
                    return bot_msg
                
                if len(accounts) == 1:
                    account = accounts[0]
                    success, message = unblock_card(str(account['_id']))
                    
                    if success:
                        bot_msg = (
                            f"✅ **CARD UNBLOCKED**\n\n"
                            f"Your {account.get('account_type')} card (Account: {account.get('account_number')}) "
                            f"is now ACTIVE.\n\n"
                            f"You can now:\n"
                            f"✅ Make purchases\n"
                            f"✅ Withdraw cash from ATMs\n"
                            f"✅ Use online transactions\n\n"
                            f"Stay safe! If you didn't request this, contact us immediately."
                        )
                    else:
                        bot_msg = f"Failed to unblock card: {message}"
                    
                    save_message(user_id, user_msg, bot_msg)
                    invalidate_cache(user_id)  # <-- ✅ FIX ADDED
                    return bot_msg
                else:
                    bot_msg = "You have multiple blocked cards. Which one would you like to unblock?\n\n"
                    for idx, acc in enumerate(accounts, 1):
                        bot_msg += f"{idx}. {acc.get('account_type')} - {acc.get('account_number')}\n"
                    bot_msg += "\nReply with the number."
                    
                    set_user_context(user_id, "card_unblock_selection", {
                        "accounts": [str(acc['_id']) for acc in accounts]
                    })
                    
                    save_message(user_id, user_msg, bot_msg)
                    invalidate_cache(user_id)  # <-- ✅ FIX ADDED
                    return bot_msg
            
        except Exception as e:
            print(f"Error unblocking card: {e}")
            traceback.print_exc()
            bot_msg = "Error unblocking card. Please contact support."
            save_message(user_id, user_msg, bot_msg)
            invalidate_cache(user_id)  # <-- ✅ FIX ADDED
            return bot_msg
    
    elif intent == "ESCALATE_TO_AGENT":
        try:
            escalation_id = create_escalation(
                user_id, 
                "User requested to speak with support agent",
                {"recent_messages": history[-10:], "user_name": user_name}
            )
            
            bot_msg = (
                f"I understand you'd like to speak with a support agent. "
                f"I've created a support case for you (Case ID: {escalation_id[:12]}).\n\n"
                f"Please click the 'Talk to Human Agent' button above to connect with our support team. "
                f"An agent will be with you shortly!"
            )
            save_message(user_id, user_msg, bot_msg)
            invalidate_cache(user_id)  # <-- ✅ FIX ADDED
            return {
                "reply": bot_msg,
                "escalation_id": escalation_id,
                "escalated": True
            }
        except Exception as e:
            print(f"Escalation error: {e}")
            bot_msg = "I'm having trouble connecting you to an agent. Please try again in a moment."
            save_message(user_id, user_msg, bot_msg)
            invalidate_cache(user_id)  # <-- ✅ FIX ADDED
            return bot_msg
    
    elif intent == "CARD_BLOCK":
        try:
            accounts_data, msg = get_account_list(user_id)
            if accounts_data:
                card_accounts = [
                    acc for acc in accounts_data 
                    if acc["account_type"] in ["Credit Card", "Savings", "Checking"]
                ]
                
                if card_accounts:
                    for acc in card_accounts:
                        if acc["account_type"] == "Credit Card":
                            acc["display_name"] = "Credit Card"
                        elif acc["account_type"] in ["Savings", "Checking"]:
                            acc["display_name"] = f"{acc['account_type']} (Debit Card)"
                    
                    bot_msg = (
                        "I can help you block a card. Please select the account:\n\n"
                        "💳 This will block the card linked to the selected account.\n"
                        "Note: Blocking the card will NOT affect your account balance."
                    )
                    
                    set_user_context(user_id, "card_block_account_selection", {
                        "action": "card_block"
                    })
                    
                    save_message(user_id, user_msg, "Displaying card accounts for blocking")
                    invalidate_cache(user_id)  # <-- ✅ FIX ADDED
                    return {
                        "reply": "ACCOUNT_LIST",
                        "accounts": card_accounts,
                        "action": "card_block"
                    }
                else:
                    bot_msg = (
                        "You don't have any active cards.\n\n"
                        "Would you like to:\n"
                        "1️⃣ Apply for a new card\n"
                        "2️⃣ Talk to a support agent\n\n"
                        "Reply with 1 or 2."
                    )
            else:
                bot_msg = msg
        except Exception as e:
            print(f"Error fetching accounts for card block: {e}")
            traceback.print_exc()
            bot_msg = "I'm having trouble accessing your accounts. Please try again or contact support."
        
        save_message(user_id, user_msg, bot_msg)
        invalidate_cache(user_id)  # <-- ✅ FIX ADDED
        return bot_msg
    
    elif intent == "GREETING":
        bot_msg = (
            f"Hello {user_name}! I'm your banking support assistant. 🏦\n\n"
            f"I can help with:\n"
            f"• Check account balance\n"
            f"• View transaction history\n"
            f"• Block/manage cards\n"
            f"• Loan information\n"
            f"• General banking queries\n\n"
            f"What would you like help with?"
        )
        save_message(user_id, user_msg, bot_msg)
        invalidate_cache(user_id)  # <-- ✅ FIX ADDED
        return bot_msg
    
    elif intent == "CONVERSATION_END":
        clear_user_context(user_id)
        bot_msg = f"You're welcome, {user_name}! Have a great day! 😊"
        save_message(user_id, user_msg, bot_msg)
        invalidate_cache(user_id)  # <-- ✅ FIX ADDED
        
        try:
            if chat_sessions_collection is not None:
                chat_sessions_collection.update_one(
                    {"user_id": user_id, "end_time": None},
                    {"$set": {"end_time": datetime.now(timezone.utc)}}
                )
        except Exception as e:
            print(f"Error marking session end: {e}")
        
        return bot_msg
    
    elif intent == "ACCOUNT_BALANCE":
        try:
            accounts_data, msg = get_account_list(user_id)
            
            if accounts_data is None:
                save_message(user_id, user_msg, msg)
                invalidate_cache(user_id)  # <-- ✅ FIX ADDED
                return msg
            else:
                # Set context to indicate we're showing accounts for balance checking
                set_user_context(user_id, "account_balance_selection", {
                    "action": "view_balance"
                })
                
                save_message(user_id, user_msg, "Displaying user accounts")
                invalidate_cache(user_id)  # <-- ✅ FIX ADDED
                return {
                    "reply": "ACCOUNT_LIST",
                    "accounts": accounts_data
                }
        except Exception as e:
            print(f"Account balance error: {e}")
            bot_msg = "I couldn't access your accounts. Please try again."
            save_message(user_id, user_msg, bot_msg)
            invalidate_cache(user_id)  # <-- ✅ FIX ADDED
            return bot_msg
    
    elif intent == "ACCOUNT_SELECTION" or intent == "ACCOUNT_DETAILS":
        # Check if user is in account balance selection context
        if context and context["type"] == "account_balance_selection":
            try:
                from bson import ObjectId
                
                user_info_data = get_user_by_id(user_id)
                customer = customers_col.find_one({"email": user_info_data.get('email')})
                
                if not customer:
                    bot_msg = "Customer profile not found."
                    save_message(user_id, user_msg, bot_msg)
                    invalidate_cache(user_id)  # <-- ✅ FIX ADDED
                    return bot_msg
                
                accounts = list(accounts_col.find({"customer_id": customer["_id"]}))
                if not accounts:
                    bot_msg = "You don't have any accounts."
                    save_message(user_id, user_msg, bot_msg)
                    invalidate_cache(user_id)  # <-- ✅ FIX ADDED
                    return bot_msg
                
                idx = parse_selection_number(user_msg, len(accounts))
                if idx is not None and idx < len(accounts):
                    account_id = str(accounts[idx]['_id'])
                    bot_msg = get_specific_account_details(account_id, user_id)
                    # DON'T clear context - keep it for follow-up actions
                    save_message(user_id, user_msg, bot_msg)
                    invalidate_cache(user_id)  # <-- ✅ FIX ADDED
                    return bot_msg
                
                bot_msg = "Which account would you like to see the details for? You can tell me the number (like '1' or 'the first one') or the type (like 'Savings')."
                save_message(user_id, user_msg, bot_msg)
                invalidate_cache(user_id)  # <-- ✅ FIX ADDED
                return bot_msg
                
            except Exception as e:
                print(f"Account selection error: {e}")
                traceback.print_exc()
                bot_msg = "I had trouble processing your selection."
                save_message(user_id, user_msg, bot_msg)
                invalidate_cache(user_id)  # <-- ✅ FIX ADDED
                return bot_msg
        else:
            # User wants account details but hasn't selected from list yet
            bot_msg = "Which account would you like to see details for? Please ask to check your account balance first to see all your accounts."
            save_message(user_id, user_msg, bot_msg)
            invalidate_cache(user_id)  # <-- ✅ FIX ADDED
            return bot_msg
    
    elif intent == "TRANSACTION_HISTORY":
        context = get_user_context(user_id)
        
        # Check if user already has a selected account in context
        if context and context["type"] in ["selected_account"]:
            # User already selected an account earlier, use it directly
            account_id = context["data"]["account_id"]
            bot_msg = get_transaction_history(account_id, user_id)
            save_message(user_id, user_msg, bot_msg)
            invalidate_cache(user_id)  # <-- ✅ FIX ADDED
            return bot_msg
        else:
            # No account selected yet - show account cards for first-time selection
            bot_msg = (
                "I can show you transaction history! First, let me show you your accounts.\n\n"
                "Which account would you like to view transactions for?"
            )
            save_message(user_id, user_msg, bot_msg)
            invalidate_cache(user_id)  # <-- ✅ FIX ADDED
            
            # Automatically fetch and show accounts as cards
            try:
                accounts_data, msg = get_account_list(user_id)
                
                if accounts_data is None:
                    return msg
                else:
                    # Set context specifically for transaction history selection
                    set_user_context(user_id, "transaction_history_selection", {
                        "action": "view_transactions"
                    })
                    
                    return {
                        "reply": "ACCOUNT_LIST",
                        "accounts": accounts_data
                    }
            except Exception as e:
                print(f"Error fetching accounts for transaction history: {e}")
                return "Please check your account balance first, then I can show you transaction history for a specific account."
    
    # Fallback to AI
    try:
        faq_knowledge = get_faq_context()
        
        system_prompt = (
            f"You are a professional banking support assistant helping {user_name}. "
            f"Be helpful, empathetic, and concise.\n\n"
            f"{faq_knowledge}\n\n"
            f"Keep responses brief (2-4 sentences)."
        )
        
        context_text = system_prompt + "\n\nRecent conversation:\n"
        for m in history[-4:]:
            role = "User" if m['role']=="user" else "Assistant"
            context_text += f"{role}: {m['content'][:150]}\n"
        context_text += f"User: {user_msg}\nAssistant:"

        response = model.generate_content(context_text)
        bot_msg = response.text.strip() if response.text else f"Hi {user_name}! How can I help?"

    except Exception as e:
        if retry_count < max_retries:
            time.sleep(1)
            return get_bot_reply(user_id, user_msg, current_user_role, retry_count+1)
        bot_msg = f"Hi {user_name}! I'm experiencing technical difficulties."

    save_message(user_id, user_msg, bot_msg)
    invalidate_cache(user_id)  # <-- ✅ FIX ADDED
    return bot_msg



