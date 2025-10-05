"""
Run this script to add sample food delivery orders and refunds to MongoDB
Usage: python seed_data.py
"""

from .config import orders_col, refunds_col, mongo_connected
from datetime import datetime, timedelta
import random
import uuid

def seed_orders():
    """Add sample food delivery orders"""
    if not mongo_connected:
        print("MongoDB not connected!")
        return
    
    # You need to replace these with actual user_ids from your database
    # Run: db.users.find({}, {user_id: 1}) in MongoDB to get real user_ids
    sample_user_ids = [
        "user_1759329154",  # Replace with your actual user_ids
        "user_1759329169",
    ]
    
    restaurants = [
        "Pizza Palace", "Burger King", "Sushi Master", "Taco Bell",
        "Chinese Garden", "Indian Spice", "Thai Kitchen", "Pasta House"
    ]
    
    food_items = {
        "Pizza Palace": ["Margherita Pizza", "Pepperoni Pizza", "Garlic Bread", "Chicken Wings"],
        "Burger King": ["Classic Burger", "Cheese Burger", "Fries", "Onion Rings", "Milkshake"],
        "Sushi Master": ["California Roll", "Salmon Sashimi", "Tempura Roll", "Miso Soup"],
        "Taco Bell": ["Beef Tacos", "Chicken Burrito", "Nachos", "Quesadilla"],
        "Chinese Garden": ["Fried Rice", "Kung Pao Chicken", "Spring Rolls", "Sweet & Sour Pork"],
        "Indian Spice": ["Butter Chicken", "Naan Bread", "Biryani", "Samosa"],
        "Thai Kitchen": ["Pad Thai", "Green Curry", "Tom Yum Soup", "Spring Rolls"],
        "Pasta House": ["Spaghetti Carbonara", "Lasagna", "Garlic Bread", "Caesar Salad"]
    }
    
    statuses = ["Processing", "Preparing", "Ready for Pickup", "Out for Delivery", "Delivered", "Cancelled"]
    addresses = [
        "123 Main Street, Apt 4B",
        "456 Oak Avenue, House 12",
        "789 Pine Road, Floor 3",
        "19 Example Street, City",
        "321 Elm Street, Unit 5A"
    ]
    
    orders = []
    for i in range(20):
        user_id = random.choice(sample_user_ids)
        restaurant = random.choice(restaurants)
        items = random.sample(food_items[restaurant], random.randint(2, 4))
        status = random.choice(statuses)
        
        # Random date within last 7 days
        days_ago = random.uniform(0, 7)
        order_date = datetime.now() - timedelta(days=days_ago)
        
        # Expected delivery 30-60 minutes after order
        expected_delivery = order_date + timedelta(minutes=random.randint(30, 60))
        
        total_amount = round(random.uniform(15.99, 89.99), 2)
        
        order = {
            "order_id": str(uuid.uuid4()),
            "user_id": user_id,
            "restaurant": restaurant,
            "items": items,
            "total_amount": total_amount,
            "status": status,
            "order_date": order_date,
            "expected_delivery_time": expected_delivery.isoformat(),
            "delivery_address": random.choice(addresses)
        }
        orders.append(order)
    
    try:
        # Don't delete existing orders, just add new ones
        # orders_col.delete_many({})  # Uncomment if you want to clear first
        result = orders_col.insert_many(orders)
        print(f"✅ Successfully added {len(result.inserted_ids)} food delivery orders")
    except Exception as e:
        print(f"❌ Error adding orders: {e}")

def seed_refunds():
    """Add sample refund requests for food orders"""
    if not mongo_connected:
        print("MongoDB not connected!")
        return
    
    # Get some order IDs from the database
    orders = list(orders_col.find().limit(10))
    
    if not orders:
        print("⚠️ No orders found. Please run seed_orders() first.")
        return
    
    refund_statuses = ["Pending", "Approved", "Rejected", "Processed"]
    refund_reasons = [
        "Food was cold",
        "Wrong items delivered",
        "Missing items",
        "Food quality poor",
        "Delivery took too long",
        "Order cancelled by restaurant"
    ]
    
    refunds = []
    for i, order in enumerate(orders[:6]):  # Create refunds for 6 orders
        days_ago = random.uniform(0, 5)
        request_time = datetime.now() - timedelta(days=days_ago)
        
        refund = {
            "refund_id": str(uuid.uuid4()),
            "order_id": order["order_id"],
            "user_id": order["user_id"],
            "amount": order["total_amount"],
            "status": random.choice(refund_statuses),
            "reason": random.choice(refund_reasons),
            "request_time": request_time
        }
        refunds.append(refund)
    
    try:
        # Don't delete existing refunds
        # refunds_col.delete_many({})  # Uncomment if you want to clear first
        result = refunds_col.insert_many(refunds)
        print(f"✅ Successfully added {len(result.inserted_ids)} refund requests")
    except Exception as e:
        print(f"❌ Error adding refunds: {e}")

def show_stats():
    """Show current database statistics"""
    if not mongo_connected:
        print("MongoDB not connected!")
        return
    
    orders_count = orders_col.count_documents({})
    refunds_count = refunds_col.count_documents({})
    
    print("\n📊 Database Statistics:")
    print(f"   Total Orders: {orders_count}")
    print(f"   Total Refunds: {refunds_count}")
    
    if orders_count > 0:
        print("\n🍕 Sample Recent Orders:")
        for order in orders_col.find().sort("order_date", -1).limit(3):
            restaurant = order.get('restaurant', 'Unknown Restaurant')
            items = order.get('items', [])
            items_str = ', '.join(items[:2]) if items else 'No items'
            print(f"   • {restaurant}: {items_str} - ${order['total_amount']} ({order['status']})")
    
    if refunds_count > 0:
        print("\n💰 Sample Refunds:")
        for refund in refunds_col.find().sort("request_time", -1).limit(3):
            print(f"   • ${refund['amount']} - {refund['status']} - {refund.get('reason', 'No reason')}")
    
    # Status breakdown
    print("\n📈 Order Status Breakdown:")
    for status in ["Processing", "Preparing", "Out for Delivery", "Delivered"]:
        count = orders_col.count_documents({"status": status})
        if count > 0:
            print(f"   • {status}: {count}")

if __name__ == "__main__":
    print("🌱 Seeding database with food delivery data...\n")
    print("⚠️ IMPORTANT: Make sure to update sample_user_ids in the script with actual user_ids from your database!")
    print("   Run this in MongoDB shell: db.users.find({}, {user_id: 1})\n")
    
    seed_orders()
    seed_refunds()
    show_stats()
    
    print("\n✨ Done! Your database is ready for testing the food delivery chatbot.")