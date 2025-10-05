import pytest
from unittest.mock import patch, MagicMock
import google.generativeai as genai

class TestExternalServiceMocks:
    """Tests for mocking external services"""

    @patch('google.generativeai.GenerativeModel')
    def test_gemini_api_mock(self, mock_model_class):
        """Test mocking Gemini API"""
        # Setup mock
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Mocked Gemini response"
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        # Test
        from config import model
        result = model.generate_content("Test prompt")
        
        assert result.text == "Mocked Gemini response"
        mock_model.generate_content.assert_called_with("Test prompt")

    @patch('pymongo.MongoClient')
    def test_mongodb_mock(self, mock_mongo_client):
        """Test mocking MongoDB operations"""
        # Setup mock
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_db.users = mock_collection
        mock_mongo_client.return_value.get_database.return_value = mock_db
        
        # Test find operation
        mock_collection.find_one.return_value = {"email": "test@example.com"}
        
        from database import get_user_by_email
        with patch('database.users_collection', mock_collection):
            user = get_user_by_email("test@example.com")
        
        assert user["email"] == "test@example.com"
        mock_collection.find_one.assert_called_once()

    @patch('smtplib.SMTP')
    def test_email_service_mock(self, mock_smtp):
        """Test mocking email service (if you add email functionality)"""
        # Setup mock
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # This would test email sending functionality
        # (Add this if you implement email notifications)
        mock_server.send_message.return_value = {}
        
        # Test would go here
        assert mock_server.send_message.call_count == 0  # Not called yet
