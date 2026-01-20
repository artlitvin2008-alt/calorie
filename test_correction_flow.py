"""
Test correction flow
"""
from modules.nutrition.correction_parser import CorrectionParser


def test_remove_correction():
    """Test removing a component"""
    parser = CorrectionParser()
    
    analysis = {
        'dish_name': 'Пельмени со сметаной',
        'components': [
            {
                'name': 'Пельмени',
                'weight_g': 250,
                'calories': 625,
                'protein_g': 30,
                'fat_g': 25,
                'carbs_g': 70,
                'confidence': 0.85
            },
            {
                'name': 'Сметана',
                'weight_g': 30,
                'calories': 60,
                'protein_g': 2,
                'fat_g': 3,
                'carbs_g': 2,
                'confidence': 0.90
            },
            {
                'name': 'Хлеб',
                'weight_g': 50,
                'calories': 120,
                'protein_g': 4,
                'fat_g': 1,
                'carbs_g': 24,
                'confidence': 0.75
            }
        ],
        'weight_grams': 330,
        'calories_total': 805,
        'protein_g': 36,
        'fat_g': 29,
        'carbs_g': 96
    }
    
    # Test remove
    success, updated, error = parser.parse_correction("нет хлеба", analysis)
    
    print("Test Remove Correction:")
    print(f"Success: {success}")
    print(f"Error: {error}")
    print(f"Components before: {len(analysis['components'])}")
    print(f"Components after: {len(updated['components']) if updated else 0}")
    
    if updated:
        print(f"Total calories before: {analysis['calories_total']}")
        print(f"Total calories after: {updated['calories_total']}")
        print(f"Components: {[c['name'] for c in updated['components']]}")
    
    print()


def test_add_correction():
    """Test adding a component"""
    parser = CorrectionParser()
    
    analysis = {
        'dish_name': 'Пельмени',
        'components': [
            {
                'name': 'Пельмени',
                'weight_g': 250,
                'calories': 625,
                'protein_g': 30,
                'fat_g': 25,
                'carbs_g': 70,
                'confidence': 0.85
            }
        ],
        'weight_grams': 250,
        'calories_total': 625,
        'protein_g': 30,
        'fat_g': 25,
        'carbs_g': 70
    }
    
    # Test add
    success, updated, error = parser.parse_correction("добавь салат 100г", analysis)
    
    print("Test Add Correction:")
    print(f"Success: {success}")
    print(f"Error: {error}")
    print(f"Components before: {len(analysis['components'])}")
    print(f"Components after: {len(updated['components']) if updated else 0}")
    
    if updated:
        print(f"Total calories before: {analysis['calories_total']}")
        print(f"Total calories after: {updated['calories_total']}")
        print(f"Components: {[c['name'] for c in updated['components']]}")
    
    print()


def test_modify_correction():
    """Test modifying a component"""
    parser = CorrectionParser()
    
    analysis = {
        'dish_name': 'Мясо с гарниром',
        'components': [
            {
                'name': 'Свинина',
                'weight_g': 200,
                'calories': 500,
                'protein_g': 40,
                'fat_g': 30,
                'carbs_g': 0,
                'confidence': 0.80
            },
            {
                'name': 'Рис',
                'weight_g': 150,
                'calories': 195,
                'protein_g': 4,
                'fat_g': 1,
                'carbs_g': 43,
                'confidence': 0.90
            }
        ],
        'weight_grams': 350,
        'calories_total': 695,
        'protein_g': 44,
        'fat_g': 31,
        'carbs_g': 43
    }
    
    # Test modify
    success, updated, error = parser.parse_correction("это курица, а не свинина", analysis)
    
    print("Test Modify Correction:")
    print(f"Success: {success}")
    print(f"Error: {error}")
    
    if updated:
        print(f"Components before: {[c['name'] for c in analysis['components']]}")
        print(f"Components after: {[c['name'] for c in updated['components']]}")
        print(f"Confidence after: {updated['components'][0]['confidence']}")
    
    print()


def test_invalid_correction():
    """Test invalid correction"""
    parser = CorrectionParser()
    
    analysis = {
        'components': [],
        'weight_grams': 0,
        'calories_total': 0
    }
    
    # Test invalid
    success, updated, error = parser.parse_correction("asdfghjkl", analysis)
    
    print("Test Invalid Correction:")
    print(f"Success: {success}")
    print(f"Error: {error}")
    print()


if __name__ == '__main__':
    print("=" * 60)
    print("CORRECTION FLOW TESTS")
    print("=" * 60)
    print()
    
    test_remove_correction()
    test_add_correction()
    test_modify_correction()
    test_invalid_correction()
    
    print("=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)
