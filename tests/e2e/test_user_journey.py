import pytest
from fastapi.testclient import TestClient

class TestUserJourney:
    """End-to-end tests for complete user journeys"""

    def test_complete_user_signup_and_chat_flow(self, client):
        """Test complete user journey from signup to chat"""
        # 1. User signup
        signup_data = {
            "name": "E2E Test User",
            "email": "e2etest@example.com",
            "password": "testpassword123",
            "role": "user"
        }
        
        signup_response = client.post("/auth/signup", json=signup_data)
        assert signup_response.status_code == 200
        
        token = signup_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Get user info
        user_info_response = client.get("/auth/me", headers=headers)
        assert user_info_response.status_code == 200
        user_data = user_info_response.json()
        assert user_data["email"] == "e2etest@example.com"
        
        # 3. Send chat message
        chat_data = {"message": "Hello, I need help with my account"}
        chat_response = client.post("/chat", json=chat_data, headers=headers)
        assert chat_response.status_code == 200
        
        bot_reply = chat_response.json()["reply"]
        assert isinstance(bot_reply, str)
        assert len(bot_reply) > 0
        
        # 4. Send follow-up message
        followup_data = {"message": "Thank you for the help!"}
        followup_response = client.post("/chat", json=followup_data, headers=headers)
        assert followup_response.status_code == 200

    def test_admin_user_management_flow(self, client):
        """Test admin user management workflow"""
        # 1. Create admin user
        admin_signup_data = {
            "name": "Test Admin",
            "email": "testadmin@example.com",
            "password": "adminpassword123",
            "role": "admin",
            "admin_secret": "admin_secret_123"  # Use your actual admin secret
        }
        
        admin_response = client.post("/auth/admin-signup", json=admin_signup_data)
        assert admin_response.status_code == 200
        
        admin_token = admin_response.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 2. Create regular user
        user_signup_data = {
            "name": "Regular User",
            "email": "regularuser@example.com",
            "password": "userpassword123",
            "role": "user"
        }
        
        user_response = client.post("/auth/signup", json=user_signup_data)
        assert user_response.status_code == 200
        
        # 3. Admin gets all users
        users_response = client.get("/auth/users", headers=admin_headers)
        assert users_response.status_code == 200
        users = users_response.json()
        assert len(users) >= 2  # At least admin and regular user
        
        # 4. Find regular user ID
        regular_user = next(u for u in users if u["email"] == "regularuser@example.com")
        user_id = regular_user["user_id"]
        
        # 5. Admin updates user role
        role_update_data = {
            "user_id": user_id,
            "new_role": "customer_support_agent"
        }
        
        role_update_response = client.put("/auth/update-role", 
                                        json=role_update_data, 
                                        headers=admin_headers)
        assert role_update_response.status_code == 200
        
        # 6. Verify role update
        updated_users_response = client.get("/auth/users", headers=admin_headers)
        updated_users = updated_users_response.json()
        updated_user = next(u for u in updated_users if u["user_id"] == user_id)
        assert updated_user["role"] == "customer_support_agent"
