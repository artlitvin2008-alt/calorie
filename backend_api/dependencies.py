"""
Authentication and dependency injection for FastAPI
"""
import hmac
import hashlib
import json
from urllib.parse import parse_qs
from typing import Optional
from fastapi import Header, HTTPException, Depends
import os
import logging

logger = logging.getLogger(__name__)

# Get bot token from environment
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not found in environment")


def validate_init_data(init_data: str) -> dict:
    """
    Validate Telegram WebApp initData signature
    
    Args:
        init_data: Raw initData string from Telegram WebApp
        
    Returns:
        Parsed and validated user data
        
    Raises:
        ValueError: If signature is invalid
    """
    try:
        # Parse query string
        parsed = parse_qs(init_data)
        
        # Extract hash
        received_hash = parsed.get('hash', [None])[0]
        if not received_hash:
            raise ValueError("No hash in initData")
        
        # Remove hash from data for validation
        data_check_string_parts = []
        for key in sorted(parsed.keys()):
            if key == 'hash':
                continue
            value = parsed[key][0]
            data_check_string_parts.append(f"{key}={value}")
        
        data_check_string = '\n'.join(data_check_string_parts)
        
        # Calculate secret key
        secret_key = hmac.new(
            b"WebAppData",
            BOT_TOKEN.encode(),
            hashlib.sha256
        ).digest()
        
        # Calculate hash
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Verify hash
        if not hmac.compare_digest(calculated_hash, received_hash):
            raise ValueError("Invalid signature")
        
        # Parse user data
        user_data = json.loads(parsed.get('user', ['{}'])[0])
        
        return {
            'user_id': user_data.get('id'),
            'username': user_data.get('username'),
            'first_name': user_data.get('first_name'),
            'last_name': user_data.get('last_name'),
            'language_code': user_data.get('language_code'),
            'auth_date': parsed.get('auth_date', [None])[0],
            'query_id': parsed.get('query_id', [None])[0]
        }
        
    except Exception as e:
        logger.error(f"Failed to validate initData: {e}")
        raise ValueError(f"Invalid initData: {str(e)}")


async def get_current_user(
    x_telegram_init_data: Optional[str] = Header(None, alias="X-Telegram-Init-Data")
) -> dict:
    """
    Dependency to get current authenticated user from Telegram WebApp initData
    
    Args:
        x_telegram_init_data: initData from request header
        
    Returns:
        User data dictionary
        
    Raises:
        HTTPException: If authentication fails
    """
    if not x_telegram_init_data:
        raise HTTPException(
            status_code=401,
            detail={
                "error_code": "MISSING_INIT_DATA",
                "message": "X-Telegram-Init-Data header is required"
            }
        )
    
    try:
        user_data = validate_init_data(x_telegram_init_data)
        
        if not user_data.get('user_id'):
            raise HTTPException(
                status_code=401,
                detail={
                    "error_code": "INVALID_USER_ID",
                    "message": "User ID not found in initData"
                }
            )
        
        return user_data
        
    except ValueError as e:
        raise HTTPException(
            status_code=401,
            detail={
                "error_code": "INVALID_INITDATA",
                "message": str(e)
            }
        )


# Optional: Dependency for internal bot requests (without initData validation)
async def get_user_from_token(
    x_bot_token: Optional[str] = Header(None, alias="X-Bot-Token")
) -> dict:
    """
    Dependency for internal bot requests
    
    Args:
        x_bot_token: Bot token from request header
        
    Returns:
        User data dictionary
        
    Raises:
        HTTPException: If authentication fails
    """
    if not x_bot_token:
        raise HTTPException(
            status_code=401,
            detail={
                "error_code": "MISSING_BOT_TOKEN",
                "message": "X-Bot-Token header is required"
            }
        )
    
    if x_bot_token != BOT_TOKEN:
        raise HTTPException(
            status_code=401,
            detail={
                "error_code": "INVALID_BOT_TOKEN",
                "message": "Invalid bot token"
            }
        )
    
    # For internal requests, user_id should be in another header
    return {"internal": True}
