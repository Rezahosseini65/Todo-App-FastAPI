import pytest
from datetime import datetime, timedelta
import jwt
from app.auths.jwt_auth import generate_access_token, verify_access_token, refresh_access_token, generate_refresh_token
from app.core.config import settings


@pytest.mark.usefixtures("setup_database", "override_dependency")
class TestJWTAuth:
    
    def test_generate_and_verify_access_token(self):
        """Test generating and verifying a valid access token"""
        user_data = {"user_id": 123}
        token = generate_access_token(user_data)
        
        payload = verify_access_token(token, "access")
        assert payload is not None
        assert payload["user_id"] == 123
        assert payload["type"] == "access"
        assert "exp" in payload

    def test_expired_access_token(self):
        """Test that expired token returns None"""
        # Create an expired token manually with proper timestamp
        expired_data = {
            "user_id": 999,
            "type": "access",
            "exp": datetime.now() - timedelta(minutes=10)  # Expired 10 minutes ago
        }
        # Convert datetime to timestamp (seconds since epoch)
        expired_data["exp"] = int(expired_data["exp"].timestamp())
        
        expired_token = jwt.encode(expired_data, settings.SECRET_KEY, algorithm="HS256")
        
        payload = verify_access_token(expired_token, "access")
        assert payload is None  # This should be None for expired tokens

    def test_invalid_token_type(self):
        """Test that wrong token type returns None"""
        user_data = {"user_id": 123}
        token = generate_access_token(user_data)
        
        # Try to verify access token as refresh token
        payload = verify_access_token(token, "refresh")
        assert payload is None

    def test_refresh_token_flow(self):
        """Test refresh token generation and access token refresh"""
        user_data = {"user_id": 456}
        refresh_token = generate_refresh_token(user_data)
        
        # Verify refresh token
        refresh_payload = verify_access_token(refresh_token, "refresh")
        assert refresh_payload is not None
        assert refresh_payload["user_id"] == 456
        assert refresh_payload["type"] == "refresh"
        
        # Refresh access token
        new_access_token = refresh_access_token(refresh_token)
        assert new_access_token is not None
        
        # Verify new access token
        access_payload = verify_access_token(new_access_token, "access")
        assert access_payload is not None
        assert access_payload["user_id"] == 456
        assert access_payload["type"] == "access"