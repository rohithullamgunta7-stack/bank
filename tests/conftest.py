# tests/conftest.py
import sys
import os
import pytest

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
sys.path.insert(0, backend_path)

@pytest.fixture
def mock_database():
    """Mock database fixture for testing"""
    # Add your database mocking logic here
    pass

@pytest.fixture
def sample_user():
    """Sample user data for testing"""
    return {
        "id": "test_user_123",
        "email": "test@example.com",
        "username": "testuser",
        "role": "user"
    }

@pytest.fixture
def auth_token():
    """Mock JWT token for testing"""
    return "mock_jwt_token_for_testing"