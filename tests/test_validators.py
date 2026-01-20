"""
Unit tests for validators
"""
import pytest
from utils.validators import (
    FoodAnalysisValidator,
    UserInputValidator,
    CorrectionValidator,
    PhotoValidator
)


def test_food_analysis_validator_valid():
    """Test valid food analysis"""
    data = {
        'dish_name': 'Пельмени',
        'weight_grams': 250,
        'calories_total': 625,
        'protein_g': 30,
        'fat_g': 25,
        'carbs_g': 70,
        'components': []
    }
    
    is_valid, warnings = FoodAnalysisValidator.validate_analysis(data)
    assert is_valid is True
    assert len(warnings) == 0


def test_food_analysis_validator_missing_fields():
    """Test missing required fields"""
    data = {
        'dish_name': 'Test',
        'weight_grams': 100
        # Missing other required fields
    }
    
    is_valid, warnings = FoodAnalysisValidator.validate_analysis(data)
    assert is_valid is False
    assert len(warnings) > 0


def test_food_analysis_validator_unrealistic_weight():
    """Test unrealistic weight"""
    data = {
        'dish_name': 'Test',
        'weight_grams': 3,  # Too low
        'calories_total': 100,
        'protein_g': 10,
        'fat_g': 5,
        'carbs_g': 10
    }
    
    is_valid, warnings = FoodAnalysisValidator.validate_analysis(data)
    assert is_valid is False
    assert any('Weight too low' in w for w in warnings)


def test_food_analysis_validator_macro_mismatch():
    """Test macro mismatch"""
    data = {
        'dish_name': 'Test',
        'weight_grams': 100,
        'calories_total': 1000,  # Stated calories
        'protein_g': 10,  # 40 kcal
        'fat_g': 5,       # 45 kcal
        'carbs_g': 10     # 40 kcal
        # Total from macros: 125 kcal (big mismatch!)
    }
    
    is_valid, warnings = FoodAnalysisValidator.validate_analysis(data)
    assert is_valid is False
    assert any('Macro mismatch' in w for w in warnings)


def test_user_input_validator_weight_valid():
    """Test valid weight input"""
    is_valid, weight, error = UserInputValidator.validate_weight("75")
    assert is_valid is True
    assert weight == 75.0
    assert error is None
    
    # Test with comma
    is_valid, weight, error = UserInputValidator.validate_weight("75,5")
    assert is_valid is True
    assert weight == 75.5


def test_user_input_validator_weight_invalid():
    """Test invalid weight input"""
    # Too low
    is_valid, weight, error = UserInputValidator.validate_weight("20")
    assert is_valid is False
    assert "слишком мал" in error.lower()
    
    # Too high
    is_valid, weight, error = UserInputValidator.validate_weight("350")
    assert is_valid is False
    assert "слишком велик" in error.lower()
    
    # Invalid format
    is_valid, weight, error = UserInputValidator.validate_weight("abc")
    assert is_valid is False
    assert "неверный формат" in error.lower()


def test_user_input_validator_height_valid():
    """Test valid height input"""
    is_valid, height, error = UserInputValidator.validate_height("175")
    assert is_valid is True
    assert height == 175
    assert error is None


def test_user_input_validator_height_invalid():
    """Test invalid height input"""
    # Too low
    is_valid, height, error = UserInputValidator.validate_height("50")
    assert is_valid is False
    
    # Too high
    is_valid, height, error = UserInputValidator.validate_height("300")
    assert is_valid is False
    
    # Invalid format
    is_valid, height, error = UserInputValidator.validate_height("abc")
    assert is_valid is False


def test_user_input_validator_age_valid():
    """Test valid age input"""
    is_valid, age, error = UserInputValidator.validate_age("28")
    assert is_valid is True
    assert age == 28
    assert error is None


def test_user_input_validator_age_invalid():
    """Test invalid age input"""
    # Too low
    is_valid, age, error = UserInputValidator.validate_age("5")
    assert is_valid is False
    
    # Too high
    is_valid, age, error = UserInputValidator.validate_age("150")
    assert is_valid is False


def test_user_input_validator_goal():
    """Test goal validation"""
    # Valid inputs
    is_valid, goal, error = UserInputValidator.validate_goal("1")
    assert is_valid is True
    assert goal == "weight_loss"
    
    is_valid, goal, error = UserInputValidator.validate_goal("похудение")
    assert is_valid is True
    assert goal == "weight_loss"
    
    is_valid, goal, error = UserInputValidator.validate_goal("2")
    assert is_valid is True
    assert goal == "muscle_gain"
    
    # Invalid input
    is_valid, goal, error = UserInputValidator.validate_goal("invalid")
    assert is_valid is False


def test_user_input_validator_gender():
    """Test gender validation"""
    # Valid inputs
    is_valid, gender, error = UserInputValidator.validate_gender("1")
    assert is_valid is True
    assert gender == "male"
    
    is_valid, gender, error = UserInputValidator.validate_gender("мужской")
    assert is_valid is True
    assert gender == "male"
    
    is_valid, gender, error = UserInputValidator.validate_gender("2")
    assert is_valid is True
    assert gender == "female"
    
    # Invalid input
    is_valid, gender, error = UserInputValidator.validate_gender("invalid")
    assert is_valid is False


def test_correction_validator_detect_remove():
    """Test remove correction detection"""
    action, details = CorrectionValidator.detect_correction_type("нет хлеба")
    assert action == "remove"
    assert details['item'] == "хлеба"
    
    action, details = CorrectionValidator.detect_correction_type("убери салат")
    assert action == "remove"
    assert details['item'] == "салат"


def test_correction_validator_detect_add():
    """Test add correction detection"""
    action, details = CorrectionValidator.detect_correction_type("добавь салат 100г")
    assert action == "add"
    assert details['item'] == "салат"
    assert details['weight'] == 100
    
    action, details = CorrectionValidator.detect_correction_type("добавь огурец")
    assert action == "add"
    assert details['item'] == "огурец"
    assert details['weight'] is None


def test_correction_validator_detect_modify():
    """Test modify correction detection"""
    action, details = CorrectionValidator.detect_correction_type("это курица, а не свинина")
    assert action == "modify"
    assert details['new_item'] == "курица"
    assert details['old_item'] == "свинина"


def test_correction_validator_validate():
    """Test correction validation"""
    # Valid
    is_valid, error = CorrectionValidator.validate_correction("нет хлеба")
    assert is_valid is True
    assert error is None
    
    # Too short
    is_valid, error = CorrectionValidator.validate_correction("ab")
    assert is_valid is False
    
    # Too long
    is_valid, error = CorrectionValidator.validate_correction("a" * 600)
    assert is_valid is False
    
    # Unrecognized
    is_valid, error = CorrectionValidator.validate_correction("какой-то текст")
    assert is_valid is False


def test_photo_validator_size():
    """Test photo size validation"""
    # Valid size (1 MB)
    is_valid, error = PhotoValidator.validate_photo_size(1024 * 1024)
    assert is_valid is True
    assert error is None
    
    # Too large (15 MB)
    is_valid, error = PhotoValidator.validate_photo_size(15 * 1024 * 1024)
    assert is_valid is False
    assert "слишком большое" in error.lower()


def test_photo_validator_format():
    """Test photo format validation"""
    # Valid formats
    is_valid, error = PhotoValidator.validate_photo_format("image/jpeg")
    assert is_valid is True
    
    is_valid, error = PhotoValidator.validate_photo_format("image/png")
    assert is_valid is True
    
    # Invalid format
    is_valid, error = PhotoValidator.validate_photo_format("image/gif")
    assert is_valid is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
