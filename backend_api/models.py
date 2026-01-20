"""
Pydantic models for API request/response validation
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# ==================== ENUMS ====================

class MealTime(str, Enum):
    breakfast = "breakfast"
    lunch = "lunch"
    dinner = "dinner"
    snack = "snack"


class Gender(str, Enum):
    male = "male"
    female = "female"
    other = "other"


class Goal(str, Enum):
    weight_loss = "weight_loss"
    muscle_gain = "muscle_gain"
    maintenance = "maintenance"


class AnalyticsPeriod(str, Enum):
    week = "week"
    month = "month"
    year = "year"


# ==================== USER MODELS ====================

class UserGoals(BaseModel):
    calories: int = Field(..., ge=1000, le=5000)
    protein: int = Field(..., ge=50, le=300)
    fats: int = Field(..., ge=30, le=200)
    carbs: int = Field(..., ge=50, le=500)


class UserProfile(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    goals: UserGoals
    height: Optional[int] = Field(None, ge=100, le=250)
    weight: Optional[float] = Field(None, ge=20, le=500)
    age: Optional[int] = Field(None, ge=10, le=120)
    gender: Optional[Gender] = None
    notifications_enabled: bool = True


class UserProfileUpdate(BaseModel):
    goals: Optional[UserGoals] = None
    height: Optional[int] = Field(None, ge=100, le=250)
    weight: Optional[float] = Field(None, ge=20, le=500)
    age: Optional[int] = Field(None, ge=10, le=120)
    gender: Optional[Gender] = None
    notifications_enabled: Optional[bool] = None


class MacroNutrients(BaseModel):
    calories: float
    protein: float
    fats: float
    carbs: float


class DailyStats(BaseModel):
    date: str
    consumed: MacroNutrients
    goals: MacroNutrients
    progress: Dict[str, float]  # percentage for each macro
    meals_count: int


# ==================== NUTRITION MODELS ====================

class Ingredient(BaseModel):
    name: str
    weight: float = Field(..., ge=0)
    calories: float = Field(..., ge=0)
    protein: float = Field(..., ge=0)
    fats: float = Field(..., ge=0)
    carbs: float = Field(..., ge=0)
    confidence: Optional[float] = Field(None, ge=0, le=1)


class AnalysisResult(BaseModel):
    ingredients: List[Ingredient]
    nutrition: MacroNutrients
    photo_path: str
    dish_name: Optional[str] = None
    health_score: Optional[int] = Field(None, ge=1, le=10)
    detailed_analysis: Optional[str] = None
    recommendations: Optional[str] = None


class MealCreate(BaseModel):
    meal_time: MealTime
    ingredients: List[Ingredient]
    photo_path: Optional[str] = None
    video_path: Optional[str] = None
    dish_name: Optional[str] = None


class MealUpdate(BaseModel):
    meal_time: Optional[MealTime] = None
    ingredients: Optional[List[Ingredient]] = None
    dish_name: Optional[str] = None


class Meal(BaseModel):
    id: int
    user_id: int
    meal_time: MealTime
    photo_path: Optional[str] = None
    video_path: Optional[str] = None
    ingredients: List[Ingredient]
    calories: float
    protein: float
    fats: float
    carbs: float
    created_at: datetime
    dish_name: Optional[str] = None
    health_score: Optional[int] = None


# ==================== ANALYTICS MODELS ====================

class WeightDataPoint(BaseModel):
    date: str
    weight: float


class CalorieDataPoint(BaseModel):
    date: str
    calories: float
    protein: float
    fats: float
    carbs: float


class WeightData(BaseModel):
    period: AnalyticsPeriod
    data: List[WeightDataPoint]
    average: Optional[float] = None
    trend: Optional[str] = None  # "increasing", "decreasing", "stable"


class CalorieData(BaseModel):
    period: AnalyticsPeriod
    data: List[CalorieDataPoint]
    daily_average: Optional[MacroNutrients] = None


# ==================== ERROR MODELS ====================

class ErrorResponse(BaseModel):
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None


# ==================== AI CHAT MODELS ====================

class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)


class ChatResponse(BaseModel):
    response: str
    timestamp: datetime
