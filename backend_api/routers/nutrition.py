"""
Nutrition management router
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from datetime import datetime
import os
import json
import logging
from typing import List, Optional

from backend_api.dependencies import get_current_user
from backend_api.models import (
    AnalysisResult, MealCreate, MealUpdate, Meal,
    Ingredient, MacroNutrients
)
from backend_api.utils import (
    generate_unique_filename,
    calculate_macros_from_ingredients,
    parse_date_from_string,
    format_date_for_db
)
from core.database import Database
from modules.nutrition.photo_analyzer import PhotoAnalyzer
from modules.video_analysis.video_analyzer import VideoAnalyzer

logger = logging.getLogger(__name__)

router = APIRouter()
db = Database()

# Initialize analyzers
photo_analyzer = PhotoAnalyzer()
video_analyzer = VideoAnalyzer()


@router.post("/analyze-photo", response_model=AnalysisResult)
async def analyze_photo(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze food photo using AI
    
    Accepts an image file, saves it, and returns nutrition analysis.
    """
    user_id = current_user['user_id']
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail={
                "error_code": "INVALID_FILE_TYPE",
                "message": "File must be an image"
            }
        )
    
    try:
        # Generate unique filename
        filename = generate_unique_filename(file.filename, prefix=f"user_{user_id}")
        file_path = os.path.join("uploads", filename)
        
        # Save file
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        logger.info(f"Photo saved: {file_path}")
        
        # Analyze photo
        analysis = await photo_analyzer.analyze(content)
        
        # Parse analysis result
        if isinstance(analysis, str):
            analysis = json.loads(analysis)
        
        # Build ingredients list
        ingredients = []
        for component in analysis.get('components', []):
            ingredients.append(Ingredient(
                name=component.get('name', 'Unknown'),
                weight=component.get('weight_g', 0),
                calories=component.get('calories', 0),
                protein=component.get('protein_g', 0),
                fats=component.get('fat_g', 0),
                carbs=component.get('carbs_g', 0),
                confidence=component.get('confidence', 0.5)
            ))
        
        # Calculate total nutrition
        nutrition = MacroNutrients(
            calories=analysis.get('calories_total', 0),
            protein=analysis.get('protein_g', 0),
            fats=analysis.get('fat_g', 0),
            carbs=analysis.get('carbs_g', 0)
        )
        
        return AnalysisResult(
            ingredients=ingredients,
            nutrition=nutrition,
            photo_path=file_path,
            dish_name=analysis.get('dish_name'),
            health_score=analysis.get('health_score'),
            detailed_analysis=analysis.get('detailed_analysis'),
            recommendations=analysis.get('recommendations')
        )
        
    except Exception as e:
        logger.error(f"Photo analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "ANALYSIS_FAILED",
                "message": f"Failed to analyze photo: {str(e)}"
            }
        )


@router.post("/analyze-video", response_model=AnalysisResult)
async def analyze_video(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze food video using AI
    
    Accepts a video file, saves it, and returns nutrition analysis.
    """
    user_id = current_user['user_id']
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith('video/'):
        raise HTTPException(
            status_code=400,
            detail={
                "error_code": "INVALID_FILE_TYPE",
                "message": "File must be a video"
            }
        )
    
    try:
        # Generate unique filename
        filename = generate_unique_filename(file.filename, prefix=f"user_{user_id}_video")
        file_path = os.path.join("uploads", filename)
        
        # Save file
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        logger.info(f"Video saved: {file_path}")
        
        # Analyze video
        analysis = await video_analyzer.analyze(file_path)
        
        # Parse analysis result (same structure as photo)
        if isinstance(analysis, str):
            analysis = json.loads(analysis)
        
        # Build ingredients list
        ingredients = []
        for component in analysis.get('components', []):
            ingredients.append(Ingredient(
                name=component.get('name', 'Unknown'),
                weight=component.get('weight_g', 0),
                calories=component.get('calories', 0),
                protein=component.get('protein_g', 0),
                fats=component.get('fat_g', 0),
                carbs=component.get('carbs_g', 0),
                confidence=component.get('confidence', 0.5)
            ))
        
        # Calculate total nutrition
        nutrition = MacroNutrients(
            calories=analysis.get('calories_total', 0),
            protein=analysis.get('protein_g', 0),
            fats=analysis.get('fat_g', 0),
            carbs=analysis.get('carbs_g', 0)
        )
        
        return AnalysisResult(
            ingredients=ingredients,
            nutrition=nutrition,
            photo_path=file_path,  # Store video path in photo_path field
            dish_name=analysis.get('dish_name'),
            health_score=analysis.get('health_score'),
            detailed_analysis=analysis.get('detailed_analysis'),
            recommendations=analysis.get('recommendations')
        )
        
    except Exception as e:
        logger.error(f"Video analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "ANALYSIS_FAILED",
                "message": f"Failed to analyze video: {str(e)}"
            }
        )


@router.post("/meals", response_model=Meal)
async def create_meal(
    meal_data: MealCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new meal record
    
    Saves meal with ingredients and nutrition information.
    """
    user_id = current_user['user_id']
    
    try:
        # Calculate total nutrition from ingredients
        ingredients_list = [ing.dict() for ing in meal_data.ingredients]
        totals = calculate_macros_from_ingredients(ingredients_list)
        
        # Calculate average confidence
        confidences = [ing.confidence for ing in meal_data.ingredients if ing.confidence]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5
        
        # Prepare meal data for database
        meal_db_data = {
            'user_id': user_id,
            'session_id': f"meal_{user_id}_{datetime.now().timestamp()}",
            'dish_name': meal_data.dish_name or "Meal",
            'meal_type': meal_data.meal_time.value,
            'photo_file_id': meal_data.photo_path,
            'components': json.dumps(ingredients_list, ensure_ascii=False),
            'total_weight': sum(ing.weight for ing in meal_data.ingredients),
            'total_calories': int(totals['calories']),
            'protein_g': int(totals['protein']),
            'fat_g': int(totals['fats']),
            'carbs_g': int(totals['carbs']),
            'health_score': 7,  # Default score
            'confidence_avg': avg_confidence,
            'corrections_count': 0,
            'eaten_at': datetime.now()
        }
        
        # Save meal
        meal_id = await db.save_meal(meal_db_data)
        
        # Return created meal
        return Meal(
            id=meal_id,
            user_id=user_id,
            meal_time=meal_data.meal_time,
            photo_path=meal_data.photo_path,
            video_path=meal_data.video_path,
            ingredients=meal_data.ingredients,
            calories=totals['calories'],
            protein=totals['protein'],
            fats=totals['fats'],
            carbs=totals['carbs'],
            created_at=datetime.now(),
            dish_name=meal_data.dish_name,
            health_score=7
        )
        
    except Exception as e:
        logger.error(f"Failed to create meal: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "MEAL_CREATION_FAILED",
                "message": f"Failed to create meal: {str(e)}"
            }
        )


@router.get("/meals", response_model=List[Meal])
async def get_meals(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get meals for user
    
    Returns meals for specified date or today if no date provided.
    Meals are grouped by meal_time.
    """
    user_id = current_user['user_id']
    
    try:
        # Get meals
        if date:
            # Validate and parse date
            try:
                parse_date_from_string(date)
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error_code": "INVALID_DATE_FORMAT",
                        "message": str(e)
                    }
                )
            
            # Get meals for specific date
            # For now, use get_meals_today and filter (can be optimized later)
            meals = await db.get_meals_today(user_id)
            # Filter by date
            meals = [m for m in meals if m['eaten_at'].startswith(date)]
        else:
            # Get today's meals
            meals = await db.get_meals_today(user_id)
        
        # Convert to Meal objects
        result = []
        for meal in meals:
            # Parse components
            components = meal.get('components', '[]')
            if isinstance(components, str):
                components = json.loads(components)
            
            ingredients = [
                Ingredient(
                    name=comp.get('name', 'Unknown'),
                    weight=comp.get('weight_g', 0),
                    calories=comp.get('calories', 0),
                    protein=comp.get('protein_g', 0),
                    fats=comp.get('fat_g', 0),
                    carbs=comp.get('carbs_g', 0),
                    confidence=comp.get('confidence', 0.5)
                )
                for comp in components
            ]
            
            result.append(Meal(
                id=meal['meal_id'],
                user_id=meal['user_id'],
                meal_time=meal.get('meal_type', 'snack'),
                photo_path=meal.get('photo_file_id'),
                video_path=None,
                ingredients=ingredients,
                calories=meal.get('total_calories', 0),
                protein=meal.get('protein_g', 0),
                fats=meal.get('fat_g', 0),
                carbs=meal.get('carbs_g', 0),
                created_at=datetime.fromisoformat(meal['eaten_at']) if isinstance(meal['eaten_at'], str) else meal['eaten_at'],
                dish_name=meal.get('dish_name'),
                health_score=meal.get('health_score')
            ))
        
        # Sort by meal_time order
        meal_time_order = {'breakfast': 0, 'lunch': 1, 'dinner': 2, 'snack': 3}
        result.sort(key=lambda m: meal_time_order.get(m.meal_time, 4))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get meals: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "MEALS_FETCH_FAILED",
                "message": f"Failed to get meals: {str(e)}"
            }
        )


@router.patch("/meals/{meal_id}", response_model=Meal)
async def update_meal(
    meal_id: int,
    meal_update: MealUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update meal record
    
    Updates meal with corrections or changes.
    """
    user_id = current_user['user_id']
    
    try:
        # Get existing meal
        meal = await db.get_meal_by_id(meal_id)
        
        if not meal:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "MEAL_NOT_FOUND",
                    "message": f"Meal {meal_id} not found"
                }
            )
        
        # Verify ownership
        if meal['user_id'] != user_id:
            raise HTTPException(
                status_code=403,
                detail={
                    "error_code": "FORBIDDEN",
                    "message": "You don't have permission to update this meal"
                }
            )
        
        # Build update dictionary
        update_data = {}
        
        if meal_update.meal_time:
            update_data['meal_type'] = meal_update.meal_time.value
        
        if meal_update.dish_name:
            update_data['dish_name'] = meal_update.dish_name
        
        if meal_update.ingredients:
            # Recalculate nutrition
            ingredients_list = [ing.dict() for ing in meal_update.ingredients]
            totals = calculate_macros_from_ingredients(ingredients_list)
            
            update_data['components'] = ingredients_list
            update_data['total_weight'] = sum(ing.weight for ing in meal_update.ingredients)
            update_data['total_calories'] = int(totals['calories'])
            update_data['protein_g'] = int(totals['protein'])
            update_data['fat_g'] = int(totals['fats'])
            update_data['carbs_g'] = int(totals['carbs'])
            update_data['corrections_count'] = meal.get('corrections_count', 0) + 1
        
        # Update meal
        if update_data:
            await db.update_meal(meal_id, **update_data)
        
        # Get updated meal
        updated_meal = await db.get_meal_by_id(meal_id)
        
        # Parse components
        components = updated_meal.get('components', '[]')
        if isinstance(components, str):
            components = json.loads(components)
        
        ingredients = [
            Ingredient(
                name=comp.get('name', 'Unknown'),
                weight=comp.get('weight_g', 0),
                calories=comp.get('calories', 0),
                protein=comp.get('protein_g', 0),
                fats=comp.get('fat_g', 0),
                carbs=comp.get('carbs_g', 0),
                confidence=comp.get('confidence', 0.5)
            )
            for comp in components
        ]
        
        return Meal(
            id=updated_meal['meal_id'],
            user_id=updated_meal['user_id'],
            meal_time=updated_meal.get('meal_type', 'snack'),
            photo_path=updated_meal.get('photo_file_id'),
            video_path=None,
            ingredients=ingredients,
            calories=updated_meal.get('total_calories', 0),
            protein=updated_meal.get('protein_g', 0),
            fats=updated_meal.get('fat_g', 0),
            carbs=updated_meal.get('carbs_g', 0),
            created_at=datetime.fromisoformat(updated_meal['eaten_at']) if isinstance(updated_meal['eaten_at'], str) else updated_meal['eaten_at'],
            dish_name=updated_meal.get('dish_name'),
            health_score=updated_meal.get('health_score')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update meal: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "MEAL_UPDATE_FAILED",
                "message": f"Failed to update meal: {str(e)}"
            }
        )


@router.delete("/meals/{meal_id}", status_code=204)
async def delete_meal(
    meal_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete meal record
    
    Removes meal from database.
    """
    user_id = current_user['user_id']
    
    try:
        # Get existing meal
        meal = await db.get_meal_by_id(meal_id)
        
        if not meal:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "MEAL_NOT_FOUND",
                    "message": f"Meal {meal_id} not found"
                }
            )
        
        # Verify ownership
        if meal['user_id'] != user_id:
            raise HTTPException(
                status_code=403,
                detail={
                    "error_code": "FORBIDDEN",
                    "message": "You don't have permission to delete this meal"
                }
            )
        
        # Delete meal
        await db.delete_meal(meal_id)
        
        # Return 204 No Content (no body)
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete meal: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "MEAL_DELETION_FAILED",
                "message": f"Failed to delete meal: {str(e)}"
            }
        )
