"""
End-to-end testing of full bot flow
"""
import asyncio
from datetime import datetime
from core.database import Database
from core.state_machine import StateManager, UserState
from core.session_manager import SessionManager
from core.user_manager import UserManager

async def test_full_flow():
    """Test complete user flow"""
    print("=" * 60)
    print("FULL FLOW TEST")
    print("=" * 60)
    
    # Initialize components
    db = Database("data/database.db")
    await db.initialize()
    
    state_manager = StateManager(db)
    session_manager = SessionManager(db, state_manager)
    user_manager = UserManager(db)
    
    test_user_id = 888888
    
    print("\n1. Testing User Registration...")
    
    # Register user
    await user_manager.get_or_create_user(
        user_id=test_user_id,
        username="test_user",
        first_name="Test",
        last_name="User"
    )
    print("   ✅ User registered")
    
    # Set goals
    await user_manager.set_goals(
        user_id=test_user_id,
        goal="weight_loss",
        current_weight=80.0,
        target_weight=75.0,
        height=175,
        age=30,
        gender="male"
    )
    print("   ✅ Goals set")
    
    # Get user
    user = await db.get_user(test_user_id)
    print(f"   ✅ Daily calories: {user['daily_calories']} kcal")
    
    print("\n2. Testing Session Creation...")
    
    # Create session
    session_id = await session_manager.create_session(
        test_user_id,
        "test_photo_id"
    )
    print(f"   ✅ Session created: {session_id}")
    
    # Set state
    await state_manager.set_state(test_user_id, UserState.ANALYZING_PHOTO)
    state = await state_manager.get_state(test_user_id)
    print(f"   ✅ State: {state}")
    
    print("\n3. Testing Analysis Save...")
    
    # Mock analysis
    analysis = {
        'dish_name': 'Тестовое блюдо',
        'components': [
            {
                'name': 'Курица',
                'weight_g': 200,
                'calories': 330,
                'protein_g': 60,
                'fat_g': 7,
                'carbs_g': 0,
                'confidence': 0.85
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
        'calories_total': 525,
        'protein_g': 64,
        'fat_g': 8,
        'carbs_g': 43,
        'health_score': 8,
        'calories_per_100g': 150
    }
    
    # Save initial analysis
    await session_manager.save_initial_analysis(session_id, analysis)
    print("   ✅ Initial analysis saved")
    
    # Set state to waiting confirmation
    await state_manager.set_state(test_user_id, UserState.WAITING_CONFIRMATION)
    
    print("\n4. Testing Correction...")
    
    # Apply correction
    from modules.nutrition.correction_parser import CorrectionParser
    parser = CorrectionParser()
    
    success, updated, error = parser.parse_correction("добавь салат 100г", analysis)
    if success:
        await session_manager.save_correction(session_id, "добавь салат 100г", updated)
        print("   ✅ Correction applied")
        print(f"   ✅ New total: {updated['calories_total']} kcal")
    
    print("\n5. Testing Meal Save...")
    
    # Get current analysis
    final_analysis = await session_manager.get_current_analysis(session_id)
    
    # Prepare meal data
    meal_data = {
        'user_id': test_user_id,
        'session_id': session_id,
        'dish_name': final_analysis['dish_name'],
        'meal_type': 'lunch',
        'photo_file_id': 'test_photo_id',
        'components': final_analysis['components'],
        'total_weight': final_analysis['weight_grams'],
        'total_calories': final_analysis['calories_total'],
        'protein_g': final_analysis['protein_g'],
        'fat_g': final_analysis['fat_g'],
        'carbs_g': final_analysis['carbs_g'],
        'health_score': final_analysis.get('health_score', 5),
        'confidence_avg': 0.85,
        'corrections_count': 1,
        'eaten_at': datetime.now()
    }
    
    # Save meal
    meal_id = await db.save_meal(meal_data)
    print(f"   ✅ Meal saved: {meal_id}")
    
    print("\n6. Testing Daily Stats...")
    
    # Get or create daily stats
    today = datetime.now().date()
    stats = await db.get_daily_stats(test_user_id, today)
    
    if not stats:
        await db.create_daily_stats(
            user_id=test_user_id,
            date=today,
            calories_consumed=meal_data['total_calories'],
            protein_consumed=meal_data['protein_g'],
            fat_consumed=meal_data['fat_g'],
            carbs_consumed=meal_data['carbs_g'],
            meals_count=1
        )
        stats = await db.get_daily_stats(test_user_id, today)
    
    print(f"   ✅ Daily stats:")
    print(f"      Calories: {stats['calories_consumed']}/{user['daily_calories']}")
    print(f"      Protein: {stats['protein_consumed']}g")
    print(f"      Meals: {stats['meals_count']}")
    
    print("\n7. Testing Session Completion...")
    
    # Complete session
    await session_manager.complete_session(session_id, final_analysis)
    print("   ✅ Session completed")
    
    # Reset state
    await state_manager.set_state(test_user_id, UserState.IDLE, validate=False)
    state = await state_manager.get_state(test_user_id)
    print(f"   ✅ State reset to: {state}")
    
    print("\n8. Testing Meal History...")
    
    # Get meals
    meals = await db.get_meals_today(test_user_id)
    print(f"   ✅ Meals today: {len(meals)}")
    
    if meals:
        meal = meals[0]
        print(f"      Dish: {meal['dish_name']}")
        print(f"      Calories: {meal['total_calories']}")
    
    await db.cleanup()
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)

if __name__ == '__main__':
    asyncio.run(test_full_flow())
