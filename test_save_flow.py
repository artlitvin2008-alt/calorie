"""
Quick test for meal save flow
"""
import asyncio
from datetime import datetime
from core.database import Database

async def test_save_meal():
    """Test saving meal and updating stats"""
    db = Database("data/database.db")
    await db.initialize()
    
    # Test data
    user_id = 999999  # Test user
    
    meal_data = {
        'user_id': user_id,
        'session_id': 'test_session_123',
        'dish_name': 'Тестовое блюдо',
        'meal_type': 'lunch',
        'photo_file_id': 'test_photo_id',
        'components': [
            {'name': 'Курица', 'weight_g': 200, 'calories': 330},
            {'name': 'Рис', 'weight_g': 150, 'calories': 195}
        ],
        'total_weight': 350,
        'total_calories': 525,
        'protein_g': 50,
        'fat_g': 10,
        'carbs_g': 45,
        'health_score': 7,
        'confidence_avg': 0.85,
        'corrections_count': 1,
        'eaten_at': datetime.now()
    }
    
    print("Testing meal save...")
    
    # Save meal
    meal_id = await db.save_meal(meal_data)
    print(f"✅ Meal saved with ID: {meal_id}")
    
    # Get daily stats
    today = datetime.now().date()
    stats = await db.get_daily_stats(user_id, today)
    
    if stats:
        print(f"✅ Daily stats found:")
        print(f"   Calories: {stats['calories_consumed']}")
        print(f"   Meals: {stats['meals_count']}")
    else:
        print("Creating daily stats...")
        await db.create_daily_stats(
            user_id=user_id,
            date=today,
            calories_consumed=meal_data['total_calories'],
            protein_consumed=meal_data['protein_g'],
            fat_consumed=meal_data['fat_g'],
            carbs_consumed=meal_data['carbs_g'],
            meals_count=1
        )
        print("✅ Daily stats created")
    
    # Get updated stats
    stats = await db.get_daily_stats(user_id, today)
    print(f"\n📊 Final stats:")
    print(f"   Calories: {stats['calories_consumed']}")
    print(f"   Protein: {stats['protein_consumed']}g")
    print(f"   Fat: {stats['fat_consumed']}g")
    print(f"   Carbs: {stats['carbs_consumed']}g")
    print(f"   Meals: {stats['meals_count']}")
    
    await db.cleanup()
    print("\n✅ Test completed!")

if __name__ == '__main__':
    asyncio.run(test_save_meal())
