
# from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends, Query
# from datetime import datetime, timezone
# from config import escalations_collection, mongo_connected
# from database import save_message, get_user_by_id
# from auth import get_current_user
# import json
# import asyncio
# import traceback

# router = APIRouter()

# # WebSocket connection manager
# class ConnectionManager:
#     def __init__(self):
#         self.user_connections: dict[str, WebSocket] = {}
#         self.agent_connections: dict[str, WebSocket] = {}
    
#     async def connect_user(self, user_id: str, websocket: WebSocket):
#         await websocket.accept()
#         self.user_connections[user_id] = websocket
#         print(f"✅ User {user_id} connected. Total users: {len(self.user_connections)}")
    
#     async def connect_agent(self, agent_id: str, websocket: WebSocket):
#         await websocket.accept()
#         self.agent_connections[agent_id] = websocket
#         print(f"✅ Agent {agent_id} connected. Total agents: {len(self.agent_connections)}")
    
#     def disconnect_user(self, user_id: str):
#         if user_id in self.user_connections:
#             del self.user_connections[user_id]
#             print(f"❌ User {user_id} disconnected. Total users: {len(self.user_connections)}")
    
#     def disconnect_agent(self, agent_id: str):
#         if agent_id in self.agent_connections:
#             del self.agent_connections[agent_id]
#             print(f"❌ Agent {agent_id} disconnected. Total agents: {len(self.agent_connections)}")
    
#     async def send_to_user(self, user_id: str, message: dict):
#         if user_id in self.user_connections:
#             try:
#                 await self.user_connections[user_id].send_json(message)
#                 print(f"📤 Sent to user {user_id}: {message.get('type')}")
#                 return True
#             except Exception as e:
#                 print(f"❌ Error sending to user {user_id}: {e}")
#                 self.disconnect_user(user_id)
#         else:
#             print(f"⚠️ User {user_id} not connected")
#         return False
    
#     async def send_to_agent(self, agent_id: str, message: dict):
#         if agent_id in self.agent_connections:
#             try:
#                 await self.agent_connections[agent_id].send_json(message)
#                 print(f"📤 Sent to agent {agent_id}: {message.get('type')}")
#                 return True
#             except Exception as e:
#                 print(f"❌ Error sending to agent {agent_id}: {e}")
#                 self.disconnect_agent(agent_id)
#         else:
#             print(f"⚠️ Agent {agent_id} not connected")
#         return False
    
#     async def broadcast_to_agents(self, message: dict):
#         """Broadcast message to all connected agents"""
#         print(f"📢 Broadcasting to {len(self.agent_connections)} agents: {message.get('type')}")
#         disconnected = []
#         for agent_id, websocket in self.agent_connections.items():
#             try:
#                 await websocket.send_json(message)
#             except Exception as e:
#                 print(f"❌ Error broadcasting to agent {agent_id}: {e}")
#                 disconnected.append(agent_id)
        
#         for agent_id in disconnected:
#             self.disconnect_agent(agent_id)

# manager = ConnectionManager()

# # ==================== ESCALATION FUNCTIONS ====================

# def should_escalate(user_msg, history):
#     """Determine if conversation should be escalated to human agent"""
#     escalation_keywords = [
#         "agent", "human", "representative", "manager", "supervisor",
#         "talk to someone", "speak to", "call", "phone",
#         "complaint", "dispute", "fraud", "unauthorized",
#         "urgent", "emergency", "problem", "issue", "error",
#         "bug", "broken", "not working", "failed transaction",
#         "block card", "lost card", "stolen card", "permanent"
#     ]
    
#     msg_lower = user_msg.lower()
    
#     for keyword in escalation_keywords:
#         if keyword in msg_lower:
#             return True, f"User requested escalation: {keyword} mentioned"
    
#     if len(history) > 6:
#         recent_msgs = [m.get("content", "").lower() for m in history[-6:] if m.get("role") == "user"]
#         if len(recent_msgs) >= 3:
#             same_word_count = {}
#             for msg in recent_msgs:
#                 words = msg.split()
#                 for word in words:
#                     if len(word) > 4:
#                         same_word_count[word] = same_word_count.get(word, 0) + 1
            
#             for word, count in same_word_count.items():
#                 if count >= 3:
#                     return True, f"User repeating concern: '{word}' mentioned multiple times"
    
#     return False, None


# async def create_escalation_async(user_id, reason, context=None, priority="medium"):
#     """Create an escalation record in database with async notification"""
#     if not mongo_connected or escalations_collection is None:
#         return f"ESC_{int(datetime.now(timezone.utc).timestamp())}"
    
#     try:
#         escalation_id = f"ESC_{int(datetime.now(timezone.utc).timestamp())}"
        
#         escalation_doc = {
#             "escalation_id": escalation_id,
#             "user_id": user_id,
#             "reason": reason,
#             "status": "open",
#             "priority": priority,
#             "created_at": datetime.now(timezone.utc),
#             "assigned_to": None,
#             "context": context or {},
#             "messages": []
#         }
        
#         escalations_collection.insert_one(escalation_doc)
#         print(f"🚨 Escalation created: {escalation_id} with priority {priority}")
        
#         # Notify all agents about new escalation
#         await manager.broadcast_to_agents({
#             "type": "new_escalation",
#             "escalation": {
#                 "escalation_id": escalation_id,
#                 "user_id": user_id,
#                 "reason": reason,
#                 "priority": priority,
#                 "created_at": datetime.now(timezone.utc).isoformat()
#             }
#         })
        
#         return escalation_id
    
#     except Exception as e:
#         print(f"❌ Error creating escalation: {e}")
#         traceback.print_exc()
#         return f"ESC_{int(datetime.now(timezone.utc).timestamp())}"


# def create_escalation(user_id, reason, context=None, priority="medium"):
#     """Synchronous wrapper for create_escalation_async"""
#     escalation_id = f"ESC_{int(datetime.now(timezone.utc).timestamp())}"
    
#     if not mongo_connected or escalations_collection is None:
#         return escalation_id
    
#     try:
#         escalation_doc = {
#             "escalation_id": escalation_id,
#             "user_id": user_id,
#             "reason": reason,
#             "status": "open",
#             "priority": priority,
#             "created_at": datetime.now(timezone.utc),
#             "assigned_to": None,
#             "context": context or {},
#             "messages": []
#         }
        
#         escalations_collection.insert_one(escalation_doc)
#         print(f"🚨 Escalation created: {escalation_id} with priority {priority}")
        
#         # Schedule async notification
#         try:
#             loop = asyncio.get_event_loop()
#             loop.create_task(manager.broadcast_to_agents({
#                 "type": "new_escalation",
#                 "escalation": {
#                     "escalation_id": escalation_id,
#                     "user_id": user_id,
#                     "reason": reason,
#                     "priority": priority,
#                     "created_at": datetime.now(timezone.utc).isoformat()
#                 }
#             }))
#         except Exception as e:
#             print(f"⚠️ Could not send broadcast notification: {e}")
        
#         return escalation_id
    
#     except Exception as e:
#         print(f"❌ Error creating escalation: {e}")
#         traceback.print_exc()
#         return escalation_id


# def get_escalation(escalation_id):
#     """Retrieve escalation details"""
#     if not mongo_connected or escalations_collection is None:
#         return None
    
#     try:
#         return escalations_collection.find_one({"escalation_id": escalation_id})
#     except Exception as e:
#         print(f"❌ Error fetching escalation: {e}")
#         return None


# def add_agent_message(escalation_id, agent_id, message):
#     """Add agent message to escalation"""
#     if not mongo_connected or escalations_collection is None:
#         return False
    
#     try:
#         escalations_collection.update_one(
#             {"escalation_id": escalation_id},
#             {
#                 "$push": {
#                     "messages": {
#                         "sender": "agent",
#                         "agent_id": agent_id,
#                         "message": message,
#                         "timestamp": datetime.now(timezone.utc).isoformat()
#                     }
#                 }
#             }
#         )
#         print(f"💾 Agent message saved to {escalation_id}")
#         return True
#     except Exception as e:
#         print(f"❌ Error adding agent message: {e}")
#         return False


# def add_user_message(escalation_id, message):
#     """Add user message to escalation"""
#     if not mongo_connected or escalations_collection is None:
#         return False
    
#     try:
#         escalations_collection.update_one(
#             {"escalation_id": escalation_id},
#             {
#                 "$push": {
#                     "messages": {
#                         "sender": "user",
#                         "message": message,
#                         "timestamp": datetime.now(timezone.utc).isoformat()
#                     }
#                 }
#             }
#         )
#         print(f"💾 User message saved to {escalation_id}")
#         return True
#     except Exception as e:
#         print(f"❌ Error adding user message: {e}")
#         return False


# def close_escalation(escalation_id, resolution):
#     """Close an escalation"""
#     if not mongo_connected or escalations_collection is None:
#         return False
    
#     try:
#         escalations_collection.update_one(
#             {"escalation_id": escalation_id},
#             {
#                 "$set": {
#                     "status": "closed",
#                     "closed_at": datetime.now(timezone.utc),
#                     "resolution": resolution
#                 }
#             }
#         )
#         print(f"✅ Escalation {escalation_id} closed")
#         return True
#     except Exception as e:
#         print(f"❌ Error closing escalation: {e}")
#         return False


# # ==================== WEBSOCKET ENDPOINTS ====================

# @router.websocket("/ws/user/{user_id}")
# async def websocket_user_endpoint(websocket: WebSocket, user_id: str):
#     """WebSocket for real-time escalation messages for users"""
#     await manager.connect_user(user_id, websocket)
    
#     try:
#         while True:
#             try:
#                 # Check if websocket is still connected before receiving
#                 if websocket.client_state.value != 1:  # 1 = CONNECTED
#                     print(f"⚠️ WebSocket for user {user_id} is not in CONNECTED state")
#                     break
                
#                 data = await websocket.receive_text()
#                 message_data = json.loads(data)
#                 print(f"📨 Received from user {user_id}: {message_data.get('type')}")
                
#                 if message_data.get("type") == "ping":
#                     await websocket.send_json({"type": "pong"})
#                     continue
                
#                 if message_data.get("type") == "message":
#                     escalation_id = message_data.get("escalation_id")
#                     user_message = message_data.get("message")
                    
#                     if not escalation_id or not user_message:
#                         await websocket.send_json({
#                             "type": "error",
#                             "message": "Missing escalation_id or message"
#                         })
#                         continue
                    
#                     # Get escalation to find assigned agent
#                     escalation = get_escalation(escalation_id)
#                     if not escalation:
#                         await websocket.send_json({
#                             "type": "error",
#                             "message": "Escalation not found"
#                         })
#                         continue
                    
#                     # Save user message to escalation
#                     add_user_message(escalation_id, user_message)
                    
#                     # Send to assigned agent if connected
#                     if escalation.get("assigned_to"):
#                         sent = await manager.send_to_agent(escalation["assigned_to"], {
#                             "type": "user_message",
#                             "escalation_id": escalation_id,
#                             "message": user_message,
#                             "timestamp": datetime.now(timezone.utc).isoformat()
#                         })
#                         if sent:
#                             print(f"✅ Message forwarded to agent {escalation['assigned_to']}")
#                     else:
#                         print(f"⚠️ No agent assigned to escalation {escalation_id}")
                    
#                     # Acknowledge receipt
#                     await websocket.send_json({
#                         "type": "ack",
#                         "message": "Message received"
#                     })
                    
#             except json.JSONDecodeError as e:
#                 print(f"❌ JSON decode error from user {user_id}: {e}")
#                 try:
#                     await websocket.send_json({
#                         "type": "error",
#                         "message": "Invalid JSON format"
#                     })
#                 except:
#                     break
#             except RuntimeError as e:
#                 # This catches "Cannot call receive once a disconnect message has been received"
#                 if "disconnect message has been received" in str(e):
#                     print(f"🔌 User {user_id} WebSocket received disconnect message")
#                     break
#                 else:
#                     print(f"❌ RuntimeError for user {user_id}: {e}")
#                     traceback.print_exc()
#                     break
#             except Exception as e:
#                 print(f"❌ Error processing message from user {user_id}: {e}")
#                 traceback.print_exc()
#                 # Don't break on general exceptions, but check connection state
#                 if websocket.client_state.value != 1:
#                     break
    
#     except WebSocketDisconnect:
#         manager.disconnect_user(user_id)
#         print(f"🔌 User {user_id} disconnected normally")
#     except Exception as e:
#         print(f"❌ WebSocket error for user {user_id}: {e}")
#         traceback.print_exc()
#         manager.disconnect_user(user_id)


# @router.websocket("/ws/agent/{agent_id}")
# async def websocket_agent_endpoint(websocket: WebSocket, agent_id: str):
#     """WebSocket for real-time escalation messages for agents"""
#     await manager.connect_agent(agent_id, websocket)
    
#     try:
#         while True:
#             try:
#                 # Check if websocket is still connected before receiving
#                 if websocket.client_state.value != 1:  # 1 = CONNECTED
#                     print(f"⚠️ WebSocket for agent {agent_id} is not in CONNECTED state")
#                     break
                
#                 data = await websocket.receive_text()
#                 message_data = json.loads(data)
#                 print(f"📨 Received from agent {agent_id}: {message_data.get('type')}")
                
#                 if message_data.get("type") == "ping":
#                     await websocket.send_json({"type": "pong"})
#                     continue
                
#                 if message_data.get("type") == "message":
#                     escalation_id = message_data.get("escalation_id")
#                     agent_message = message_data.get("message")
                    
#                     if not escalation_id or not agent_message:
#                         await websocket.send_json({
#                             "type": "error",
#                             "message": "Missing escalation_id or message"
#                         })
#                         continue
                    
#                     # Get escalation to find user
#                     escalation = get_escalation(escalation_id)
#                     if not escalation:
#                         await websocket.send_json({
#                             "type": "error",
#                             "message": "Escalation not found"
#                         })
#                         continue
                    
#                     # Save agent message to escalation
#                     add_agent_message(escalation_id, agent_id, agent_message)
                    
#                     # Send to user if connected
#                     sent = await manager.send_to_user(escalation["user_id"], {
#                         "type": "agent_message",
#                         "escalation_id": escalation_id,
#                         "message": agent_message,
#                         "timestamp": datetime.now(timezone.utc).isoformat()
#                     })
                    
#                     # Acknowledge receipt
#                     await websocket.send_json({
#                         "type": "ack",
#                         "message": "Message sent to user" if sent else "User not connected, message saved"
#                     })
                    
#             except json.JSONDecodeError as e:
#                 print(f"❌ JSON decode error from agent {agent_id}: {e}")
#                 try:
#                     await websocket.send_json({
#                         "type": "error",
#                         "message": "Invalid JSON format"
#                     })
#                 except:
#                     break
#             except RuntimeError as e:
#                 # This catches "Cannot call receive once a disconnect message has been received"
#                 if "disconnect message has been received" in str(e):
#                     print(f"🔌 Agent {agent_id} WebSocket received disconnect message")
#                     break
#                 else:
#                     print(f"❌ RuntimeError for agent {agent_id}: {e}")
#                     traceback.print_exc()
#                     break
#             except Exception as e:
#                 print(f"❌ Error processing message from agent {agent_id}: {e}")
#                 traceback.print_exc()
#                 # Don't break on general exceptions, but check connection state
#                 if websocket.client_state.value != 1:
#                     break
    
#     except WebSocketDisconnect:
#         manager.disconnect_agent(agent_id)
#         print(f"🔌 Agent {agent_id} disconnected normally")
#     except Exception as e:
#         print(f"❌ WebSocket error for agent {agent_id}: {e}")
#         traceback.print_exc()
#         manager.disconnect_agent(agent_id)


# # ==================== REST API ENDPOINTS ====================

# @router.post("/escalate")
# async def escalate_conversation(current_user: dict = Depends(get_current_user)):
#     """Escalate current conversation to human agent"""
#     if not mongo_connected:
#         raise HTTPException(status_code=503, detail="Database unavailable")
    
#     try:
#         from database import get_or_create_user
        
#         user = get_or_create_user(
#             current_user["email"],
#             current_user.get("name"),
#             current_user.get("role", "user")
#         )
        
#         if not user or "user_id" not in user:
#             raise HTTPException(status_code=500, detail="User not found")
        
#         # Use async version to properly send notifications
#         escalation_id = await create_escalation_async(
#             user["user_id"],
#             "User requested to speak with support agent",
#             {"user_email": current_user["email"], "user_name": current_user.get("name")},
#             priority="medium"
#         )
        
#         return {
#             "escalation_id": escalation_id,
#             "status": "escalated",
#             "message": "Your case has been escalated. A support agent will assist you shortly."
#         }
    
#     except Exception as e:
#         print(f"❌ Escalation error: {e}")
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail="Failed to escalate conversation")


# @router.get("/escalations/my")
# def get_my_escalations(current_user: dict = Depends(get_current_user)):
#     """Get user's escalations"""
#     if not mongo_connected:
#         raise HTTPException(status_code=503, detail="Database unavailable")
    
#     try:
#         from database import get_or_create_user
        
#         user = get_or_create_user(
#             current_user["email"],
#             current_user.get("name"),
#             current_user.get("role", "user")
#         )
        
#         if not user or "user_id" not in user:
#             raise HTTPException(status_code=500, detail="User not found")
        
#         escalations = list(escalations_collection.find(
#             {"user_id": user["user_id"]}
#         ).sort("created_at", -1))
        
#         result = []
#         for esc in escalations:
#             esc["_id"] = str(esc.get("_id", ""))
#             if hasattr(esc.get("created_at"), "isoformat"):
#                 esc["created_at"] = esc["created_at"].isoformat()
#             if hasattr(esc.get("closed_at"), "isoformat"):
#                 esc["closed_at"] = esc["closed_at"].isoformat()
#             result.append(esc)
        
#         return {"escalations": result, "total": len(result)}
    
#     except Exception as e:
#         print(f"❌ Get my escalations error: {e}")
#         raise HTTPException(status_code=500, detail="Failed to fetch escalations")


# @router.get("/escalations/pending")
# def get_pending_escalations(current_user: dict = Depends(get_current_user)):
#     """Get pending escalations (unassigned)"""
#     if not mongo_connected:
#         raise HTTPException(status_code=503, detail="Database unavailable")
    
#     role = current_user.get("role", "user")
#     if role not in ["customer_support_agent", "admin"]:
#         raise HTTPException(status_code=403, detail="Insufficient permissions")
    
#     try:
#         escalations = list(escalations_collection.find({
#             "status": "open",
#             "assigned_to": None
#         }).sort("created_at", -1))
        
#         result = []
#         for esc in escalations:
#             esc["_id"] = str(esc.get("_id", ""))
#             if hasattr(esc.get("created_at"), "isoformat"):
#                 esc["created_at"] = esc["created_at"].isoformat()
#             if hasattr(esc.get("closed_at"), "isoformat"):
#                 esc["closed_at"] = esc["closed_at"].isoformat()
#             result.append(esc)
        
#         return {"escalations": result, "total": len(result)}
    
#     except Exception as e:
#         print(f"❌ Get pending escalations error: {e}")
#         raise HTTPException(status_code=500, detail="Failed to fetch pending escalations")


# @router.get("/escalations/assigned")
# def get_assigned_escalations(current_user: dict = Depends(get_current_user)):
#     """Get escalations assigned to current agent"""
#     if not mongo_connected:
#         raise HTTPException(status_code=503, detail="Database unavailable")
    
#     role = current_user.get("role", "user")
#     if role not in ["customer_support_agent", "admin"]:
#         raise HTTPException(status_code=403, detail="Insufficient permissions")
    
#     try:
#         from database import get_or_create_user
        
#         user = get_or_create_user(
#             current_user["email"],
#             current_user.get("name"),
#             current_user.get("role", "user")
#         )
        
#         if not user or "user_id" not in user:
#             raise HTTPException(status_code=500, detail="User not found")
        
#         escalations = list(escalations_collection.find({
#             "assigned_to": user["user_id"],
#             "status": {"$ne": "closed"}
#         }).sort("created_at", -1))
        
#         result = []
#         for esc in escalations:
#             esc["_id"] = str(esc.get("_id", ""))
#             if hasattr(esc.get("created_at"), "isoformat"):
#                 esc["created_at"] = esc["created_at"].isoformat()
#             if hasattr(esc.get("closed_at"), "isoformat"):
#                 esc["closed_at"] = esc["closed_at"].isoformat()
#             result.append(esc)
        
#         return {"escalations": result, "total": len(result)}
    
#     except Exception as e:
#         print(f"❌ Get assigned escalations error: {e}")
#         raise HTTPException(status_code=500, detail="Failed to fetch assigned escalations")


# @router.get("/escalations")
# def get_all_escalations(current_user: dict = Depends(get_current_user)):
#     """Get all escalations (support agents and admins only)"""
#     if not mongo_connected:
#         raise HTTPException(status_code=503, detail="Database unavailable")
    
#     role = current_user.get("role", "user")
#     if role not in ["customer_support_agent", "admin"]:
#         raise HTTPException(status_code=403, detail="Insufficient permissions")
    
#     try:
#         escalations = list(escalations_collection.find().sort("created_at", -1))
        
#         result = []
#         for esc in escalations:
#             esc["_id"] = str(esc.get("_id", ""))
#             if hasattr(esc.get("created_at"), "isoformat"):
#                 esc["created_at"] = esc["created_at"].isoformat()
#             if hasattr(esc.get("closed_at"), "isoformat"):
#                 esc["closed_at"] = esc["closed_at"].isoformat()
#             result.append(esc)
        
#         return {"escalations": result, "total": len(result)}
    
#     except Exception as e:
#         print(f"❌ Get all escalations error: {e}")
#         raise HTTPException(status_code=500, detail="Failed to fetch escalations")


# @router.get("/{escalation_id}")
# def get_escalation_details(escalation_id: str, current_user: dict = Depends(get_current_user)):
#     """Get specific escalation details"""
#     if not mongo_connected:
#         raise HTTPException(status_code=503, detail="Database unavailable")
    
#     try:
#         escalation = get_escalation(escalation_id)
#         if not escalation:
#             raise HTTPException(status_code=404, detail="Escalation not found")
        
#         role = current_user.get("role", "user")
#         from database import get_or_create_user
#         user = get_or_create_user(current_user["email"], current_user.get("name"), role)
        
#         if role == "user" and escalation["user_id"] != user.get("user_id"):
#             raise HTTPException(status_code=403, detail="Insufficient permissions")
        
#         escalation["_id"] = str(escalation.get("_id", ""))
#         if hasattr(escalation.get("created_at"), "isoformat"):
#             escalation["created_at"] = escalation["created_at"].isoformat()
#         if hasattr(escalation.get("closed_at"), "isoformat"):
#             escalation["closed_at"] = escalation["closed_at"].isoformat()
        
#         return escalation
    
#     except HTTPException:
#         raise
#     except Exception as e:
#         print(f"❌ Get escalation details error: {e}")
#         raise HTTPException(status_code=500, detail="Failed to fetch escalation")


# @router.get("/messages/{escalation_id}")
# def get_escalation_messages(escalation_id: str, current_user: dict = Depends(get_current_user)):
#     """Get messages for an escalation"""
#     if not mongo_connected:
#         raise HTTPException(status_code=503, detail="Database unavailable")
    
#     try:
#         escalation = get_escalation(escalation_id)
#         if not escalation:
#             raise HTTPException(status_code=404, detail="Escalation not found")
        
#         role = current_user.get("role", "user")
#         from database import get_or_create_user
#         user = get_or_create_user(current_user["email"], current_user.get("name"), role)
        
#         if role == "user" and escalation["user_id"] != user.get("user_id"):
#             raise HTTPException(status_code=403, detail="Insufficient permissions")
        
#         return {"messages": escalation.get("messages", [])}
    
#     except HTTPException:
#         raise
#     except Exception as e:
#         print(f"❌ Get escalation messages error: {e}")
#         raise HTTPException(status_code=500, detail="Failed to fetch messages")


# @router.post("/{escalation_id}/message")
# async def send_escalation_message(escalation_id: str, message: str = Query(...), current_user: dict = Depends(get_current_user)):
#     """Send message in escalation (agent or user)"""
#     if not mongo_connected:
#         raise HTTPException(status_code=503, detail="Database unavailable")
    
#     try:
#         escalation = get_escalation(escalation_id)
#         if not escalation:
#             raise HTTPException(status_code=404, detail="Escalation not found")
        
#         role = current_user.get("role", "user")
#         from database import get_or_create_user
#         user = get_or_create_user(current_user["email"], current_user.get("name"), role)
        
#         if role == "user" and escalation["user_id"] != user.get("user_id"):
#             raise HTTPException(status_code=403, detail="Insufficient permissions")
        
#         if role in ["customer_support_agent", "admin"]:
#             add_agent_message(escalation_id, user.get("user_id"), message)
#             # Send to user via WebSocket
#             await manager.send_to_user(escalation["user_id"], {
#                 "type": "agent_message",
#                 "escalation_id": escalation_id,
#                 "message": message,
#                 "timestamp": datetime.now(timezone.utc).isoformat()
#             })
#         else:
#             add_user_message(escalation_id, message)
#             # Send to agent via WebSocket
#             if escalation.get("assigned_to"):
#                 await manager.send_to_agent(escalation["assigned_to"], {
#                     "type": "user_message",
#                     "escalation_id": escalation_id,
#                     "message": message,
#                     "timestamp": datetime.now(timezone.utc).isoformat()
#                 })
        
#         return {"status": "sent", "message": "Message added to escalation"}
    
#     except HTTPException:
#         raise
#     except Exception as e:
#         print(f"❌ Send escalation message error: {e}")
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail="Failed to send message")


# @router.post("/{escalation_id}/assign")
# async def assign_escalation(escalation_id: str, current_user: dict = Depends(get_current_user)):
#     """Assign escalation to current agent"""
#     if not mongo_connected:
#         raise HTTPException(status_code=503, detail="Database unavailable")
    
#     role = current_user.get("role", "user")
#     if role not in ["customer_support_agent", "admin"]:
#         raise HTTPException(status_code=403, detail="Insufficient permissions")
    
#     try:
#         from database import get_or_create_user
        
#         user = get_or_create_user(
#             current_user["email"],
#             current_user.get("name"),
#             current_user.get("role", "user")
#         )
        
#         if not user or "user_id" not in user:
#             raise HTTPException(status_code=500, detail="User not found")
        
#         escalation = get_escalation(escalation_id)
#         if not escalation:
#             raise HTTPException(status_code=404, detail="Escalation not found")
        
#         if escalation.get("assigned_to") and escalation["assigned_to"] != user["user_id"]:
#             raise HTTPException(status_code=400, detail="Escalation already assigned to another agent")
        
#         escalations_collection.update_one(
#             {"escalation_id": escalation_id},
#             {"$set": {
#                 "assigned_to": user["user_id"],
#                 "assigned_at": datetime.now(timezone.utc)
#             }}
#         )
        
#         # Notify user that agent has joined
#         await manager.send_to_user(escalation["user_id"], {
#             "type": "escalation_assigned",
#             "escalation_id": escalation_id,
#             "agent_name": user.get("name", "Support Agent"),
#             "message": f"{user.get('name', 'Support Agent')} has joined the chat"
#         })
        
#         return {"status": "assigned", "message": f"Escalation assigned to {user.get('name', 'agent')}"}
    
#     except HTTPException:
#         raise
#     except Exception as e:
#         print(f"❌ Assign escalation error: {e}")
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail="Failed to assign escalation")


# @router.post("/{escalation_id}/close")
# def close_escalation_endpoint(escalation_id: str, resolution: str = Query(...), current_user: dict = Depends(get_current_user)):
#     """Close an escalation (support agents and admins only)"""
#     if not mongo_connected:
#         raise HTTPException(status_code=503, detail="Database unavailable")
    
#     role = current_user.get("role", "user")
#     if role not in ["customer_support_agent", "admin"]:
#         raise HTTPException(status_code=403, detail="Insufficient permissions")
    
#     try:
#         if close_escalation(escalation_id, resolution):
#             return {"status": "closed", "message": "Escalation closed successfully"}
#         else:
#             raise HTTPException(status_code=500, detail="Failed to close escalation")
    
#     except HTTPException:
#         raise
#     except Exception as e:
#         print(f"❌ Close escalation error: {e}")
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail="Failed to close escalation")


from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends, Query
from datetime import datetime, timezone
import json
import asyncio
import traceback

# Corrected relative imports
from .config import escalations_collection, mongo_connected
from .database import save_message, get_user_by_id
from .auth import get_current_user


router = APIRouter()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.user_connections: dict[str, WebSocket] = {}
        self.agent_connections: dict[str, WebSocket] = {}
    
    async def connect_user(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.user_connections[user_id] = websocket
        print(f"✅ User {user_id} connected. Total users: {len(self.user_connections)}")
    
    async def connect_agent(self, agent_id: str, websocket: WebSocket):
        await websocket.accept()
        self.agent_connections[agent_id] = websocket
        print(f"✅ Agent {agent_id} connected. Total agents: {len(self.agent_connections)}")
    
    def disconnect_user(self, user_id: str):
        if user_id in self.user_connections:
            del self.user_connections[user_id]
            print(f"❌ User {user_id} disconnected. Total users: {len(self.user_connections)}")
    
    def disconnect_agent(self, agent_id: str):
        if agent_id in self.agent_connections:
            del self.agent_connections[agent_id]
            print(f"❌ Agent {agent_id} disconnected. Total agents: {len(self.agent_connections)}")
    
    async def send_to_user(self, user_id: str, message: dict):
        if user_id in self.user_connections:
            try:
                await self.user_connections[user_id].send_json(message)
                print(f"📤 Sent to user {user_id}: {message.get('type')}")
                return True
            except Exception as e:
                print(f"❌ Error sending to user {user_id}: {e}")
                self.disconnect_user(user_id)
        else:
            print(f"⚠️ User {user_id} not connected")
        return False
    
    async def send_to_agent(self, agent_id: str, message: dict):
        if agent_id in self.agent_connections:
            try:
                await self.agent_connections[agent_id].send_json(message)
                print(f"📤 Sent to agent {agent_id}: {message.get('type')}")
                return True
            except Exception as e:
                print(f"❌ Error sending to agent {agent_id}: {e}")
                self.disconnect_agent(agent_id)
        else:
            print(f"⚠️ Agent {agent_id} not connected")
        return False
    
    async def broadcast_to_agents(self, message: dict):
        """Broadcast message to all connected agents"""
        print(f"📢 Broadcasting to {len(self.agent_connections)} agents: {message.get('type')}")
        disconnected = []
        for agent_id, websocket in self.agent_connections.items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                print(f"❌ Error broadcasting to agent {agent_id}: {e}")
                disconnected.append(agent_id)
        
        for agent_id in disconnected:
            self.disconnect_agent(agent_id)

manager = ConnectionManager()

# ==================== ESCALATION FUNCTIONS ====================

def should_escalate(user_msg, history):
    """Determine if conversation should be escalated to human agent"""
    escalation_keywords = [
        "agent", "human", "representative", "manager", "supervisor",
        "talk to someone", "speak to", "call", "phone",
        "complaint", "dispute", "fraud", "unauthorized",
        "urgent", "emergency", "problem", "issue", "error",
        "bug", "broken", "not working", "failed transaction",
        "block card", "lost card", "stolen card", "permanent"
    ]
    
    msg_lower = user_msg.lower()
    
    for keyword in escalation_keywords:
        if keyword in msg_lower:
            return True, f"User requested escalation: {keyword} mentioned"
    
    if len(history) > 6:
        recent_msgs = [m.get("content", "").lower() for m in history[-6:] if m.get("role") == "user"]
        if len(recent_msgs) >= 3:
            same_word_count = {}
            for msg in recent_msgs:
                words = msg.split()
                for word in words:
                    if len(word) > 4:
                        same_word_count[word] = same_word_count.get(word, 0) + 1
            
            for word, count in same_word_count.items():
                if count >= 3:
                    return True, f"User repeating concern: '{word}' mentioned multiple times"
    
    return False, None


async def create_escalation_async(user_id, reason, context=None, priority="medium"):
    """Create an escalation record in database with async notification"""
    if not mongo_connected or escalations_collection is None:
        return f"ESC_{int(datetime.now(timezone.utc).timestamp())}"
    
    try:
        escalation_id = f"ESC_{int(datetime.now(timezone.utc).timestamp())}"
        
        escalation_doc = {
            "escalation_id": escalation_id,
            "user_id": user_id,
            "reason": reason,
            "status": "open",
            "priority": priority,
            "created_at": datetime.now(timezone.utc),
            "assigned_to": None,
            "context": context or {},
            "messages": []
        }
        
        escalations_collection.insert_one(escalation_doc)
        print(f"🚨 Escalation created: {escalation_id} with priority {priority}")
        
        # Notify all agents about new escalation
        await manager.broadcast_to_agents({
            "type": "new_escalation",
            "escalation": {
                "escalation_id": escalation_id,
                "user_id": user_id,
                "reason": reason,
                "priority": priority,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        })
        
        return escalation_id
    
    except Exception as e:
        print(f"❌ Error creating escalation: {e}")
        traceback.print_exc()
        return f"ESC_{int(datetime.now(timezone.utc).timestamp())}"


def create_escalation(user_id, reason, context=None, priority="medium"):
    """Synchronous wrapper for create_escalation_async"""
    escalation_id = f"ESC_{int(datetime.now(timezone.utc).timestamp())}"
    
    if not mongo_connected or escalations_collection is None:
        return escalation_id
    
    try:
        escalation_doc = {
            "escalation_id": escalation_id,
            "user_id": user_id,
            "reason": reason,
            "status": "open",
            "priority": priority,
            "created_at": datetime.now(timezone.utc),
            "assigned_to": None,
            "context": context or {},
            "messages": []
        }
        
        escalations_collection.insert_one(escalation_doc)
        print(f"🚨 Escalation created: {escalation_id} with priority {priority}")
        
        # Schedule async notification
        try:
            # Try to get existing loop or run a new one if none exists
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(manager.broadcast_to_agents({
                    "type": "new_escalation",
                    "escalation": {
                        "escalation_id": escalation_id,
                        "user_id": user_id,
                        "reason": reason,
                        "priority": priority,
                        "created_at": datetime.now(timezone.utc).isoformat()
                    }
                }))
            else:
                 loop.run_until_complete(manager.broadcast_to_agents({
                    "type": "new_escalation",
                    "escalation": {
                        "escalation_id": escalation_id,
                        "user_id": user_id,
                        "reason": reason,
                        "priority": priority,
                        "created_at": datetime.now(timezone.utc).isoformat()
                    }
                }))
        except RuntimeError:
             # This can happen if no event loop is set for the current thread
             # In a production server (like gunicorn/uvicorn), this is less likely
             print(f"⚠️ Could not send broadcast notification: No event loop.")
        except Exception as e:
            print(f"⚠️ Could not send broadcast notification: {e}")
        
        return escalation_id
    
    except Exception as e:
        print(f"❌ Error creating escalation: {e}")
        traceback.print_exc()
        return escalation_id


def get_escalation(escalation_id):
    """Retrieve escalation details"""
    if not mongo_connected or escalations_collection is None:
        return None
    
    try:
        return escalations_collection.find_one({"escalation_id": escalation_id})
    except Exception as e:
        print(f"❌ Error fetching escalation: {e}")
        return None


def add_agent_message(escalation_id, agent_id, message):
    """Add agent message to escalation"""
    if not mongo_connected or escalations_collection is None:
        return False
    
    try:
        escalations_collection.update_one(
            {"escalation_id": escalation_id},
            {
                "$push": {
                    "messages": {
                        "sender": "agent",
                        "agent_id": agent_id,
                        "message": message,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                }
            }
        )
        print(f"💾 Agent message saved to {escalation_id}")
        return True
    except Exception as e:
        print(f"❌ Error adding agent message: {e}")
        return False


def add_user_message(escalation_id, message):
    """Add user message to escalation"""
    if not mongo_connected or escalations_collection is None:
        return False
    
    try:
        escalations_collection.update_one(
            {"escalation_id": escalation_id},
            {
                "$push": {
                    "messages": {
                        "sender": "user",
                        "message": message,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                }
            }
        )
        print(f"💾 User message saved to {escalation_id}")
        return True
    except Exception as e:
        print(f"❌ Error adding user message: {e}")
        return False


def close_escalation(escalation_id, resolution):
    """Close an escalation"""
    if not mongo_connected or escalations_collection is None:
        return False
    
    try:
        escalations_collection.update_one(
            {"escalation_id": escalation_id},
            {
                "$set": {
                    "status": "closed",
                    "closed_at": datetime.now(timezone.utc),
                    "resolution": resolution
                }
            }
        )
        print(f"✅ Escalation {escalation_id} closed")
        return True
    except Exception as e:
        print(f"❌ Error closing escalation: {e}")
        return False


# ==================== WEBSOCKET ENDPOINTS ====================

@router.websocket("/ws/user/{user_id}")
async def websocket_user_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket for real-time escalation messages for users"""
    await manager.connect_user(user_id, websocket)
    
    try:
        while True:
            try:
                # Check if websocket is still connected before receiving
                if websocket.client_state.value != 1:  # 1 = CONNECTED
                    print(f"⚠️ WebSocket for user {user_id} is not in CONNECTED state")
                    break
                
                data = await websocket.receive_text()
                message_data = json.loads(data)
                print(f"📨 Received from user {user_id}: {message_data.get('type')}")
                
                if message_data.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                    continue
                
                if message_data.get("type") == "message":
                    escalation_id = message_data.get("escalation_id")
                    user_message = message_data.get("message")
                    
                    if not escalation_id or not user_message:
                        await websocket.send_json({
                            "type": "error",
                            "message": "Missing escalation_id or message"
                        })
                        continue
                    
                    # Get escalation to find assigned agent
                    escalation = get_escalation(escalation_id)
                    if not escalation:
                        await websocket.send_json({
                            "type": "error",
                            "message": "Escalation not found"
                        })
                        continue
                    
                    # Save user message to escalation
                    add_user_message(escalation_id, user_message)
                    
                    # Send to assigned agent if connected
                    if escalation.get("assigned_to"):
                        sent = await manager.send_to_agent(escalation["assigned_to"], {
                            "type": "user_message",
                            "escalation_id": escalation_id,
                            "message": user_message,
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        })
                        if sent:
                            print(f"✅ Message forwarded to agent {escalation['assigned_to']}")
                    else:
                        print(f"⚠️ No agent assigned to escalation {escalation_id}")
                    
                    # Acknowledge receipt
                    await websocket.send_json({
                        "type": "ack",
                        "message": "Message received"
                    })
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error from user {user_id}: {e}")
                try:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Invalid JSON format"
                    })
                except:
                    break
            except RuntimeError as e:
                # This catches "Cannot call receive once a disconnect message has been received"
                if "disconnect message has been received" in str(e):
                    print(f"🔌 User {user_id} WebSocket received disconnect message")
                    break
                else:
                    print(f"❌ RuntimeError for user {user_id}: {e}")
                    traceback.print_exc()
                    break
            except Exception as e:
                print(f"❌ Error processing message from user {user_id}: {e}")
                traceback.print_exc()
                # Don't break on general exceptions, but check connection state
                if websocket.client_state.value != 1:
                    break
    
    except WebSocketDisconnect:
        manager.disconnect_user(user_id)
        print(f"🔌 User {user_id} disconnected normally")
    except Exception as e:
        print(f"❌ WebSocket error for user {user_id}: {e}")
        traceback.print_exc()
        manager.disconnect_user(user_id)


@router.websocket("/ws/agent/{agent_id}")
async def websocket_agent_endpoint(websocket: WebSocket, agent_id: str):
    """WebSocket for real-time escalation messages for agents"""
    await manager.connect_agent(agent_id, websocket)
    
    try:
        while True:
            try:
                # Check if websocket is still connected before receiving
                if websocket.client_state.value != 1:  # 1 = CONNECTED
                    print(f"⚠️ WebSocket for agent {agent_id} is not in CONNECTED state")
                    break
                
                data = await websocket.receive_text()
                message_data = json.loads(data)
                print(f"📨 Received from agent {agent_id}: {message_data.get('type')}")
                
                if message_data.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                    continue
                
                if message_data.get("type") == "message":
                    escalation_id = message_data.get("escalation_id")
                    agent_message = message_data.get("message")
                    
                    if not escalation_id or not agent_message:
                        await websocket.send_json({
                            "type": "error",
                            "message": "Missing escalation_id or message"
                        })
                        continue
                    
                    # Get escalation to find user
                    escalation = get_escalation(escalation_id)
                    if not escalation:
                        await websocket.send_json({
                            "type": "error",
                            "message": "Escalation not found"
                        })
                        continue
                    
                    # Save agent message to escalation
                    add_agent_message(escalation_id, agent_id, agent_message)
                    
                    # Send to user if connected
                    sent = await manager.send_to_user(escalation["user_id"], {
                        "type": "agent_message",
                        "escalation_id": escalation_id,
                        "message": agent_message,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                    
                    # Acknowledge receipt
                    await websocket.send_json({
                        "type": "ack",
                        "message": "Message sent to user" if sent else "User not connected, message saved"
                    })
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error from agent {agent_id}: {e}")
                try:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Invalid JSON format"
                    })
                except:
                    break
            except RuntimeError as e:
                # This catches "Cannot call receive once a disconnect message has been received"
                if "disconnect message has been received" in str(e):
                    print(f"🔌 Agent {agent_id} WebSocket received disconnect message")
                    break
                else:
                    print(f"❌ RuntimeError for agent {agent_id}: {e}")
                    traceback.print_exc()
                    break
            except Exception as e:
                print(f"❌ Error processing message from agent {agent_id}: {e}")
                traceback.print_exc()
                # Don't break on general exceptions, but check connection state
                if websocket.client_state.value != 1:
                    break
    
    except WebSocketDisconnect:
        manager.disconnect_agent(agent_id)
        print(f"🔌 Agent {agent_id} disconnected normally")
    except Exception as e:
        print(f"❌ WebSocket error for agent {agent_id}: {e}")
        traceback.print_exc()
        manager.disconnect_agent(agent_id)


# ==================== REST API ENDPOINTS ====================

@router.post("/escalate")
async def escalate_conversation(current_user: dict = Depends(get_current_user)):
    """Escalate current conversation to human agent"""
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        # Corrected relative import
        from .database import get_or_create_user
        
        user = get_or_create_user(
            current_user["email"],
            current_user.get("name"),
            current_user.get("role", "user")
        )
        
        if not user or "user_id" not in user:
            raise HTTPException(status_code=500, detail="User not found")
        
        # Use async version to properly send notifications
        escalation_id = await create_escalation_async(
            user["user_id"],
            "User requested to speak with support agent",
            {"user_email": current_user["email"], "user_name": current_user.get("name")},
            priority="medium"
        )
        
        return {
            "escalation_id": escalation_id,
            "status": "escalated",
            "message": "Your case has been escalated. A support agent will assist you shortly."
        }
    
    except Exception as e:
        print(f"❌ Escalation error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to escalate conversation")


@router.get("/escalations/my")
def get_my_escalations(current_user: dict = Depends(get_current_user)):
    """Get user's escalations"""
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        # Corrected relative import
        from .database import get_or_create_user
        
        user = get_or_create_user(
            current_user["email"],
            current_user.get("name"),
            current_user.get("role", "user")
        )
        
        if not user or "user_id" not in user:
            raise HTTPException(status_code=500, detail="User not found")
        
        escalations = list(escalations_collection.find(
            {"user_id": user["user_id"]}
        ).sort("created_at", -1))
        
        result = []
        for esc in escalations:
            esc["_id"] = str(esc.get("_id", ""))
            if hasattr(esc.get("created_at"), "isoformat"):
                esc["created_at"] = esc["created_at"].isoformat()
            if hasattr(esc.get("closed_at"), "isoformat"):
                esc["closed_at"] = esc["closed_at"].isoformat()
            result.append(esc)
        
        return {"escalations": result, "total": len(result)}
    
    except Exception as e:
        print(f"❌ Get my escalations error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch escalations")


@router.get("/escalations/pending")
def get_pending_escalations(current_user: dict = Depends(get_current_user)):
    """Get pending escalations (unassigned)"""
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    role = current_user.get("role", "user")
    if role not in ["customer_support_agent", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        escalations = list(escalations_collection.find({
            "status": "open",
            "assigned_to": None
        }).sort("created_at", -1))
        
        result = []
        for esc in escalations:
            esc["_id"] = str(esc.get("_id", ""))
            if hasattr(esc.get("created_at"), "isoformat"):
                esc["created_at"] = esc["created_at"].isoformat()
            if hasattr(esc.get("closed_at"), "isoformat"):
                esc["closed_at"] = esc["closed_at"].isoformat()
            result.append(esc)
        
        return {"escalations": result, "total": len(result)}
    
    except Exception as e:
        print(f"❌ Get pending escalations error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch pending escalations")


@router.get("/escalations/assigned")
def get_assigned_escalations(current_user: dict = Depends(get_current_user)):
    """Get escalations assigned to current agent"""
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    role = current_user.get("role", "user")
    if role not in ["customer_support_agent", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        # Corrected relative import
        from .database import get_or_create_user
        
        user = get_or_create_user(
            current_user["email"],
            current_user.get("name"),
            current_user.get("role", "user")
        )
        
        if not user or "user_id" not in user:
            raise HTTPException(status_code=500, detail="User not found")
        
        escalations = list(escalations_collection.find({
            "assigned_to": user["user_id"],
            "status": {"$ne": "closed"}
        }).sort("created_at", -1))
        
        result = []
        for esc in escalations:
            esc["_id"] = str(esc.get("_id", ""))
            if hasattr(esc.get("created_at"), "isoformat"):
                esc["created_at"] = esc["created_at"].isoformat()
            if hasattr(esc.get("closed_at"), "isoformat"):
                esc["closed_at"] = esc["closed_at"].isoformat()
            result.append(esc)
        
        return {"escalations": result, "total": len(result)}
    
    except Exception as e:
        print(f"❌ Get assigned escalations error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch assigned escalations")


@router.get("/escalations")
def get_all_escalations(current_user: dict = Depends(get_current_user)):
    """Get all escalations (support agents and admins only)"""
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    role = current_user.get("role", "user")
    if role not in ["customer_support_agent", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        escalations = list(escalations_collection.find().sort("created_at", -1))
        
        result = []
        for esc in escalations:
            esc["_id"] = str(esc.get("_id", ""))
            if hasattr(esc.get("created_at"), "isoformat"):
                esc["created_at"] = esc["created_at"].isoformat()
            if hasattr(esc.get("closed_at"), "isoformat"):
                esc["closed_at"] = esc["closed_at"].isoformat()
            result.append(esc)
        
        return {"escalations": result, "total": len(result)}
    
    except Exception as e:
        print(f"❌ Get all escalations error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch escalations")


@router.get("/{escalation_id}")
def get_escalation_details(escalation_id: str, current_user: dict = Depends(get_current_user)):
    """Get specific escalation details"""
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        escalation = get_escalation(escalation_id)
        if not escalation:
            raise HTTPException(status_code=404, detail="Escalation not found")
        
        role = current_user.get("role", "user")
        # Corrected relative import
        from .database import get_or_create_user
        user = get_or_create_user(current_user["email"], current_user.get("name"), role)
        
        if role == "user" and escalation["user_id"] != user.get("user_id"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        escalation["_id"] = str(escalation.get("_id", ""))
        if hasattr(escalation.get("created_at"), "isoformat"):
            escalation["created_at"] = escalation["created_at"].isoformat()
        if hasattr(escalation.get("closed_at"), "isoformat"):
            escalation["closed_at"] = escalation["closed_at"].isoformat()
        
        return escalation
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Get escalation details error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch escalation")


@router.get("/messages/{escalation_id}")
def get_escalation_messages(escalation_id: str, current_user: dict = Depends(get_current_user)):
    """Get messages for an escalation"""
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        escalation = get_escalation(escalation_id)
        if not escalation:
            raise HTTPException(status_code=404, detail="Escalation not found")
        
        role = current_user.get("role", "user")
        # Corrected relative import
        from .database import get_or_create_user
        user = get_or_create_user(current_user["email"], current_user.get("name"), role)
        
        if role == "user" and escalation["user_id"] != user.get("user_id"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        return {"messages": escalation.get("messages", [])}
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Get escalation messages error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch messages")


@router.post("/{escalation_id}/message")
async def send_escalation_message(escalation_id: str, message: str = Query(...), current_user: dict = Depends(get_current_user)):
    """Send message in escalation (agent or user)"""
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        escalation = get_escalation(escalation_id)
        if not escalation:
            raise HTTPException(status_code=404, detail="Escalation not found")
        
        role = current_user.get("role", "user")
        # Corrected relative import
        from .database import get_or_create_user
        user = get_or_create_user(current_user["email"], current_user.get("name"), role)
        
        if role == "user" and escalation["user_id"] != user.get("user_id"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        if role in ["customer_support_agent", "admin"]:
            add_agent_message(escalation_id, user.get("user_id"), message)
            # Send to user via WebSocket
            await manager.send_to_user(escalation["user_id"], {
                "type": "agent_message",
                "escalation_id": escalation_id,
                "message": message,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        else:
            add_user_message(escalation_id, message)
            # Send to agent via WebSocket
            if escalation.get("assigned_to"):
                await manager.send_to_agent(escalation["assigned_to"], {
                    "type": "user_message",
                    "escalation_id": escalation_id,
                    "message": message,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
        
        return {"status": "sent", "message": "Message added to escalation"}
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Send escalation message error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to send message")


@router.post("/{escalation_id}/assign")
async def assign_escalation(escalation_id: str, current_user: dict = Depends(get_current_user)):
    """Assign escalation to current agent"""
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    role = current_user.get("role", "user")
    if role not in ["customer_support_agent", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        # Corrected relative import
        from .database import get_or_create_user
        
        user = get_or_create_user(
            current_user["email"],
            current_user.get("name"),
            current_user.get("role", "user")
        )
        
        if not user or "user_id" not in user:
            raise HTTPException(status_code=500, detail="User not found")
        
        escalation = get_escalation(escalation_id)
        if not escalation:
            raise HTTPException(status_code=404, detail="Escalation not found")
        
        if escalation.get("assigned_to") and escalation["assigned_to"] != user["user_id"]:
            raise HTTPException(status_code=400, detail="Escalation already assigned to another agent")
        
        escalations_collection.update_one(
            {"escalation_id": escalation_id},
            {"$set": {
                "assigned_to": user["user_id"],
                "assigned_at": datetime.now(timezone.utc)
            }}
        )
        
        # Notify user that agent has joined
        await manager.send_to_user(escalation["user_id"], {
            "type": "escalation_assigned",
            "escalation_id": escalation_id,
            "agent_name": user.get("name", "Support Agent"),
            "message": f"{user.get('name', 'Support Agent')} has joined the chat"
        })
        
        return {"status": "assigned", "message": f"Escalation assigned to {user.get('name', 'agent')}"}
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Assign escalation error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to assign escalation")


@router.post("/{escalation_id}/close")
def close_escalation_endpoint(escalation_id: str, resolution: str = Query(...), current_user: dict = Depends(get_current_user)):
    """Close an escalation (support agents and admins only)"""
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    role = current_user.get("role", "user")
    if role not in ["customer_support_agent", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        if close_escalation(escalation_id, resolution):
            return {"status": "closed", "message": "Escalation closed successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to close escalation")
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Close escalation error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to close escalation")