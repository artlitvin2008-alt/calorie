"""
Unit tests for calorie calculator
"""
import pytest
from modules.nutrition.calorie_calculator import CalorieCalculator


def test_calculate_calories_from_macros():
    """Test calorie calculation from macros"""
    # 30g protein = 120 kcal
    # 25g fat = 225 kcal
    # 70g carbs = 280 kcal
    # Total = 625 kcal
    calories = CalorieCalculator.calculate_calories_from_macros(30, 25, 70)
    assert calories == 625


def test_calculate_macros_from_calories():
    """Test macro calculation from calories"""
    # 2000 kcal with 30/30/40 split
    macros = CalorieCalculator.calculate_macros_from_calories(2000, 30, 30, 40)
    
    assert macros['protein_g'] == 150  # 600 kcal / 4
    assert macros['fat_g'] == 66       # 600 kcal / 9
    assert macros['carbs_g'] == 200    # 800 kcal / 4


def test_calculate_calories_per_100g():
    """Test calorie density calculation"""
    # 625 kcal in 250g = 250 kcal/100g
    density = CalorieCalculator.calculate_calories_per_100g(625, 250)
    assert density == 250.0
    
    # Zero weight
    density = CalorieCalculator.calculate_calories_per_100g(100, 0)
    assert density == 0


def test_estimate_weight_from_calories():
    """Test weight estimation"""
    # 400 kcal of meat (200 kcal/100g) = 200g
    weight = CalorieCalculator.estimate_weight_from_calories(400, 'meat')
    assert weight == 200
    
    # 300 kcal of vegetables (30 kcal/100g) = 1000g
    weight = CalorieCalculator.estimate_weight_from_calories(300, 'vegetables')
    assert weight == 1000


def test_calculate_component_totals():
    """Test totals calculation from components"""
    components = [
        {
            'weight_g': 250,
            'calories': 625,
            'protein_g': 30,
            'fat_g': 25,
            'carbs_g': 70
        },
        {
            'weight_g': 30,
            'calories': 60,
            'protein_g': 2,
            'fat_g': 3,
            'carbs_g': 2
        }
    ]
    
    totals = CalorieCalculator.calculate_component_totals(components)
    
    assert totals['weight_grams'] == 280
    assert totals['calories_total'] == 685
    assert totals['protein_g'] == 32
    assert totals['fat_g'] == 28
    assert totals['carbs_g'] == 72
    assert 240 < totals['calories_per_100g'] < 250  # ~245


def test_calculate_health_score():
    """Test health score calculation"""
    # Balanced meal
    score = CalorieCalculator.calculate_health_score(
        protein_g=30,
        fat_g=20,
        carbs_g=50,
        total_calories=500,
        has_vegetables=True,
        is_fried=False
    )
    assert 5 <= score <= 10
    
    # Unhealthy meal (high fat, fried, no vegetables)
    score = CalorieCalculator.calculate_health_score(
        protein_g=10,
        fat_g=50,
        carbs_g=30,
        total_calories=700,
        has_vegetables=False,
        is_fried=True
    )
    assert 1 <= score <= 5


def test_generate_recommendations_weight_loss():
    """Test recommendations for weight loss"""
    recommendations = CalorieCalculator.generate_recommendations(
        total_calories=800,
        protein_g=20,
        fat_g=40,
        carbs_g=60,
        goal='weight_loss'
    )
    
    assert isinstance(recommendations, str)
    assert len(recommendations) > 0
    # Should suggest reducing portion for high calories
    assert "порцию" in recommendations.lower() or "жиров" in recommendations.lower()


def test_generate_recommendations_muscle_gain():
    """Test recommendations for muscle gain"""
    recommendations = CalorieCalculator.generate_recommendations(
        total_calories=300,
        protein_g=15,
        fat_g=10,
        carbs_g=30,
        goal='muscle_gain'
    )
    
    assert isinstance(recommendations, str)
    # Should suggest increasing protein or portion
    assert "белк" in recommendations.lower() or "порци" in recommendations.lower()


def test_generate_portion_advice_weight_loss():
    """Test portion advice for weight loss"""
    # Large portion
    advice = CalorieCalculator.generate_portion_advice(
        total_calories=800,
        weight_g=400,
        goal='weight_loss'
    )
    assert "большая" in advice.lower() or "уменьш" in advice.lower()
    
    # Small portion
    advice = CalorieCalculator.generate_portion_advice(
        total_calories=300,
        weight_g=200,
        goal='weight_loss'
    )
    assert "небольш" in advice.lower() or "хорошо" in advice.lower()


def test_generate_portion_advice_muscle_gain():
    """Test portion advice for muscle gain"""
    # Small portion
    advice = CalorieCalculator.generate_portion_advice(
        total_calories=300,
        weight_g=200,
        goal='muscle_gain'
    )
    assert "маленьк" in advice.lower() or "увелич" in advice.lower()
    
    # Good portion
    advice = CalorieCalculator.generate_portion_advice(
        total_calories=600,
        weight_g=350,
        goal='muscle_gain'
    )
    assert "хорош" in advice.lower() or "масс" in advice.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
