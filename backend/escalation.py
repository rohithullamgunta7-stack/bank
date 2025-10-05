from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from typing import Dict, List, Optional
from datetime import datetime, timezone
from database import messages_collection, users_collection
from config import orders_col, refunds_col
from auth import get_current_user, require_support_or_admin
from models import EscalationRequest
from bson import ObjectId
import json
import asyncio

router = APIRouter()

# In-memory storage
active_escalations: Dict[str, dict] = {}
agent_connections: Dict[str, WebSocket] = {}
user_connections: Dict[str, WebSocket] = {}

CRITICAL_KEYWORDS = [
    "insect", "bug", "hair", "foreign object", "food poisoning", "sick", 
    "allergy", "allergic reaction", "wrong address", "missing order",
    "not delivered", "3 hours", "4 hours", "very late", "extremely late",
    "refund not received", "charged twice", "overcharged", "fraud"
]

# ----------------- Helper Functions -----------------

def convert_objectid(obj):
    """Recursively convert ObjectId to str"""
    if isinstance(obj, list):
        return [convert_objectid(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_objectid(v) for k, v in obj.items()}
    elif isinstance(obj, ObjectId):
        return str(obj)
    else:
        return obj

def should_escalate(message: str, conversation_history: list) -> tuple[bool, str]:
    msg_lower = message.lower()
    for keyword in CRITICAL_KEYWORDS:
        if keyword in msg_lower:
            return True, f"Critical issue detected: {keyword}"
    
    if len(conversation_history) >= 6:
        recent_user_msgs = [msg.get('content', '').lower() for msg in conversation_history[-6:] if msg.get('role') == 'user']
        complaint_indicators = ["not", "no", "still", "again", "problem", "issue", "wrong"]
        complaint_count = sum(1 for msg in recent_user_msgs if any(word in msg for word in complaint_indicators))
        if complaint_count >= 3:
            return True, "Multiple unresolved complaints"
    
    agent_requests = ["speak to agent", "human agent", "talk to person", "real person", "customer service", "supervisor", "manager"]
    if any(req in msg_lower for req in agent_requests):
        return True, "User requested human agent"
    
    return False, ""

def determine_priority(reason: str) -> str:
    critical_terms = ["food poisoning", "allergic", "sick", "insect", "fraud"]
    high_terms = ["not delivered", "missing", "wrong address", "3 hours", "4 hours"]
    reason_lower = reason.lower()
    
    if any(term in reason_lower for term in critical_terms):
        return "critical"
    elif any(term in reason_lower for term in high_terms):
        return "high"
    else:
        return "medium"

def get_available_agents() -> List[dict]:
    try:
        agents = list(users_collection.find(
            {"role": "customer_support_agent"}, 
            {"_id": 0, "user_id": 1, "name": 1, "email": 1}
        ))
        return [agent for agent in agents if agent["user_id"] in agent_connections]
    except Exception as e:
        print(f"Error fetching agents: {e}")
        return []

async def notify_agent_new_escalation(agent_id: str, escalation_id: str, escalation: dict):
    """Send WebSocket notification to agent about new escalation"""
    if agent_id in agent_connections:
        try:
            await agent_connections[agent_id].send_json({
                "type": "new_escalation",
                "escalation_id": escalation_id,
                "escalation": convert_objectid(escalation)
            })
            print(f"Notified agent {agent_id} about escalation {escalation_id}")
            return True
        except Exception as e:
            print(f"Error notifying agent: {e}")
            return False
    else:
        print(f"Agent {agent_id} not connected to WebSocket")
        return False

async def assign_escalation_to_agent(escalation_id: str, agent_id: str) -> bool:
    try:
        if escalation_id not in active_escalations:
            return False
        
        active_escalations[escalation_id]["assigned_agent_id"] = agent_id
        active_escalations[escalation_id]["status"] = "assigned"
        active_escalations[escalation_id]["assigned_at"] = datetime.now(timezone.utc).isoformat()

        from config import db
        if db is not None:
            db["escalations"].update_one(
                {"escalation_id": escalation_id},
                {"$set": {
                    "assigned_agent_id": agent_id,
                    "status": "assigned",
                    "assigned_at": datetime.now(timezone.utc).isoformat()
                }},
                upsert=True
            )
        
        await notify_agent_new_escalation(agent_id, escalation_id, active_escalations[escalation_id])
        
        return True
    except Exception as e:
        print(f"Error assigning escalation: {e}")
        return False

def create_escalation(user_id: str, reason: str, context: dict) -> str:
    try:
        escalation_id = f"ESC_{int(datetime.now(timezone.utc).timestamp())}"
        escalation = {
            "escalation_id": escalation_id,
            "user_id": user_id,
            "reason": reason,
            "status": "pending",
            "assigned_agent_id": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "resolved_at": None,
            "context": context,
            "priority": determine_priority(reason),
            "notes": []
        }
        active_escalations[escalation_id] = escalation

        from config import db
        if db is not None:
            db["escalations"].insert_one(escalation.copy())

        return escalation_id
    except Exception as e:
        print(f"Error creating escalation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create escalation: {str(e)}")

# ----------------- REST Endpoints -----------------

@router.post("/escalate")
async def escalate_conversation(escalation_req: EscalationRequest, current_user: dict = Depends(get_current_user)):
    try:
        user = users_collection.find_one({"email": current_user["email"]})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        try:
            recent_messages = list(messages_collection.find({"user_id": user["user_id"]}).sort("timestamp", -1).limit(20))
        except Exception as e:
            print(f"Error fetching messages: {e}")
            recent_messages = []

        try:
            orders = list(orders_col.find({"user_id": user["user_id"]}).sort("order_date", -1).limit(5))
        except Exception as e:
            print(f"Error fetching orders: {e}")
            orders = []

        try:
            refunds = list(refunds_col.find({"user_id": user["user_id"]}).sort("request_time", -1).limit(5))
        except Exception as e:
            print(f"Error fetching refunds: {e}")
            refunds = []

        context = {
            "user_name": user.get("name", "Unknown"),
            "user_email": user.get("email", "Unknown"),
            "recent_messages": [
                {
                    "role": "user" if i % 2 == 0 else "bot",
                    "content": msg.get("user", "") if i % 2 == 0 else msg.get("bot", ""),
                    "timestamp": msg.get("timestamp", datetime.now(timezone.utc)).isoformat() if hasattr(msg.get("timestamp", datetime.now(timezone.utc)), "isoformat") else str(msg.get("timestamp", ""))
                } for i, msg in enumerate(recent_messages[::-1])
            ],
            "recent_orders": [
                {
                    "order_id": o.get("order_id", ""), 
                    "restaurant": o.get("restaurant", ""), 
                    "status": o.get("status", ""), 
                    "total_amount": o.get("total_amount", 0)
                } for o in orders
            ],
            "recent_refunds": [
                {
                    "refund_id": r.get("refund_id", ""), 
                    "order_id": r.get("order_id", ""), 
                    "amount": r.get("amount", 0), 
                    "status": r.get("status", "")
                } for r in refunds
            ]
        }

        escalation_id = create_escalation(user["user_id"], escalation_req.reason, context)

        available_agents = get_available_agents()
        if available_agents:
            agent = available_agents[0]
            await assign_escalation_to_agent(escalation_id, agent["user_id"])

        return {
            "escalation_id": escalation_id,
            "status": "created",
            "message": "Your issue has been escalated to a human agent. Please wait for assistance."
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Escalation error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/escalations/my")
async def get_my_escalations(current_user: dict = Depends(get_current_user)):
    try:
        user = users_collection.find_one({"email": current_user["email"]})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_escalations = []
        
        for esc in active_escalations.values():
            if esc.get("user_id") == user.get("user_id"):
                user_escalations.append(convert_objectid(esc))
        
        from config import db
        if db is not None:
            try:
                db_escalations = list(db["escalations"].find({"user_id": user.get("user_id")}))
                for esc in db_escalations:
                    if not any(e.get("escalation_id") == esc.get("escalation_id") for e in user_escalations):
                        user_escalations.append(convert_objectid(esc))
            except Exception as e:
                print(f"Error fetching from DB: {e}")
        
        return {"escalations": user_escalations}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_my_escalations: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/escalations/pending")
async def get_pending_escalations(current_user: dict = Depends(require_support_or_admin)):
    try:
        from config import db
        escalations = []
        
        for esc in active_escalations.values():
            if esc.get("status") == "pending":
                escalations.append(convert_objectid(esc))
        
        if db is not None:
            try:
                db_escalations = list(db["escalations"].find({"status": "pending"}))
                for esc in db_escalations:
                    if not any(e.get("escalation_id") == esc.get("escalation_id") for e in escalations):
                        escalations.append(convert_objectid(esc))
            except Exception as e:
                print(f"Error fetching pending from DB: {e}")

        priority_order = {"critical": 0, "high": 1, "medium": 2}
        escalations.sort(key=lambda x: priority_order.get(x.get("priority", "medium"), 3))
        
        return {"escalations": escalations, "count": len(escalations)}
    except Exception as e:
        print(f"Error in get_pending_escalations: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/escalations/assigned")
async def get_assigned_escalations(current_user: dict = Depends(require_support_or_admin)):
    try:
        user = users_collection.find_one({"email": current_user["email"]})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        from config import db
        escalations = []
        
        for esc in active_escalations.values():
            if esc.get("assigned_agent_id") == user.get("user_id") and esc.get("status") == "assigned":
                escalations.append(convert_objectid(esc))
        
        if db is not None:
            try:
                db_escalations = list(db["escalations"].find({
                    "assigned_agent_id": user.get("user_id"), 
                    "status": "assigned"
                }))
                for esc in db_escalations:
                    if not any(e.get("escalation_id") == esc.get("escalation_id") for e in escalations):
                        escalations.append(convert_objectid(esc))
            except Exception as e:
                print(f"Error fetching assigned from DB: {e}")

        return {"escalations": escalations, "count": len(escalations)}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_assigned_escalations: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/escalations/{escalation_id}/claim")
async def claim_escalation(escalation_id: str, current_user: dict = Depends(require_support_or_admin)):
    try:
        user = users_collection.find_one({"email": current_user["email"]})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        from config import db
        
        escalation = None
        if escalation_id in active_escalations:
            escalation = active_escalations[escalation_id]
        elif db is not None:
            escalation = db["escalations"].find_one({"escalation_id": escalation_id})
            if escalation:
                active_escalations[escalation_id] = escalation
        
        if not escalation:
            raise HTTPException(status_code=404, detail="Escalation not found")
        
        if escalation.get("status") != "pending":
            raise HTTPException(status_code=400, detail="Escalation is not available to claim")
        
        success = await assign_escalation_to_agent(escalation_id, user.get("user_id"))
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to assign escalation")
        
        return {
            "message": "Escalation claimed successfully",
            "escalation_id": escalation_id,
            "agent_id": user.get("user_id")
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in claim_escalation: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/messages/{escalation_id}")
async def get_escalation_messages(
    escalation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get message history for an escalation"""
    try:
        messages = list(messages_collection.find({
            "escalation_id": escalation_id
        }).sort("timestamp", 1))
        
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "sender": msg.get("sender"),
                "message": msg.get("message"),
                "timestamp": msg.get("timestamp").isoformat() if hasattr(msg.get("timestamp"), 'isoformat') else str(msg.get("timestamp"))
            })
        
        return {"messages": formatted_messages, "count": len(formatted_messages)}
    except Exception as e:
        print(f"Error fetching escalation messages: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch messages")
    
@router.post("/escalations/{escalation_id}/resolve")
async def resolve_escalation(
    escalation_id: str,
    resolution: dict,
    current_user: dict = Depends(require_support_or_admin)
):
    try:
        from config import db
        
        if escalation_id in active_escalations:
            active_escalations[escalation_id]["status"] = "resolved"
            active_escalations[escalation_id]["resolved_at"] = datetime.now(timezone.utc).isoformat()
            active_escalations[escalation_id]["resolution"] = resolution
        
        if db is not None:
            db["escalations"].update_one(
                {"escalation_id": escalation_id},
                {"$set": {
                    "status": "resolved",
                    "resolved_at": datetime.now(timezone.utc).isoformat(),
                    "resolution": resolution
                }}
            )
        
        return {"message": "Escalation resolved successfully", "escalation_id": escalation_id}
    except Exception as e:
        print(f"Error in resolve_escalation: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# ----------------- WebSocket Endpoints -----------------

@router.websocket("/ws/agent/{agent_id}")
async def agent_websocket(websocket: WebSocket, agent_id: str):
    await websocket.accept()
    agent_connections[agent_id] = websocket
    print(f"Agent {agent_id} connected to WebSocket")
    
    # Heartbeat task
    async def send_heartbeat():
        while True:
            try:
                if websocket.client_state.value == 1:  # Connected
                    await websocket.send_json({"type": "ping"})
                await asyncio.sleep(30)
            except:
                break
    
    heartbeat_task = asyncio.create_task(send_heartbeat())
    
    try:
        while True:
            data = await websocket.receive_json()
            print(f"Agent {agent_id} sent: {data}")
            
            if data.get("type") == "pong":
                continue
            
            if data.get("type") == "message":
                escalation_id = data.get("escalation_id")
                message = data.get("message")
                
                if escalation_id not in active_escalations:
                    from config import db
                    if db is not None:
                        escalation = db["escalations"].find_one({"escalation_id": escalation_id})
                        if escalation:
                            active_escalations[escalation_id] = escalation
                        else:
                            await websocket.send_json({
                                "type": "error",
                                "message": "Escalation not found"
                            })
                            continue
                    else:
                        await websocket.send_json({
                            "type": "error",
                            "message": "Database unavailable"
                        })
                        continue
                
                escalation = active_escalations[escalation_id]
                
                if escalation.get("assigned_agent_id") != agent_id:
                    await websocket.send_json({
                        "type": "error",
                        "message": "You are not assigned to this escalation"
                    })
                    continue
                
                user_id = escalation.get("user_id")

                msg_doc = {
                    "escalation_id": escalation_id,
                    "user_id": user_id,
                    "agent_id": agent_id,
                    "sender": "agent",
                    "message": message,
                    "timestamp": datetime.now(timezone.utc)
                }
                
                try:
                    messages_collection.insert_one(msg_doc)
                    print(f"Saved agent message to database")
                except Exception as e:
                    print(f"Error saving message: {e}")

                if user_id in user_connections:
                    try:
                        await user_connections[user_id].send_json({
                            "type": "agent_message",
                            "escalation_id": escalation_id,
                            "message": message,
                            "timestamp": msg_doc["timestamp"].isoformat()
                        })
                        print(f"Message delivered to user {user_id}")
                    except Exception as e:
                        print(f"Error sending to user: {e}")
                else:
                    print(f"User {user_id} not connected")

                await websocket.send_json({
                    "type": "message_sent",
                    "escalation_id": escalation_id,
                    "timestamp": msg_doc["timestamp"].isoformat()
                })
                
    except WebSocketDisconnect:
        print(f"Agent {agent_id} disconnected")
    except Exception as e:
        print(f"WebSocket error for agent {agent_id}: {e}")
    finally:
        heartbeat_task.cancel()
        if agent_id in agent_connections:
            del agent_connections[agent_id]


@router.websocket("/ws/user/{user_id}")
async def user_websocket(websocket: WebSocket, user_id: str):
    await websocket.accept()
    user_connections[user_id] = websocket
    print(f"User {user_id} connected to WebSocket")
    
    # Heartbeat task
    async def send_heartbeat():
        while True:
            try:
                if websocket.client_state.value == 1:
                    await websocket.send_json({"type": "ping"})
                await asyncio.sleep(30)
            except:
                break
    
    heartbeat_task = asyncio.create_task(send_heartbeat())
    
    try:
        while True:
            data = await websocket.receive_json()
            print(f"User {user_id} sent: {data}")
            
            if data.get("type") == "pong":
                continue
            
            if data.get("type") == "message":
                escalation_id = data.get("escalation_id")
                message = data.get("message")
                
                if escalation_id not in active_escalations:
                    from config import db
                    if db is not None:
                        escalation = db["escalations"].find_one({"escalation_id": escalation_id})
                        if escalation:
                            active_escalations[escalation_id] = escalation
                        else:
                            await websocket.send_json({
                                "type": "error",
                                "message": "Escalation not found"
                            })
                            continue
                    else:
                        await websocket.send_json({
                            "type": "error",
                            "message": "Database unavailable"
                        })
                        continue
                
                escalation = active_escalations[escalation_id]
                
                if escalation.get("user_id") != user_id:
                    await websocket.send_json({
                        "type": "error",
                        "message": "This is not your escalation"
                    })
                    continue
                
                agent_id = escalation.get("assigned_agent_id")

                msg_doc = {
                    "escalation_id": escalation_id,
                    "user_id": user_id,
                    "agent_id": agent_id,
                    "sender": "user",
                    "message": message,
                    "timestamp": datetime.now(timezone.utc)
                }
                
                try:
                    messages_collection.insert_one(msg_doc)
                    print(f"Saved user message to database")
                except Exception as e:
                    print(f"Error saving message: {e}")

                # CRITICAL FIX: Send to agent
                if agent_id and agent_id in agent_connections:
                    try:
                        await agent_connections[agent_id].send_json({
                            "type": "user_message",
                            "escalation_id": escalation_id,
                            "user_id": user_id,
                            "message": message,
                            "timestamp": msg_doc["timestamp"].isoformat()
                        })
                        print(f"Message delivered to agent {agent_id}")
                    except Exception as e:
                        print(f"Error sending to agent: {e}")
                        if agent_id in agent_connections:
                            del agent_connections[agent_id]
                else:
                    print(f"No agent assigned or agent not connected")

                await websocket.send_json({
                    "type": "message_sent",
                    "escalation_id": escalation_id,
                    "timestamp": msg_doc["timestamp"].isoformat()
                })
                
    except WebSocketDisconnect:
        print(f"User {user_id} disconnected")
    except Exception as e:
        print(f"WebSocket error for user {user_id}: {e}")
    finally:
        heartbeat_task.cancel()
        if user_id in user_connections:
            del user_connections[user_id]