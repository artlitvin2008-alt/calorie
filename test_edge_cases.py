"""
Test edge cases and error scenarios
"""
import asyncio
from core.database import Database
from core.state_machine import StateManager, UserState
from modules.nutrition.correction_parser import CorrectionParser
from utils.validators import CorrectionValidator, UserInputValidator

async def test_edge_cases():
    """Test various edge cases"""
    print("=" * 60)
    print("EDGE CASES TESTING")
    print("=" * 60)
    
    # Test 1: Empty/Invalid inputs
    print("\n1. Testing Invalid Inputs...")
    
    validator = UserInputValidator()
    
    # Invalid weight
    valid, value, error = validator.validate_weight("-10")
    print(f"   Weight -10: {'❌' if not valid else '✅'} {error}")
    
    valid, value, error = validator.validate_weight("500")
    print(f"   Weight 500: {'❌' if not valid else '✅'} {error}")
    
    # Invalid height
    valid, value, error = validator.validate_height("50")
    print(f"   Height 50: {'❌' if not valid else '✅'} {error}")
    
    # Invalid age
    valid, value, error = validator.validate_age("5")
    print(f"   Age 5: {'❌' if not valid else '✅'} {error}")
    
    # Test 2: Correction edge cases
    print("\n2. Testing Correction Edge Cases...")
    
    parser = CorrectionParser()
    
    # Empty analysis
    empty_analysis = {'components': [], 'weight_grams': 0, 'calories_total': 0}
    success, updated, error = parser.parse_correction("нет хлеба", empty_analysis)
    print(f"   Remove from empty: {'✅' if not success else '❌'} {error}")
    
    # Very long correction
    long_text = "добавь " + "салат " * 100
    corr_validator = CorrectionValidator()
    valid, error = corr_validator.validate_correction(long_text)
    print(f"   Long correction: {'❌' if not valid else '✅'} {error}")
    
    # Special characters
    special = "добавь салат!@#$%^&*()"
    valid, error = corr_validator.validate_correction(special)
    print(f"   Special chars: {'✅' if valid else '❌'}")
    
    # Test 3: Database edge cases
    print("\n3. Testing Database Edge Cases...")
    
    db = Database("data/database.db")
    await db.initialize()
    
    # Non-existent user
    user = await db.get_user(999999999)
    print(f"   Non-existent user: {'✅' if user is None else '❌'}")
    
    # Non-existent session
    from core.session_manager import SessionManager
    state_manager = StateManager(db)
    session_manager = SessionManager(db, state_manager)
    
    session = await session_manager.get_session("invalid_session_id")
    print(f"   Non-existent session: {'✅' if session is None else '❌'}")
    
    # Test 4: State transitions
    print("\n4. Testing Invalid State Transitions...")
    
    test_user = 777777
    
    # Try invalid transition
    await state_manager.set_state(test_user, UserState.IDLE, validate=False)
    current = await state_manager.get_state(test_user)
    print(f"   Initial state: {current}")
    
    # Try to go from IDLE to WAITING_CONFIRMATION (invalid)
    try:
        await state_manager.set_state(test_user, UserState.WAITING_CONFIRMATION)
        print(f"   Invalid transition: ❌ Should have failed")
    except:
        print(f"   Invalid transition blocked: ✅")
    
    # Test 5: Extreme values
    print("\n5. Testing Extreme Values...")
    
    # Very high calories
    extreme_analysis = {
        'components': [{'name': 'Test', 'weight_g': 10000, 'calories': 50000}],
        'weight_grams': 10000,
        'calories_total': 50000,
        'protein_g': 1000,
        'fat_g': 1000,
        'carbs_g': 1000
    }
    
    from utils.validators import FoodAnalysisValidator
    food_validator = FoodAnalysisValidator()
    valid, error = food_validator.validate_analysis(extreme_analysis)
    print(f"   Extreme calories: {'❌' if not valid else '✅'} {error if error else 'OK'}")
    
    await db.cleanup()
    
    print("\n" + "=" * 60)
    print("✅ EDGE CASES TESTING COMPLETED")
    print("=" * 60)

if __name__ == '__main__':
    asyncio.run(test_edge_cases())
