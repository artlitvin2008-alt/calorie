"""
Utility functions for Backend API
"""
import uuid
import os
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def generate_unique_filename(original_filename: str, prefix: str = "") -> str:
    """
    Generate unique filename for uploaded files
    
    Args:
        original_filename: Original filename with extension
        prefix: Optional prefix for filename
        
    Returns:
        Unique filename
    """
    # Extract extension
    _, ext = os.path.splitext(original_filename)
    
    # Generate unique ID
    unique_id = uuid.uuid4().hex[:12]
    
    # Create timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Combine parts
    if prefix:
        filename = f"{prefix}_{timestamp}_{unique_id}{ext}"
    else:
        filename = f"{timestamp}_{unique_id}{ext}"
    
    return filename


def calculate_date_range(period: str) -> tuple[datetime, datetime]:
    """
    Calculate date range based on period
    
    Args:
        period: "week", "month", or "year"
        
    Returns:
        Tuple of (start_date, end_date)
    """
    end_date = datetime.now()
    
    if period == "week":
        start_date = end_date - timedelta(days=7)
    elif period == "month":
        start_date = end_date - timedelta(days=30)
    elif period == "year":
        start_date = end_date - timedelta(days=365)
    else:
        raise ValueError(f"Invalid period: {period}")
    
    return start_date, end_date


def calculate_progress_percentage(consumed: float, goal: float) -> float:
    """
    Calculate progress percentage
    
    Args:
        consumed: Amount consumed
        goal: Goal amount
        
    Returns:
        Progress percentage (0-100+)
    """
    if goal <= 0:
        return 0.0
    
    return round((consumed / goal) * 100, 1)


def calculate_macros_from_ingredients(ingredients: list) -> dict:
    """
    Calculate total macros from list of ingredients
    
    Args:
        ingredients: List of ingredient dictionaries
        
    Returns:
        Dictionary with total calories, protein, fats, carbs
    """
    total_calories = sum(ing.get('calories', 0) for ing in ingredients)
    total_protein = sum(ing.get('protein', 0) for ing in ingredients)
    total_fats = sum(ing.get('fats', 0) for ing in ingredients)
    total_carbs = sum(ing.get('carbs', 0) for ing in ingredients)
    
    return {
        'calories': round(total_calories, 1),
        'protein': round(total_protein, 1),
        'fats': round(total_fats, 1),
        'carbs': round(total_carbs, 1)
    }


def validate_nutrition_data(calories: float, protein: float, fats: float, carbs: float) -> bool:
    """
    Validate nutrition data consistency
    
    Args:
        calories: Total calories
        protein: Protein in grams
        fats: Fats in grams
        carbs: Carbs in grams
        
    Returns:
        True if data is consistent, False otherwise
    """
    # Calculate calories from macros (protein: 4 kcal/g, fats: 9 kcal/g, carbs: 4 kcal/g)
    calculated_calories = (protein * 4) + (fats * 9) + (carbs * 4)
    
    # Allow 10% tolerance
    tolerance = 0.10
    lower_bound = calculated_calories * (1 - tolerance)
    upper_bound = calculated_calories * (1 + tolerance)
    
    is_valid = lower_bound <= calories <= upper_bound
    
    if not is_valid:
        logger.warning(
            f"Nutrition data inconsistency: "
            f"Calories={calories}, Calculated={calculated_calories:.1f} "
            f"(P:{protein}g, F:{fats}g, C:{carbs}g)"
        )
    
    return is_valid


def format_date_for_db(date: Optional[datetime] = None) -> str:
    """
    Format date for database storage
    
    Args:
        date: Date to format (defaults to now)
        
    Returns:
        Formatted date string (YYYY-MM-DD)
    """
    if date is None:
        date = datetime.now()
    
    return date.strftime("%Y-%m-%d")


def parse_date_from_string(date_str: str) -> datetime:
    """
    Parse date from string
    
    Args:
        date_str: Date string in YYYY-MM-DD format
        
    Returns:
        Datetime object
        
    Raises:
        ValueError: If date format is invalid
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}. Expected YYYY-MM-DD")
