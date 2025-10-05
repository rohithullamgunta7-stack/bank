
# # import time
# # from datetime import datetime, timezone, timedelta
# # from .database import load_chat_history, save_message, get_user_by_id, messages_collection
# # from .config import orders_col, refunds_col, db, model
# # from .escalation import should_escalate, create_escalation
# # from .faq_context import get_faq_context
# # import re

# # # In-memory session cache
# # session_cache = {}
# # CACHE_DURATION = timedelta(minutes=15)

# # # Initialize collections
# # chat_sessions_collection = db["chat_sessions"] if db is not None else None


# # def get_cached_history(user_id, limit=30):
# #     """Retrieve recent conversation history from cache or database."""
# #     now = datetime.now(timezone.utc)
# #     if user_id in session_cache:
# #         cached_data, timestamp = session_cache[user_id]
# #         if now - timestamp < CACHE_DURATION:
# #             return cached_data[:limit]

# #     history = load_chat_history(user_id, limit=limit)
# #     session_cache[user_id] = (history, now)
# #     cleanup_cache()
# #     return history

# # def cleanup_cache():
# #     """Remove expired cache entries."""
# #     now = datetime.now(timezone.utc)
# #     expired = [uid for uid, (_, ts) in session_cache.items() if now - ts > CACHE_DURATION]
# #     for uid in expired:
# #         del session_cache[uid]

# # def invalidate_cache(user_id):
# #     """Clear cache when new message is saved."""
# #     if user_id in session_cache:
# #         del session_cache[uid]

# # def get_or_create_session(user_id: str) -> str:
# #     """Get current session or create new one"""
# #     if chat_sessions_collection is None:
# #         return f"SESSION_{int(datetime.now(timezone.utc).timestamp())}"
    
# #     # Check for active session (within last 30 minutes)
# #     cutoff = datetime.now(timezone.utc) - timedelta(minutes=30)
# #     active_session = chat_sessions_collection.find_one({
# #         "user_id": user_id,
# #         "end_time": None,
# #         "start_time": {"$gte": cutoff}
# #     })
    
# #     if active_session:
# #         print(f"Reusing session: {active_session['session_id']}")
# #         return active_session["session_id"]
    
# #     # Create new session
# #     session_id = f"SESSION_{int(datetime.now(timezone.utc).timestamp())}"
# #     session_doc = {
# #         "session_id": session_id,
# #         "user_id": user_id,
# #         "start_time": datetime.now(timezone.utc),
# #         "end_time": None,
# #         "message_count": 0,
# #         "escalated": False,
# #         "feedback_submitted": False
# #     }
# #     chat_sessions_collection.insert_one(session_doc)
# #     print(f"Created new session: {session_id}")
# #     return session_id

# # def update_session_message_count(session_id: str):
# #     """Increment message count for session"""
# #     if chat_sessions_collection is None:
# #         return
    
# #     chat_sessions_collection.update_one(
# #         {"session_id": session_id},
# #         {"$inc": {"message_count": 1}}
# #     )

# # def classify_user_intent(user_msg, history, user_name="there"):
# #     """Use AI to classify user intent with smart goodbye detection"""
    
# #     msg_lower = user_msg.lower().strip()
# #     msg_words = msg_lower.split()
    
# #     # STRICT goodbye detection - only exact matches or clear phrases
# #     goodbye_exact = ['bye', 'goodbye', 'thanks', 'thank you', 'thankyou', 'done', 'ok', 'okay']
# #     goodbye_starts = ['thanks for', 'thank you for', "that's all", 'all set', 'got it', 
# #                      "i'm good", "im good", 'nothing else', "that's it", "thats it"]
    
# #     # Check if it's a question first - questions are NEVER goodbyes
# #     if '?' in user_msg:
# #         pass  # Continue to AI classification
    
# #     # Very short messages (1-3 words) - check exact match
# #     elif len(msg_words) <= 3:
# #         # Must be EXACTLY one of the goodbye phrases
# #         if msg_lower in goodbye_exact:
# #             print(f"DETECTED CONVERSATION END: '{user_msg}'")
# #             return "CONVERSATION_END"
    
# #     # Medium messages (4-6 words) - check if starts with goodbye phrase
# #     elif len(msg_words) <= 6:
# #         for phrase in goodbye_starts:
# #             if msg_lower.startswith(phrase):
# #                 print(f"DETECTED CONVERSATION END: '{user_msg}'")
# #                 return "CONVERSATION_END"
    
# #     # Get last bot message for context
# #     last_bot_msg = ""
# #     if history and len(history) > 0:
# #         last_bot_msg = history[-1].get("content", "")[:200]
    
# #     classification_prompt = f"""You are analyzing a user's message in a food delivery support chat.

# # User message: "{user_msg}"
# # Last assistant message: "{last_bot_msg}"

# # Classify the user's PRIMARY INTENT into ONE category:

# # GREETING - Starting conversation (hi, hello, hey, good morning)
# # ORDER_TRACKING - Wants to see/track their orders
# # ORDER_SELECTION - Selecting specific order by number/ID (1, 2, 3, first, second, or UUID pattern)
# # REFUND_CHECK - Wants to check refund status
# # REFUND_SELECTION - Selecting specific refund by number/ID
# # PROFILE_INFO - Asking what you know about them, account info, chat history, context, memory
# # EMAIL_REQUEST - Asking for their email address specifically
# # ORDER_ISSUE - Reporting problem (wrong items, missing, cold, damaged, late)
# # CANCELLATION - Wants to cancel order
# # FAQ_DELIVERY - Questions about delivery partner, driver contact, tracking
# # FAQ_PAYMENT - Questions about payment methods, charges, promo codes, discounts, offers, subscriptions
# # FAQ_ADDRESS - Questions about changing delivery address
# # FAQ_GENERAL - Other policy questions (timing, refunds policy, etc)
# # RECOMMENDATION - Asking for food/restaurant suggestions
# # CONVERSATION_END - User is EXPLICITLY ending (bye, thanks alone, done alone - NOT questions with these words)
# # OTHER - Anything that doesn't fit above

# # CRITICAL RULES:
# # - "is your food good?" = OTHER (it's a question)
# # - "thanks" alone = CONVERSATION_END
# # - "ok thanks" = CONVERSATION_END
# # - Random text = OTHER
# # - Any message with "?" = NOT conversation end
# # - "how good is..." = OTHER (question)
# # - Promo codes/discounts/subscriptions = FAQ_PAYMENT

# # Respond with ONLY the category name in uppercase."""

# #     try:
# #         response = model.generate_content(classification_prompt)
# #         intent = response.text.strip().upper().replace(" ", "_")
# #         print(f"[Intent Classification] User: '{user_msg[:50]}...' -> Intent: {intent}")
# #         return intent
# #     except Exception as e:
# #         print(f"Intent classification error: {e}")
# #         return "OTHER"

# # def is_uuid_pattern(text):
# #     """Check if text matches UUID pattern"""
# #     uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
# #     return bool(re.match(uuid_pattern, text.lower().strip()))

# # def parse_selection_number(user_msg, max_items=5):
# #     """Parse selection number from various formats"""
# #     msg = user_msg.lower().strip()
    
# #     # Direct number
# #     if msg.isdigit():
# #         num = int(msg)
# #         if 1 <= num <= max_items:
# #             return num - 1
    
# #     # Extract number from phrases like "order 2" or "refund 3"
# #     match = re.search(r'\b(\d+)\b', msg)
# #     if match:
# #         num = int(match.group(1))
# #         if 1 <= num <= max_items:
# #             return num - 1
    
# #     # Text numbers
# #     words = {'first':0,'second':1,'third':2,'fourth':3,'fifth':4,'one':0,'two':1,'three':2,'four':3,'five':4}
# #     for word, idx in words.items():
# #         if word in msg and idx < max_items:
# #             return idx
    
# #     return None

# # def get_user_profile_summary(user_id):
# #     """Generate user profile summary without exact message counts"""
# #     try:
# #         user_info = get_user_by_id(user_id)
        
# #         recent_orders = list(orders_col.find({"user_id": user_id}).sort("order_date", -1).limit(5))
# #         total_orders = orders_col.count_documents({"user_id": user_id})
        
# #         refunds = list(refunds_col.find({"user_id": user_id}))
# #         total_refunds = len(refunds)
# #         pending_refunds = len([r for r in refunds if r.get('status') == 'Pending'])
# #         processed_refunds = len([r for r in refunds if r.get('status') == 'Processed'])
        
# #         total_conversations = messages_collection.count_documents({"user_id": user_id})
        
# #         summary = f"User Information:\n"
# #         summary += f"- Name: {user_info.get('name', 'Unknown')}\n"
# #         summary += f"- Total Orders: {total_orders}\n"
        
# #         if recent_orders:
# #             summary += f"\nRecent Orders:\n"
# #             for idx, order in enumerate(recent_orders[:3], 1):
# #                 restaurant = order.get('restaurant', 'Unknown')
# #                 status = order.get('status', 'Unknown')
# #                 summary += f"  {idx}. {restaurant} - {status}\n"
        
# #         if total_refunds > 0:
# #             summary += f"\nRefunds: {total_refunds} total"
# #             if pending_refunds > 0:
# #                 summary += f", {pending_refunds} pending"
# #             if processed_refunds > 0:
# #                 summary += f", {processed_refunds} processed"
# #             summary += "\n"
        
# #         # Vague conversation history mention
# #         if total_conversations > 50:
# #             summary += f"\nConversation History: Extensive chat history available\n"
# #         elif total_conversations > 10:
# #             summary += f"\nConversation History: Previous conversations on record\n"
# #         else:
# #             summary += f"\nConversation History: Recent chat history available\n"
        
# #         return summary
        
# #     except Exception as e:
# #         print(f"Error generating user profile: {e}")
# #         return ""

# # def get_order_list(user_id):
# #     """Get order list formatted for frontend cards"""
# #     if orders_col is None:
# #          return None, "System error: Order database is not available."

# #     orders = list(orders_col.find({"user_id": user_id}).sort("order_date", -1))
# #     if not orders:
# #         return None, "You don't have any orders yet. Place your first order through our app or website!"

# #     orders_data = []
# #     for o in orders[:10]:
# #         try:
# #             order_date = o.get('order_date')
# #             if isinstance(order_date, str):
# #                 dt = datetime.fromisoformat(order_date.replace('Z', '+00:00'))
# #             else:
# #                 dt = order_date
# #             date_str = dt.strftime("%b %d, %Y at %I:%M %p")
# #         except:
# #             date_str = str(order_date) if order_date else "Unknown"
        
# #         orders_data.append({
# #             "order_id": o['order_id'],
# #             "restaurant": o.get('restaurant', 'Unknown Restaurant'),
# #             "items": o.get('items', []),
# #             "total_amount": o.get('total_amount', 0),
# #             "status": o.get('status', 'Unknown'),
# #             "order_date": date_str,
# #             "delivery_address": o.get('delivery_address', 'Not specified')
# #         })
    
# #     return orders_data, "ORDER_LIST"

# # def get_specific_order_details(order_id, user_id):
# #     """Get detailed order information"""
# #     if orders_col is None:
# #         return "System error: Order database unavailable."

# #     order = orders_col.find_one({"order_id": order_id, "user_id": user_id})
# #     if not order:
# #         return "I couldn't find that order. Please verify the order ID."

# #     items = order.get("items", [])
# #     items_str = ", ".join(items) if items else "No items"
# #     status_lower = order.get('status','Unknown').lower()
    
# #     try:
# #         expected_delivery = order.get('expected_delivery_time')
# #         if expected_delivery:
# #             dt = datetime.fromisoformat(expected_delivery.replace('Z', '+00:00')) if isinstance(expected_delivery, str) else expected_delivery
# #             expected_str = dt.strftime("%I:%M %p")
# #         else:
# #             expected_str = "Not available"
# #     except:
# #         expected_str = "Not available"

# #     try:
# #         order_date = order.get('order_date')
# #         if order_date:
# #             dt = datetime.fromisoformat(order_date.replace('Z', '+00:00')) if isinstance(order_date, str) else order_date
# #             order_date_str = dt.strftime("%b %d, %Y at %I:%M %p")
# #         else:
# #             order_date_str = "Not available"
# #     except:
# #         order_date_str = "Not available"

# #     status_msg = ""
# #     if 'preparing' in status_lower or 'processing' in status_lower:
# #         status_msg = "Your food is being prepared."
# #     elif 'ready' in status_lower:
# #         status_msg = "Your food is ready for pickup."
# #     elif 'out for delivery' in status_lower:
# #         status_msg = "Your order is on the way!"
# #     elif 'delivered' in status_lower:
# #         status_msg = "Order delivered."
# #     elif 'cancelled' in status_lower:
# #         status_msg = "This order was cancelled."

# #     response = f"""ORDER DETAILS — {order.get('restaurant', 'Unknown')}

# # Status: {order.get('status', 'Unknown')} | Ordered: {order_date_str} | Expected: {expected_str}

# # Items: {items_str}

# # Total: ${order.get('total_amount','N/A')} | Delivery: {order.get('delivery_address', 'Not specified')}

# # {status_msg}

# # Order ID: {order['order_id'][:18]}..."""

# #     return response

# # def get_refund_list(user_id):
# #     """List refunds"""
# #     if refunds_col is None:
# #         return None, "System error: Refund database unavailable."

# #     refunds = list(refunds_col.find({"user_id": user_id}).sort("request_time", -1))
# #     if not refunds:
# #         return None, "No refund requests found. Need help with an order issue?"

# #     response = "YOUR REFUND REQUESTS\n═══════════════════════════\n\n"
    
# #     for idx, r in enumerate(refunds[:5], 1):
# #         status = r.get('status', 'Unknown')
# #         amount = r.get('amount', 0)
# #         reason = r.get('reason', 'No reason provided')
# #         refund_id_short = r['refund_id'][:8]
# #         order_id_short = r['order_id'][:8]
        
# #         try:
# #             req_time = r.get('request_time')
# #             dt = datetime.fromisoformat(req_time.replace('Z', '+00:00')) if isinstance(req_time, str) else req_time
# #             time_str = dt.strftime("%b %d, %Y")
# #         except:
# #             time_str = "Unknown date"
        
# #         status_emoji = "⏳" if status == "Pending" else "✓" if status in ["Processed", "Approved"] else "✗"
        
# #         response += f"{idx}. Refund #{refund_id_short}... | Order #{order_id_short}...\n"
# #         response += f"   {status_emoji} Status: {status} | Amount: ${amount} | {time_str}\n"
# #         response += f"   Reason: {reason}\n\n"
    
# #     response += "═══════════════════════════\n\nType a number (1-5) for details."
    
# #     return [r['refund_id'] for r in refunds[:5]], response

# # def get_specific_refund_details(refund_id, user_id):
# #     """Get detailed refund information"""
# #     if refunds_col is None:
# #         return "System error: Refund database unavailable."

# #     refund = refunds_col.find_one({"refund_id": refund_id, "user_id": user_id})
# #     if not refund:
# #         return "I couldn't find that refund request."

# #     status = refund.get('status', 'Unknown')
# #     amount = refund.get('amount', 0)
# #     reason = refund.get('reason', 'No reason provided')
# #     order_id = refund.get('order_id', 'Unknown')
    
# #     try:
# #         req_time = refund.get('request_time')
# #         dt = datetime.fromisoformat(req_time.replace('Z', '+00:00')) if isinstance(req_time, str) else req_time
# #         time_str = dt.strftime("%b %d, %Y at %I:%M %p")
# #     except:
# #         time_str = "Unknown date"
    
# #     status_lower = status.lower()
    
# #     if 'pending' in status_lower:
# #         status_msg = "Your refund is being reviewed (typically 1-2 business days)."
# #     elif 'approved' in status_lower:
# #         status_msg = "Your refund has been approved and will be processed soon."
# #     elif 'processed' in status_lower:
# #         status_msg = "Refund processed. You should receive it within 5-7 business days (bank) or instantly (wallet)."
# #     elif 'rejected' in status_lower:
# #         status_msg = "Your refund request was not approved. Contact support for details."
# #     else:
# #         status_msg = ""
    
# #     response = f"""REFUND DETAILS
# # ═══════════════════════════

# # Refund ID: {refund['refund_id'][:18]}...
# # Order ID: {order_id[:18]}...

# # Status: {status}
# # Amount: ${amount}
# # Reason: {reason}
# # Requested: {time_str}

# # {status_msg}

# # ═══════════════════════════"""

# #     return response

# # def get_bot_reply(user_id, user_msg, current_user_role="user", retry_count=0):
# #     """Generate bot reply using AI-based intent classification"""
# #     max_retries = 2
# #     history = get_cached_history(user_id, limit=30)
# #     user_info = get_user_by_id(user_id)
# #     user_name = user_info.get("name","there") if user_info else "there"

# #     # Track session
# #     try:
# #         session_id = get_or_create_session(user_id)
# #         update_session_message_count(session_id)
        
# #         print(f"Session: {session_id}")
        
# #         if chat_sessions_collection is not None:
# #             current_session = chat_sessions_collection.find_one({"session_id": session_id})
# #             if current_session:
# #                 print(f"Message count: {current_session.get('message_count', 0)}")
# #                 print(f"Feedback submitted: {current_session.get('feedback_submitted', False)}")
# #     except Exception as e:
# #         print(f"Session tracking error: {e}")

# #     # ESCALATION CHECK
# #     try:
# #         escalate_flag, reason = should_escalate(user_msg, history)
# #         if escalate_flag:
# #             escalation_id = create_escalation(user_id, reason, {"recent_messages": history[-10:]})
# #             bot_msg = f"I understand this requires immediate attention. Case ID: {escalation_id}. Click 'Talk to Human Agent' above."
# #             save_message(user_id, user_msg, bot_msg)
# #             return bot_msg
# #     except Exception as e:
# #         print(f"Escalation check error: {e}")

# #     # DIRECT UUID DETECTION
# #     if is_uuid_pattern(user_msg):
# #         print(f"Detected UUID pattern: {user_msg}")
# #         try:
# #             bot_msg = get_specific_order_details(user_msg, user_id)
# #             save_message(user_id, user_msg, bot_msg)
# #             return bot_msg
# #         except Exception as e:
# #             print(f"Error fetching order: {e}")
# #             bot_msg = "I couldn't find that order. Please verify the order ID."
# #             save_message(user_id, user_msg, bot_msg)
# #             return bot_msg

# #     # AI-BASED INTENT CLASSIFICATION
# #     intent = classify_user_intent(user_msg, history, user_name)
    
# #     # HANDLE INTENT-BASED ROUTING
# #     if intent == "EMAIL_REQUEST":
# #         bot_msg = f"Hi {user_name}! For your security, I can't display your email address in the chat. You can view it in your account settings. Need help with something else?"
# #         save_message(user_id, user_msg, bot_msg)
# #         return bot_msg
    
# #     elif intent == "GREETING":
# #         bot_msg = (
# #             f"Hello {user_name}! I'm your food delivery support assistant.\n\n"
# #             f"I can help with:\n"
# #             f"- Track order status\n"
# #             f"- Check refunds\n"
# #             f"- Answer delivery questions\n"
# #             f"- Resolve order issues\n\n"
# #             f"What would you like help with?"
# #         )
# #         save_message(user_id, user_msg, bot_msg)
# #         return bot_msg
    
# #     elif intent == "CONVERSATION_END":
# #         bot_msg = f"You're welcome, {user_name}! Have a great day!"
# #         save_message(user_id, user_msg, bot_msg)
        
# #         try:
# #             if chat_sessions_collection is not None:
# #                 result = chat_sessions_collection.update_one(
# #                     {"user_id": user_id, "end_time": None},
# #                     {"$set": {"end_time": datetime.now(timezone.utc)}},
# #                     upsert=False
# #                 )
# #                 if result.modified_count > 0:
# #                     print(f"Session ended for user {user_id}")
# #         except Exception as e:
# #             print(f"Error marking session end: {e}")
        
# #         return bot_msg
    
# #     elif intent == "ORDER_TRACKING":
# #         try:
# #             ids, bot_msg = get_order_list(user_id)
# #             save_message(user_id, user_msg, bot_msg)
# #             return bot_msg
# #         except Exception as e:
# #             print(f"Order tracking error: {e}")
# #             bot_msg = "I couldn't access your orders right now. Please try again."
# #             save_message(user_id, user_msg, bot_msg)
# #             return bot_msg
    
# #     elif intent == "ORDER_SELECTION":
# #         try:
# #             orders = list(orders_col.find({"user_id": user_id}).sort("order_date",-1).limit(5))
# #             if not orders:
# #                 bot_msg = "You don't have any orders to select from."
# #                 save_message(user_id, user_msg, bot_msg)
# #                 return bot_msg
            
# #             idx = parse_selection_number(user_msg, len(orders))
# #             if idx is not None and idx < len(orders):
# #                 order_id = orders[idx]['order_id']
# #                 bot_msg = get_specific_order_details(order_id, user_id)
# #                 save_message(user_id, user_msg, bot_msg)
# #                 return bot_msg
            
# #             msg_lower = user_msg.lower().strip()
# #             for order in orders:
# #                 if order['order_id'][:8].lower() in msg_lower:
# #                     bot_msg = get_specific_order_details(order['order_id'], user_id)
# #                     save_message(user_id, user_msg, bot_msg)
# #                     return bot_msg
            
# #             bot_msg = "I couldn't identify that order. Please type a number (1-5) or the full order ID."
# #             save_message(user_id, user_msg, bot_msg)
# #             return bot_msg
            
# #         except Exception as e:
# #             print(f"Order selection error: {e}")
# #             bot_msg = "I had trouble processing your selection. Please try again."
# #             save_message(user_id, user_msg, bot_msg)
# #             return bot_msg
    
# #     elif intent == "REFUND_CHECK":
# #         try:
# #             ids, bot_msg = get_refund_list(user_id)
# #             save_message(user_id, user_msg, bot_msg)
# #             return bot_msg
# #         except Exception as e:
# #             print(f"Refund check error: {e}")
# #             bot_msg = "I couldn't access your refunds right now. Please try again."
# #             save_message(user_id, user_msg, bot_msg)
# #             return bot_msg
    
# #     elif intent == "REFUND_SELECTION":
# #         try:
# #             refunds = list(refunds_col.find({"user_id": user_id}).sort("request_time",-1).limit(5))
# #             if not refunds:
# #                 bot_msg = "You don't have any refunds to select from."
# #                 save_message(user_id, user_msg, bot_msg)
# #                 return bot_msg
            
# #             idx = parse_selection_number(user_msg, len(refunds))
# #             if idx is not None and idx < len(refunds):
# #                 refund_id = refunds[idx]['refund_id']
# #                 bot_msg = get_specific_refund_details(refund_id, user_id)
# #                 save_message(user_id, user_msg, bot_msg)
# #                 return bot_msg
            
# #             bot_msg = "I couldn't identify that refund. Please type a number (1-5)."
# #             save_message(user_id, user_msg, bot_msg)
# #             return bot_msg
            
# #         except Exception as e:
# #             print(f"Refund selection error: {e}")
# #             bot_msg = "I had trouble processing your selection. Please try again."
# #             save_message(user_id, user_msg, bot_msg)
# #             return bot_msg
    
# #     elif intent == "PROFILE_INFO":
# #         user_profile = get_user_profile_summary(user_id)
        
# #         profile_prompt = f"""You are a helpful food delivery assistant talking to {user_name}.

# # User asked: "{user_msg}"

# # Here's what you know about them:
# # {user_profile}

# # Respond naturally and conversationally. Mention:
# # - You have access to their conversation history and remember previous chats
# # - Their order activity
# # - Current refund status if any
# # - Be friendly and helpful

# # IMPORTANT: Don't mention exact message counts (sounds creepy). Just say you remember previous conversations.
# # Keep response under 4 sentences."""

# #         try:
# #             response = model.generate_content(profile_prompt)
# #             bot_msg = response.text.strip()
# #         except:
# #             bot_msg = f"I have access to your order history and our previous conversations, {user_name}. You've placed {orders_col.count_documents({'user_id': user_id})} orders with us. How can I help you today?"
        
# #         save_message(user_id, user_msg, bot_msg)
# #         return bot_msg
    
# #     elif intent == "RECOMMENDATION":
# #         bot_msg = (
# #             f"I'm a support assistant, so I can't place orders or make recommendations.\n\n"
# #             f"To browse restaurants and menus, use our main app or website. Once you place an order, I can help track it!"
# #         )
# #         save_message(user_id, user_msg, bot_msg)
# #         return bot_msg
    
# #     # FAQ HANDLING - Dynamic, no hardcoding
# #     elif intent.startswith("FAQ_"):
# #         try:
# #             from .faq_context import find_best_faq_match
            
# #             faq_match = find_best_faq_match(user_msg, intent)
            
# #             if faq_match and faq_match.get("answer"):
# #                 bot_msg = faq_match["answer"]
# #                 save_message(user_id, user_msg, bot_msg)
                
# #                 # Update usage count
# #                 try:
# #                     if db is not None:
# #                         db["faqs"].update_one(
# #                             {"faq_id": faq_match["faq_id"]},
# #                             {"$inc": {"usage_count": 1}}
# #                         )
# #                         print(f"Returned FAQ: {faq_match.get('faq_id')} - {faq_match.get('question')}")
# #                 except Exception as update_error:
# #                     print(f"Failed to update FAQ usage: {update_error}")
                
# #                 return bot_msg
# #             else:
# #                 print(f"No FAQ match found for intent: {intent}, falling back to AI")
        
# #         except Exception as e:
# #             print(f"FAQ lookup error: {e}")
# #             import traceback
# #             traceback.print_exc()
    
# #     # FALLBACK: Use AI with FAQ context
# #     try:
# #         faq_knowledge = get_faq_context()
        
# #         system_prompt = (
# #             f"You are a professional food delivery support assistant helping {user_name}. "
# #             f"Be helpful, empathetic, and concise.\n\n"
# #             f"{faq_knowledge}\n\n"
# #             f"Use the FAQ knowledge to answer questions accurately. "
# #             f"Keep responses brief (2-4 sentences).\n\n"
# #             f"GUIDELINES:\n"
# #             f"- For order problems: Empathize and guide them to track their order first\n"
# #             f"- For cancellations: Explain the policy from FAQ\n"
# #             f"- For delivery partner contact: Explain it shows in app once order is out for delivery\n"
# #             f"- For policy questions: Answer directly from FAQ knowledge\n"
# #         )
        
# #         context_text = system_prompt + "\n\nRecent conversation:\n"
# #         for m in history[-4:]:
# #             role = "User" if m['role']=="user" else "Assistant"
# #             context_text += f"{role}: {m['content'][:150]}\n"
# #         context_text += f"User: {user_msg}\nAssistant:"

# #         response = model.generate_content(context_text)
# #         bot_msg = response.text.strip() if response.text else f"Hi {user_name}! How can I help?"

# #     except Exception as e:
# #         if retry_count < max_retries:
# #             time.sleep(1)
# #             return get_bot_reply(user_id, user_msg, current_user_role, retry_count+1)
# #         bot_msg = f"Hi {user_name}! I'm experiencing technical difficulties. Please try again."

# #     save_message(user_id, user_msg, bot_msg)
# #     return bot_msg


# # import time
# # from datetime import datetime, timezone, timedelta
# # from .database import load_chat_history, save_message, get_user_by_id, messages_collection
# # from .config import orders_col, refunds_col, db, model
# # from .escalation import should_escalate, create_escalation
# # from .faq_context import get_faq_context
# # import re

# # # In-memory session cache
# # session_cache = {}
# # CACHE_DURATION = timedelta(minutes=15)

# # # Initialize collections
# # chat_sessions_collection = db["chat_sessions"] if db is not None else None


# # def get_cached_history(user_id, limit=30):
# #     """Retrieve recent conversation history from cache or database."""
# #     now = datetime.now(timezone.utc)
# #     if user_id in session_cache:
# #         cached_data, timestamp = session_cache[user_id]
# #         if now - timestamp < CACHE_DURATION:
# #             return cached_data[:limit]

# #     history = load_chat_history(user_id, limit=limit)
# #     session_cache[user_id] = (history, now)
# #     cleanup_cache()
# #     return history

# # def cleanup_cache():
# #     """Remove expired cache entries."""
# #     now = datetime.now(timezone.utc)
# #     expired = [uid for uid, (_, ts) in session_cache.items() if now - ts > CACHE_DURATION]
# #     for uid in expired:
# #         del session_cache[uid]

# # def invalidate_cache(user_id):
# #     """Clear cache when new message is saved."""
# #     if user_id in session_cache:
# #         del session_cache[user_id]

# # def get_or_create_session(user_id: str) -> str:
# #     """Get current session or create new one"""
# #     if chat_sessions_collection is None:
# #         return f"SESSION_{int(datetime.now(timezone.utc).timestamp())}"
    
# #     # Check for active session (within last 30 minutes)
# #     cutoff = datetime.now(timezone.utc) - timedelta(minutes=30)
# #     active_session = chat_sessions_collection.find_one({
# #         "user_id": user_id,
# #         "end_time": None,
# #         "start_time": {"$gte": cutoff}
# #     })
    
# #     if active_session:
# #         print(f"Reusing session: {active_session['session_id']}")
# #         return active_session["session_id"]
    
# #     # Create new session
# #     session_id = f"SESSION_{int(datetime.now(timezone.utc).timestamp())}"
# #     session_doc = {
# #         "session_id": session_id,
# #         "user_id": user_id,
# #         "start_time": datetime.now(timezone.utc),
# #         "end_time": None,
# #         "message_count": 0,
# #         "escalated": False,
# #         "feedback_submitted": False
# #     }
# #     chat_sessions_collection.insert_one(session_doc)
# #     print(f"Created new session: {session_id}")
# #     return session_id

# # def update_session_message_count(session_id: str):
# #     """Increment message count for session"""
# #     if chat_sessions_collection is None:
# #         return
    
# #     chat_sessions_collection.update_one(
# #         {"session_id": session_id},
# #         {"$inc": {"message_count": 1}}
# #     )

# # def classify_user_intent(user_msg, history, user_name="there"):
# #     """Use AI to classify user intent with smart goodbye detection"""
    
# #     msg_lower = user_msg.lower().strip()
# #     msg_words = msg_lower.split()
    
# #     # STRICT goodbye detection - only exact matches or clear phrases
# #     goodbye_exact = ['bye', 'goodbye', 'thanks', 'thank you', 'thankyou', 'done', 'ok', 'okay']
# #     goodbye_starts = ['thanks for', 'thank you for', "that's all", 'all set', 'got it', 
# #                      "i'm good", "im good", 'nothing else', "that's it", "thats it"]
    
# #     # Check if it's a question first - questions are NEVER goodbyes
# #     if '?' in user_msg:
# #         pass  # Continue to AI classification
    
# #     # Very short messages (1-3 words) - check exact match
# #     elif len(msg_words) <= 3:
# #         # Must be EXACTLY one of the goodbye phrases
# #         if msg_lower in goodbye_exact:
# #             print(f"DETECTED CONVERSATION END: '{user_msg}'")
# #             return "CONVERSATION_END"
    
# #     # Medium messages (4-6 words) - check if starts with goodbye phrase
# #     elif len(msg_words) <= 6:
# #         for phrase in goodbye_starts:
# #             if msg_lower.startswith(phrase):
# #                 print(f"DETECTED CONVERSATION END: '{user_msg}'")
# #                 return "CONVERSATION_END"
    
# #     # Get last bot message for context
# #     last_bot_msg = ""
# #     if history and len(history) > 0:
# #         last_bot_msg = history[-1].get("content", "")[:200]
    
# #     classification_prompt = f"""You are analyzing a user's message in a food delivery support chat.

# # User message: "{user_msg}"
# # Last assistant message: "{last_bot_msg}"

# # Classify the user's PRIMARY INTENT into ONE category:

# # GREETING - Starting conversation (hi, hello, hey, good morning)
# # ORDER_TRACKING - Wants to see/track their orders
# # ORDER_SELECTION - Selecting specific order by number/ID (1, 2, 3, first, second, or UUID pattern)
# # REFUND_CHECK - Wants to check refund status
# # REFUND_SELECTION - Selecting specific refund by number/ID
# # PROFILE_INFO - Asking what you know about them, account info, chat history, context, memory
# # EMAIL_REQUEST - Asking for their email address specifically
# # ORDER_ISSUE - Reporting problem (wrong items, missing, cold, damaged, late)
# # CANCELLATION - Wants to cancel order
# # FAQ_DELIVERY - Questions about delivery partner, driver contact, tracking
# # FAQ_PAYMENT - Questions about payment methods, charges, promo codes, discounts, offers, subscriptions
# # FAQ_ADDRESS - Questions about changing delivery address
# # FAQ_GENERAL - Other policy questions (timing, refunds policy, etc)
# # RECOMMENDATION - Asking for food/restaurant suggestions
# # CONVERSATION_END - User is EXPLICITLY ending (bye, thanks alone, done alone - NOT questions with these words)
# # OTHER - Anything that doesn't fit above

# # CRITICAL RULES:
# # - "is your food good?" = OTHER (it's a question)
# # - "thanks" alone = CONVERSATION_END
# # - "ok thanks" = CONVERSATION_END
# # - Random text = OTHER
# # - Any message with "?" = NOT conversation end
# # - "how good is..." = OTHER (question)
# # - Promo codes/discounts/subscriptions = FAQ_PAYMENT

# # Respond with ONLY the category name in uppercase."""

# #     try:
# #         response = model.generate_content(classification_prompt)
# #         intent = response.text.strip().upper().replace(" ", "_")
# #         print(f"[Intent Classification] User: '{user_msg[:50]}...' -> Intent: {intent}")
# #         return intent
# #     except Exception as e:
# #         print(f"Intent classification error: {e}")
# #         return "OTHER"

# # def is_uuid_pattern(text):
# #     """Check if text matches UUID pattern"""
# #     uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
# #     return bool(re.match(uuid_pattern, text.lower().strip()))

# # def parse_selection_number(user_msg, max_items=5):
# #     """Parse selection number from various formats"""
# #     msg = user_msg.lower().strip()
    
# #     # Direct number
# #     if msg.isdigit():
# #         num = int(msg)
# #         if 1 <= num <= max_items:
# #             return num - 1
    
# #     # Extract number from phrases like "order 2" or "refund 3"
# #     match = re.search(r'\b(\d+)\b', msg)
# #     if match:
# #         num = int(match.group(1))
# #         if 1 <= num <= max_items:
# #             return num - 1
    
# #     # Text numbers
# #     words = {'first':0,'second':1,'third':2,'fourth':3,'fifth':4,'one':0,'two':1,'three':2,'four':3,'five':4}
# #     for word, idx in words.items():
# #         if word in msg and idx < max_items:
# #             return idx
    
# #     return None

# # def get_user_profile_summary(user_id):
# #     """Generate user profile summary without exact message counts"""
# #     try:
# #         user_info = get_user_by_id(user_id)
        
# #         recent_orders = list(orders_col.find({"user_id": user_id}).sort("order_date", -1).limit(5))
# #         total_orders = orders_col.count_documents({"user_id": user_id})
        
# #         refunds = list(refunds_col.find({"user_id": user_id}))
# #         total_refunds = len(refunds)
# #         pending_refunds = len([r for r in refunds if r.get('status') == 'Pending'])
# #         processed_refunds = len([r for r in refunds if r.get('status') == 'Processed'])
        
# #         total_conversations = messages_collection.count_documents({"user_id": user_id})
        
# #         summary = f"User Information:\n"
# #         summary += f"- Name: {user_info.get('name', 'Unknown')}\n"
# #         summary += f"- Total Orders: {total_orders}\n"
        
# #         if recent_orders:
# #             summary += f"\nRecent Orders:\n"
# #             for idx, order in enumerate(recent_orders[:3], 1):
# #                 restaurant = order.get('restaurant', 'Unknown')
# #                 status = order.get('status', 'Unknown')
# #                 summary += f"  {idx}. {restaurant} - {status}\n"
        
# #         if total_refunds > 0:
# #             summary += f"\nRefunds: {total_refunds} total"
# #             if pending_refunds > 0:
# #                 summary += f", {pending_refunds} pending"
# #             if processed_refunds > 0:
# #                 summary += f", {processed_refunds} processed"
# #             summary += "\n"
        
# #         # Vague conversation history mention
# #         if total_conversations > 50:
# #             summary += f"\nConversation History: Extensive chat history available\n"
# #         elif total_conversations > 10:
# #             summary += f"\nConversation History: Previous conversations on record\n"
# #         else:
# #             summary += f"\nConversation History: Recent chat history available\n"
        
# #         return summary
        
# #     except Exception as e:
# #         print(f"Error generating user profile: {e}")
# #         return ""

# # def get_order_list(user_id):
# #     """Get order list formatted for frontend cards"""
# #     if orders_col is None:
# #          return None, "System error: Order database is not available."

# #     orders = list(orders_col.find({"user_id": user_id}).sort("order_date", -1))
# #     if not orders:
# #         return None, "You don't have any orders yet. Place your first order through our app or website!"

# #     orders_data = []
# #     for o in orders[:10]:
# #         try:
# #             order_date = o.get('order_date')
# #             if isinstance(order_date, str):
# #                 dt = datetime.fromisoformat(order_date.replace('Z', '+00:00'))
# #             else:
# #                 dt = order_date
# #             date_str = dt.strftime("%b %d, %Y at %I:%M %p")
# #         except:
# #             date_str = str(order_date) if order_date else "Unknown"
        
# #         orders_data.append({
# #             "order_id": o['order_id'],
# #             "restaurant": o.get('restaurant', 'Unknown Restaurant'),
# #             "items": o.get('items', []),
# #             "total_amount": o.get('total_amount', 0),
# #             "status": o.get('status', 'Unknown'),
# #             "order_date": date_str,
# #             "delivery_address": o.get('delivery_address', 'Not specified')
# #         })
    
# #     return orders_data, "ORDER_LIST"

# # def get_specific_order_details(order_id, user_id):
# #     """Get detailed order information"""
# #     if orders_col is None:
# #         return "System error: Order database unavailable."

# #     order = orders_col.find_one({"order_id": order_id, "user_id": user_id})
# #     if not order:
# #         return "I couldn't find that order. Please verify the order ID."

# #     items = order.get("items", [])
# #     items_str = ", ".join(items) if items else "No items"
# #     status_lower = order.get('status','Unknown').lower()
    
# #     try:
# #         expected_delivery = order.get('expected_delivery_time')
# #         if expected_delivery:
# #             dt = datetime.fromisoformat(expected_delivery.replace('Z', '+00:00')) if isinstance(expected_delivery, str) else expected_delivery
# #             expected_str = dt.strftime("%I:%M %p")
# #         else:
# #             expected_str = "Not available"
# #     except:
# #         expected_str = "Not available"

# #     try:
# #         order_date = order.get('order_date')
# #         if order_date:
# #             dt = datetime.fromisoformat(order_date.replace('Z', '+00:00')) if isinstance(order_date, str) else order_date
# #             order_date_str = dt.strftime("%b %d, %Y at %I:%M %p")
# #         else:
# #             order_date_str = "Not available"
# #     except:
# #         order_date_str = "Not available"

# #     status_msg = ""
# #     if 'preparing' in status_lower or 'processing' in status_lower:
# #         status_msg = "Your food is being prepared."
# #     elif 'ready' in status_lower:
# #         status_msg = "Your food is ready for pickup."
# #     elif 'out for delivery' in status_lower:
# #         status_msg = "Your order is on the way!"
# #     elif 'delivered' in status_lower:
# #         status_msg = "Order delivered."
# #     elif 'cancelled' in status_lower:
# #         status_msg = "This order was cancelled."

# #     response = f"""ORDER DETAILS — {order.get('restaurant', 'Unknown')}

# # Status: {order.get('status', 'Unknown')} | Ordered: {order_date_str} | Expected: {expected_str}

# # Items: {items_str}

# # Total: ${order.get('total_amount','N/A')} | Delivery: {order.get('delivery_address', 'Not specified')}

# # {status_msg}

# # Order ID: {order['order_id'][:18]}..."""

# #     return response

# # def get_refund_list(user_id):
# #     """List refunds"""
# #     if refunds_col is None:
# #         return None, "System error: Refund database unavailable."

# #     refunds = list(refunds_col.find({"user_id": user_id}).sort("request_time", -1))
# #     if not refunds:
# #         return None, "No refund requests found. Need help with an order issue?"

# #     response = "YOUR REFUND REQUESTS\n═══════════════════════════\n\n"
    
# #     for idx, r in enumerate(refunds[:5], 1):
# #         status = r.get('status', 'Unknown')
# #         amount = r.get('amount', 0)
# #         reason = r.get('reason', 'No reason provided')
# #         refund_id_short = r['refund_id'][:8]
# #         order_id_short = r['order_id'][:8]
        
# #         try:
# #             req_time = r.get('request_time')
# #             dt = datetime.fromisoformat(req_time.replace('Z', '+00:00')) if isinstance(req_time, str) else req_time
# #             time_str = dt.strftime("%b %d, %Y")
# #         except:
# #             time_str = "Unknown date"
        
# #         status_emoji = "⏳" if status == "Pending" else "✓" if status in ["Processed", "Approved"] else "✗"
        
# #         response += f"{idx}. Refund #{refund_id_short}... | Order #{order_id_short}...\n"
# #         response += f"   {status_emoji} Status: {status} | Amount: ${amount} | {time_str}\n"
# #         response += f"   Reason: {reason}\n\n"
    
# #     response += "═══════════════════════════\n\nType a number (1-5) for details."
    
# #     return [r['refund_id'] for r in refunds[:5]], response

# # def get_specific_refund_details(refund_id, user_id):
# #     """Get detailed refund information"""
# #     if refunds_col is None:
# #         return "System error: Refund database unavailable."

# #     refund = refunds_col.find_one({"refund_id": refund_id, "user_id": user_id})
# #     if not refund:
# #         return "I couldn't find that refund request."

# #     status = refund.get('status', 'Unknown')
# #     amount = refund.get('amount', 0)
# #     reason = refund.get('reason', 'No reason provided')
# #     order_id = refund.get('order_id', 'Unknown')
    
# #     try:
# #         req_time = refund.get('request_time')
# #         dt = datetime.fromisoformat(req_time.replace('Z', '+00:00')) if isinstance(req_time, str) else req_time
# #         time_str = dt.strftime("%b %d, %Y at %I:%M %p")
# #     except:
# #         time_str = "Unknown date"
    
# #     status_lower = status.lower()
    
# #     if 'pending' in status_lower:
# #         status_msg = "Your refund is being reviewed (typically 1-2 business days)."
# #     elif 'approved' in status_lower:
# #         status_msg = "Your refund has been approved and will be processed soon."
# #     elif 'processed' in status_lower:
# #         status_msg = "Refund processed. You should receive it within 5-7 business days (bank) or instantly (wallet)."
# #     elif 'rejected' in status_lower:
# #         status_msg = "Your refund request was not approved. Contact support for details."
# #     else:
# #         status_msg = ""
    
# #     response = f"""REFUND DETAILS
# # ═══════════════════════════

# # Refund ID: {refund['refund_id'][:18]}...
# # Order ID: {order_id[:18]}...

# # Status: {status}
# # Amount: ${amount}
# # Reason: {reason}
# # Requested: {time_str}

# # {status_msg}

# # ═══════════════════════════"""

# #     return response

# # def get_bot_reply(user_id, user_msg, current_user_role="user", retry_count=0):
# #     """Generate bot reply using AI-based intent classification"""
# #     max_retries = 2
# #     history = get_cached_history(user_id, limit=30)
# #     user_info = get_user_by_id(user_id)
# #     user_name = user_info.get("name","there") if user_info else "there"

# #     # Track session
# #     try:
# #         session_id = get_or_create_session(user_id)
# #         update_session_message_count(session_id)
        
# #         print(f"Session: {session_id}")
        
# #         if chat_sessions_collection is not None:
# #             current_session = chat_sessions_collection.find_one({"session_id": session_id})
# #             if current_session:
# #                 print(f"Message count: {current_session.get('message_count', 0)}")
# #                 print(f"Feedback submitted: {current_session.get('feedback_submitted', False)}")
# #     except Exception as e:
# #         print(f"Session tracking error: {e}")

# #     # ESCALATION CHECK
# #     try:
# #         escalate_flag, reason = should_escalate(user_msg, history)
# #         if escalate_flag:
# #             escalation_id = create_escalation(user_id, reason, {"recent_messages": history[-10:]})
# #             bot_msg = f"I understand this requires immediate attention. Case ID: {escalation_id}. Click 'Talk to Human Agent' above."
# #             save_message(user_id, user_msg, bot_msg)
# #             return bot_msg
# #     except Exception as e:
# #         print(f"Escalation check error: {e}")

# #     # DIRECT UUID DETECTION
# #     if is_uuid_pattern(user_msg):
# #         print(f"Detected UUID pattern: {user_msg}")
# #         try:
# #             bot_msg = get_specific_order_details(user_msg, user_id)
# #             save_message(user_id, user_msg, bot_msg)
# #             return bot_msg
# #         except Exception as e:
# #             print(f"Error fetching order: {e}")
# #             bot_msg = "I couldn't find that order. Please verify the order ID."
# #             save_message(user_id, user_msg, bot_msg)
# #             return bot_msg

# #     # AI-BASED INTENT CLASSIFICATION
# #     intent = classify_user_intent(user_msg, history, user_name)
    
# #     # HANDLE INTENT-BASED ROUTING
# #     if intent == "EMAIL_REQUEST":
# #         bot_msg = f"Hi {user_name}! For your security, I can't display your email address in the chat. You can view it in your account settings. Need help with something else?"
# #         save_message(user_id, user_msg, bot_msg)
# #         return bot_msg
    
# #     elif intent == "GREETING":
# #         bot_msg = (
# #             f"Hello {user_name}! I'm your food delivery support assistant.\n\n"
# #             f"I can help with:\n"
# #             f"- Track order status\n"
# #             f"- Check refunds\n"
# #             f"- Answer delivery questions\n"
# #             f"- Resolve order issues\n\n"
# #             f"What would you like help with?"
# #         )
# #         save_message(user_id, user_msg, bot_msg)
# #         return bot_msg
    
# #     elif intent == "CONVERSATION_END":
# #         bot_msg = f"You're welcome, {user_name}! Have a great day!"
# #         save_message(user_id, user_msg, bot_msg)
        
# #         try:
# #             if chat_sessions_collection is not None:
# #                 result = chat_sessions_collection.update_one(
# #                     {"user_id": user_id, "end_time": None},
# #                     {"$set": {"end_time": datetime.now(timezone.utc)}},
# #                     upsert=False
# #                 )
# #                 if result.modified_count > 0:
# #                     print(f"Session ended for user {user_id}")
# #         except Exception as e:
# #             print(f"Error marking session end: {e}")
        
# #         return bot_msg
    
# #     elif intent == "ORDER_TRACKING":
# #         try:
# #             orders_data, msg = get_order_list(user_id)
            
# #             if orders_data is None:
# #                 # No orders found - return error message
# #                 save_message(user_id, user_msg, msg)
# #                 return msg
# #             else:
# #                 # Return orders in dictionary format for frontend
# #                 save_message(user_id, user_msg, "Showing user their orders")
# #                 return {
# #                     "reply": "ORDER_LIST",
# #                     "orders": orders_data
# #                 }
# #         except Exception as e:
# #             print(f"Order tracking error: {e}")
# #             bot_msg = "I couldn't access your orders right now. Please try again."
# #             save_message(user_id, user_msg, bot_msg)
# #             return bot_msg
    
# #     elif intent == "ORDER_SELECTION":
# #         try:
# #             orders = list(orders_col.find({"user_id": user_id}).sort("order_date",-1).limit(5))
# #             if not orders:
# #                 bot_msg = "You don't have any orders to select from."
# #                 save_message(user_id, user_msg, bot_msg)
# #                 return bot_msg
            
# #             idx = parse_selection_number(user_msg, len(orders))
# #             if idx is not None and idx < len(orders):
# #                 order_id = orders[idx]['order_id']
# #                 bot_msg = get_specific_order_details(order_id, user_id)
# #                 save_message(user_id, user_msg, bot_msg)
# #                 return bot_msg
            
# #             msg_lower = user_msg.lower().strip()
# #             for order in orders:
# #                 if order['order_id'][:8].lower() in msg_lower:
# #                     bot_msg = get_specific_order_details(order['order_id'], user_id)
# #                     save_message(user_id, user_msg, bot_msg)
# #                     return bot_msg
            
# #             bot_msg = "I couldn't identify that order. Please type a number (1-5) or the full order ID."
# #             save_message(user_id, user_msg, bot_msg)
# #             return bot_msg
            
# #         except Exception as e:
# #             print(f"Order selection error: {e}")
# #             bot_msg = "I had trouble processing your selection. Please try again."
# #             save_message(user_id, user_msg, bot_msg)
# #             return bot_msg
    
# #     elif intent == "REFUND_CHECK":
# #         try:
# #             ids, bot_msg = get_refund_list(user_id)
# #             save_message(user_id, user_msg, bot_msg)
# #             return bot_msg
# #         except Exception as e:
# #             print(f"Refund check error: {e}")
# #             bot_msg = "I couldn't access your refunds right now. Please try again."
# #             save_message(user_id, user_msg, bot_msg)
# #             return bot_msg
    
# #     elif intent == "REFUND_SELECTION":
# #         try:
# #             refunds = list(refunds_col.find({"user_id": user_id}).sort("request_time",-1).limit(5))
# #             if not refunds:
# #                 bot_msg = "You don't have any refunds to select from."
# #                 save_message(user_id, user_msg, bot_msg)
# #                 return bot_msg
            
# #             idx = parse_selection_number(user_msg, len(refunds))
# #             if idx is not None and idx < len(refunds):
# #                 refund_id = refunds[idx]['refund_id']
# #                 bot_msg = get_specific_refund_details(refund_id, user_id)
# #                 save_message(user_id, user_msg, bot_msg)
# #                 return bot_msg
            
# #             bot_msg = "I couldn't identify that refund. Please type a number (1-5)."
# #             save_message(user_id, user_msg, bot_msg)
# #             return bot_msg
            
# #         except Exception as e:
# #             print(f"Refund selection error: {e}")
# #             bot_msg = "I had trouble processing your selection. Please try again."
# #             save_message(user_id, user_msg, bot_msg)
# #             return bot_msg
    
# #     elif intent == "PROFILE_INFO":
# #         user_profile = get_user_profile_summary(user_id)
        
# #         profile_prompt = f"""You are a helpful food delivery assistant talking to {user_name}.

# # User asked: "{user_msg}"

# # Here's what you know about them:
# # {user_profile}

# # Respond naturally and conversationally. Mention:
# # - You have access to their conversation history and remember previous chats
# # - Their order activity
# # - Current refund status if any
# # - Be friendly and helpful

# # IMPORTANT: Don't mention exact message counts (sounds creepy). Just say you remember previous conversations.
# # Keep response under 4 sentences."""

# #         try:
# #             response = model.generate_content(profile_prompt)
# #             bot_msg = response.text.strip()
# #         except:
# #             bot_msg = f"I have access to your order history and our previous conversations, {user_name}. You've placed {orders_col.count_documents({'user_id': user_id})} orders with us. How can I help you today?"
        
# #         save_message(user_id, user_msg, bot_msg)
# #         return bot_msg
    
# #     elif intent == "RECOMMENDATION":
# #         bot_msg = (
# #             f"I'm a support assistant, so I can't place orders or make recommendations.\n\n"
# #             f"To browse restaurants and menus, use our main app or website. Once you place an order, I can help track it!"
# #         )
# #         save_message(user_id, user_msg, bot_msg)
# #         return bot_msg
    
# #     # FAQ HANDLING - Dynamic, no hardcoding
# #     elif intent.startswith("FAQ_"):
# #         try:
# #             from .faq_context import find_best_faq_match
            
# #             faq_match = find_best_faq_match(user_msg, intent)
            
# #             if faq_match and faq_match.get("answer"):
# #                 bot_msg = faq_match["answer"]
# #                 save_message(user_id, user_msg, bot_msg)
                
# #                 # Update usage count
# #                 try:
# #                     if db is not None:
# #                         db["faqs"].update_one(
# #                             {"faq_id": faq_match["faq_id"]},
# #                             {"$inc": {"usage_count": 1}}
# #                         )
# #                         print(f"Returned FAQ: {faq_match.get('faq_id')} - {faq_match.get('question')}")
# #                 except Exception as update_error:
# #                     print(f"Failed to update FAQ usage: {update_error}")
                
# #                 return bot_msg
# #             else:
# #                 print(f"No FAQ match found for intent: {intent}, falling back to AI")
        
# #         except Exception as e:
# #             print(f"FAQ lookup error: {e}")
# #             import traceback
# #             traceback.print_exc()
    
# #     # FALLBACK: Use AI with FAQ context
# #     try:
# #         faq_knowledge = get_faq_context()
        
# #         system_prompt = (
# #             f"You are a professional food delivery support assistant helping {user_name}. "
# #             f"Be helpful, empathetic, and concise.\n\n"
# #             f"{faq_knowledge}\n\n"
# #             f"Use the FAQ knowledge to answer questions accurately. "
# #             f"Keep responses brief (2-4 sentences).\n\n"
# #             f"GUIDELINES:\n"
# #             f"- For order problems: Empathize and guide them to track their order first\n"
# #             f"- For cancellations: Explain the policy from FAQ\n"
# #             f"- For delivery partner contact: Explain it shows in app once order is out for delivery\n"
# #             f"- For policy questions: Answer directly from FAQ knowledge\n"
# #         )
        
# #         context_text = system_prompt + "\n\nRecent conversation:\n"
# #         for m in history[-4:]:
# #             role = "User" if m['role']=="user" else "Assistant"
# #             context_text += f"{role}: {m['content'][:150]}\n"
# #         context_text += f"User: {user_msg}\nAssistant:"

# #         response = model.generate_content(context_text)
# #         bot_msg = response.text.strip() if response.text else f"Hi {user_name}! How can I help?"

# #     except Exception as e:
# #         if retry_count < max_retries:
# #             time.sleep(1)
# #             return get_bot_reply(user_id, user_msg, current_user_role, retry_count+1)
# #         bot_msg = f"Hi {user_name}! I'm experiencing technical difficulties. Please try again."

# #     save_message(user_id, user_msg, bot_msg)
# #     return bot_msg







# import time
# import re
# from datetime import datetime, timezone, timedelta
# from .database import load_chat_history, save_message, get_user_by_id, messages_collection
# from .config import orders_col, refunds_col, db, model
# from .escalation import should_escalate, create_escalation
# from .faq_context import get_faq_context

# # In-memory session cache
# session_cache = {}
# CACHE_DURATION = timedelta(minutes=15)

# # Initialize collections
# chat_sessions_collection = db["chat_sessions"] if db is not None else None


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
#         # FIX: Changed 'uid' to 'user_id' to match the function's argument
#         del session_cache[user_id]

# def get_or_create_session(user_id: str) -> str:
#     """Get current session or create new one"""
#     if chat_sessions_collection is None:
#         return f"SESSION_{int(datetime.now(timezone.utc).timestamp())}"
    
#     # Check for active session (within last 30 minutes)
#     cutoff = datetime.now(timezone.utc) - timedelta(minutes=30)
#     active_session = chat_sessions_collection.find_one({
#         "user_id": user_id,
#         "end_time": None,
#         "start_time": {"$gte": cutoff}
#     })
    
#     if active_session:
#         print(f"Reusing session: {active_session['session_id']}")
#         return active_session["session_id"]
    
#     # Create new session
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
#     print(f"Created new session: {session_id}")
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
    
#     # STRICT goodbye detection - only exact matches or clear phrases
#     goodbye_exact = ['bye', 'goodbye', 'thanks', 'thank you', 'thankyou', 'done', 'ok', 'okay']
#     goodbye_starts = ['thanks for', 'thank you for', "that's all", 'all set', 'got it', 
#                       "i'm good", "im good", 'nothing else', "that's it", "thats it"]
    
#     # Check if it's a question first - questions are NEVER goodbyes
#     if '?' in user_msg:
#         pass  # Continue to AI classification
    
#     # Very short messages (1-3 words) - check exact match
#     elif len(msg_words) <= 3:
#         # Must be EXACTLY one of the goodbye phrases
#         if msg_lower in goodbye_exact:
#             print(f"DETECTED CONVERSATION END: '{user_msg}'")
#             return "CONVERSATION_END"
    
#     # Medium messages (4-6 words) - check if starts with goodbye phrase
#     elif len(msg_words) <= 6:
#         for phrase in goodbye_starts:
#             if msg_lower.startswith(phrase):
#                 print(f"DETECTED CONVERSATION END: '{user_msg}'")
#                 return "CONVERSATION_END"
    
#     # Get last bot message for context
#     last_bot_msg = ""
#     if history and len(history) > 0:
#         last_bot_msg = history[-1].get("content", "")[:200]
    
#     classification_prompt = f"""You are analyzing a user's message in a food delivery support chat.

# User message: "{user_msg}"
# Last assistant message: "{last_bot_msg}"

# Classify the user's PRIMARY INTENT into ONE category:

# GREETING - Starting conversation (hi, hello, hey, good morning)
# ORDER_TRACKING - Wants to see/track their orders
# ORDER_SELECTION - Selecting specific order by number/ID (1, 2, 3, first, second, or UUID pattern)
# REFUND_CHECK - Wants to check refund status
# REFUND_SELECTION - Selecting specific refund by number/ID
# PROFILE_INFO - Asking what you know about them, account info, chat history, context, memory
# EMAIL_REQUEST - Asking for their email address specifically
# ORDER_ISSUE - Reporting problem (wrong items, missing, cold, damaged, late)
# CANCELLATION - Wants to cancel order
# FAQ_DELIVERY - Questions about delivery partner, driver contact, tracking
# FAQ_PAYMENT - Questions about payment methods, charges, promo codes, discounts, offers, subscriptions
# FAQ_ADDRESS - Questions about changing delivery address
# FAQ_GENERAL - Other policy questions (timing, refunds policy, etc)
# RECOMMENDATION - Asking for food/restaurant suggestions
# CONVERSATION_END - User is EXPLICITLY ending (bye, thanks alone, done alone - NOT questions with these words)
# OTHER - Anything that doesn't fit above

# CRITICAL RULES:
# - "is your food good?" = OTHER (it's a question)
# - "thanks" alone = CONVERSATION_END
# - "ok thanks" = CONVERSATION_END
# - Random text = OTHER
# - Any message with "?" = NOT conversation end
# - "how good is..." = OTHER (question)
# - Promo codes/discounts/subscriptions = FAQ_PAYMENT

# Respond with ONLY the category name in uppercase."""

#     try:
#         response = model.generate_content(classification_prompt)
#         intent = response.text.strip().upper().replace(" ", "_")
#         print(f"[Intent Classification] User: '{user_msg[:50]}...' -> Intent: {intent}")
#         return intent
#     except Exception as e:
#         print(f"Intent classification error: {e}")
#         return "OTHER"

# def is_uuid_pattern(text):
#     """Check if text matches UUID pattern"""
#     uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
#     return bool(re.match(uuid_pattern, text.lower().strip()))

# def parse_selection_number(user_msg, max_items=5):
#     """Parse selection number from various formats"""
#     msg = user_msg.lower().strip()
    
#     # Direct number
#     if msg.isdigit():
#         num = int(msg)
#         if 1 <= num <= max_items:
#             return num - 1
    
#     # Extract number from phrases like "order 2" or "refund 3"
#     match = re.search(r'\b(\d+)\b', msg)
#     if match:
#         num = int(match.group(1))
#         if 1 <= num <= max_items:
#             return num - 1
    
#     # Text numbers
#     words = {'first':0,'second':1,'third':2,'fourth':3,'fifth':4,'one':0,'two':1,'three':2,'four':3,'five':4}
#     for word, idx in words.items():
#         if word in msg and idx < max_items:
#             return idx
    
#     return None

# def get_user_profile_summary(user_id):
#     """Generate user profile summary without exact message counts"""
#     try:
#         user_info = get_user_by_id(user_id)
        
#         recent_orders = list(orders_col.find({"user_id": user_id}).sort("order_date", -1).limit(5))
#         total_orders = orders_col.count_documents({"user_id": user_id})
        
#         refunds = list(refunds_col.find({"user_id": user_id}))
#         total_refunds = len(refunds)
#         pending_refunds = len([r for r in refunds if r.get('status') == 'Pending'])
#         processed_refunds = len([r for r in refunds if r.get('status') == 'Processed'])
        
#         total_conversations = messages_collection.count_documents({"user_id": user_id})
        
#         summary = f"User Information:\n"
#         summary += f"- Name: {user_info.get('name', 'Unknown')}\n"
#         summary += f"- Total Orders: {total_orders}\n"
        
#         if recent_orders:
#             summary += f"\nRecent Orders:\n"
#             for idx, order in enumerate(recent_orders[:3], 1):
#                 restaurant = order.get('restaurant', 'Unknown')
#                 status = order.get('status', 'Unknown')
#                 summary += f"  {idx}. {restaurant} - {status}\n"
        
#         if total_refunds > 0:
#             summary += f"\nRefunds: {total_refunds} total"
#             if pending_refunds > 0:
#                 summary += f", {pending_refunds} pending"
#             if processed_refunds > 0:
#                 summary += f", {processed_refunds} processed"
#             summary += "\n"
        
#         # Vague conversation history mention
#         if total_conversations > 50:
#             summary += f"\nConversation History: Extensive chat history available\n"
#         elif total_conversations > 10:
#             summary += f"\nConversation History: Previous conversations on record\n"
#         else:
#             summary += f"\nConversation History: Recent chat history available\n"
        
#         return summary
        
#     except Exception as e:
#         print(f"Error generating user profile: {e}")
#         return ""

# def get_order_list(user_id):
#     """Get order list formatted for frontend cards"""
#     if orders_col is None:
#         return None, "System error: Order database is not available."

#     orders = list(orders_col.find({"user_id": user_id}).sort("order_date", -1))
#     if not orders:
#         return None, "You don't have any orders yet. Place your first order through our app or website!"

#     orders_data = []
#     for o in orders[:10]:
#         try:
#             order_date = o.get('order_date')
#             if isinstance(order_date, str):
#                 dt = datetime.fromisoformat(order_date.replace('Z', '+00:00'))
#             else:
#                 dt = order_date
#             date_str = dt.strftime("%b %d, %Y at %I:%M %p")
#         except:
#             date_str = str(order_date) if order_date else "Unknown"
        
#         orders_data.append({
#             "order_id": o['order_id'],
#             "restaurant": o.get('restaurant', 'Unknown Restaurant'),
#             "items": o.get('items', []),
#             "total_amount": o.get('total_amount', 0),
#             "status": o.get('status', 'Unknown'),
#             "order_date": date_str,
#             "delivery_address": o.get('delivery_address', 'Not specified')
#         })
    
#     return orders_data, "ORDER_LIST"

# def get_specific_order_details(order_id, user_id):
#     """Get detailed order information"""
#     if orders_col is None:
#         return "System error: Order database unavailable."

#     order = orders_col.find_one({"order_id": order_id, "user_id": user_id})
#     if not order:
#         return "I couldn't find that order. Please verify the order ID."

#     items = order.get("items", [])
#     items_str = ", ".join(items) if items else "No items"
#     status_lower = order.get('status','Unknown').lower()
    
#     try:
#         expected_delivery = order.get('expected_delivery_time')
#         if expected_delivery:
#             dt = datetime.fromisoformat(expected_delivery.replace('Z', '+00:00')) if isinstance(expected_delivery, str) else expected_delivery
#             expected_str = dt.strftime("%I:%M %p")
#         else:
#             expected_str = "Not available"
#     except:
#         expected_str = "Not available"

#     try:
#         order_date = order.get('order_date')
#         if order_date:
#             dt = datetime.fromisoformat(order_date.replace('Z', '+00:00')) if isinstance(order_date, str) else order_date
#             order_date_str = dt.strftime("%b %d, %Y at %I:%M %p")
#         else:
#             order_date_str = "Not available"
#     except:
#         order_date_str = "Not available"

#     status_msg = ""
#     if 'preparing' in status_lower or 'processing' in status_lower:
#         status_msg = "Your food is being prepared."
#     elif 'ready' in status_lower:
#         status_msg = "Your food is ready for pickup."
#     elif 'out for delivery' in status_lower:
#         status_msg = "Your order is on the way!"
#     elif 'delivered' in status_lower:
#         status_msg = "Order delivered."
#     elif 'cancelled' in status_lower:
#         status_msg = "This order was cancelled."

#     response = f"""ORDER DETAILS — {order.get('restaurant', 'Unknown')}

# Status: {order.get('status', 'Unknown')} | Ordered: {order_date_str} | Expected: {expected_str}

# Items: {items_str}

# Total: ${order.get('total_amount','N/A')} | Delivery: {order.get('delivery_address', 'Not specified')}

# {status_msg}

# Order ID: {order['order_id'][:18]}..."""

#     return response

# def get_refund_list(user_id):
#     """List refunds"""
#     if refunds_col is None:
#         return None, "System error: Refund database unavailable."

#     refunds = list(refunds_col.find({"user_id": user_id}).sort("request_time", -1))
#     if not refunds:
#         return None, "No refund requests found. Need help with an order issue?"

#     response = "YOUR REFUND REQUESTS\n═══════════════════════════\n\n"
    
#     for idx, r in enumerate(refunds[:5], 1):
#         status = r.get('status', 'Unknown')
#         amount = r.get('amount', 0)
#         reason = r.get('reason', 'No reason provided')
#         refund_id_short = r['refund_id'][:8]
#         order_id_short = r['order_id'][:8]
        
#         try:
#             req_time = r.get('request_time')
#             dt = datetime.fromisoformat(req_time.replace('Z', '+00:00')) if isinstance(req_time, str) else req_time
#             time_str = dt.strftime("%b %d, %Y")
#         except:
#             time_str = "Unknown date"
        
#         status_emoji = "⏳" if status == "Pending" else "✓" if status in ["Processed", "Approved"] else "✗"
        
#         response += f"{idx}. Refund #{refund_id_short}... | Order #{order_id_short}...\n"
#         response += f"   {status_emoji} Status: {status} | Amount: ${amount} | {time_str}\n"
#         response += f"   Reason: {reason}\n\n"
    
#     response += "═══════════════════════════\n\nType a number (1-5) for details."
    
#     return [r['refund_id'] for r in refunds[:5]], response

# def get_specific_refund_details(refund_id, user_id):
#     """Get detailed refund information"""
#     if refunds_col is None:
#         return "System error: Refund database unavailable."

#     refund = refunds_col.find_one({"refund_id": refund_id, "user_id": user_id})
#     if not refund:
#         return "I couldn't find that refund request."

#     status = refund.get('status', 'Unknown')
#     amount = refund.get('amount', 0)
#     reason = refund.get('reason', 'No reason provided')
#     order_id = refund.get('order_id', 'Unknown')
    
#     try:
#         req_time = refund.get('request_time')
#         dt = datetime.fromisoformat(req_time.replace('Z', '+00:00')) if isinstance(req_time, str) else req_time
#         time_str = dt.strftime("%b %d, %Y at %I:%M %p")
#     except:
#         time_str = "Unknown date"
    
#     status_lower = status.lower()
    
#     if 'pending' in status_lower:
#         status_msg = "Your refund is being reviewed (typically 1-2 business days)."
#     elif 'approved' in status_lower:
#         status_msg = "Your refund has been approved and will be processed soon."
#     elif 'processed' in status_lower:
#         status_msg = "Refund processed. You should receive it within 5-7 business days (bank) or instantly (wallet)."
#     elif 'rejected' in status_lower:
#         status_msg = "Your refund request was not approved. Contact support for details."
#     else:
#         status_msg = ""
    
#     response = f"""REFUND DETAILS
# ═══════════════════════════

# Refund ID: {refund['refund_id'][:18]}...
# Order ID: {order_id[:18]}...

# Status: {status}
# Amount: ${amount}
# Reason: {reason}
# Requested: {time_str}

# {status_msg}

# ═══════════════════════════"""

#     return response

# def get_bot_reply(user_id, user_msg, current_user_role="user", retry_count=0):
#     """Generate bot reply using AI-based intent classification"""
#     max_retries = 2
#     history = get_cached_history(user_id, limit=30)
#     user_info = get_user_by_id(user_id)
#     user_name = user_info.get("name","there") if user_info else "there"

#     # Track session
#     try:
#         session_id = get_or_create_session(user_id)
#         update_session_message_count(session_id)
        
#         print(f"Session: {session_id}")
        
#         if chat_sessions_collection is not None:
#             current_session = chat_sessions_collection.find_one({"session_id": session_id})
#             if current_session:
#                 print(f"Message count: {current_session.get('message_count', 0)}")
#                 print(f"Feedback submitted: {current_session.get('feedback_submitted', False)}")
#     except Exception as e:
#         print(f"Session tracking error: {e}")

#     # ESCALATION CHECK
#     try:
#         escalate_flag, reason = should_escalate(user_msg, history)
#         if escalate_flag:
#             escalation_id = create_escalation(user_id, reason, {"recent_messages": history[-10:]})
#             bot_msg = f"I understand this requires immediate attention. Case ID: {escalation_id}. Click 'Talk to Human Agent' above."
#             save_message(user_id, user_msg, bot_msg)
#             return bot_msg
#     except Exception as e:
#         print(f"Escalation check error: {e}")

#     # DIRECT UUID DETECTION
#     if is_uuid_pattern(user_msg):
#         print(f"Detected UUID pattern: {user_msg}")
#         try:
#             bot_msg = get_specific_order_details(user_msg, user_id)
#             save_message(user_id, user_msg, bot_msg)
#             return bot_msg
#         except Exception as e:
#             print(f"Error fetching order: {e}")
#             bot_msg = "I couldn't find that order. Please verify the order ID."
#             save_message(user_id, user_msg, bot_msg)
#             return bot_msg

#     # AI-BASED INTENT CLASSIFICATION
#     intent = classify_user_intent(user_msg, history, user_name)
    
#     # HANDLE INTENT-BASED ROUTING
#     if intent == "EMAIL_REQUEST":
#         bot_msg = f"Hi {user_name}! For your security, I can't display your email address in the chat. You can view it in your account settings. Need help with something else?"
#         save_message(user_id, user_msg, bot_msg)
#         return bot_msg
    
#     elif intent == "GREETING":
#         bot_msg = (
#             f"Hello {user_name}! I'm your food delivery support assistant.\n\n"
#             f"I can help with:\n"
#             f"- Track order status\n"
#             f"- Check refunds\n"
#             f"- Answer delivery questions\n"
#             f"- Resolve order issues\n\n"
#             f"What would you like help with?"
#         )
#         save_message(user_id, user_msg, bot_msg)
#         return bot_msg
    
#     elif intent == "CONVERSATION_END":
#         bot_msg = f"You're welcome, {user_name}! Have a great day!"
#         save_message(user_id, user_msg, bot_msg)
        
#         try:
#             if chat_sessions_collection is not None:
#                 result = chat_sessions_collection.update_one(
#                     {"user_id": user_id, "end_time": None},
#                     {"$set": {"end_time": datetime.now(timezone.utc)}},
#                     upsert=False
#                 )
#                 if result.modified_count > 0:
#                     print(f"Session ended for user {user_id}")
#         except Exception as e:
#             print(f"Error marking session end: {e}")
        
#         return bot_msg
    
#     elif intent == "ORDER_TRACKING":
#         try:
#             ids, bot_msg = get_order_list(user_id)
#             save_message(user_id, user_msg, bot_msg)
#             return bot_msg
#         except Exception as e:
#             print(f"Order tracking error: {e}")
#             bot_msg = "I couldn't access your orders right now. Please try again."
#             save_message(user_id, user_msg, bot_msg)
#             return bot_msg
    
#     elif intent == "ORDER_SELECTION":
#         try:
#             orders = list(orders_col.find({"user_id": user_id}).sort("order_date",-1).limit(5))
#             if not orders:
#                 bot_msg = "You don't have any orders to select from."
#                 save_message(user_id, user_msg, bot_msg)
#                 return bot_msg
            
#             idx = parse_selection_number(user_msg, len(orders))
#             if idx is not None and idx < len(orders):
#                 order_id = orders[idx]['order_id']
#                 bot_msg = get_specific_order_details(order_id, user_id)
#                 save_message(user_id, user_msg, bot_msg)
#                 return bot_msg
            
#             msg_lower = user_msg.lower().strip()
#             for order in orders:
#                 if order['order_id'][:8].lower() in msg_lower:
#                     bot_msg = get_specific_order_details(order['order_id'], user_id)
#                     save_message(user_id, user_msg, bot_msg)
#                     return bot_msg
            
#             bot_msg = "I couldn't identify that order. Please type a number (1-5) or the full order ID."
#             save_message(user_id, user_msg, bot_msg)
#             return bot_msg
            
#         except Exception as e:
#             print(f"Order selection error: {e}")
#             bot_msg = "I had trouble processing your selection. Please try again."
#             save_message(user_id, user_msg, bot_msg)
#             return bot_msg
    
#     elif intent == "REFUND_CHECK":
#         try:
#             ids, bot_msg = get_refund_list(user_id)
#             save_message(user_id, user_msg, bot_msg)
#             return bot_msg
#         except Exception as e:
#             print(f"Refund check error: {e}")
#             bot_msg = "I couldn't access your refunds right now. Please try again."
#             save_message(user_id, user_msg, bot_msg)
#             return bot_msg
    
#     elif intent == "REFUND_SELECTION":
#         try:
#             refunds = list(refunds_col.find({"user_id": user_id}).sort("request_time",-1).limit(5))
#             if not refunds:
#                 bot_msg = "You don't have any refunds to select from."
#                 save_message(user_id, user_msg, bot_msg)
#                 return bot_msg
            
#             idx = parse_selection_number(user_msg, len(refunds))
#             if idx is not None and idx < len(refunds):
#                 refund_id = refunds[idx]['refund_id']
#                 bot_msg = get_specific_refund_details(refund_id, user_id)
#                 save_message(user_id, user_msg, bot_msg)
#                 return bot_msg
            
#             bot_msg = "I couldn't identify that refund. Please type a number (1-5)."
#             save_message(user_id, user_msg, bot_msg)
#             return bot_msg
            
#         except Exception as e:
#             print(f"Refund selection error: {e}")
#             bot_msg = "I had trouble processing your selection. Please try again."
#             save_message(user_id, user_msg, bot_msg)
#             return bot_msg
    
#     elif intent == "PROFILE_INFO":
#         user_profile = get_user_profile_summary(user_id)
        
#         profile_prompt = f"""You are a helpful food delivery assistant talking to {user_name}.

# User asked: "{user_msg}"

# Here's what you know about them:
# {user_profile}

# Respond naturally and conversationally. Mention:
# - You have access to their conversation history and remember previous chats
# - Their order activity
# - Current refund status if any
# - Be friendly and helpful

# IMPORTANT: Don't mention exact message counts (sounds creepy). Just say you remember previous conversations.
# Keep response under 4 sentences."""

#         try:
#             response = model.generate_content(profile_prompt)
#             bot_msg = response.text.strip()
#         except:
#             bot_msg = f"I have access to your order history and our previous conversations, {user_name}. You've placed {orders_col.count_documents({'user_id': user_id})} orders with us. How can I help you today?"
        
#         save_message(user_id, user_msg, bot_msg)
#         return bot_msg
    
#     elif intent == "RECOMMENDATION":
#         bot_msg = (
#             f"I'm a support assistant, so I can't place orders or make recommendations.\n\n"
#             f"To browse restaurants and menus, use our main app or website. Once you place an order, I can help track it!"
#         )
#         save_message(user_id, user_msg, bot_msg)
#         return bot_msg
    
#     # FAQ HANDLING - Dynamic, no hardcoding
#     elif intent.startswith("FAQ_"):
#         try:
#             from .faq_context import find_best_faq_match
            
#             faq_match = find_best_faq_match(user_msg, intent)
            
#             if faq_match and faq_match.get("answer"):
#                 bot_msg = faq_match["answer"]
#                 save_message(user_id, user_msg, bot_msg)
                
#                 # Update usage count
#                 try:
#                     if db is not None:
#                         db["faqs"].update_one(
#                             {"faq_id": faq_match["faq_id"]},
#                             {"$inc": {"usage_count": 1}}
#                         )
#                         print(f"Returned FAQ: {faq_match.get('faq_id')} - {faq_match.get('question')}")
#                 except Exception as update_error:
#                     print(f"Failed to update FAQ usage: {update_error}")
                
#                 return bot_msg
#             else:
#                 print(f"No FAQ match found for intent: {intent}, falling back to AI")
        
#         except Exception as e:
#             print(f"FAQ lookup error: {e}")
#             import traceback
#             traceback.print_exc()
    
#     # FALLBACK: Use AI with FAQ context
#     try:
#         faq_knowledge = get_faq_context()
        
#         system_prompt = (
#             f"You are a professional food delivery support assistant helping {user_name}. "
#             f"Be helpful, empathetic, and concise.\n\n"
#             f"{faq_knowledge}\n\n"
#             f"Use the FAQ knowledge to answer questions accurately. "
#             f"Keep responses brief (2-4 sentences).\n\n"
#             f"GUIDELINES:\n"
#             f"- For order problems: Empathize and guide them to track their order first\n"
#             f"- For cancellations: Explain the policy from FAQ\n"
#             f"- For delivery partner contact: Explain it shows in app once order is out for delivery\n"
#             f"- For policy questions: Answer directly from FAQ knowledge\n"
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
#         bot_msg = f"Hi {user_name}! I'm experiencing technical difficulties. Please try again."

#     save_message(user_id, user_msg, bot_msg)
#     return bot_msg


import time
import re
from datetime import datetime, timezone, timedelta
from .database import load_chat_history, save_message, get_user_by_id, messages_collection
from .config import orders_col, refunds_col, db, model
from .escalation import should_escalate, create_escalation
from .faq_context import get_faq_context

# In-memory session cache
session_cache = {}
CACHE_DURATION = timedelta(minutes=15)

# Initialize collections
chat_sessions_collection = db["chat_sessions"] if db is not None else None


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

def get_or_create_session(user_id: str) -> str:
    """Get current session or create new one"""
    if chat_sessions_collection is None:
        return f"SESSION_{int(datetime.now(timezone.utc).timestamp())}"
    
    # Check for active session (within last 30 minutes)
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=30)
    active_session = chat_sessions_collection.find_one({
        "user_id": user_id,
        "end_time": None,
        "start_time": {"$gte": cutoff}
    })
    
    if active_session:
        print(f"Reusing session: {active_session['session_id']}")
        return active_session["session_id"]
    
    # Create new session
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
    print(f"Created new session: {session_id}")
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
    
    # STRICT goodbye detection - only exact matches or clear phrases
    goodbye_exact = ['bye', 'goodbye', 'thanks', 'thank you', 'thankyou', 'done', 'ok', 'okay']
    goodbye_starts = ['thanks for', 'thank you for', "that's all", 'all set', 'got it', 
                      "i'm good", "im good", 'nothing else', "that's it", "thats it"]
    
    # Check if it's a question first - questions are NEVER goodbyes
    if '?' in user_msg:
        pass  # Continue to AI classification
    
    # Very short messages (1-3 words) - check exact match
    elif len(msg_words) <= 3:
        # Must be EXACTLY one of the goodbye phrases
        if msg_lower in goodbye_exact:
            print(f"DETECTED CONVERSATION END: '{user_msg}'")
            return "CONVERSATION_END"
    
    # Medium messages (4-6 words) - check if starts with goodbye phrase
    elif len(msg_words) <= 6:
        for phrase in goodbye_starts:
            if msg_lower.startswith(phrase):
                print(f"DETECTED CONVERSATION END: '{user_msg}'")
                return "CONVERSATION_END"
    
    # Get last bot message for context
    last_bot_msg = ""
    if history and len(history) > 0:
        last_bot_msg = history[-1].get("content", "")[:200]
    
    classification_prompt = f"""You are analyzing a user's message in a food delivery support chat.

User message: "{user_msg}"
Last assistant message: "{last_bot_msg}"

Classify the user's PRIMARY INTENT into ONE category:

GREETING - Starting conversation (hi, hello, hey, good morning)
ORDER_TRACKING - Wants to see/track their orders
ORDER_SELECTION - Selecting specific order by number/ID (1, 2, 3, first, second, or UUID pattern)
REFUND_CHECK - Wants to check refund status
REFUND_SELECTION - Selecting specific refund by number/ID
PROFILE_INFO - Asking what you know about them, account info, chat history, context, memory
EMAIL_REQUEST - Asking for their email address specifically
ORDER_ISSUE - Reporting problem (wrong items, missing, cold, damaged, late)
CANCELLATION - Wants to cancel order
FAQ_DELIVERY - Questions about delivery partner, driver contact, tracking
FAQ_PAYMENT - Questions about payment methods, charges, promo codes, discounts, offers, subscriptions
FAQ_ADDRESS - Questions about changing delivery address
FAQ_GENERAL - Other policy questions (timing, refunds policy, etc)
RECOMMENDATION - Asking for food/restaurant suggestions
CONVERSATION_END - User is EXPLICITLY ending (bye, thanks alone, done alone - NOT questions with these words)
OTHER - Anything that doesn't fit above

CRITICAL RULES:
- "is your food good?" = OTHER (it's a question)
- "thanks" alone = CONVERSATION_END
- "ok thanks" = CONVERSATION_END
- Random text = OTHER
- Any message with "?" = NOT conversation end
- "how good is..." = OTHER (question)
- Promo codes/discounts/subscriptions = FAQ_PAYMENT

Respond with ONLY the category name in uppercase."""

    try:
        response = model.generate_content(classification_prompt)
        intent = response.text.strip().upper().replace(" ", "_")
        print(f"[Intent Classification] User: '{user_msg[:50]}...' -> Intent: {intent}")
        return intent
    except Exception as e:
        print(f"Intent classification error: {e}")
        return "OTHER"

def is_uuid_pattern(text):
    """Check if text matches UUID pattern"""
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(uuid_pattern, text.lower().strip()))

def parse_selection_number(user_msg, max_items=5):
    """Parse selection number from various formats"""
    msg = user_msg.lower().strip()
    
    # Direct number
    if msg.isdigit():
        num = int(msg)
        if 1 <= num <= max_items:
            return num - 1
    
    # Extract number from phrases like "order 2" or "refund 3"
    match = re.search(r'\b(\d+)\b', msg)
    if match:
        num = int(match.group(1))
        if 1 <= num <= max_items:
            return num - 1
    
    # Text numbers
    words = {'first':0,'second':1,'third':2,'fourth':3,'fifth':4,'one':0,'two':1,'three':2,'four':3,'five':4}
    for word, idx in words.items():
        if word in msg and idx < max_items:
            return idx
    
    return None

def get_user_profile_summary(user_id):
    """Generate user profile summary without exact message counts"""
    try:
        user_info = get_user_by_id(user_id)
        
        recent_orders = list(orders_col.find({"user_id": user_id}).sort("order_date", -1).limit(5))
        total_orders = orders_col.count_documents({"user_id": user_id})
        
        refunds = list(refunds_col.find({"user_id": user_id}))
        total_refunds = len(refunds)
        pending_refunds = len([r for r in refunds if r.get('status') == 'Pending'])
        processed_refunds = len([r for r in refunds if r.get('status') == 'Processed'])
        
        total_conversations = messages_collection.count_documents({"user_id": user_id})
        
        summary = f"User Information:\n"
        summary += f"- Name: {user_info.get('name', 'Unknown')}\n"
        summary += f"- Total Orders: {total_orders}\n"
        
        if recent_orders:
            summary += f"\nRecent Orders:\n"
            for idx, order in enumerate(recent_orders[:3], 1):
                restaurant = order.get('restaurant', 'Unknown')
                status = order.get('status', 'Unknown')
                summary += f"  {idx}. {restaurant} - {status}\n"
        
        if total_refunds > 0:
            summary += f"\nRefunds: {total_refunds} total"
            if pending_refunds > 0:
                summary += f", {pending_refunds} pending"
            if processed_refunds > 0:
                summary += f", {processed_refunds} processed"
            summary += "\n"
        
        # Vague conversation history mention
        if total_conversations > 50:
            summary += f"\nConversation History: Extensive chat history available\n"
        elif total_conversations > 10:
            summary += f"\nConversation History: Previous conversations on record\n"
        else:
            summary += f"\nConversation History: Recent chat history available\n"
        
        return summary
        
    except Exception as e:
        print(f"Error generating user profile: {e}")
        return ""

def get_order_list(user_id):
    """Get order list formatted for frontend cards"""
    if orders_col is None:
        return None, "System error: Order database is not available."

    orders = list(orders_col.find({"user_id": user_id}).sort("order_date", -1))
    if not orders:
        return None, "You don't have any orders yet. Place your first order through our app or website!"

    orders_data = []
    for o in orders[:10]:
        try:
            order_date = o.get('order_date')
            if isinstance(order_date, str):
                dt = datetime.fromisoformat(order_date.replace('Z', '+00:00'))
            else:
                dt = order_date
            date_str = dt.strftime("%b %d, %Y at %I:%M %p")
        except:
            date_str = str(order_date) if order_date else "Unknown"
        
        orders_data.append({
            "order_id": o['order_id'],
            "restaurant": o.get('restaurant', 'Unknown Restaurant'),
            "items": o.get('items', []),
            "total_amount": o.get('total_amount', 0),
            "status": o.get('status', 'Unknown'),
            "order_date": date_str,
            "delivery_address": o.get('delivery_address', 'Not specified')
        })
    
    return orders_data, "ORDER_LIST"

def get_specific_order_details(order_id, user_id):
    """Get detailed order information"""
    if orders_col is None:
        return "System error: Order database unavailable."

    order = orders_col.find_one({"order_id": order_id, "user_id": user_id})
    if not order:
        return "I couldn't find that order. Please verify the order ID."

    items = order.get("items", [])
    items_str = ", ".join(items) if items else "No items"
    status_lower = order.get('status','Unknown').lower()
    
    try:
        expected_delivery = order.get('expected_delivery_time')
        if expected_delivery:
            dt = datetime.fromisoformat(expected_delivery.replace('Z', '+00:00')) if isinstance(expected_delivery, str) else expected_delivery
            expected_str = dt.strftime("%I:%M %p")
        else:
            expected_str = "Not available"
    except:
        expected_str = "Not available"

    try:
        order_date = order.get('order_date')
        if order_date:
            dt = datetime.fromisoformat(order_date.replace('Z', '+00:00')) if isinstance(order_date, str) else order_date
            order_date_str = dt.strftime("%b %d, %Y at %I:%M %p")
        else:
            order_date_str = "Not available"
    except:
        order_date_str = "Not available"

    status_msg = ""
    if 'preparing' in status_lower or 'processing' in status_lower:
        status_msg = "Your food is being prepared."
    elif 'ready' in status_lower:
        status_msg = "Your food is ready for pickup."
    elif 'out for delivery' in status_lower:
        status_msg = "Your order is on the way!"
    elif 'delivered' in status_lower:
        status_msg = "Order delivered."
    elif 'cancelled' in status_lower:
        status_msg = "This order was cancelled."

    response = f"""ORDER DETAILS — {order.get('restaurant', 'Unknown')}

Status: {order.get('status', 'Unknown')} | Ordered: {order_date_str} | Expected: {expected_str}

Items: {items_str}

Total: ${order.get('total_amount','N/A')} | Delivery: {order.get('delivery_address', 'Not specified')}

{status_msg}

Order ID: {order['order_id'][:18]}..."""

    return response

def get_refund_list(user_id):
    """List refunds"""
    if refunds_col is None:
        return None, "System error: Refund database unavailable."

    refunds = list(refunds_col.find({"user_id": user_id}).sort("request_time", -1))
    if not refunds:
        return None, "No refund requests found. Need help with an order issue?"

    response = "YOUR REFUND REQUESTS\n═══════════════════════════\n\n"
    
    for idx, r in enumerate(refunds[:5], 1):
        status = r.get('status', 'Unknown')
        amount = r.get('amount', 0)
        reason = r.get('reason', 'No reason provided')
        refund_id_short = r['refund_id'][:8]
        order_id_short = r['order_id'][:8]
        
        try:
            req_time = r.get('request_time')
            dt = datetime.fromisoformat(req_time.replace('Z', '+00:00')) if isinstance(req_time, str) else req_time
            time_str = dt.strftime("%b %d, %Y")
        except:
            time_str = "Unknown date"
        
        status_emoji = "⏳" if status == "Pending" else "✓" if status in ["Processed", "Approved"] else "✗"
        
        response += f"{idx}. Refund #{refund_id_short}... | Order #{order_id_short}...\n"
        response += f"   {status_emoji} Status: {status} | Amount: ${amount} | {time_str}\n"
        response += f"   Reason: {reason}\n\n"
    
    response += "═══════════════════════════\n\nType a number (1-5) for details."
    
    return [r['refund_id'] for r in refunds[:5]], response

def get_specific_refund_details(refund_id, user_id):
    """Get detailed refund information"""
    if refunds_col is None:
        return "System error: Refund database unavailable."

    refund = refunds_col.find_one({"refund_id": refund_id, "user_id": user_id})
    if not refund:
        return "I couldn't find that refund request."

    status = refund.get('status', 'Unknown')
    amount = refund.get('amount', 0)
    reason = refund.get('reason', 'No reason provided')
    order_id = refund.get('order_id', 'Unknown')
    
    try:
        req_time = refund.get('request_time')
        dt = datetime.fromisoformat(req_time.replace('Z', '+00:00')) if isinstance(req_time, str) else req_time
        time_str = dt.strftime("%b %d, %Y at %I:%M %p")
    except:
        time_str = "Unknown date"
    
    status_lower = status.lower()
    
    if 'pending' in status_lower:
        status_msg = "Your refund is being reviewed (typically 1-2 business days)."
    elif 'approved' in status_lower:
        status_msg = "Your refund has been approved and will be processed soon."
    elif 'processed' in status_lower:
        status_msg = "Refund processed. You should receive it within 5-7 business days (bank) or instantly (wallet)."
    elif 'rejected' in status_lower:
        status_msg = "Your refund request was not approved. Contact support for details."
    else:
        status_msg = ""
    
    response = f"""REFUND DETAILS
═══════════════════════════

Refund ID: {refund['refund_id'][:18]}...
Order ID: {order_id[:18]}...

Status: {status}
Amount: ${amount}
Reason: {reason}
Requested: {time_str}

{status_msg}

═══════════════════════════"""

    return response

def get_bot_reply(user_id, user_msg, current_user_role="user", retry_count=0):
    """Generate bot reply using AI-based intent classification"""
    max_retries = 2
    history = get_cached_history(user_id, limit=30)
    user_info = get_user_by_id(user_id)
    user_name = user_info.get("name","there") if user_info else "there"

    # Track session
    try:
        session_id = get_or_create_session(user_id)
        update_session_message_count(session_id)
        
        print(f"Session: {session_id}")
        
        if chat_sessions_collection is not None:
            current_session = chat_sessions_collection.find_one({"session_id": session_id})
            if current_session:
                print(f"Message count: {current_session.get('message_count', 0)}")
                print(f"Feedback submitted: {current_session.get('feedback_submitted', False)}")
    except Exception as e:
        print(f"Session tracking error: {e}")

    # ESCALATION CHECK
    try:
        escalate_flag, reason = should_escalate(user_msg, history)
        if escalate_flag:
            escalation_id = create_escalation(user_id, reason, {"recent_messages": history[-10:]})
            bot_msg = f"I understand this requires immediate attention. Case ID: {escalation_id}. Click 'Talk to Human Agent' above."
            save_message(user_id, user_msg, bot_msg)
            return bot_msg
    except Exception as e:
        print(f"Escalation check error: {e}")

    # DIRECT UUID DETECTION
    if is_uuid_pattern(user_msg):
        print(f"Detected UUID pattern: {user_msg}")
        try:
            bot_msg = get_specific_order_details(user_msg, user_id)
            save_message(user_id, user_msg, bot_msg)
            return bot_msg
        except Exception as e:
            print(f"Error fetching order: {e}")
            bot_msg = "I couldn't find that order. Please verify the order ID."
            save_message(user_id, user_msg, bot_msg)
            return bot_msg

    # AI-BASED INTENT CLASSIFICATION
    intent = classify_user_intent(user_msg, history, user_name)
    
    # HANDLE INTENT-BASED ROUTING
    if intent == "EMAIL_REQUEST":
        bot_msg = f"Hi {user_name}! For your security, I can't display your email address in the chat. You can view it in your account settings. Need help with something else?"
        save_message(user_id, user_msg, bot_msg)
        return bot_msg
    
    elif intent == "GREETING":
        bot_msg = (
            f"Hello {user_name}! I'm your food delivery support assistant.\n\n"
            f"I can help with:\n"
            f"- Track order status\n"
            f"- Check refunds\n"
            f"- Answer delivery questions\n"
            f"- Resolve order issues\n\n"
            f"What would you like help with?"
        )
        save_message(user_id, user_msg, bot_msg)
        return bot_msg
    
    elif intent == "CONVERSATION_END":
        bot_msg = f"You're welcome, {user_name}! Have a great day!"
        save_message(user_id, user_msg, bot_msg)
        
        try:
            if chat_sessions_collection is not None:
                result = chat_sessions_collection.update_one(
                    {"user_id": user_id, "end_time": None},
                    {"$set": {"end_time": datetime.now(timezone.utc)}},
                    upsert=False
                )
                if result.modified_count > 0:
                    print(f"Session ended for user {user_id}")
        except Exception as e:
            print(f"Error marking session end: {e}")
        
        return bot_msg
    
    elif intent == "ORDER_TRACKING":
        try:
            orders_data, msg = get_order_list(user_id)
            
            if orders_data is None:
                # No orders found - return error message as string
                save_message(user_id, user_msg, msg)
                return msg
            else:
                # FIXED: Return orders in dictionary format for frontend
                save_message(user_id, user_msg, "Showing user their orders")
                return {
                    "reply": "ORDER_LIST",
                    "orders": orders_data
                }
        except Exception as e:
            print(f"Order tracking error: {e}")
            bot_msg = "I couldn't access your orders right now. Please try again."
            save_message(user_id, user_msg, bot_msg)
            return bot_msg
    
    elif intent == "ORDER_SELECTION":
        try:
            orders = list(orders_col.find({"user_id": user_id}).sort("order_date",-1).limit(5))
            if not orders:
                bot_msg = "You don't have any orders to select from."
                save_message(user_id, user_msg, bot_msg)
                return bot_msg
            
            idx = parse_selection_number(user_msg, len(orders))
            if idx is not None and idx < len(orders):
                order_id = orders[idx]['order_id']
                bot_msg = get_specific_order_details(order_id, user_id)
                save_message(user_id, user_msg, bot_msg)
                return bot_msg
            
            msg_lower = user_msg.lower().strip()
            for order in orders:
                if order['order_id'][:8].lower() in msg_lower:
                    bot_msg = get_specific_order_details(order['order_id'], user_id)
                    save_message(user_id, user_msg, bot_msg)
                    return bot_msg
            
            bot_msg = "I couldn't identify that order. Please type a number (1-5) or the full order ID."
            save_message(user_id, user_msg, bot_msg)
            return bot_msg
            
        except Exception as e:
            print(f"Order selection error: {e}")
            bot_msg = "I had trouble processing your selection. Please try again."
            save_message(user_id, user_msg, bot_msg)
            return bot_msg
    
    elif intent == "REFUND_CHECK":
        try:
            ids, bot_msg = get_refund_list(user_id)
            save_message(user_id, user_msg, bot_msg)
            return bot_msg
        except Exception as e:
            print(f"Refund check error: {e}")
            bot_msg = "I couldn't access your refunds right now. Please try again."
            save_message(user_id, user_msg, bot_msg)
            return bot_msg
    
    elif intent == "REFUND_SELECTION":
        try:
            refunds = list(refunds_col.find({"user_id": user_id}).sort("request_time",-1).limit(5))
            if not refunds:
                bot_msg = "You don't have any refunds to select from."
                save_message(user_id, user_msg, bot_msg)
                return bot_msg
            
            idx = parse_selection_number(user_msg, len(refunds))
            if idx is not None and idx < len(refunds):
                refund_id = refunds[idx]['refund_id']
                bot_msg = get_specific_refund_details(refund_id, user_id)
                save_message(user_id, user_msg, bot_msg)
                return bot_msg
            
            bot_msg = "I couldn't identify that refund. Please type a number (1-5)."
            save_message(user_id, user_msg, bot_msg)
            return bot_msg
            
        except Exception as e:
            print(f"Refund selection error: {e}")
            bot_msg = "I had trouble processing your selection. Please try again."
            save_message(user_id, user_msg, bot_msg)
            return bot_msg
    
    elif intent == "PROFILE_INFO":
        user_profile = get_user_profile_summary(user_id)
        
        profile_prompt = f"""You are a helpful food delivery assistant talking to {user_name}.

User asked: "{user_msg}"

Here's what you know about them:
{user_profile}

Respond naturally and conversationally. Mention:
- You have access to their conversation history and remember previous chats
- Their order activity
- Current refund status if any
- Be friendly and helpful

IMPORTANT: Don't mention exact message counts (sounds creepy). Just say you remember previous conversations.
Keep response under 4 sentences."""

        try:
            response = model.generate_content(profile_prompt)
            bot_msg = response.text.strip()
        except:
            bot_msg = f"I have access to your order history and our previous conversations, {user_name}. You've placed {orders_col.count_documents({'user_id': user_id})} orders with us. How can I help you today?"
        
        save_message(user_id, user_msg, bot_msg)
        return bot_msg
    
    elif intent == "RECOMMENDATION":
        bot_msg = (
            f"I'm a support assistant, so I can't place orders or make recommendations.\n\n"
            f"To browse restaurants and menus, use our main app or website. Once you place an order, I can help track it!"
        )
        save_message(user_id, user_msg, bot_msg)
        return bot_msg
    
    # FAQ HANDLING - Dynamic, no hardcoding
    elif intent.startswith("FAQ_"):
        try:
            from .faq_context import find_best_faq_match
            
            faq_match = find_best_faq_match(user_msg, intent)
            
            if faq_match and faq_match.get("answer"):
                bot_msg = faq_match["answer"]
                save_message(user_id, user_msg, bot_msg)
                
                # Update usage count
                try:
                    if db is not None:
                        db["faqs"].update_one(
                            {"faq_id": faq_match["faq_id"]},
                            {"$inc": {"usage_count": 1}}
                        )
                        print(f"Returned FAQ: {faq_match.get('faq_id')} - {faq_match.get('question')}")
                except Exception as update_error:
                    print(f"Failed to update FAQ usage: {update_error}")
                
                return bot_msg
            else:
                print(f"No FAQ match found for intent: {intent}, falling back to AI")
        
        except Exception as e:
            print(f"FAQ lookup error: {e}")
            import traceback
            traceback.print_exc()
    
    # FALLBACK: Use AI with FAQ context
    try:
        faq_knowledge = get_faq_context()
        
        system_prompt = (
            f"You are a professional food delivery support assistant helping {user_name}. "
            f"Be helpful, empathetic, and concise.\n\n"
            f"{faq_knowledge}\n\n"
            f"Use the FAQ knowledge to answer questions accurately. "
            f"Keep responses brief (2-4 sentences).\n\n"
            f"GUIDELINES:\n"
            f"- For order problems: Empathize and guide them to track their order first\n"
            f"- For cancellations: Explain the policy from FAQ\n"
            f"- For delivery partner contact: Explain it shows in app once order is out for delivery\n"
            f"- For policy questions: Answer directly from FAQ knowledge\n"
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
        bot_msg = f"Hi {user_name}! I'm experiencing technical difficulties. Please try again."

    save_message(user_id, user_msg, bot_msg)
    return bot_msg