"""
Test weight correction parsing
"""
from utils.validators import CorrectionValidator
from modules.nutrition.correction_parser import CorrectionParser

# Test data
test_corrections = [
    "500г",
    "500 г",
    "500грамм",
    "вес 500г",
    "300г",
]

# Sample analysis
sample_analysis = {
    "components": [
        {
            "name": "Говядина жареная",
            "weight_g": 100,
            "calories": 250,
            "protein_g": 25,
            "fat_g": 15,
            "carbs_g": 0,
            "confidence": 0.85
        },
        {
            "name": "Булочка",
            "weight_g": 50,
            "calories": 140,
            "protein_g": 5,
            "fat_g": 3,
            "carbs_g": 23,
            "confidence": 0.85
        }
    ],
    "dish_name": "Бургер",
    "weight_grams": 150,
    "calories_total": 390,
    "calories_per_100g": 260,
    "protein_g": 30,
    "fat_g": 18,
    "carbs_g": 23,
    "health_score": 5
}

print("=" * 60)
print("ТЕСТ: Распознавание изменения веса")
print("=" * 60)

validator = CorrectionValidator()
parser = CorrectionParser()

for text in test_corrections:
    print(f"\nТекст: '{text}'")
    
    # Detect type
    action_type, details = validator.detect_correction_type(text)
    print(f"  Тип: {action_type}")
    print(f"  Детали: {details}")
    
    if action_type == 'change_weight':
        # Apply correction
        success, updated, error = parser.parse_correction(text, sample_analysis.copy())
        
        if success:
            print(f"  ✅ Успешно применено!")
            print(f"  Старый вес: {sample_analysis['weight_grams']}г")
            print(f"  Новый вес: {updated['weight_grams']}г")
            print(f"  Старые калории: {sample_analysis['calories_total']} ккал")
            print(f"  Новые калории: {updated['calories_total']} ккал")
        else:
            print(f"  ❌ Ошибка: {error}")
    else:
        print(f"  ⚠️ Неправильный тип (ожидался 'change_weight')")

print("\n" + "=" * 60)
print("ТЕСТ ЗАВЕРШЁН")
print("=" * 60)
