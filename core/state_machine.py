"""
State machine for user workflow management
"""
from enum import Enum
from typing import Optional, Dict, Any
import logging
from expiringdict import ExpiringDict

logger = logging.getLogger(__name__)


class UserState(Enum):
    """User states in the bot workflow"""
    
    # Core states
    IDLE = "idle"
    REGISTERING = "registering"
    
    # Nutrition states
    WAITING_FOR_PHOTO = "waiting_for_photo"
    ANALYZING_PHOTO = "analyzing_photo"
    WAITING_CONFIRMATION = "waiting_confirmation"
    WAITING_CORRECTION = "waiting_correction"
    
    # Workout states
    CONFIGURING_WORKOUT = "configuring_workout"
    LOGGING_WORKOUT = "logging_workout"
    
    # Motivation states
    CREATING_CONTRACT = "creating_contract"
    DOING_CHECKIN = "doing_checkin"
    
    # Support states
    VIEWING_LESSON = "viewing_lesson"
    EXPORTING_DATA = "exporting_data"


class StateTransition:
    """Defines valid state transitions"""
    
    TRANSITIONS = {
        UserState.IDLE: [
            UserState.REGISTERING,
            UserState.WAITING_FOR_PHOTO,
            UserState.ANALYZING_PHOTO,
            UserState.WAITING_CONFIRMATION,
            UserState.CONFIGURING_WORKOUT,
            UserState.CREATING_CONTRACT,
            UserState.DOING_CHECKIN,
            UserState.VIEWING_LESSON,
            UserState.EXPORTING_DATA,
        ],
        UserState.REGISTERING: [
            UserState.IDLE,
        ],
        UserState.WAITING_FOR_PHOTO: [
            UserState.ANALYZING_PHOTO,
            UserState.IDLE,
        ],
        UserState.ANALYZING_PHOTO: [
            UserState.WAITING_CONFIRMATION,
            UserState.IDLE,
        ],
        UserState.WAITING_CONFIRMATION: [
            UserState.IDLE,
            UserState.WAITING_CORRECTION,
        ],
        UserState.WAITING_CORRECTION: [
            UserState.WAITING_CONFIRMATION,
            UserState.IDLE,
        ],
        UserState.CONFIGURING_WORKOUT: [
            UserState.IDLE,
        ],
        UserState.LOGGING_WORKOUT: [
            UserState.IDLE,
        ],
        UserState.CREATING_CONTRACT: [
            UserState.IDLE,
        ],
        UserState.DOING_CHECKIN: [
            UserState.IDLE,
        ],
        UserState.VIEWING_LESSON: [
            UserState.IDLE,
        ],
        UserState.EXPORTING_DATA: [
            UserState.IDLE,
        ],
    }
    
    @classmethod
    def is_valid(cls, from_state: UserState, to_state: UserState) -> bool:
        """Check if transition is valid"""
        return to_state in cls.TRANSITIONS.get(from_state, [])


class StateManager:
    """Manages user states with in-memory cache and DB persistence"""
    
    def __init__(self, database):
        self.db = database
        # In-memory cache with 30 minute expiration
        self.state_cache: ExpiringDict = ExpiringDict(max_len=10000, max_age_seconds=1800)
        # Session data cache
        self.session_cache: ExpiringDict = ExpiringDict(max_len=10000, max_age_seconds=1800)
    
    async def get_state(self, user_id: int) -> UserState:
        """Get current user state"""
        # Try cache first
        if user_id in self.state_cache:
            return self.state_cache[user_id]
        
        # Fallback to database
        user = await self.db.get_user(user_id)
        if user:
            state = UserState(user['current_state'])
            self.state_cache[user_id] = state
            return state
        
        # Default state for new users
        return UserState.IDLE
    
    async def set_state(self, user_id: int, new_state: UserState, 
                       validate: bool = True) -> bool:
        """Set user state with optional validation"""
        current_state = await self.get_state(user_id)
        
        # Validate transition
        if validate and not StateTransition.is_valid(current_state, new_state):
            logger.warning(
                f"Invalid state transition for user {user_id}: "
                f"{current_state.value} -> {new_state.value}"
            )
            return False
        
        # Update cache
        self.state_cache[user_id] = new_state
        
        # Update database
        await self.db.update_user_state(user_id, new_state.value)
        
        logger.info(f"User {user_id} state: {current_state.value} -> {new_state.value}")
        return True
    
    async def reset_state(self, user_id: int):
        """Reset user to IDLE state"""
        await self.set_state(user_id, UserState.IDLE, validate=False)
    
    def get_session_data(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get session data from cache"""
        return self.session_cache.get(user_id)
    
    def set_session_data(self, user_id: int, data: Dict[str, Any]):
        """Set session data in cache"""
        self.session_cache[user_id] = data
        logger.debug(f"Session data cached for user {user_id}")
    
    def clear_session_data(self, user_id: int):
        """Clear session data from cache"""
        if user_id in self.session_cache:
            del self.session_cache[user_id]
            logger.debug(f"Session data cleared for user {user_id}")
    
    async def is_in_state(self, user_id: int, *states: UserState) -> bool:
        """Check if user is in any of the given states"""
        current_state = await self.get_state(user_id)
        return current_state in states
    
    async def require_state(self, user_id: int, *states: UserState) -> bool:
        """Check if user is in required state, log warning if not"""
        if not await self.is_in_state(user_id, *states):
            current_state = await self.get_state(user_id)
            logger.warning(
                f"User {user_id} not in required state. "
                f"Current: {current_state.value}, Required: {[s.value for s in states]}"
            )
            return False
        return True
