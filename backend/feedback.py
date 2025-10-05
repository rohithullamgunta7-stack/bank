

from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone, timedelta
from typing import Optional
from .models import FeedbackSubmission, FeedbackResponse, FeedbackAnalytics
from .auth import get_current_user, require_admin, require_support_or_admin
from .config import db, mongo_connected, model
from .database import get_user_by_email, messages_collection
import json
import re

router = APIRouter()

# Initialize feedback collection
feedback_collection = db["feedback"] if db is not None else None
chat_sessions_collection = db["chat_sessions"] if db is not None else None

def analyze_sentiment(comment: str) -> dict:
    """Use Gemini to analyze sentiment and extract insights"""
    if not comment or not comment.strip():
        return {
            "sentiment": "neutral",
            "topics": [],
            "key_phrases": []
        }
    
    try:
        prompt = f"""Analyze this customer feedback and return ONLY valid JSON.

Feedback: "{comment}"

Return this exact structure:
{{
    "sentiment": "positive" or "neutral" or "negative",
    "topics": ["topic1", "topic2"],
    "key_phrases": ["phrase1", "phrase2"]
}}

Rules for sentiment:
- "positive" if: happy, satisfied, excellent, good, great, love, amazing, perfect, fast, helpful
- "negative" if: bad, worst, terrible, awful, slow, late, cold, wrong, missing, horrible, poor
- "neutral" if: none of the above or just informational

Rules for topics (pick 1-3 relevant ones):
- "food_quality" - taste, temperature, freshness
- "delivery_speed" - fast, slow, late, on-time
- "customer_service" - helpful, rude, response
- "order_accuracy" - wrong items, missing items
- "packaging" - damaged, spilled, secure
- "price" - expensive, value, cost
- "app_experience" - easy, difficult, confusing

Rules for key_phrases:
- Extract 2-3 SHORT phrases (2-5 words) that capture the main points
- Use actual words from the feedback

Return ONLY the JSON object, nothing else."""

        response = model.generate_content(prompt)
        
        # Clean the response
        text = response.text.strip()
        
        # Remove markdown code blocks if present
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        
        # Parse JSON
        result = json.loads(text.strip())
        
        # Validate and set defaults
        if "sentiment" not in result or result["sentiment"] not in ["positive", "neutral", "negative"]:
            # Fallback: basic keyword detection
            comment_lower = comment.lower()
            positive_words = ["excellent", "great", "good", "love", "amazing", "perfect", "fast", "helpful", "best"]
            negative_words = ["worst", "terrible", "awful", "bad", "slow", "late", "cold", "wrong", "missing", "horrible"]
            
            pos_count = sum(1 for word in positive_words if word in comment_lower)
            neg_count = sum(1 for word in negative_words if word in comment_lower)
            
            if pos_count > neg_count:
                result["sentiment"] = "positive"
            elif neg_count > pos_count:
                result["sentiment"] = "negative"
            else:
                result["sentiment"] = "neutral"
        
        if "topics" not in result or not isinstance(result["topics"], list):
            result["topics"] = []
        
        if "key_phrases" not in result or not isinstance(result["key_phrases"], list):
            # Extract first few words as fallback
            words = comment.strip().split()[:5]
            result["key_phrases"] = [" ".join(words)]
            
        return result
        
    except Exception as e:
        print(f"Sentiment analysis error: {e}")
        print(f"Response text: {response.text if 'response' in locals() else 'N/A'}")
        
        # FALLBACK: Simple keyword-based sentiment
        comment_lower = comment.lower()
        positive_words = ["excellent", "great", "good", "love", "amazing", "perfect", "fast", "helpful", "best", "happy", "satisfied"]
        negative_words = ["worst", "terrible", "awful", "bad", "slow", "late", "cold", "wrong", "missing", "horrible", "poor", "disappointed"]
        
        pos_count = sum(1 for word in positive_words if word in comment_lower)
        neg_count = sum(1 for word in negative_words if word in comment_lower)
        
        if pos_count > neg_count:
            sentiment = "positive"
        elif neg_count > pos_count:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return {
            "sentiment": sentiment,
            "topics": [],
            "key_phrases": [comment[:50]]
        }

def get_or_create_session(user_id: str) -> str:
    """Get current session or create new one"""
    if chat_sessions_collection is None:
        return f"SESSION_{int(datetime.now(timezone.utc).timestamp())}"
    
    # Check for active session OR recently ended session (within last 5 minutes)
    five_minutes_ago = datetime.now(timezone.utc) - timedelta(minutes=5)
    
    active_session = chat_sessions_collection.find_one({
        "user_id": user_id,
        "$or": [
            {"end_time": None},  # Active session
            {"end_time": {"$gte": five_minutes_ago}}  # Recently ended (within 5 min)
        ],
        "start_time": {"$gte": datetime.now(timezone.utc) - timedelta(minutes=30)}
    }, sort=[("start_time", -1)])
    
    if active_session:
        print(f"♻️ Reusing session: {active_session['session_id']}")
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
    print(f"🆕 Created new session: {session_id}")
    return session_id

def update_session_message_count(session_id: str):
    """Increment message count for session"""
    if chat_sessions_collection is None:
        return
    
    chat_sessions_collection.update_one(
        {"session_id": session_id},
        {"$inc": {"message_count": 1}}
    )

def should_ask_for_feedback(user_id: str) -> dict:
    """Determine if we should prompt for feedback - ONLY after conversation ends"""
    if chat_sessions_collection is None:
        print("❌ chat_sessions_collection is None")
        return {"should_ask": False}
    
    try:
        # Look for sessions that ended within last 3 minutes
        three_minutes_ago = datetime.now(timezone.utc) - timedelta(minutes=3)
        
        session = chat_sessions_collection.find_one({
            "user_id": user_id,
            "feedback_submitted": False,
            "end_time": {"$gte": three_minutes_ago, "$ne": None}  # Must have end_time
        }, sort=[("end_time", -1)])
        
        print(f"🔍 Checking feedback for user: {user_id}")
        
        if not session:
            print("❌ No recently ended session found")
            return {"should_ask": False}
        
        message_count = session.get("message_count", 0)
        print(f"📊 Session found: {session.get('session_id')}")
        print(f"📈 Message count: {message_count}")
        print(f"🎯 Feedback submitted: {session.get('feedback_submitted', False)}")
        print(f"⏰ Session ended: {session.get('end_time')}")
        
        # Ask after 2+ messages AND session has ended
        if message_count >= 2:
            print("✅ SHOULD ASK FOR FEEDBACK!")
            return {
                "should_ask": True,
                "session_id": session["session_id"],
                "reason": "conversation_complete"
            }
        else:
            print(f"⏳ Not enough messages (need 2, have {message_count})")
        
        return {"should_ask": False}
    except Exception as e:
        print(f"❌ Error in should_ask_for_feedback: {e}")
        import traceback
        traceback.print_exc()
        return {"should_ask": False}

@router.post("/submit", response_model=FeedbackResponse)
def submit_feedback(
    feedback: FeedbackSubmission,
    current_user: dict = Depends(get_current_user)
):
    """Submit user feedback after chat interaction"""
    if not mongo_connected or feedback_collection is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        user = get_user_by_email(current_user["email"])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Analyze sentiment if comment provided
        sentiment_data = {"sentiment": "neutral", "topics": [], "key_phrases": []}
        if feedback.comment:
            sentiment_data = analyze_sentiment(feedback.comment)
        
        # Create feedback document
        feedback_id = f"FBK_{int(datetime.now(timezone.utc).timestamp())}"
        feedback_doc = {
            "feedback_id": feedback_id,
            "user_id": user["user_id"],
            "rating": feedback.rating,
            "comment": feedback.comment,
            "issue_resolved": feedback.issue_resolved,
            "conversation_id": feedback.conversation_id,
            "escalation_id": feedback.escalation_id,
            "feedback_type": feedback.feedback_type,
            "sentiment": sentiment_data["sentiment"],
            "topics": sentiment_data["topics"],
            "key_phrases": sentiment_data["key_phrases"],
            "submitted_at": datetime.now(timezone.utc),
            "user_name": user.get("name", "Unknown"),
            "user_email": user.get("email", "unknown@example.com")
        }
        
        feedback_collection.insert_one(feedback_doc)
        
        # Mark session as feedback submitted
        if chat_sessions_collection is not None and feedback.conversation_id:
            chat_sessions_collection.update_one(
                {"session_id": feedback.conversation_id},
                {
                    "$set": {
                        "feedback_submitted": True,
                        "feedback_at": datetime.now(timezone.utc)
                    }
                }
            )
        
        return FeedbackResponse(
            feedback_id=feedback_id,
            message="Thank you for your feedback!",
            sentiment=sentiment_data["sentiment"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Feedback submission error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to submit feedback")

@router.get("/check-prompt/{user_id}")
def check_feedback_prompt(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Check if user should be prompted for feedback"""
    try:
        result = should_ask_for_feedback(user_id)
        return result
    except Exception as e:
        print(f"Check feedback prompt error: {e}")
        return {"should_ask": False}

@router.get("/analytics")
def get_feedback_analytics(
    days: int = 30,
    admin_user: dict = Depends(require_admin)
):
    """Get comprehensive feedback analytics for admin dashboard"""
    if not mongo_connected or feedback_collection is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Total feedback count
        total_feedback = feedback_collection.count_documents({
            "submitted_at": {"$gte": cutoff_date}
        })
        
        # Average rating
        pipeline = [
            {"$match": {"submitted_at": {"$gte": cutoff_date}}},
            {"$group": {
                "_id": None,
                "avg_rating": {"$avg": "$rating"}
            }}
        ]
        avg_result = list(feedback_collection.aggregate(pipeline))
        average_rating = round(avg_result[0]["avg_rating"], 2) if avg_result else 0.0
        
        # Sentiment distribution
        sentiment_pipeline = [
            {"$match": {"submitted_at": {"$gte": cutoff_date}}},
            {"$group": {
                "_id": "$sentiment",
                "count": {"$sum": 1}
            }}
        ]
        sentiment_results = list(feedback_collection.aggregate(sentiment_pipeline))
        sentiment_distribution = {
            "positive": 0,
            "neutral": 0,
            "negative": 0
        }
        for result in sentiment_results:
            sentiment_distribution[result["_id"]] = result["count"]
        
        # Rating distribution
        rating_pipeline = [
            {"$match": {"submitted_at": {"$gte": cutoff_date}}},
            {"$group": {
                "_id": "$rating",
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]
        rating_results = list(feedback_collection.aggregate(rating_pipeline))
        rating_distribution = {str(i): 0 for i in range(1, 6)}
        for result in rating_results:
            rating_distribution[str(result["_id"])] = result["count"]
        
        # Response rate calculation
        if chat_sessions_collection is not None:
            total_sessions = chat_sessions_collection.count_documents({
                "start_time": {"$gte": cutoff_date},
                "message_count": {"$gte": 2}
            })
            sessions_with_feedback = chat_sessions_collection.count_documents({
                "start_time": {"$gte": cutoff_date},
                "feedback_submitted": True
            })
            response_rate = round(
                (sessions_with_feedback / total_sessions * 100) if total_sessions > 0 else 0,
                1
            )
        else:
            response_rate = 0.0
        
        # Recent feedback
        recent_feedback = list(feedback_collection.find(
            {"submitted_at": {"$gte": cutoff_date}}
        ).sort("submitted_at", -1).limit(20))
        
        for item in recent_feedback:
            item["_id"] = str(item["_id"])
            item["submitted_at"] = item["submitted_at"].isoformat()
        
        # Trend calculation
        previous_cutoff = cutoff_date - timedelta(days=days)
        previous_feedback = feedback_collection.count_documents({
            "submitted_at": {"$gte": previous_cutoff, "$lt": cutoff_date}
        })
        
        if previous_feedback > 0:
            trend_percentage = round(
                ((total_feedback - previous_feedback) / previous_feedback) * 100,
                1
            )
        else:
            trend_percentage = 100.0 if total_feedback > 0 else 0.0
        
        # Issue resolution rate
        total_with_resolution = feedback_collection.count_documents({
            "submitted_at": {"$gte": cutoff_date},
            "issue_resolved": {"$exists": True}
        })
        resolved_count = feedback_collection.count_documents({
            "submitted_at": {"$gte": cutoff_date},
            "issue_resolved": True
        })
        resolution_rate = round(
            (resolved_count / total_with_resolution * 100) if total_with_resolution > 0 else 0,
            1
        )
        
        # Top topics
        topics_pipeline = [
            {"$match": {"submitted_at": {"$gte": cutoff_date}}},
            {"$unwind": "$topics"},
            {"$group": {
                "_id": "$topics",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        top_topics = list(feedback_collection.aggregate(topics_pipeline))
        
        return {
            "total_feedback": total_feedback,
            "average_rating": average_rating,
            "sentiment_distribution": sentiment_distribution,
            "rating_distribution": rating_distribution,
            "response_rate": response_rate,
            "recent_feedback": recent_feedback,
            "trend": {
                "percentage": trend_percentage,
                "direction": "up" if trend_percentage > 0 else "down" if trend_percentage < 0 else "stable"
            },
            "resolution_rate": resolution_rate,
            "top_topics": [{"topic": item["_id"], "count": item["count"]} for item in top_topics],
            "period_days": days
        }
    
    except Exception as e:
        print(f"Analytics error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to fetch analytics")

@router.get("/recent")
def get_recent_feedback(
    limit: int = 50,
    sentiment: Optional[str] = None,
    support_user: dict = Depends(require_support_or_admin)
):
    """Get recent feedback entries with optional filtering"""
    if not mongo_connected or feedback_collection is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        query = {}
        if sentiment and sentiment in ["positive", "neutral", "negative"]:
            query["sentiment"] = sentiment
        
        feedback_list = list(feedback_collection.find(query).sort("submitted_at", -1).limit(limit))
        
        for item in feedback_list:
            item["_id"] = str(item["_id"])
            item["submitted_at"] = item["submitted_at"].isoformat()
        
        return {
            "feedback": feedback_list,
            "total": len(feedback_list)
        }
    
    except Exception as e:
        print(f"Recent feedback error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch feedback")

@router.get("/agent-performance")
def get_agent_performance(
    days: int = 30,
    admin_user: dict = Depends(require_admin)
):
    """Get individual agent performance metrics"""
    if not mongo_connected or feedback_collection is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        from .database import get_users_by_role
        
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        agents = get_users_by_role("customer_support_agent")
        
        agent_stats = []
        for agent in agents:
            agent_feedback = list(feedback_collection.find({
                "escalation_id": {"$exists": True},
                "feedback_type": "agent_support",
                "submitted_at": {"$gte": cutoff_date}
            }))
            
            relevant_feedback = []
            for fb in agent_feedback:
                if fb.get("escalation_id"):
                    from .config import db
                    if db is not None:
                        escalation = db["escalations"].find_one({"escalation_id": fb["escalation_id"]})
                        if escalation and escalation.get("assigned_agent_id") == agent["user_id"]:
                            relevant_feedback.append(fb)
            
            if relevant_feedback:
                avg_rating = sum(fb["rating"] for fb in relevant_feedback) / len(relevant_feedback)
                resolved_count = sum(1 for fb in relevant_feedback if fb.get("issue_resolved"))
                
                agent_stats.append({
                    "agent_id": agent["user_id"],
                    "agent_name": agent["name"],
                    "agent_email": agent["email"],
                    "total_feedback": len(relevant_feedback),
                    "average_rating": round(avg_rating, 2),
                    "resolution_rate": round((resolved_count / len(relevant_feedback)) * 100, 1),
                    "positive_feedback": sum(1 for fb in relevant_feedback if fb.get("sentiment") == "positive")
                })
        
        agent_stats.sort(key=lambda x: x["average_rating"], reverse=True)
        
        return {
            "agents": agent_stats,
            "period_days": days
        }
    
    except Exception as e:
        print(f"Agent performance error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to fetch agent performance")