"""
Calorie and macro calculator
"""
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class CalorieCalculator:
    """Calculator for calories and macronutrients"""
    
    # Calorie values per gram
    PROTEIN_KCAL_PER_G = 4
    FAT_KCAL_PER_G = 9
    CARBS_KCAL_PER_G = 4
    
    # Average calorie density by food category (kcal/100g)
    CALORIE_DENSITY = {
        'vegetables': 30,
        'fruits': 50,
        'grains': 350,
        'meat': 200,
        'fish': 150,
        'dairy': 100,
        'oils': 900,
        'sweets': 400,
        'bread': 250,
        'pasta': 350,
        'rice': 130,
        'potatoes': 80,
        'cheese': 350,
        'nuts': 600,
    }
    
    @staticmethod
    def calculate_calories_from_macros(protein_g: float, fat_g: float, carbs_g: float) -> int:
        """
        Calculate total calories from macronutrients
        
        Args:
            protein_g: Protein in grams
            fat_g: Fat in grams
            carbs_g: Carbohydrates in grams
        
        Returns:
            Total calories
        """
        calories = (
            protein_g * CalorieCalculator.PROTEIN_KCAL_PER_G +
            fat_g * CalorieCalculator.FAT_KCAL_PER_G +
            carbs_g * CalorieCalculator.CARBS_KCAL_PER_G
        )
        return int(calories)
    
    @staticmethod
    def calculate_macros_from_calories(
        total_calories: int,
        protein_percent: float = 30,
        fat_percent: float = 30,
        carbs_percent: float = 40
    ) -> Dict[str, int]:
        """
        Calculate macro distribution from total calories
        
        Args:
            total_calories: Total calories
            protein_percent: Percentage of calories from protein (default 30%)
            fat_percent: Percentage of calories from fat (default 30%)
            carbs_percent: Percentage of calories from carbs (default 40%)
        
        Returns:
            Dict with protein_g, fat_g, carbs_g
        """
        protein_calories = total_calories * (protein_percent / 100)
        fat_calories = total_calories * (fat_percent / 100)
        carbs_calories = total_calories * (carbs_percent / 100)
        
        return {
            'protein_g': int(protein_calories / CalorieCalculator.PROTEIN_KCAL_PER_G),
            'fat_g': int(fat_calories / CalorieCalculator.FAT_KCAL_PER_G),
            'carbs_g': int(carbs_calories / CalorieCalculator.CARBS_KCAL_PER_G)
        }
    
    @staticmethod
    def calculate_calories_per_100g(total_calories: int, weight_g: int) -> float:
        """
        Calculate calorie density (calories per 100g)
        
        Args:
            total_calories: Total calories
            weight_g: Weight in grams
        
        Returns:
            Calories per 100g
        """
        if weight_g <= 0:
            return 0
        
        return (total_calories / weight_g) * 100
    
    @staticmethod
    def estimate_weight_from_calories(
        calories: int,
        category: str = 'meat'
    ) -> int:
        """
        Estimate weight from calories based on food category
        
        Args:
            calories: Total calories
            category: Food category
        
        Returns:
            Estimated weight in grams
        """
        density = CalorieCalculator.CALORIE_DENSITY.get(category, 200)
        weight = (calories / density) * 100
        return int(weight)
    
    @staticmethod
    def calculate_component_totals(components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate totals from list of components
        
        Args:
            components: List of food components with calories and macros
        
        Returns:
            Dict with totals
        """
        total_weight = 0
        total_calories = 0
        total_protein = 0
        total_fat = 0
        total_carbs = 0
        
        for comp in components:
            total_weight += comp.get('weight_g', 0)
            total_calories += comp.get('calories', 0)
            total_protein += comp.get('protein_g', 0)
            total_fat += comp.get('fat_g', 0)
            total_carbs += comp.get('carbs_g', 0)
        
        calories_per_100g = CalorieCalculator.calculate_calories_per_100g(
            total_calories, total_weight
        ) if total_weight > 0 else 0
        
        return {
            'weight_grams': total_weight,
            'calories_total': total_calories,
            'calories_per_100g': round(calories_per_100g, 1),
            'protein_g': total_protein,
            'fat_g': total_fat,
            'carbs_g': total_carbs
        }
    
    @staticmethod
    def calculate_health_score(
        protein_g: float,
        fat_g: float,
        carbs_g: float,
        total_calories: int,
        has_vegetables: bool = False,
        is_fried: bool = False
    ) -> int:
        """
        Calculate health score (1-10) based on nutritional profile
        
        Args:
            protein_g: Protein in grams
            fat_g: Fat in grams
            carbs_g: Carbohydrates in grams
            total_calories: Total calories
            has_vegetables: Whether meal includes vegetables
            is_fried: Whether meal is fried
        
        Returns:
            Health score from 1 to 10
        """
        score = 5  # Start with neutral score
        
        if total_calories == 0:
            return score
        
        # Calculate macro percentages
        protein_percent = (protein_g * 4 / total_calories) * 100
        fat_percent = (fat_g * 9 / total_calories) * 100
        carbs_percent = (carbs_g * 4 / total_calories) * 100
        
        # Good protein content (20-35%)
        if 20 <= protein_percent <= 35:
            score += 1
        elif protein_percent < 15:
            score -= 1
        
        # Moderate fat (20-35%)
        if 20 <= fat_percent <= 35:
            score += 1
        elif fat_percent > 40:
            score -= 2
        elif fat_percent < 15:
            score -= 1
        
        # Moderate carbs (40-60%)
        if 40 <= carbs_percent <= 60:
            score += 1
        elif carbs_percent > 70:
            score -= 1
        
        # Bonus for vegetables
        if has_vegetables:
            score += 2
        
        # Penalty for fried food
        if is_fried:
            score -= 2
        
        # Clamp to 1-10 range
        return max(1, min(10, score))
    
    @staticmethod
    def generate_recommendations(
        total_calories: int,
        protein_g: float,
        fat_g: float,
        carbs_g: float,
        goal: str = 'weight_loss'
    ) -> str:
        """
        Generate dietary recommendations based on analysis
        
        Args:
            total_calories: Total calories
            protein_g: Protein in grams
            fat_g: Fat in grams
            carbs_g: Carbohydrates in grams
            goal: User's goal (weight_loss, muscle_gain, maintenance)
        
        Returns:
            Recommendation text
        """
        recommendations = []
        
        if total_calories == 0:
            return "Недостаточно данных для рекомендаций"
        
        # Calculate percentages
        protein_percent = (protein_g * 4 / total_calories) * 100
        fat_percent = (fat_g * 9 / total_calories) * 100
        
        if goal == 'weight_loss':
            if total_calories > 600:
                recommendations.append("• Уменьши порцию на 20-30%")
            
            if fat_percent > 35:
                recommendations.append("• Слишком много жиров - выбирай менее жирные варианты")
            
            if protein_percent < 20:
                recommendations.append("• Добавь больше белка (мясо, рыба, яйца)")
            
            recommendations.append("• Добавь овощей для сытости")
            recommendations.append("• Пей воду перед едой")
        
        elif goal == 'muscle_gain':
            if protein_percent < 25:
                recommendations.append("• Увеличь количество белка до 30-35%")
            
            if total_calories < 500:
                recommendations.append("• Увеличь порцию для набора массы")
            
            recommendations.append("• Ешь каждые 3-4 часа")
        
        else:  # maintenance
            if protein_percent < 20:
                recommendations.append("• Добавь немного белка")
            
            if fat_percent > 40:
                recommendations.append("• Уменьши количество жиров")
        
        if not recommendations:
            recommendations.append("• Сбалансированный приём пищи!")
        
        return "\n".join(recommendations)
    
    @staticmethod
    def generate_portion_advice(
        total_calories: int,
        weight_g: int,
        goal: str = 'weight_loss'
    ) -> str:
        """
        Generate portion size advice
        
        Args:
            total_calories: Total calories
            weight_g: Weight in grams
            goal: User's goal
        
        Returns:
            Portion advice text
        """
        if goal == 'weight_loss':
            if total_calories > 700:
                return f"Порция большая ({weight_g}г). Попробуй уменьшить до {int(weight_g * 0.7)}г"
            elif total_calories > 500:
                return f"Нормальная порция. Можешь оставить как есть"
            else:
                return f"Небольшая порция - хорошо для похудения"
        
        elif goal == 'muscle_gain':
            if total_calories < 400:
                return f"Маленькая порция. Увеличь до {int(weight_g * 1.3)}г"
            else:
                return f"Хорошая порция для набора массы"
        
        else:  # maintenance
            if 400 <= total_calories <= 600:
                return f"Оптимальная порция"
            elif total_calories > 600:
                return f"Немного большая порция"
            else:
                return f"Небольшая порция"
