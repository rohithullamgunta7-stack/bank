
from .config import db, mongo_connected

def get_faq_context():
    """Return FAQ context dynamically from database"""
    if not mongo_connected or db is None:
        return "Use general knowledge to help users with food delivery questions."
    
    try:
        faq_collection = db["faqs"]
        faqs = list(faq_collection.find({"is_active": True}))
        
        if not faqs:
            return "No FAQs available. Use general knowledge."
        
        context = "FOOD DELIVERY PLATFORM FAQ KNOWLEDGE:\n\n"
        
        for faq in faqs:
            context += f"Q: {faq['question']}\n"
            context += f"A: {faq['answer']}\n\n"
        
        context += "\nProvide helpful answers based on this knowledge."
        
        print(f"Loaded {len(faqs)} FAQs from database")
        return context
        
    except Exception as e:
        print(f"Error loading FAQ context: {e}")
        return "Use general knowledge."


def find_best_faq_match(user_message: str, intent: str):
    """
    Find best matching FAQ using semantic matching - NO HARDCODING
    """
    if db is None:
        return None
    
    try:
        faqs_collection = db["faqs"]
        
        # Get ALL active FAQs - no category filtering
        faqs = list(faqs_collection.find({"is_active": True}))
        
        if not faqs:
            return None
        
        print(f"Searching ALL {len(faqs)} FAQs for: '{user_message}'")
        
        user_lower = user_message.lower().strip()
        user_words = set(user_lower.split())
        
        best_match = None
        best_score = 0
        
        for faq in faqs:
            question = faq.get("question", "").lower()
            answer = faq.get("answer", "").lower()
            tags = [t.lower() for t in faq.get("tags", [])]
            category = faq.get("category", "").lower()
            
            score = 0
            
            # 1. Exact question match
            if user_lower == question:
                score += 100
            
            # 2. Question contains user query or vice versa
            if user_lower in question:
                score += 50
            elif question in user_lower:
                score += 40
            
            # 3. Word overlap (excluding stop words)
            stop_words = {'is', 'there', 'any', 'the', 'a', 'an', 'how', 'what', 
                         'do', 'can', 'i', 'my', 'to', 'for', 'of', 'in', 'on'}
            question_words = set(question.split())
            common_words = (user_words & question_words) - stop_words
            score += len(common_words) * 8
            
            # 4. Tag matching
            for tag in tags:
                if tag in user_lower:
                    score += 15
                # Partial tag match
                for user_word in user_words - stop_words:
                    if user_word in tag or tag in user_word:
                        score += 10
            
            # 5. Category relevance (soft boost, not filtering)
            if category in user_lower:
                score += 5
            
            # 6. Answer relevance (keywords in answer)
            answer_words = set(answer.split())
            common_answer_words = (user_words & answer_words) - stop_words
            score += len(common_answer_words) * 2
            
            if score > best_score:
                best_score = score
                best_match = faq
                print(f"  New best: '{faq['question'][:60]}' (score: {score})")
        
        # Only return if we have a reasonable match
        if best_match and best_score >= 10:
            print(f"✅ Best match: {best_match['faq_id']}")
            print(f"   Question: {best_match['question']}")
            print(f"   Category: {best_match.get('category')}")
            print(f"   Score: {best_score}")
            return best_match
        
        print(f"⚠️ No good match found (best score: {best_score})")
        return None
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None