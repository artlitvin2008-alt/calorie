"""
Unit tests for database module
"""
import pytest
import pytest_asyncio
import asyncio
import os
from pathlib import Path
from core.database import Database


@pytest_asyncio.fixture
async def db():
    """Create test database"""
    test_db_path = "data/test_database.db"
    
    # Remove existing test db
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    database = Database(test_db_path)
    await database.initialize()
    
    yield database
    
    # Cleanup
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


@pytest.mark.asyncio
async def test_create_user(db):
    """Test user creation"""
    result = await db.create_user(
        user_id=123456,
        username="testuser",
        first_name="Test",
        last_name="User"
    )
    
    assert result is True
    
    # Verify user exists
    user = await db.get_user(123456)
    assert user is not None
    assert user['username'] == "testuser"
    assert user['first_name'] == "Test"
    assert user['current_state'] == 'idle'


@pytest.mark.asyncio
async def test_duplicate_user(db):
    """Test duplicate user creation"""
    await db.create_user(123456, "testuser")
    result = await db.create_user(123456, "testuser")
    
    assert result is False


@pytest.mark.asyncio
async def test_update_user(db):
    """Test user update"""
    await db.create_user(123456, "testuser")
    
    result = await db.update_user(
        123456,
        goal="weight_loss",
        current_weight=85.5,
        target_weight=75.0
    )
    
    assert result is True
    
    user = await db.get_user(123456)
    assert user['goal'] == "weight_loss"
    assert user['current_weight'] == 85.5


@pytest.mark.asyncio
async def test_create_session(db):
    """Test session creation"""
    await db.create_user(123456, "testuser")
    
    result = await db.create_session(
        session_id="test_session_123",
        user_id=123456,
        photo_file_id="photo_123"
    )
    
    assert result is True
    
    session = await db.get_session("test_session_123")
    assert session is not None
    assert session['user_id'] == 123456
    assert session['status'] == 'pending'


@pytest.mark.asyncio
async def test_get_active_session(db):
    """Test getting active session"""
    await db.create_user(123456, "testuser")
    await db.create_session("session_1", 123456, "photo_1")
    
    session = await db.get_active_session(123456)
    assert session is not None
    assert session['session_id'] == "session_1"


@pytest.mark.asyncio
async def test_update_session(db):
    """Test session update"""
    await db.create_user(123456, "testuser")
    await db.create_session("session_1", 123456, "photo_1")
    
    analysis = {
        "components": [{"name": "test", "weight_g": 100}],
        "total_calories": 500
    }
    
    result = await db.update_session(
        "session_1",
        initial_analysis=analysis,
        status="analyzing"
    )
    
    assert result is True
    
    session = await db.get_session("session_1")
    assert session['status'] == "analyzing"
    assert session['initial_analysis']['total_calories'] == 500


@pytest.mark.asyncio
async def test_create_meal(db):
    """Test meal creation"""
    await db.create_user(123456, "testuser")
    await db.create_session("session_1", 123456, "photo_1")
    
    meal_id = await db.create_meal(
        user_id=123456,
        session_id="session_1",
        total_calories=650,
        protein_g=30,
        fat_g=25,
        carbs_g=70
    )
    
    assert meal_id > 0


@pytest.mark.asyncio
async def test_get_meals_today(db):
    """Test getting today's meals"""
    await db.create_user(123456, "testuser")
    await db.create_session("session_1", 123456, "photo_1")
    
    await db.create_meal(123456, "session_1", 500, 20, 15, 60)
    await db.create_meal(123456, "session_1", 700, 30, 25, 80)
    
    meals = await db.get_meals_today(123456)
    assert len(meals) == 2


@pytest.mark.asyncio
async def test_get_daily_calories(db):
    """Test daily calorie calculation"""
    await db.create_user(123456, "testuser")
    await db.create_session("session_1", 123456, "photo_1")
    
    await db.create_meal(123456, "session_1", 500, 20, 15, 60)
    await db.create_meal(123456, "session_1", 700, 30, 25, 80)
    
    total = await db.get_daily_calories(123456)
    assert total == 1200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
