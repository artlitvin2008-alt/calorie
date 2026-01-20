"""
Authentication router
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging

from backend_api.dependencies import validate_init_data

logger = logging.getLogger(__name__)

router = APIRouter()


class InitDataRequest(BaseModel):
    init_data: str


class AuthResponse(BaseModel):
    user_id: int
    username: str | None
    first_name: str | None
    valid: bool


@router.post("/verify", response_model=AuthResponse)
async def verify_init_data(request: InitDataRequest):
    """
    Verify Telegram WebApp initData
    
    This endpoint validates the initData signature and returns user information.
    Used for testing authentication from the frontend.
    """
    try:
        user_data = validate_init_data(request.init_data)
        
        return AuthResponse(
            user_id=user_data['user_id'],
            username=user_data.get('username'),
            first_name=user_data.get('first_name'),
            valid=True
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=401,
            detail={
                "error_code": "INVALID_INITDATA",
                "message": str(e)
            }
        )
