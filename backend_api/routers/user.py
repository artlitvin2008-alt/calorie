"""
User management router
"""
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, date
import logging

from backend_api.dependencies import get_current_user
from backend_api.models import (
    UserProfile, UserProfileUpdate, DailyStats,
    MacroNutrients, UserGoals
)
from backend_api.utils import calculate_progress_percentage, format_date_for_db
from core.database import Database

logger = logging.getLogger(__name__)

router = APIRouter()
db = Database()


@router.get("/profile", response_model=UserProfile)
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """
    Get user profile
    
    Returns complete user profile including goals, physical stats, and preferences.
    """
    user_id = current_user['user_id']
    
    # Get user from database
    user = await db.get_user(user_id)
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail={
                "error_code": "USER_NOT_FOUND",
                "message": f"User {user_id} not found"
            }
        )
    
    # Parse goals from JSON string if needed
    import json
    goals_data = user.get('goals')
    if isinstance(goals_data, str):
        goals_data = json.loads(goals_data)
    
    # Build goals object
    goals = UserGoals(
        calories=user.get('daily_calories', 2000),
        protein=user.get('protein_goal', 150),
        fats=user.get('fat_goal', 65),
        carbs=user.get('carbs_goal', 250)
    )
    
    return UserProfile(
        telegram_id=user['user_id'],
        username=user.get('username'),
        first_name=user.get('first_name'),
        goals=goals,
        height=user.get('height'),
        weight=user.get('current_weight'),
        age=user.get('age'),
        gender=user.get('gender'),
        notifications_enabled=user.get('notifications_enabled', True)
    )


@router.patch("/profile", response_model=UserProfile)
async def update_user_profile(
    profile_update: UserProfileUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update user profile
    
    Updates user profile fields. Only provided fields will be updated.
    Validates data ranges before updating.
    """
    user_id = current_user['user_id']
    
    # Build update dictionary
    update_data = {}
    
    if profile_update.goals:
        update_data['daily_calories'] = profile_update.goals.calories
        update_data['protein_goal'] = profile_update.goals.protein
        update_data['fat_goal'] = profile_update.goals.fats
        update_data['carbs_goal'] = profile_update.goals.carbs
    
    if profile_update.height is not None:
        update_data['height'] = profile_update.height
    
    if profile_update.weight is not None:
        update_data['current_weight'] = profile_update.weight
    
    if profile_update.age is not None:
        update_data['age'] = profile_update.age
    
    if profile_update.gender is not None:
        update_data['gender'] = profile_update.gender.value
    
    if profile_update.notifications_enabled is not None:
        update_data['notifications_enabled'] = profile_update.notifications_enabled
    
    # Update user
    if update_data:
        await db.update_user(user_id, **update_data)
    
    # Return updated profile
    return await get_user_profile(current_user)


@router.get("/stats/today", response_model=DailyStats)
async def get_today_stats(current_user: dict = Depends(get_current_user)):
    """
    Get today's nutrition statistics
    
    Returns consumed calories and macros, goals, and progress percentages.
    """
    user_id = current_user['user_id']
    
    # Get user for goals
    user = await db.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail={
                "error_code": "USER_NOT_FOUND",
                "message": f"User {user_id} not found"
            }
        )
    
    # Get today's meals
    meals = await db.get_meals_today(user_id)
    
    # Calculate consumed totals
    total_calories = sum(meal.get('total_calories', 0) for meal in meals)
    total_protein = sum(meal.get('protein_g', 0) for meal in meals)
    total_fats = sum(meal.get('fat_g', 0) for meal in meals)
    total_carbs = sum(meal.get('carbs_g', 0) for meal in meals)
    
    # Get goals
    goal_calories = user.get('daily_calories', 2000)
    goal_protein = user.get('protein_goal', 150)
    goal_fats = user.get('fat_goal', 65)
    goal_carbs = user.get('carbs_goal', 250)
    
    # Calculate progress
    progress = {
        'calories': calculate_progress_percentage(total_calories, goal_calories),
        'protein': calculate_progress_percentage(total_protein, goal_protein),
        'fats': calculate_progress_percentage(total_fats, goal_fats),
        'carbs': calculate_progress_percentage(total_carbs, goal_carbs)
    }
    
    return DailyStats(
        date=format_date_for_db(),
        consumed=MacroNutrients(
            calories=total_calories,
            protein=total_protein,
            fats=total_fats,
            carbs=total_carbs
        ),
        goals=MacroNutrients(
            calories=goal_calories,
            protein=goal_protein,
            fats=goal_fats,
            carbs=goal_carbs
        ),
        progress=progress,
        meals_count=len(meals)
    )
