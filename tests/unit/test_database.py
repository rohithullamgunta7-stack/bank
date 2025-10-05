import pytest
from unittest.mock import patch, MagicMock
from database import (
    get_or_create_user, get_user_by_id, save_message, 
    load_chat_history, get_system_statistics
)
from datetime import datetime, timezone

class TestDatabaseFunctions:
    """Unit tests for database functions"""

    @patch('database.mongo_connected', True)
    @patch('database.users_collection')
    def test_get_or_create_user_existing(self, mock_collection):
        """Test getting an existing user"""
        existing_user = {
            "user_id": "user_123",
            "email": "test@example.com",
            "name": "Test User",
            "role": "user"
        }
        mock_collection.find_one.return_value = existing_user
        
        result = get_or_create_user("test@example.com", "Test User")
        
        assert result == existing_user
        mock_collection.find_one.assert_called_once_with({"email": "test@example.com"})

    @patch('database.mongo_connected', True)
    @patch('database.users_collection')
    def test_get_or_create_user_new(self, mock_collection):
        """Test creating a new user"""
        mock_collection.find_one.return_value = None
        mock_collection.insert_one.return_value = MagicMock()
        
        result = get_or_create_user("new@example.com", "New User")
        
        assert result["email"] == "new@example.com"
        assert result["name"] == "New User"
        assert result["role"] == "user"
        assert "user_id" in result
        mock_collection.insert_one.assert_called_once()

    @patch('database.mongo_connected', False)
    def test_get_or_create_user_no_connection(self):
        """Test fallback when database not connected"""
        result = get_or_create_user("test@example.com")
        
        assert result["user_id"] == "local_user"
        assert result["name"] == "Guest"
        assert result["role"] == "user"

    @patch('database.mongo_connected', True)
    @patch('database.messages_collection')
    def test_save_message(self, mock_collection):
        """Test saving a message"""
        mock_collection.insert_one.return_value = MagicMock()
        
        save_message("user_123", "Hello", "Hi there!")
        
        mock_collection.insert_one.assert_called_once()
        call_args = mock_collection.insert_one.call_args[0][0]
        assert call_args["user_id"] == "user_123"
        assert call_args["user"] == "Hello"
        assert call_args["bot"] == "Hi there!"

    @patch('database.mongo_connected', True)
    @patch('database.messages_collection')
    def test_load_chat_history(self, mock_collection):
        """Test loading chat history"""
        mock_messages = [
            {
                "user": "Hello",
                "bot": "Hi there!",
                "timestamp": datetime.now(timezone.utc)
            }
        ]
        mock_collection.find.return_value.sort.return_value = mock_messages
        
        result = load_chat_history("user_123")
        
        assert len(result) == 2  # One user message + one bot message
        assert result[0]["role"] == "user"
        assert result[0]["content"] == "Hello"
        assert result[1]["role"] == "assistant"
        assert result[1]["content"] == "Hi there!"