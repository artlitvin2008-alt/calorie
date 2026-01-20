"""
User management module
"""
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class UserManager:
    """Manages user profiles and settings"""
    
    def __init__(self, database):
        self.db = database
    
    async def get_or_create_user(self, user_id: int, username: str = None,
                                 first_name: str = None, last_name: str = None) -> Dict[str, Any]:
        """Get existing user or create new one"""
        user = await self.db.get_user(user_id)
        
        if not user:
            await self.db.create_user(user_id, username, first_name, last_name)
            user = await self.db.get_user(user_id)
            logger.info(f"New user created: {user_id}")
        
        return user
    
    async def is_registered(self, user_id: int) -> bool:
        """Check if user has completed registration"""
        user = await self.db.get_user(user_id)
        if not user:
            return False
        
        # User is registered if they have set their goals
        return (
            user.get('goal') is not None and
            user.get('current_weight') is not None and
            user.get('target_weight') is not None
        )
    
    async def update_profile(self, user_id: int, **kwargs) -> bool:
        """Update user profile"""
        return await self.db.update_user(user_id, **kwargs)
    
    async def set_goals(self, user_id: int, goal: str, current_weight: float,
                       target_weight: float, height: int, age: int, gender: str) -> bool:
        """Set user fitness goals"""
        # Calculate daily calorie target
        daily_calories = self._calculate_daily_calories(
            current_weight, height, age, gender, goal
        )
        
        # Calculate macro goals (simple distribution)
        protein_goal = int(current_weight * 2)  # 2g per kg
        fat_goal = int(daily_calories * 0.25 / 9)  # 25% from fat
        carbs_goal = int((daily_calories - protein_goal * 4 - fat_goal * 9) / 4)
        
        return await self.db.update_user(
            user_id,
            goal=goal,
            current_weight=current_weight,
            start_weight=current_weight,
            target_weight=target_weight,
            height=height,
            age=age,
            gender=gender,
            daily_calories=daily_calories,
            protein_goal=protein_goal,
            fat_goal=fat_goal,
            carbs_goal=carbs_goal
        )
    
    def _calculate_daily_calories(self, weight: float, height: int, 
                                  age: int, gender: str, goal: str) -> int:
        """Calculate daily calorie target using Mifflin-St Jeor equation"""
        # BMR calculation
        if gender.lower() in ['male', 'm', 'мужской', 'м']:
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        
        # Activity multiplier (assuming moderate activity)
        tdee = bmr * 1.55
        
        # Adjust for goal
        if goal == 'weight_loss':
            # 500 calorie deficit for ~0.5kg per week loss
            return int(tdee - 500)
        elif goal == 'muscle_gain':
            # 300 calorie surplus
            return int(tdee + 300)
        else:
            # Maintenance
            return int(tdee)
    
    async def get_daily_progress(self, user_id: int) -> Dict[str, Any]:
        """Get user's daily progress"""
        user = await self.db.get_user(user_id)
        if not user:
            return {}
        
        # Get today's calories
        consumed_calories = await self.db.get_daily_calories(user_id)
        
        # Get today's meals
        meals = await self.db.get_meals_today(user_id)
        
        # Calculate totals
        total_protein = sum(m['protein_g'] for m in meals)
        total_fat = sum(m['fat_g'] for m in meals)
        total_carbs = sum(m['carbs_g'] for m in meals)
        
        return {
            'consumed_calories': consumed_calories,
            'target_calories': user.get('daily_calories', 0),
            'remaining_calories': user.get('daily_calories', 0) - consumed_calories,
            'protein': {
                'consumed': total_protein,
                'target': user.get('protein_goal', 0)
            },
            'fat': {
                'consumed': total_fat,
                'target': user.get('fat_goal', 0)
            },
            'carbs': {
                'consumed': total_carbs,
                'target': user.get('carbs_goal', 0)
            },
            'meals_count': len(meals)
        }
    
    async def update_weight(self, user_id: int, new_weight: float) -> bool:
        """Update user's current weight"""
        return await self.db.update_user(user_id, current_weight=new_weight)
    
    async def get_profile_summary(self, user_id: int) -> Optional[str]:
        """Get formatted profile summary"""
        user = await self.db.get_user(user_id)
        if not user:
            return None
        
        goal_text = {
            'weight_loss': '🎯 Похудение',
            'muscle_gain': '💪 Набор массы',
            'maintenance': '⚖️ Поддержание'
        }.get(user.get('goal'), 'Не указана')
        
        summary = f"""👤 **Профиль**

{goal_text}
📊 Текущий вес: {user.get('current_weight', 'не указан')} кг
🎯 Целевой вес: {user.get('target_weight', 'не указан')} кг
📏 Рост: {user.get('height', 'не указан')} см
🎂 Возраст: {user.get('age', 'не указан')} лет

**Дневная норма:**
🔥 Калории: {user.get('daily_calories', 0)} ккал
🥚 Белки: {user.get('protein_goal', 0)} г
🥑 Жиры: {user.get('fat_goal', 0)} г
🌾 Углеводы: {user.get('carbs_goal', 0)} г

**Статистика:**
📅 Дней подряд: {user.get('streak_days', 0)}
🍽️ Приёмов пищи: {user.get('total_meals_logged', 0)}
💪 Тренировок: {user.get('total_workouts', 0)}
"""
        return summary
