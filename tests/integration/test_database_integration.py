import pytest
from unittest.mock import patch, MagicMock
from database import (
    get_or_create_user, save_message, load_chat_history,
    get_conversation_summaries, get_system_statistics
)

class TestDatabaseIntegration:
    """Integration tests for database operations"""

    @patch('database.mongo_connected', True)
    def test_user_conversation_flow(self, mock_mongo_client):
        """Test complete user and conversation flow"""
        with patch('database.users_collection', mock_mongo_client.users), \
             patch('database.messages_collection', mock_mongo_client.messages):
            
            # Create user
            user = get_or_create_user("integration@example.com", "Integration User")
            assert user["email"] == "integration@example.com"
            
            # Save messages
            save_message(user["user_id"], "Hello", "Hi there!")
            save_message(user["user_id"], "How are you?", "I'm doing well!")
            
            # Load history
            history = load_chat_history(user["user_id"])
            assert len(history) == 4  # 2 exchanges = 4 messages
            
            # Check conversation summaries
            summaries = get_conversation_summaries("admin")
            assert len(summaries) >= 1
