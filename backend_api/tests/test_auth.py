"""
Unit tests for authentication
"""
import pytest
import hmac
import hashlib
import json
from urllib.parse import urlencode

from backend_api.dependencies import validate_init_data


def create_valid_init_data(user_data: dict, bot_token: str) -> str:
    """
    Helper function to create valid initData for testing
    
    Args:
        user_data: User data dictionary
        bot_token: Bot token for signature
        
    Returns:
        Valid initData string
    """
    # Create data check string
    data = {
        'user': json.dumps(user_data),
        'auth_date': '1234567890',
        'query_id': 'test_query_id'
    }
    
    # Sort keys and create data check string
    data_check_string = '\n'.join(f"{k}={v}" for k, v in sorted(data.items()))
    
    # Calculate secret key
    secret_key = hmac.new(
        b"WebAppData",
        bot_token.encode(),
        hashlib.sha256
    ).digest()
    
    # Calculate hash
    hash_value = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # Add hash to data
    data['hash'] = hash_value
    
    # Return as query string
    return urlencode(data)


def test_validate_init_data_valid():
    """Test validation with valid initData"""
    import os
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN', 'test_token_123')
    
    user_data = {
        'id': 12345,
        'username': 'testuser',
        'first_name': 'Test',
        'last_name': 'User',
        'language_code': 'en'
    }
    
    init_data = create_valid_init_data(user_data, bot_token)
    
    result = validate_init_data(init_data)
    
    assert result['user_id'] == 12345
    assert result['username'] == 'testuser'
    assert result['first_name'] == 'Test'
    assert result['last_name'] == 'User'


def test_validate_init_data_invalid_signature():
    """Test validation with invalid signature"""
    init_data = urlencode({
        'user': json.dumps({'id': 12345}),
        'auth_date': '1234567890',
        'hash': 'invalid_hash'
    })
    
    with pytest.raises(ValueError, match="Invalid signature"):
        validate_init_data(init_data)


def test_validate_init_data_missing_hash():
    """Test validation with missing hash"""
    init_data = urlencode({
        'user': json.dumps({'id': 12345}),
        'auth_date': '1234567890'
    })
    
    with pytest.raises(ValueError, match="No hash in initData"):
        validate_init_data(init_data)


def test_validate_init_data_empty():
    """Test validation with empty initData"""
    with pytest.raises(ValueError):
        validate_init_data("")


def test_validate_init_data_malformed():
    """Test validation with malformed initData"""
    with pytest.raises(ValueError):
        validate_init_data("not_a_valid_query_string")


def test_validate_init_data_missing_user():
    """Test validation with missing user data"""
    import os
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN', 'test_token_123')
    
    # Create valid signature but without user data
    data = {
        'auth_date': '1234567890',
        'query_id': 'test_query_id'
    }
    
    data_check_string = '\n'.join(f"{k}={v}" for k, v in sorted(data.items()))
    
    secret_key = hmac.new(
        b"WebAppData",
        bot_token.encode(),
        hashlib.sha256
    ).digest()
    
    hash_value = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()
    
    data['hash'] = hash_value
    init_data = urlencode(data)
    
    # Should not raise error but user_id will be None
    result = validate_init_data(init_data)
    assert result['user_id'] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
