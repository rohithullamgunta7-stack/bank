from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from .models import FAQCreate, FAQUpdate, FAQResponse, FAQSearchQuery, FAQFeedback
from .auth import get_current_user, require_admin, require_support_or_admin
from .config import db, mongo_connected, model
from .database import messages_collection
import json
import re

router = APIRouter()

# Initialize collections
faq_collection = db["faqs"] if db is not None else None
conversation_patterns_collection = db["conversation_patterns"] if db is not None else None

def extract_keywords(text: str) -> List[str]:
    """Extract meaningful keywords from text"""
    # Remove common words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'my', 'your', 'his', 'her', 'its', 'our', 'their'}
    
    # Tokenize and filter
    words = re.findall(r'\b[a-z]+\b', text.lower())
    keywords = [w for w in words if w not in stop_words and len(w) > 3]
    
    # Get unique keywords
    return list(set(keywords[:10]))  # Limit to 10 keywords

def categorize_question(question: str) -> str:
    """Auto-categorize question using keywords"""
    question_lower = question.lower()
    
    categories = {
        'order_tracking': ['order', 'track', 'status', 'where', 'delivery', 'delivered'],
        'payment': ['payment', 'pay', 'charged', 'refund', 'money', 'card', 'wallet'],
        'delivery': ['delivery', 'driver', 'partner', 'deliver', 'late', 'delayed'],
        'cancellation': ['cancel', 'cancellation', 'refund'],
        'address': ['address', 'change', 'location', 'wrong address'],
        'menu': ['menu', 'item', 'food', 'restaurant', 'available'],
        'account': ['account', 'login', 'password', 'profile', 'email'],
        'promo': ['promo', 'coupon', 'discount', 'offer', 'code'],
        'general': []
    }
    
    for category, keywords in categories.items():
        if any(keyword in question_lower for keyword in keywords):
            return category
    
    return 'general'

@router.post("/create", response_model=FAQResponse)
async def create_faq(
    faq: FAQCreate,
    current_user: dict = Depends(require_support_or_admin)
):
    """Create a new FAQ entry"""
    if not mongo_connected or faq_collection is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        # Auto-categorize if not provided or if general
        if not faq.category or faq.category == 'general':
            faq.category = categorize_question(faq.question)
        
        # Extract keywords if tags not provided
        if not faq.tags:
            faq.tags = extract_keywords(faq.question + " " + faq.answer)
        
        faq_id = f"FAQ_{int(datetime.now(timezone.utc).timestamp())}"
        faq_doc = {
            "faq_id": faq_id,
            "question": faq.question,
            "answer": faq.answer,
            "category": faq.category,
            "tags": faq.tags,
            "source": faq.source,
            "usage_count": 0,
            "helpful_count": 0,
            "not_helpful_count": 0,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "created_by": current_user.get("email"),
            "updated_at": None
        }
        
        faq_collection.insert_one(faq_doc)
        
        return FAQResponse(
            faq_id=faq_id,
            question=faq.question,
            answer=faq.answer,
            category=faq.category,
            tags=faq.tags,
            source=faq.source,
            usage_count=0,
            helpful_count=0,
            not_helpful_count=0,
            is_active=True,
            created_at=faq_doc["created_at"]
        )
    
    except Exception as e:
        print(f"FAQ creation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create FAQ")

@router.get("/all", response_model=List[FAQResponse])
async def get_all_faqs(
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get all FAQs with optional filtering"""
    if not mongo_connected or faq_collection is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        query = {}
        if category:
            query["category"] = category
        if is_active is not None:
            query["is_active"] = is_active
        
        faqs = list(faq_collection.find(query).sort("usage_count", -1))
        
        return [
            FAQResponse(
                faq_id=faq["faq_id"],
                question=faq["question"],
                answer=faq["answer"],
                category=faq["category"],
                tags=faq.get("tags", []),
                source=faq.get("source", "manual"),
                usage_count=faq.get("usage_count", 0),
                helpful_count=faq.get("helpful_count", 0),
                not_helpful_count=faq.get("not_helpful_count", 0),
                is_active=faq.get("is_active", True),
                created_at=faq["created_at"],
                updated_at=faq.get("updated_at")
            )
            for faq in faqs
        ]
    
    except Exception as e:
        print(f"Get FAQs error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch FAQs")

@router.get("/categories")
async def get_categories(current_user: dict = Depends(get_current_user)):
    """Get all FAQ categories with counts"""
    if not mongo_connected or faq_collection is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        pipeline = [
            {"$match": {"is_active": True}},
            {"$group": {
                "_id": "$category",
                "count": {"$sum": 1},
                "total_usage": {"$sum": "$usage_count"}
            }},
            {"$sort": {"total_usage": -1}}
        ]
        
        results = list(faq_collection.aggregate(pipeline))
        
        return {
            "categories": [
                {
                    "category": r["_id"],
                    "count": r["count"],
                    "total_usage": r["total_usage"]
                }
                for r in results
            ]
        }
    
    except Exception as e:
        print(f"Get categories error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch categories")

@router.post("/search")
async def search_faqs(
    search: FAQSearchQuery,
    current_user: dict = Depends(get_current_user)
):
    """Search FAQs using semantic matching"""
    if not mongo_connected or faq_collection is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        # Get all active FAQs
        all_faqs = list(faq_collection.find({"is_active": True}))
        
        # Use Gemini to find best matches
        faq_text = "\n\n".join([
            f"FAQ {i+1}:\nQ: {faq['question']}\nA: {faq['answer']}\nCategory: {faq['category']}\nTags: {', '.join(faq.get('tags', []))}"
            for i, faq in enumerate(all_faqs)
        ])
        
        prompt = f"""You are a FAQ search expert. Find the most relevant FAQs for the user's query.

User Query: "{search.query}"

Available FAQs:
{faq_text}

Return ONLY a JSON array of FAQ numbers (1-based index) that are relevant, ordered by relevance.
Example: [3, 1, 7]

If no FAQs are relevant, return an empty array: []

Return ONLY the JSON array, nothing else."""

        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Clean response
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        
        relevant_indices = json.loads(text.strip())
        
        # Get matching FAQs
        results = []
        for idx in relevant_indices[:search.limit]:
            if 1 <= idx <= len(all_faqs):
                faq = all_faqs[idx - 1]
                results.append({
                    "faq_id": faq["faq_id"],
                    "question": faq["question"],
                    "answer": faq["answer"],
                    "category": faq["category"],
                    "tags": faq.get("tags", []),
                    "usage_count": faq.get("usage_count", 0),
                    "relevance_score": 1.0 / (len(results) + 1)  # Simple relevance
                })
                
                # Increment usage count
                faq_collection.update_one(
                    {"faq_id": faq["faq_id"]},
                    {"$inc": {"usage_count": 1}}
                )
        
        return {
            "query": search.query,
            "results": results,
            "total": len(results)
        }
    
    except Exception as e:
        print(f"FAQ search error: {e}")
        # Fallback to keyword search
        keywords = extract_keywords(search.query)
        faqs = list(faq_collection.find({
            "is_active": True,
            "$or": [
                {"tags": {"$in": keywords}},
                {"question": {"$regex": search.query, "$options": "i"}}
            ]
        }).limit(search.limit))
        
        return {
            "query": search.query,
            "results": [
                {
                    "faq_id": faq["faq_id"],
                    "question": faq["question"],
                    "answer": faq["answer"],
                    "category": faq["category"],
                    "tags": faq.get("tags", []),
                    "usage_count": faq.get("usage_count", 0)
                }
                for faq in faqs
            ],
            "total": len(faqs)
        }

@router.put("/{faq_id}", response_model=FAQResponse)
async def update_faq(
    faq_id: str,
    updates: FAQUpdate,
    current_user: dict = Depends(require_support_or_admin)
):
    """Update an existing FAQ"""
    if not mongo_connected or faq_collection is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        faq = faq_collection.find_one({"faq_id": faq_id})
        if not faq:
            raise HTTPException(status_code=404, detail="FAQ not found")
        
        update_data = {k: v for k, v in updates.dict().items() if v is not None}
        
        if update_data:
            update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
            update_data["updated_by"] = current_user.get("email")
            
            faq_collection.update_one(
                {"faq_id": faq_id},
                {"$set": update_data}
            )
            
            # Refresh FAQ data
            faq = faq_collection.find_one({"faq_id": faq_id})
        
        return FAQResponse(
            faq_id=faq["faq_id"],
            question=faq["question"],
            answer=faq["answer"],
            category=faq["category"],
            tags=faq.get("tags", []),
            source=faq.get("source", "manual"),
            usage_count=faq.get("usage_count", 0),
            helpful_count=faq.get("helpful_count", 0),
            not_helpful_count=faq.get("not_helpful_count", 0),
            is_active=faq.get("is_active", True),
            created_at=faq["created_at"],
            updated_at=faq.get("updated_at")
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"FAQ update error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update FAQ")

@router.delete("/{faq_id}")
async def delete_faq(
    faq_id: str,
    current_user: dict = Depends(require_admin)
):
    """Delete (deactivate) an FAQ"""
    if not mongo_connected or faq_collection is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        result = faq_collection.update_one(
            {"faq_id": faq_id},
            {"$set": {
                "is_active": False,
                "deleted_at": datetime.now(timezone.utc).isoformat(),
                "deleted_by": current_user.get("email")
            }}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="FAQ not found")
        
        return {"message": "FAQ deleted successfully", "faq_id": faq_id}
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"FAQ deletion error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete FAQ")

@router.post("/feedback")
async def submit_faq_feedback(
    feedback: FAQFeedback,
    current_user: dict = Depends(get_current_user)
):
    """Submit feedback on FAQ helpfulness"""
    if not mongo_connected or faq_collection is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        field = "helpful_count" if feedback.helpful else "not_helpful_count"
        
        result = faq_collection.update_one(
            {"faq_id": feedback.faq_id},
            {"$inc": {field: 1}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="FAQ not found")
        
        return {
            "message": "Feedback recorded",
            "faq_id": feedback.faq_id,
            "helpful": feedback.helpful
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"FAQ feedback error: {e}")
        raise HTTPException(status_code=500, detail="Failed to record feedback")

@router.get("/analytics")
async def get_faq_analytics(
    current_user: dict = Depends(require_support_or_admin)
):
    """Get FAQ usage analytics"""
    if not mongo_connected or faq_collection is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        total_faqs = faq_collection.count_documents({"is_active": True})
        total_usage = list(faq_collection.aggregate([
            {"$match": {"is_active": True}},
            {"$group": {"_id": None, "total": {"$sum": "$usage_count"}}}
        ]))
        
        # Most used FAQs
        top_faqs = list(faq_collection.find(
            {"is_active": True}
        ).sort("usage_count", -1).limit(10))
        
        # Most helpful FAQs
        helpful_pipeline = [
            {"$match": {"is_active": True, "helpful_count": {"$gt": 0}}},
            {"$addFields": {
                "helpfulness_ratio": {
                    "$divide": [
                        "$helpful_count",
                        {"$add": ["$helpful_count", "$not_helpful_count"]}
                    ]
                }
            }},
            {"$sort": {"helpfulness_ratio": -1}},
            {"$limit": 10}
        ]
        most_helpful = list(faq_collection.aggregate(helpful_pipeline))
        
        # FAQs by source
        source_stats = list(faq_collection.aggregate([
            {"$match": {"is_active": True}},
            {"$group": {"_id": "$source", "count": {"$sum": 1}}}
        ]))
        
        return {
            "total_faqs": total_faqs,
            "total_usage": total_usage[0]["total"] if total_usage else 0,
            "top_used_faqs": [
                {
                    "faq_id": faq["faq_id"],
                    "question": faq["question"],
                    "usage_count": faq["usage_count"],
                    "category": faq["category"]
                }
                for faq in top_faqs
            ],
            "most_helpful_faqs": [
                {
                    "faq_id": faq["faq_id"],
                    "question": faq["question"],
                    "helpfulness_ratio": faq.get("helpfulness_ratio", 0),
                    "helpful_count": faq.get("helpful_count", 0)
                }
                for faq in most_helpful
            ],
            "faqs_by_source": {r["_id"]: r["count"] for r in source_stats}
        }
    
    except Exception as e:
        print(f"FAQ analytics error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch analytics")