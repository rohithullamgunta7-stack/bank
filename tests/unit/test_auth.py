import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from auth import (
    hash_password, verify_password, create_access_token, 
    verify_token, get_current_user
)
from datetime import datetime, timedelta
import jwt

class TestAuthFunctions:
    """Unit tests for authentication functions"""

    def test_hash_password(self):
        """Test password hashing"""
        password = "test_password"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 20  # bcrypt hashes are long
        assert hashed.startswith("$2b$")

    def test_verify_password(self):
        """Test password verification"""
        password = "test_password"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) == True
        assert verify_password("wrong_password", hashed) == False

    def test_create_access_token(self):
        """Test JWT token creation"""
        data = {"sub": "test@example.com", "role": "user"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 50  # JWT tokens are long
        
        # Verify token can be decoded
        from config import SECRET_KEY, ALGORITHM
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == "test@example.com"
        assert decoded["role"] == "user"
        assert "exp" in decoded

    def test_verify_token_valid(self):
        """Test token verification with valid token"""
        data = {"sub": "test@example.com", "name": "Test", "role": "user"}
        token = create_access_token(data)
        
        result = verify_token(token)
        assert result["email"] == "test@example.com"
        assert result["name"] == "Test"
        assert result["role"] == "user"

    def test_verify_token_invalid(self):
        """Test token verification with invalid token"""
        invalid_token = "invalid.token.here"
        result = verify_token(invalid_token)
        assert result is None

    def test_verify_token_expired(self):
        """Test token verification with expired token"""
        # Create token that expires immediately
        data = {"sub": "test@example.com"}
        expire = datetime.utcnow() - timedelta(minutes=1)  # Already expired
        data.update({"exp": expire})
        
        from config import SECRET_KEY, ALGORITHM
        expired_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
        
        result = verify_token(expired_token)
        assert result is None

    def test_get_current_user_no_header(self):
        """Test get_current_user with no authorization header"""
        with pytest.raises(HTTPException) as exc_info:
            # Call the function directly with None authorization
            get_current_user(authorization=None)
        
        assert exc_info.value.status_code == 401
        assert "Authorization header required" in str(exc_info.value.detail)

    def test_get_current_user_invalid_format(self):
        """Test get_current_user with invalid header format"""
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(authorization="InvalidFormat")
        
        assert exc_info.value.status_code == 401

    def test_get_current_user_invalid_token(self):
        """Test get_current_user with invalid token"""
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(authorization="Bearer invalid_token")
        
        assert exc_info.value.status_code == 401
        assert "Invalid or expired token" in str(exc_info.value.detail)

    def test_get_current_user_valid_token(self):
        """Test get_current_user with valid token"""
        # Create a valid token first
        data = {"sub": "test@example.com", "name": "Test User", "role": "user"}
        valid_token = create_access_token(data)
        
        result = get_current_user(authorization=f"Bearer {valid_token}")
        
        assert result["email"] == "test@example.com"
        assert result["name"] == "Test User"
        assert result["role"] == "user"