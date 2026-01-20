"""
Test keyboard utilities
"""
from utils.keyboards import (
    create_confirmation_keyboard,
    create_goal_keyboard,
    create_gender_keyboard,
    create_meal_type_keyboard,
    create_yes_no_keyboard,
    create_analysis_actions_keyboard,
    parse_callback_data,
    build_callback_data
)


def test_keyboards():
    """Test all keyboard functions"""
    print("Testing keyboards...\n")
    
    # Test confirmation keyboard
    kb = create_confirmation_keyboard()
    print(f"✅ Confirmation keyboard: {len(kb.inline_keyboard)} rows")
    
    # Test goal keyboard
    kb = create_goal_keyboard()
    print(f"✅ Goal keyboard: {len(kb.inline_keyboard)} rows")
    
    # Test gender keyboard
    kb = create_gender_keyboard()
    print(f"✅ Gender keyboard: {len(kb.inline_keyboard)} rows")
    
    # Test meal type keyboard
    kb = create_meal_type_keyboard()
    print(f"✅ Meal type keyboard: {len(kb.inline_keyboard)} rows")
    
    # Test yes/no keyboard
    kb = create_yes_no_keyboard("yes_action", "no_action")
    print(f"✅ Yes/No keyboard: {len(kb.inline_keyboard)} rows")
    
    # Test analysis actions keyboard
    kb = create_analysis_actions_keyboard()
    print(f"✅ Analysis actions keyboard: {len(kb.inline_keyboard)} rows")
    
    print("\nTesting callback data parsing...\n")
    
    # Test parse_callback_data
    test_cases = [
        "goal_weight_loss",
        "gender_male",
        "confirm_analysis",
        "meal_breakfast",
        "cancel_action"
    ]
    
    for data in test_cases:
        action, value = parse_callback_data(data)
        print(f"  '{data}' → action='{action}', value='{value}'")
    
    print("\nTesting callback data building...\n")
    
    # Test build_callback_data
    test_cases = [
        ("goal", "weight_loss"),
        ("gender", "male"),
        ("confirm", "analysis"),
        ("meal", "breakfast"),
        ("cancel", "action")
    ]
    
    for action, value in test_cases:
        data = build_callback_data(action, value)
        print(f"  action='{action}', value='{value}' → '{data}'")
    
    print("\n✅ All keyboard tests passed!")


if __name__ == "__main__":
    test_keyboards()
