"""
Data validation utilities
"""
import re
from typing import Dict, Any, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom validation error"""
    pass


class FoodAnalysisValidator:
    """Validator for food analysis data"""
    
    # Realistic ranges
    MIN_CALORIES_PER_100G = 10
    MAX_CALORIES_PER_100G = 900
    MIN_WEIGHT = 5
    MAX_WEIGHT = 2000
    MIN_CONFIDENCE = 0.0
    MAX_CONFIDENCE = 1.0
    
    # Macro ratios (percentage of calories)
    PROTEIN_RATIO_RANGE = (5, 40)  # 5-40% of calories
    FAT_RATIO_RANGE = (10, 50)     # 10-50% of calories
    CARBS_RATIO_RANGE = (20, 80)   # 20-80% of calories
    
    @staticmethod
    def validate_analysis(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate food analysis data
        
        Returns:
            (is_valid, warnings)
        """
        warnings = []
        
        # Check required fields
        required_fields = [
            'dish_name', 'weight_grams', 'calories_total',
            'protein_g', 'fat_g', 'carbs_g'
        ]
        
        for field in required_fields:
            if field not in data or data[field] is None:
                warnings.append(f"Missing required field: {field}")
        
        if warnings:
            return False, warnings
        
        # Validate weight
        weight = data.get('weight_grams', 0)
        if weight < FoodAnalysisValidator.MIN_WEIGHT:
            warnings.append(f"Weight too low: {weight}g (min: {FoodAnalysisValidator.MIN_WEIGHT}g)")
        elif weight > FoodAnalysisValidator.MAX_WEIGHT:
            warnings.append(f"Weight too high: {weight}g (max: {FoodAnalysisValidator.MAX_WEIGHT}g)")
        
        # Validate calories
        calories = data.get('calories_total', 0)
        if calories < 0:
            warnings.append(f"Negative calories: {calories}")
        elif calories > 5000:
            warnings.append(f"Unrealistic calories: {calories} (typical meal: 300-1000 kcal)")
        
        # Validate calorie density
        if weight > 0:
            calories_per_100g = (calories / weight) * 100
            if calories_per_100g < FoodAnalysisValidator.MIN_CALORIES_PER_100G:
                warnings.append(
                    f"Very low calorie density: {calories_per_100g:.0f} kcal/100g "
                    f"(typical: 50-300 kcal/100g)"
                )
            elif calories_per_100g > FoodAnalysisValidator.MAX_CALORIES_PER_100G:
                warnings.append(
                    f"Very high calorie density: {calories_per_100g:.0f} kcal/100g "
                    f"(typical: 50-300 kcal/100g)"
                )
        
        # Validate macros consistency
        protein = data.get('protein_g', 0)
        fat = data.get('fat_g', 0)
        carbs = data.get('carbs_g', 0)
        
        calculated_calories = protein * 4 + fat * 9 + carbs * 4
        if calories > 0:
            diff_percent = abs(calories - calculated_calories) / calories * 100
            if diff_percent > 20:
                warnings.append(
                    f"Macro mismatch: stated {calories} kcal, "
                    f"but macros give {calculated_calories:.0f} kcal "
                    f"(difference: {diff_percent:.0f}%)"
                )
        
        # Validate macro ratios
        if calories > 0:
            protein_percent = (protein * 4 / calories) * 100
            fat_percent = (fat * 9 / calories) * 100
            carbs_percent = (carbs * 4 / calories) * 100
            
            if not (FoodAnalysisValidator.PROTEIN_RATIO_RANGE[0] <= protein_percent <= FoodAnalysisValidator.PROTEIN_RATIO_RANGE[1]):
                warnings.append(
                    f"Unusual protein ratio: {protein_percent:.0f}% "
                    f"(typical: {FoodAnalysisValidator.PROTEIN_RATIO_RANGE[0]}-{FoodAnalysisValidator.PROTEIN_RATIO_RANGE[1]}%)"
                )
            
            if not (FoodAnalysisValidator.FAT_RATIO_RANGE[0] <= fat_percent <= FoodAnalysisValidator.FAT_RATIO_RANGE[1]):
                warnings.append(
                    f"Unusual fat ratio: {fat_percent:.0f}% "
                    f"(typical: {FoodAnalysisValidator.FAT_RATIO_RANGE[0]}-{FoodAnalysisValidator.FAT_RATIO_RANGE[1]}%)"
                )
            
            if not (FoodAnalysisValidator.CARBS_RATIO_RANGE[0] <= carbs_percent <= FoodAnalysisValidator.CARBS_RATIO_RANGE[1]):
                warnings.append(
                    f"Unusual carbs ratio: {carbs_percent:.0f}% "
                    f"(typical: {FoodAnalysisValidator.CARBS_RATIO_RANGE[0]}-{FoodAnalysisValidator.CARBS_RATIO_RANGE[1]}%)"
                )
        
        # Validate components if present
        components = data.get('components', [])
        if components:
            for i, comp in enumerate(components):
                comp_warnings = FoodAnalysisValidator.validate_component(comp, i)
                warnings.extend(comp_warnings)
        
        is_valid = len(warnings) == 0
        return is_valid, warnings
    
    @staticmethod
    def validate_component(component: Dict[str, Any], index: int) -> List[str]:
        """Validate single food component"""
        warnings = []
        
        # Check required fields
        if 'name' not in component or not component['name']:
            warnings.append(f"Component {index}: missing name")
        
        if 'weight_g' not in component:
            warnings.append(f"Component {index}: missing weight")
        else:
            weight = component['weight_g']
            if weight < 1 or weight > 2000:
                warnings.append(f"Component {index}: unrealistic weight {weight}g")
        
        # Check confidence if present
        if 'confidence' in component:
            conf = component['confidence']
            if not (FoodAnalysisValidator.MIN_CONFIDENCE <= conf <= FoodAnalysisValidator.MAX_CONFIDENCE):
                warnings.append(f"Component {index}: invalid confidence {conf}")
        
        return warnings


class UserInputValidator:
    """Validator for user input"""
    
    @staticmethod
    def validate_weight(weight_str: str) -> Tuple[bool, Optional[float], Optional[str]]:
        """
        Validate weight input
        
        Returns:
            (is_valid, weight, error_message)
        """
        try:
            weight = float(weight_str.replace(',', '.'))
            
            if weight < 30:
                return False, None, "Вес слишком мал (минимум 30 кг)"
            elif weight > 300:
                return False, None, "Вес слишком велик (максимум 300 кг)"
            
            return True, weight, None
            
        except ValueError:
            return False, None, "Неверный формат. Введи число, например: 75"
    
    @staticmethod
    def validate_height(height_str: str) -> Tuple[bool, Optional[int], Optional[str]]:
        """
        Validate height input
        
        Returns:
            (is_valid, height, error_message)
        """
        try:
            height = int(height_str)
            
            if height < 100:
                return False, None, "Рост слишком мал (минимум 100 см)"
            elif height > 250:
                return False, None, "Рост слишком велик (максимум 250 см)"
            
            return True, height, None
            
        except ValueError:
            return False, None, "Неверный формат. Введи число, например: 175"
    
    @staticmethod
    def validate_age(age_str: str) -> Tuple[bool, Optional[int], Optional[str]]:
        """
        Validate age input
        
        Returns:
            (is_valid, age, error_message)
        """
        try:
            age = int(age_str)
            
            if age < 10:
                return False, None, "Возраст слишком мал (минимум 10 лет)"
            elif age > 100:
                return False, None, "Возраст слишком велик (максимум 100 лет)"
            
            return True, age, None
            
        except ValueError:
            return False, None, "Неверный формат. Введи число, например: 28"
    
    @staticmethod
    def validate_goal(goal_str: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate goal input
        
        Returns:
            (is_valid, goal, error_message)
        """
        goal_mapping = {
            '1': 'weight_loss',
            'похудение': 'weight_loss',
            'похудеть': 'weight_loss',
            'weight_loss': 'weight_loss',
            '2': 'muscle_gain',
            'набор': 'muscle_gain',
            'масса': 'muscle_gain',
            'muscle_gain': 'muscle_gain',
            '3': 'maintenance',
            'поддержание': 'maintenance',
            'maintenance': 'maintenance',
        }
        
        goal = goal_mapping.get(goal_str.lower())
        
        if goal:
            return True, goal, None
        else:
            return False, None, "Неверный выбор. Отправь номер (1, 2 или 3) или название цели"
    
    @staticmethod
    def validate_gender(gender_str: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate gender input
        
        Returns:
            (is_valid, gender, error_message)
        """
        gender_mapping = {
            '1': 'male',
            'мужской': 'male',
            'м': 'male',
            'male': 'male',
            '2': 'female',
            'женский': 'female',
            'ж': 'female',
            'female': 'female',
        }
        
        gender = gender_mapping.get(gender_str.lower())
        
        if gender:
            return True, gender, None
        else:
            return False, None, "Неверный выбор. Отправь номер (1 или 2) или название"


class CorrectionValidator:
    """Validator for correction text"""
    
    # Patterns for correction detection
    REMOVE_PATTERNS = [
        r'нет\s+(.+)',
        r'убери\s+(.+)',
        r'удали\s+(.+)',
        r'без\s+(.+)',
    ]
    
    ADD_PATTERNS = [
        r'добавь\s+(.+)',
        r'есть\s+(?:еще|ещё)\s+(.+)',
        r'плюс\s+(.+)',
    ]
    
    MODIFY_PATTERNS = [
        r'это\s+(.+?),?\s+а\s+не\s+(.+)',
        r'не\s+(.+?),?\s+а\s+(.+)',
    ]
    
    # Pattern for weight change (e.g., "500г", "вес 500г", "250 грамм")
    WEIGHT_CHANGE_PATTERNS = [
        r'^(\d+)\s*г(?:рамм)?$',  # Just "500г" or "500 грамм"
        r'вес\s+(\d+)\s*г(?:рамм)?',  # "вес 500г"
        r'(\d+)\s*г(?:рамм)?\s+(?:а не|вместо)',  # "500г а не 250г"
    ]
    
    @staticmethod
    def detect_correction_type(text: str) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        Detect correction type from text
        
        Returns:
            (action_type, details)
            action_type: 'remove', 'add', 'modify', 'change_weight', or None
            details: dict with parsed information
        """
        text = text.lower().strip()
        
        # Check for weight change (check this first as it's most specific)
        for pattern in CorrectionValidator.WEIGHT_CHANGE_PATTERNS:
            match = re.search(pattern, text)
            if match:
                weight = int(match.group(1))
                return 'change_weight', {'weight': weight}
        
        # Check for remove
        for pattern in CorrectionValidator.REMOVE_PATTERNS:
            match = re.search(pattern, text)
            if match:
                item = match.group(1).strip()
                return 'remove', {'item': item}
        
        # Check for add
        for pattern in CorrectionValidator.ADD_PATTERNS:
            match = re.search(pattern, text)
            if match:
                item_text = match.group(1).strip()
                # Try to extract weight
                weight_match = re.search(r'(\d+)\s*г', item_text)
                if weight_match:
                    weight = int(weight_match.group(1))
                    item = re.sub(r'\d+\s*г', '', item_text).strip()
                    return 'add', {'item': item, 'weight': weight}
                else:
                    return 'add', {'item': item_text, 'weight': None}
        
        # Check for modify
        for pattern in CorrectionValidator.MODIFY_PATTERNS:
            match = re.search(pattern, text)
            if match:
                new_item = match.group(1).strip()
                old_item = match.group(2).strip()
                return 'modify', {'old_item': old_item, 'new_item': new_item}
        
        return None, None
    
    @staticmethod
    def validate_correction(text: str) -> Tuple[bool, Optional[str]]:
        """
        Validate correction text
        
        Returns:
            (is_valid, error_message)
        """
        if not text or len(text.strip()) < 3:
            return False, "Слишком короткое сообщение"
        
        if len(text) > 500:
            return False, "Слишком длинное сообщение (максимум 500 символов)"
        
        action_type, details = CorrectionValidator.detect_correction_type(text)
        
        if action_type is None:
            return False, (
                "Не удалось распознать коррекцию. Примеры:\n"
                "• \"нет хлеба\" - убрать\n"
                "• \"добавь салат 100г\" - добавить\n"
                "• \"это курица, а не свинина\" - изменить"
            )
        
        return True, None


class PhotoValidator:
    """Validator for photo input"""
    
    MAX_FILE_SIZE_MB = 10
    ALLOWED_FORMATS = ['image/jpeg', 'image/png', 'image/webp']
    
    @staticmethod
    def validate_photo_size(file_size: int) -> Tuple[bool, Optional[str]]:
        """
        Validate photo file size
        
        Returns:
            (is_valid, error_message)
        """
        max_size_bytes = PhotoValidator.MAX_FILE_SIZE_MB * 1024 * 1024
        
        if file_size > max_size_bytes:
            return False, f"Фото слишком большое (максимум {PhotoValidator.MAX_FILE_SIZE_MB} МБ)"
        
        return True, None
    
    @staticmethod
    def validate_photo_format(mime_type: str) -> Tuple[bool, Optional[str]]:
        """
        Validate photo format
        
        Returns:
            (is_valid, error_message)
        """
        if mime_type not in PhotoValidator.ALLOWED_FORMATS:
            return False, f"Неподдерживаемый формат. Используй JPEG, PNG или WebP"
        
        return True, None
