import pytest
from unittest.mock import patch, MagicMock
from chat import get_bot_reply, get_role_specific_greeting

class TestChatFunctions:
    """Unit tests for chat functions"""

    @patch('chat.save_message')
    @patch('chat.get_user_by_id')
    @patch('chat.load_chat_history')
    @patch('chat.model')
    def test_get_bot_reply_first_message(self, mock_model, mock_history, mock_user, mock_save):
        """Test bot reply for first message"""
        # Setup mocks
        mock_user.return_value = {"name": "Test User", "role": "user"}
        mock_history.return_value = []
        
        mock_response = MagicMock()
        mock_response.text = "Hello Test User! How can I help you?"
        mock_model.generate_content.return_value = mock_response
        
        # Test
        result = get_bot_reply("user_123", "Hello", "user")
        
        # Assertions
        assert isinstance(result, str)
        assert "Test User" in result
        mock_save.assert_called_once()
        mock_model.generate_content.assert_called_once()

    @patch('chat.save_message')
    @patch('chat.get_user_by_id')
    @patch('chat.load_chat_history')
    @patch('chat.model')
    def test_get_bot_reply_with_history(self, mock_model, mock_history, mock_user, mock_save):
        """Test bot reply with conversation history"""
        # Setup mocks
        mock_user.return_value = {"name": "Test User", "role": "user"}
        mock_history.return_value = [
            {"role": "user", "content": "Previous message"},
            {"role": "assistant", "content": "Previous response"}
        ]
        
        mock_response = MagicMock()
        mock_response.text = "Based on our previous conversation..."
        mock_model.generate_content.return_value = mock_response
        
        # Test
        result = get_bot_reply("user_123", "Follow up question", "user")
        
        # Assertions
        assert isinstance(result, str)
        mock_model.generate_content.assert_called_once()
        
        # Verify context includes history
        call_args = mock_model.generate_content.call_args[0][0]
        assert "Previous conversation:" in call_args

    @patch('chat.save_message')
    @patch('chat.get_user_by_id')
    @patch('chat.load_chat_history')
    @patch('chat.model')
    def test_get_bot_reply_model_error(self, mock_model, mock_history, mock_user, mock_save):
        """Test bot reply when model throws error"""
        # Setup mocks
        mock_user.return_value = {"name": "Test User", "role": "user"}
        mock_history.return_value = []
        mock_model.generate_content.side_effect = Exception("API Error")
        
        # Test
        result = get_bot_reply("user_123", "Hello", "user")
        
        # Assertions
        assert isinstance(result, str)
        assert "experiencing technical difficulties" in result.lower()
        mock_save.assert_called_once()

    def test_get_role_specific_greeting_user(self):
        """Test role-specific greeting for regular user"""
        result = get_role_specific_greeting("John", "user")
        assert "John" in result
        assert "customer support assistant" in result

    def test_get_role_specific_greeting_admin(self):
        """Test role-specific greeting for admin"""
        result = get_role_specific_greeting("Admin User", "admin")
        assert "Admin User" in result
        assert "admin dashboard" in result.lower()

    def test_get_role_specific_greeting_support(self):
        """Test role-specific greeting for support agent"""
        result = get_role_specific_greeting("Support Agent", "customer_support_agent")
        assert "Support Agent" in result
        assert "support case" in result.lower()