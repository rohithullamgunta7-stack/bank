from .config import db, mongo_connected
from datetime import datetime, timezone

def migrate_faq_system():
    """Initialize FAQ collections and seed with static FAQs"""
    print("🔄 Starting FAQ system migration...")

    if not mongo_connected or db is None:
        print("❌ MongoDB not connected")
        return
    
    try:
        # Create collections
        if "faqs" not in db.list_collection_names():
            db.create_collection("faqs")
            print("✅ Created 'faqs' collection")
        
        if "conversation_patterns" not in db.list_collection_names():
            db.create_collection("conversation_patterns")
            print("✅ Created 'conversation_patterns' collection")
        
        faq_col = db["faqs"]
        patterns_col = db["conversation_patterns"]
        
        # Create indexes
        faq_col.create_index("faq_id", unique=True)
        faq_col.create_index("category")
        faq_col.create_index("tags")
        faq_col.create_index("is_active")
        faq_col.create_index("usage_count")
        faq_col.create_index([("question", "text"), ("answer", "text")])
        print("✅ Created FAQ indexes")
        
        patterns_col.create_index("pattern_id", unique=True)
        patterns_col.create_index("approved")
        patterns_col.create_index("occurrence_count")
        print("✅ Created conversation_patterns indexes")
        
        # Seed with initial FAQs from faq_context.py
        initial_faqs = [
            {
                "question": "How do I change my delivery address?",
                "answer": "You can change your delivery address within 2-3 minutes of placing your order, but only before the restaurant confirms it. After confirmation or once food preparation starts, address changes are not possible. Additional charges may apply if the new address is farther.",
                "category": "address",
                "tags": ["address", "change", "delivery", "location"]
            },
            {
                "question": "Can I cancel my order?",
                "answer": "Yes! You can cancel for free within 60 seconds of placing your order. After 60 seconds, a cancellation fee applies. If food preparation has started, only a partial refund is available. Once the order is out for delivery, cancellation is not possible.",
                "category": "cancellation",
                "tags": ["cancel", "cancellation", "refund", "order"]
            },
            {
                "question": "How can I track my order?",
                "answer": "Real-time tracking is available once your food is picked up by the delivery partner. You'll see live location updates and the delivery partner's contact number in the app during delivery.",
                "category": "order_tracking",
                "tags": ["tracking", "order", "status", "delivery"]
            },
            {
                "question": "What payment methods do you accept?",
                "answer": "We accept Credit/Debit cards, UPI, Net Banking, digital wallets (Paytm, PhonePe, Google Pay), Cash on Delivery, platform credits, and gift cards.",
                "category": "payment",
                "tags": ["payment", "methods", "card", "upi", "wallet"]
            },
            {
                "question": "How long does a refund take?",
                "answer": "Refund timelines vary by payment method: Bank account refunds take 5-7 business days, wallet refunds are instant, and credit card refunds take 7-10 business days.",
                "category": "payment",
                "tags": ["refund", "timeline", "payment", "money"]
            },
            {
                "question": "What if my order has wrong items?",
                "answer": "Please report the issue immediately through the app with a photo. Based on the severity, we'll provide a full or partial refund, or offer a replacement order.",
                "category": "order_tracking",
                "tags": ["wrong", "items", "order", "mistake", "refund"]
            },
            {
                "question": "Why is my delivery delayed?",
                "answer": "Common causes include: restaurant being busy, high demand periods, traffic conditions, weather issues, or delivery partner availability. The restaurant preparation time may also be longer than initially estimated.",
                "category": "delivery",
                "tags": ["delay", "late", "delivery", "time"]
            },
            {
                "question": "Can I add items to my order after placing it?",
                "answer": "Unfortunately, you cannot add or remove items after the restaurant confirms your order. You'll need to place a new separate order for additional items.",
                "category": "order_tracking",
                "tags": ["modify", "add", "items", "order", "change"]
            },
            {
                "question": "How do I contact the delivery partner?",
                "answer": "The delivery partner's contact number becomes visible in the app once your order is out for delivery. You can call or message them through the app. For safety, phone numbers are masked.",
                "category": "delivery",
                "tags": ["contact", "driver", "delivery", "partner", "phone"]
            },
            {
                "question": "How do promo codes work?",
                "answer": "Each promo code has specific conditions: minimum order value, restaurant eligibility, expiry date, and usage limits. You can use only one promo code per order. Check the code details before applying.",
                "category": "promo",
                "tags": ["promo", "coupon", "discount", "code", "offer"]
            },
            {
                "question": "How do I reorder from my order history?",
                "answer": "Go to Order History in the app, find the order you want to repeat, tap 'Reorder', review the items in your cart, and place the order.",
                "category": "order_tracking",
                "tags": ["reorder", "history", "repeat", "order"]
            },
            {
                "question": "Can I tip the delivery partner?",
                "answer": "Yes! Tipping is optional but appreciated. You can tip the delivery partner before or after delivery through the app payment system.",
                "category": "delivery",
                "tags": ["tip", "tipping", "delivery", "partner", "driver"]
            }
        ]
        
        # Check if FAQs already exist
        existing_count = faq_col.count_documents({})
        if existing_count > 0:
            print(f"⚠️  {existing_count} FAQs already exist, skipping seed data")
        else:
            # Insert initial FAQs
            for i, faq_data in enumerate(initial_faqs):
                faq_id = f"FAQ_{int(datetime.now(timezone.utc).timestamp())}_{i}"
                faq_doc = {
                    "faq_id": faq_id,
                    "question": faq_data["question"],
                    "answer": faq_data["answer"],
                    "category": faq_data["category"],
                    "tags": faq_data["tags"],
                    "source": "manual",
                    "usage_count": 0,
                    "helpful_count": 0,
                    "not_helpful_count": 0,
                    "is_active": True,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "created_by": "system_migration"
                }
                faq_col.insert_one(faq_doc)
            
            print(f"✅ Inserted {len(initial_faqs)} initial FAQs")
        
        print("\n🎉 FAQ system migration completed successfully!")
        print(f"📊 Total FAQs: {faq_col.count_documents({})}")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    migrate_faq_system()