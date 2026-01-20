"""
Unit tests for FastAPI dependencies
"""
import pytest
from fastapi import HTTPException
from backend_api.dependencies import get_current_user
from backend_api.tests.test_auth import create_valid_init_data
import os


@pytest.mark.asyncio
async def test_get_current_user_valid():
    """Test get_current_user with valid initData"""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN', 'test_token_123')
    
    user_data = {
        'id': 12345,
        'username': 'testuser',
        'first_name': 'Test'
    }
    
    init_data = create_valid_init_data(user_data, bot_token)
    
    result = await get_current_user(x_telegram_init_data=init_data)
    
    assert result['user_id'] == 12345
    assert result['username'] == 'testuser'


@pytest.mark.asyncio
async def test_get_current_user_missing_header():
    """Test get_current_user without initData header"""
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(x_telegram_init_data=None)
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail['error_code'] == 'MISSING_INIT_DATA'


@pytest.mark.asyncio
async def test_get_current_user_invalid_signature():
    """Test get_current_user with invalid signature"""
    invalid_init_data = "user=%7B%22id%22%3A12345%7D&hash=invalid"
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(x_telegram_init_data=invalid_init_data)
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail['error_code'] == 'INVALID_INITDATA'


@pytest.mark.asyncio
async def test_get_current_user_missing_user_id():
    """Test get_current_user with missing user_id"""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN', 'test_token_123')
    
    # Create initData without user_id
    user_data = {
        'username': 'testuser'
    }
    
    init_data = create_valid_init_data(user_data, bot_token)
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(x_telegram_init_data=init_data)
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail['error_code'] == 'INVALID_USER_ID'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
