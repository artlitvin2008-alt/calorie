"""
Analytics router
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime, timedelta
import logging
from typing import List

from backend_api.dependencies import get_current_user
from backend_api.models import (
    WeightData, CalorieData, AnalyticsPeriod,
    WeightDataPoint, CalorieDataPoint, MacroNutrients
)
from backend_api.utils import calculate_date_range
from core.database import Database

logger = logging.getLogger(__name__)

router = APIRouter()
db = Database()


@router.get("/weight", response_model=WeightData)
async def get_weight_analytics(
    period: AnalyticsPeriod = Query(AnalyticsPeriod.week, description="Time period for analytics"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get weight trend analytics
    
    Returns weight data for specified period with average and trend.
    """
    user_id = current_user['user_id']
    
    try:
        # Calculate date range
        start_date, end_date = calculate_date_range(period.value)
        
        # Get weight history from database
        # TODO: Implement weight_history query
        # For now, return mock data
        
        data_points = []
        current_date = start_date
        base_weight = 75.0  # Mock starting weight
        
        while current_date <= end_date:
            # Mock weight data with slight variation
            weight = base_weight + (current_date - start_date).days * 0.1
            data_points.append(WeightDataPoint(
                date=current_date.strftime("%Y-%m-%d"),
                weight=round(weight, 1)
            ))
            current_date += timedelta(days=1)
        
        # Calculate average
        if data_points:
            average = sum(dp.weight for dp in data_points) / len(data_points)
            average = round(average, 1)
        else:
            average = None
        
        # Determine trend
        if len(data_points) >= 2:
            first_weight = data_points[0].weight
            last_weight = data_points[-1].weight
            diff = last_weight - first_weight
            
            if diff > 0.5:
                trend = "increasing"
            elif diff < -0.5:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        return WeightData(
            period=period,
            data=data_points,
            average=average,
            trend=trend
        )
        
    except Exception as e:
        logger.error(f"Failed to get weight analytics: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "ANALYTICS_FAILED",
                "message": f"Failed to get weight analytics: {str(e)}"
            }
        )


@router.get("/calories", response_model=CalorieData)
async def get_calorie_analytics(
    period: AnalyticsPeriod = Query(AnalyticsPeriod.week, description="Time period for analytics"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get calorie consumption analytics
    
    Returns daily calorie and macro data for specified period with averages.
    """
    user_id = current_user['user_id']
    
    try:
        # Calculate date range
        start_date, end_date = calculate_date_range(period.value)
        
        # Get daily stats from database
        # TODO: Implement daily_stats query for date range
        # For now, return mock data
        
        data_points = []
        current_date = start_date
        
        while current_date <= end_date:
            # Mock calorie data
            data_points.append(CalorieDataPoint(
                date=current_date.strftime("%Y-%m-%d"),
                calories=1800 + (current_date.day % 7) * 100,
                protein=120 + (current_date.day % 5) * 10,
                fats=60 + (current_date.day % 4) * 5,
                carbs=200 + (current_date.day % 6) * 20
            ))
            current_date += timedelta(days=1)
        
        # Calculate daily averages
        if data_points:
            avg_calories = sum(dp.calories for dp in data_points) / len(data_points)
            avg_protein = sum(dp.protein for dp in data_points) / len(data_points)
            avg_fats = sum(dp.fats for dp in data_points) / len(data_points)
            avg_carbs = sum(dp.carbs for dp in data_points) / len(data_points)
            
            daily_average = MacroNutrients(
                calories=round(avg_calories, 1),
                protein=round(avg_protein, 1),
                fats=round(avg_fats, 1),
                carbs=round(avg_carbs, 1)
            )
        else:
            daily_average = None
        
        return CalorieData(
            period=period,
            data=data_points,
            daily_average=daily_average
        )
        
    except Exception as e:
        logger.error(f"Failed to get calorie analytics: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "ANALYTICS_FAILED",
                "message": f"Failed to get calorie analytics: {str(e)}"
            }
        )
