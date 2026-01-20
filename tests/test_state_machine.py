"""
Unit tests for state machine
"""
import pytest
import pytest_asyncio
import os
from core.database import Database
from core.state_machine import StateManager, UserState, StateTransition


@pytest_asyncio.fixture
async def setup():
    """Setup test environment"""
    test_db_path = "data/test_state_db.db"
    
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    db = Database(test_db_path)
    await db.initialize()
    await db.create_user(123456, "testuser")
    
    state_manager = StateManager(db)
    
    yield db, state_manager
    
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


@pytest.mark.asyncio
async def test_initial_state(setup):
    """Test initial user state"""
    db, state_manager = setup
    
    state = await state_manager.get_state(123456)
    assert state == UserState.IDLE


@pytest.mark.asyncio
async def test_valid_transition(setup):
    """Test valid state transition"""
    db, state_manager = setup
    
    result = await state_manager.set_state(123456, UserState.ANALYZING_PHOTO)
    assert result is True
    
    state = await state_manager.get_state(123456)
    assert state == UserState.ANALYZING_PHOTO


@pytest.mark.asyncio
async def test_invalid_transition(setup):
    """Test invalid state transition"""
    db, state_manager = setup
    
    # Set to ANALYZING_PHOTO
    await state_manager.set_state(123456, UserState.ANALYZING_PHOTO, validate=False)
    
    # Try invalid transition to REGISTERING
    result = await state_manager.set_state(123456, UserState.REGISTERING, validate=True)
    assert result is False
    
    # State should remain unchanged
    state = await state_manager.get_state(123456)
    assert state == UserState.ANALYZING_PHOTO


@pytest.mark.asyncio
async def test_state_persistence(setup):
    """Test state persistence in database"""
    db, state_manager = setup
    
    await state_manager.set_state(123456, UserState.WAITING_CONFIRMATION)
    
    # Create new state manager (simulating restart)
    new_state_manager = StateManager(db)
    state = await new_state_manager.get_state(123456)
    
    assert state == UserState.WAITING_CONFIRMATION


@pytest.mark.asyncio
async def test_session_data_cache(setup):
    """Test session data caching"""
    db, state_manager = setup
    
    data = {'session_id': 'test_123', 'corrections_count': 2}
    state_manager.set_session_data(123456, data)
    
    retrieved = state_manager.get_session_data(123456)
    assert retrieved == data


@pytest.mark.asyncio
async def test_clear_session_data(setup):
    """Test clearing session data"""
    db, state_manager = setup
    
    state_manager.set_session_data(123456, {'test': 'data'})
    state_manager.clear_session_data(123456)
    
    retrieved = state_manager.get_session_data(123456)
    assert retrieved is None


@pytest.mark.asyncio
async def test_is_in_state(setup):
    """Test state checking"""
    db, state_manager = setup
    
    await state_manager.set_state(123456, UserState.WAITING_CONFIRMATION)
    
    result = await state_manager.is_in_state(
        123456,
        UserState.WAITING_CONFIRMATION,
        UserState.WAITING_CORRECTION
    )
    assert result is True
    
    result = await state_manager.is_in_state(123456, UserState.IDLE)
    assert result is False


@pytest.mark.asyncio
async def test_reset_state(setup):
    """Test state reset"""
    db, state_manager = setup
    
    await state_manager.set_state(123456, UserState.ANALYZING_PHOTO, validate=False)
    await state_manager.reset_state(123456)
    
    state = await state_manager.get_state(123456)
    assert state == UserState.IDLE


def test_state_transitions():
    """Test state transition validation"""
    # Valid transitions
    assert StateTransition.is_valid(UserState.IDLE, UserState.ANALYZING_PHOTO)
    assert StateTransition.is_valid(UserState.ANALYZING_PHOTO, UserState.WAITING_CONFIRMATION)
    assert StateTransition.is_valid(UserState.WAITING_CONFIRMATION, UserState.WAITING_CORRECTION)
    assert StateTransition.is_valid(UserState.WAITING_CORRECTION, UserState.IDLE)
    
    # Invalid transitions
    assert not StateTransition.is_valid(UserState.ANALYZING_PHOTO, UserState.REGISTERING)
    assert not StateTransition.is_valid(UserState.WAITING_CONFIRMATION, UserState.ANALYZING_PHOTO)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
