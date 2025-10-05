from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone, timedelta
from typing import List, Dict
from .auth import require_admin
from .config import db, mongo_connected, model
from .database import messages_collection
import json
import re

router = APIRouter()

faq_collection = db["faqs"] if db is not None else None
conversation_patterns_collection = db["conversation_patterns"] if db is not None else None

def extract_successful_conversations(days: int = 30) -> List[Dict]:
    """Extract conversations that were resolved successfully"""
    if not mongo_connected or messages_collection is None:
        return []
    
    try:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        from .config import db
        feedback_collection = db["feedback"]
        
        positive_feedbacks = list(feedback_collection.find({
            "sentiment": "positive",
            "rating": {"$gte": 4},
            "submitted_at": {"$gte": cutoff_date}
        }))
        
        successful_conversations = []
        
        for feedback in positive_feedbacks:
            # FIX: Handle both datetime and string formats
            feedback_time = feedback.get("submitted_at")
            
            # Convert string to datetime if needed
            if isinstance(feedback_time, str):
                try:
                    feedback_time = datetime.fromisoformat(feedback_time.replace('Z', '+00:00'))
                except:
                    feedback_time = datetime.now(timezone.utc)
            elif feedback_time is None:
                feedback_time = datetime.now(timezone.utc)
            
            # Get conversation history
            messages = list(messages_collection.find({
                "user_id": feedback["user_id"],
                "timestamp": {
                    "$gte": cutoff_date,
                    "$lte": feedback_time
                }
            }).sort("timestamp", 1).limit(10))
            
            if len(messages) >= 2:
                successful_conversations.append({
                    "user_id": feedback["user_id"],
                    "messages": messages,
                    "feedback": feedback
                })
        
        return successful_conversations
    
    except Exception as e:
        print(f"Error extracting successful conversations: {e}")
        import traceback
        traceback.print_exc()
        return []

def identify_patterns(conversations: List[Dict]) -> List[Dict]:
    """Use AI to identify common question-answer patterns"""
    if not conversations:
        return []
    
    try:
        # Prepare conversation data for AI analysis
        conversation_text = ""
        for i, conv in enumerate(conversations[:20]):  # Limit to 20 for context
            conversation_text += f"\nConversation {i+1}:\n"
            for msg in conv["messages"][:6]:  # First 3 exchanges
                role = "User" if msg.get("user") else "Bot"
                content = msg.get("user", "") or msg.get("bot", "")
                conversation_text += f"{role}: {content}\n"
            conversation_text += f"Rating: {conv['feedback'].get('rating', 0)}/5\n"
            conversation_text += "---\n"
        
        prompt = f"""Analyze these successful customer support conversations and identify common question-answer patterns that should become FAQs.

{conversation_text}

For each pattern you identify, return a JSON object with:
- question: A generalized question that captures the pattern
- answer: A clear, concise answer based on successful bot responses
- category: One of [order_tracking, payment, delivery, cancellation, address, menu, account, promo, general]
- tags: List of relevant keywords
- evidence_count: How many conversations support this pattern

Return ONLY a JSON array of patterns. Example:
[
  {{
    "question": "How can I track my order?",
    "answer": "You can track your order in real-time through the app...",
    "category": "order_tracking",
    "tags": ["tracking", "order", "status"],
    "evidence_count": 5
  }}
]

Focus on patterns that appear in at least 2 conversations. Return ONLY the JSON array."""

        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Clean response
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        
        patterns = json.loads(text.strip())
        
        return patterns if isinstance(patterns, list) else []
    
    except Exception as e:
        print(f"Pattern identification error: {e}")
        return []

@router.post("/learn-from-conversations")
async def learn_from_conversations(
    days: int = 30,
    min_confidence: float = 0.2,
    admin_user: dict = Depends(require_admin)
):
    """Analyze successful conversations and generate FAQ suggestions"""
    if not mongo_connected or faq_collection is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        # Extract successful conversations
        print(f"📊 Analyzing conversations from last {days} days...")
        conversations = extract_successful_conversations(days)
        
        if not conversations:
            return {
                "message": "No successful conversations found",
                "patterns_found": 0,
                "faqs_created": 0
            }
        
        print(f"✅ Found {len(conversations)} successful conversations")
        
        # Identify patterns
        print("🔍 Identifying patterns...")
        patterns = identify_patterns(conversations)
        
        if not patterns:
            return {
                "message": "No clear patterns identified",
                "conversations_analyzed": len(conversations),
                "patterns_found": 0,
                "faqs_created": 0
            }
        
        print(f"✅ Identified {len(patterns)} patterns")
        
        # Save patterns and create FAQs
        faqs_created = 0
        suggestions = []
        
        for pattern in patterns:
            # Check if similar FAQ exists
            existing = faq_collection.find_one({
                "question": {"$regex": re.escape(pattern["question"][:30]), "$options": "i"},
                "is_active": True
            })
            
            if existing:
                print(f"⏭️  Skipping duplicate: {pattern['question'][:50]}...")
                continue
            
            # Create FAQ if confidence is high enough
            confidence = min(pattern.get("evidence_count", 1) / 5.0, 1.0)
            
            if confidence >= min_confidence:
                faq_id = f"FAQ_{int(datetime.now(timezone.utc).timestamp())}_{faqs_created}"
                faq_doc = {
                    "faq_id": faq_id,
                    "question": pattern["question"],
                    "answer": pattern["answer"],
                    "category": pattern["category"],
                    "tags": pattern.get("tags", []),
                    "source": "auto_generated",
                    "usage_count": 0,
                    "helpful_count": 0,
                    "not_helpful_count": 0,
                    "is_active": True,
                    "confidence_score": confidence,
                    "evidence_count": pattern.get("evidence_count", 0),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "created_by": "AI_Learning_System"
                }
                
                faq_collection.insert_one(faq_doc)
                faqs_created += 1
                print(f"✅ Created FAQ: {pattern['question'][:50]}...")
            else:
                suggestions.append({
                    **pattern,
                    "confidence": confidence,
                    "reason": "Low confidence - needs manual review"
                })
        
        return {
            "message": f"Learning completed successfully",
            "conversations_analyzed": len(conversations),
            "patterns_found": len(patterns),
            "faqs_created": faqs_created,
            "suggestions_for_review": suggestions
        }
    
    except Exception as e:
        print(f"Learning error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to learn from conversations")

@router.get("/suggested-faqs")
async def get_suggested_faqs(admin_user: dict = Depends(require_admin)):
    """Get AI-suggested FAQs that need manual review"""
    if not mongo_connected or conversation_patterns_collection is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        suggestions = list(conversation_patterns_collection.find({
            "approved": False,
            "rejected": False
        }).sort("occurrence_count", -1))
        
        return {
            "suggestions": [
                {
                    "pattern_id": s["pattern_id"],
                    "question": s["question_pattern"],
                    "answer": s["answer_pattern"],
                    "category": s["category"],
                    "occurrence_count": s["occurrence_count"],
                    "success_rate": s.get("success_rate", 0),
                    "tags": s.get("tags", []),
                    "sample_conversations": s.get("sample_conversations", [])[:3]
                }
                for s in suggestions
            ],
            "total": len(suggestions)
        }
    
    except Exception as e:
        print(f"Get suggestions error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch suggestions")

@router.post("/approve-suggestion/{pattern_id}")
async def approve_suggested_faq(
    pattern_id: str,
    admin_user: dict = Depends(require_admin)
):
    """Approve a suggested FAQ and create it"""
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        pattern = conversation_patterns_collection.find_one({"pattern_id": pattern_id})
        if not pattern:
            raise HTTPException(status_code=404, detail="Pattern not found")
        
        # Create FAQ from pattern
        faq_id = f"FAQ_{int(datetime.now(timezone.utc).timestamp())}"
        faq_doc = {
            "faq_id": faq_id,
            "question": pattern["question_pattern"],
            "answer": pattern["answer_pattern"],
            "category": pattern["category"],
            "tags": pattern.get("tags", []),
            "source": "auto_generated_approved",
            "usage_count": 0,
            "helpful_count": 0,
            "not_helpful_count": 0,
            "is_active": True,
            "confidence_score": pattern.get("success_rate", 0.0),
            "evidence_count": pattern.get("occurrence_count", 0),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "created_by": admin_user.get("email"),
            "approved_from_pattern": pattern_id
        }
        
        faq_collection.insert_one(faq_doc)
        
        # Mark pattern as approved
        conversation_patterns_collection.update_one(
            {"pattern_id": pattern_id},
            {"$set": {
                "approved": True,
                "approved_by": admin_user.get("email"),
                "approved_at": datetime.now(timezone.utc).isoformat(),
                "faq_id": faq_id
            }}
        )
        
        return {
            "message": "FAQ created successfully",
            "faq_id": faq_id,
            "pattern_id": pattern_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Approve suggestion error: {e}")
        raise HTTPException(status_code=500, detail="Failed to approve suggestion")

@router.post("/reject-suggestion/{pattern_id}")
async def reject_suggested_faq(
    pattern_id: str,
    reason: str = "Not suitable for FAQ",
    admin_user: dict = Depends(require_admin)
):
    """Reject a suggested FAQ"""
    if not mongo_connected or conversation_patterns_collection is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        result = conversation_patterns_collection.update_one(
            {"pattern_id": pattern_id},
            {"$set": {
                "rejected": True,
                "rejected_by": admin_user.get("email"),
                "rejected_at": datetime.now(timezone.utc).isoformat(),
                "rejection_reason": reason
            }}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Pattern not found")
        
        return {
            "message": "Suggestion rejected",
            "pattern_id": pattern_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Reject suggestion error: {e}")
        raise HTTPException(status_code=500, detail="Failed to reject suggestion")

@router.post("/analyze-gaps")
async def analyze_faq_gaps(admin_user: dict = Depends(require_admin)):
    """Analyze conversation data to identify FAQ gaps"""
    if not mongo_connected:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        # Get recent conversations with escalations or negative feedback
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)
        
        # Get escalated conversations
        from .config import db
        escalations_collection = db["escalations"]
        feedback_collection = db["feedback"]
        
        escalations = list(escalations_collection.find({
            "created_at": {"$gte": cutoff_date.isoformat()}
        }))
        
        # Get negative feedback
        negative_feedback = list(feedback_collection.find({
            "sentiment": "negative",
            "submitted_at": {"$gte": cutoff_date}
        }))
        
        # Analyze what topics are causing issues
        problem_conversations = []
        
        for esc in escalations[:20]:
            problem_conversations.append({
                "type": "escalation",
                "reason": esc.get("reason", ""),
                "context": esc.get("context", {})
            })
        
        for fb in negative_feedback[:20]:
            problem_conversations.append({
                "type": "negative_feedback",
                "comment": fb.get("comment", ""),
                "topics": fb.get("topics", [])
            })
        
        if not problem_conversations:
            return {
                "message": "No gaps identified",
                "missing_topics": []
            }
        
        # Use AI to identify missing FAQ topics
        problems_text = "\n\n".join([
            f"Issue {i+1}:\nType: {p['type']}\nDetails: {p.get('reason', p.get('comment', ''))}\nTopics: {p.get('topics', [])}"
            for i, p in enumerate(problem_conversations)
        ])
        
        # Get existing FAQ topics
        existing_faqs = list(faq_collection.find({"is_active": True}))
        existing_topics = "\n".join([f"- {faq['question']}" for faq in existing_faqs[:50]])
        
        prompt = f"""Analyze these customer support issues and identify FAQ topics that are MISSING from the current FAQ database.

EXISTING FAQs:
{existing_topics}

PROBLEM CASES (Escalations and Negative Feedback):
{problems_text}

Identify FAQ topics that would have prevented these issues. Return ONLY a JSON array of missing topics:

[
  {{
    "missing_topic": "Brief description",
    "suggested_question": "What question should be answered?",
    "priority": "high|medium|low",
    "frequency": 5,
    "reason": "Why this FAQ is needed"
  }}
]

Return ONLY the JSON array."""

        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Clean response
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        
        gaps = json.loads(text.strip())
        
        return {
            "message": "Gap analysis completed",
            "issues_analyzed": len(problem_conversations),
            "existing_faqs_count": len(existing_faqs),
            "missing_topics": gaps if isinstance(gaps, list) else [],
            "recommendations": f"Consider creating FAQs for {len(gaps)} identified gaps"
        }
    
    except Exception as e:
        print(f"Gap analysis error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to analyze FAQ gaps")