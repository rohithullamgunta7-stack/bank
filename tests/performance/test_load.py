import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

class TestPerformance:
    """Performance tests for the application"""

    def test_concurrent_chat_requests(self, client, valid_token):
        """Test handling multiple concurrent chat requests"""
        def make_chat_request():
            headers = {"Authorization": f"Bearer {valid_token}"}
            chat_data = {"message": "Test message"}
            return client.post("/chat", json=chat_data, headers=headers)
        
        # Make 10 concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            start_time = time.time()
            futures = [executor.submit(make_chat_request) for _ in range(10)]
            responses = [future.result() for future in futures]
            end_time = time.time()
        
        # All requests should succeed
        success_count = sum(1 for response in responses if response.status_code == 200)
        assert success_count == 10
        
        # Should complete within reasonable time (adjust threshold as needed)
        assert end_time - start_time < 10  # 10 seconds threshold

    def test_database_query_performance(self, mock_mongo_client, sample_users):
        """Test database query performance"""
        # Insert many users
        with patch('database.users_collection', mock_mongo_client.users), \
             patch('database.mongo_connected', True):
            
            # Insert 100 test users
            test_users = []
            for i in range(100):
                user = {
                    "user_id": f"user_{i}",
                    "email": f"user{i}@example.com",
                    "name": f"User {i}",
                    "role": "user"
                }
                test_users.append(user)
            
            mock_mongo_client.users.insert_many(test_users)
            
            # Measure query time
            start_time = time.time()
            from database import get_all_users
            users = get_all_users()
            end_time = time.time()
            
            assert len(users) == 100
            assert end_time - start_time < 1  # Should complete within 1 second
