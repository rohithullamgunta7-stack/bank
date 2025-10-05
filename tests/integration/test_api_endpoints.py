import pytest
from fastapi.testclient import TestClient
import json
from unittest.mock import patch, MagicMock

class TestAuthEndpoints:
    """Integration tests for authentication endpoints"""

    def test_signup_success(self, client, mock_mongo_client):
        """Test successful user signup"""
        signup_data = {
            "name": "New User",
            "email": "newuser@example.com",
            "password": "password123",
            "role": "user"
        }
        
        response = client.post("/auth/signup", json=signup_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_signup_duplicate_email(self, client, mock_mongo_client):
        """Test signup with duplicate email"""
        # First signup
        signup_data = {
            "name": "User One",
            "email": "duplicate@example.com",
            "password": "password123",
            "role": "user"
        }
        client.post("/auth/signup", json=signup_data)
        
        # Second signup with same email
        response = client.post("/auth/signup", json=signup_data)
        
        assert response.status_code == 400
        assert "User already exists" in response.json()["detail"]

    def test_signup_invalid_data(self, client):
        """Test signup with invalid data"""
        invalid_data = {
            "name": "",  # Empty name
            "email": "invalid-email",  # Invalid email format
            "password": "123",  # Too short password
            "role": "user"
        }
        
        response = client.post("/auth/signup", json=invalid_data)
        
        assert response.status_code == 422  # Validation error

    def test_login_success(self, client, mock_mongo_client, sample_users):
        """Test successful login"""
        # Insert test user
        mock_mongo_client.users.insert_one(sample_users[0])
        
        login_data = {
            "username": "test@example.com",
            "password": "test_password"  # This would normally be hashed
        }
        
        with patch('auth.verify_password', return_value=True):
            response = client.post("/auth/login", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client, mock_mongo_client):
        """Test login with invalid credentials"""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        response = client.post("/auth/login", data=login_data)
        
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

    def test_get_current_user_info(self, client, mock_mongo_client, sample_users, valid_token):
        """Test getting current user information"""
        # Insert test user
        mock_mongo_client.users.insert_one(sample_users[0])
        
        headers = {"Authorization": f"Bearer {valid_token}"}
        response = client.get("/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["name"] == "Test User"
        assert data["role"] == "user"

class TestChatEndpoints:
    """Integration tests for chat endpoints"""

    def test_chat_endpoint_success(self, client, mock_mongo_client, sample_users, valid_token, mock_gemini_model):
        """Test successful chat message"""
        # Insert test user
        mock_mongo_client.users.insert_one(sample_users[0])
        
        chat_data = {"message": "Hello, I need help"}
        headers = {"Authorization": f"Bearer {valid_token}"}
        
        response = client.post("/chat", json=chat_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "reply" in data
        assert isinstance(data["reply"], str)

    def test_chat_endpoint_unauthorized(self, client):
        """Test chat endpoint without authentication"""
        chat_data = {"message": "Hello"}
        
        response = client.post("/chat", json=chat_data)
        
        assert response.status_code == 401

    def test_chat_endpoint_empty_message(self, client, valid_token):
        """Test chat endpoint with empty message"""
        chat_data = {"message": ""}
        headers = {"Authorization": f"Bearer {valid_token}"}
        
        response = client.post("/chat", json=chat_data, headers=headers)
        
        assert response.status_code == 422  # Validation error

class TestAdminEndpoints:
    """Integration tests for admin endpoints"""

    def test_admin_get_users_success(self, client, mock_mongo_client, sample_users, admin_token):
        """Test admin endpoint to get all users"""
        # Insert test users
        for user in sample_users:
            mock_mongo_client.users.insert_one(user)
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/auth/users", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == len(sample_users)

    def test_admin_get_users_forbidden(self, client, valid_token):
        """Test admin endpoint with regular user token"""
        headers = {"Authorization": f"Bearer {valid_token}"}
        response = client.get("/auth/users", headers=headers)
        
        assert response.status_code == 403
        assert "Admin access required" in response.json()["detail"]

    def test_update_user_role_success(self, client, mock_mongo_client, sample_users, admin_token):
        """Test updating user role"""
        # Insert test user
        mock_mongo_client.users.insert_one(sample_users[0])
        
        update_data = {
            "user_id": "user_123",
            "new_role": "customer_support_agent"
        }
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = client.put("/auth/update-role", json=update_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["new_role"] == "customer_support_agent"