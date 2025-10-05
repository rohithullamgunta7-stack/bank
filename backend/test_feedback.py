# test_feedback.py - Test feedback system

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_feedback_system():
    print("🧪 Testing Feedback System\n")
    
    # 1. Login as user
    print("1. Logging in as user...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "user@example.com", "password": "password123"}
    )
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful\n")
    
    # 2. Submit feedback
    print("2. Submitting feedback...")
    feedback_data = {
        "rating": 5,
        "comment": "The chatbot was extremely helpful and resolved my issue quickly!",
        "issue_resolved": True,
        "feedback_type": "bot_chat"
    }
    
    feedback_response = requests.post(
        f"{BASE_URL}/feedback/submit",
        json=feedback_data,
        headers=headers
    )
    
    if feedback_response.status_code == 200:
        result = feedback_response.json()
        print(f"✅ Feedback submitted: {result['feedback_id']}")
        print(f"   Sentiment detected: {result.get('sentiment', 'N/A')}\n")
    else:
        print(f"❌ Feedback submission failed: {feedback_response.text}\n")
    
    # 3. Login as admin
    print("3. Logging in as admin...")
    admin_login = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "admin@example.com", "password": "admin123"}
    )
    
    if admin_login.status_code != 200:
        print("❌ Admin login failed")
        return
    
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("✅ Admin login successful\n")
    
    # 4. Get analytics
    print("4. Fetching feedback analytics...")
    analytics_response = requests.get(
        f"{BASE_URL}/feedback/analytics?days=30",
        headers=admin_headers
    )
    
    if analytics_response.status_code == 200:
        analytics = analytics_response.json()
        print(f"✅ Analytics retrieved:")
        print(f"   Total feedback: {analytics['total_feedback']}")
        print(f"   Average rating: {analytics['average_rating']}")
        print(f"   Response rate: {analytics['response_rate']}%")
        print(f"   Sentiment distribution: {analytics['sentiment_distribution']}\n")
    else:
        print(f"❌ Analytics retrieval failed\n")
    
    # 5. Get recent feedback
    print("5. Fetching recent feedback...")
    recent_response = requests.get(
        f"{BASE_URL}/feedback/recent?limit=5",
        headers=admin_headers
    )
    
    if recent_response.status_code == 200:
        recent = recent_response.json()
        print(f"✅ Retrieved {len(recent['feedback'])} recent feedback entries\n")
    else:
        print(f"❌ Recent feedback retrieval failed\n")
    
    print("🎉 Testing complete!")

if __name__ == "__main__":
    test_feedback_system()