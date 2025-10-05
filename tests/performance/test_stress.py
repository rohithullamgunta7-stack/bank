import pytest
import threading
import time
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor, as_completed

class TestStressTests:
    """Stress tests to check system limits"""

    def test_high_concurrent_users(self, client, mock_mongo_client, mock_gemini_model):
        """Test system behavior with many concurrent users"""
        with patch('database.users_collection', mock_mongo_client.users), \
             patch('database.messages_collection', mock_mongo_client.messages):
            
            def create_user_and_chat(user_id):
                """Create a user and send a chat message"""
                try:
                    # Signup
                    signup_data = {
                        "name": f"User {user_id}",
                        "email": f"user{user_id}@example.com",
                        "password": "password123",
                        "role": "user"
                    }
                    
                    signup_response = client.post("/auth/signup", json=signup_data)
                    if signup_response.status_code != 200:
                        return False
                    
                    token = signup_response.json()["access_token"]
                    headers = {"Authorization": f"Bearer {token}"}
                    
                    # Send chat message
                    chat_data = {"message": f"Hello from user {user_id}"}
                    chat_response = client.post("/chat", json=chat_data, headers=headers)
                    
                    return chat_response.status_code == 200
                except Exception as e:
                    print(f"Error for user {user_id}: {e}")
                    return False
            
            # Test with 50 concurrent users
            num_users = 50
            success_count = 0
            
            with ThreadPoolExecutor(max_workers=20) as executor:
                futures = [executor.submit(create_user_and_chat, i) for i in range(num_users)]
                
                for future in as_completed(futures):
                    if future.result():
                        success_count += 1
            
            # At least 80% should succeed under stress
            success_rate = success_count / num_users
            assert success_rate >= 0.8

    def test_memory_usage_under_load(self, client, mock_mongo_client):
        """Test memory usage doesn't grow excessively under load"""
        import psutil
        import os
        
        with patch('database.users_collection', mock_mongo_client.users):
            
            # Get initial memory usage
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Create many users
            for i in range(200):
                signup_data = {
                    "name": f"Memory Test User {i}",
                    "email": f"memtest{i}@example.com",
                    "password": "password123",
                    "role": "user"
                }
                
                response = client.post("/auth/signup", json=signup_data)
                # Don't assert here to continue the test even if some fail
            
            # Get final memory usage
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            # Memory increase should be reasonable (less than 100MB for 200 users)
            assert memory_increase < 100
