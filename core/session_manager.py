"""
Session manager for tracking active user sessions
"""
import uuid
import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages meal analysis sessions"""
    
    def __init__(self, database, state_manager):
        self.db = database
        self.state_manager = state_manager
    
    def generate_session_id(self) -> str:
        """Generate unique session ID"""
        return f"session_{uuid.uuid4().hex[:16]}"
    
    async def create_session(self, user_id: int, photo_file_id: str) -> str:
        """Create new meal analysis session"""
        session_id = self.generate_session_id()
        
        # Create in database
        await self.db.create_session(
            session_id=session_id,
            user_id=user_id,
            photo_file_id=photo_file_id,
            expires_in_minutes=30
        )
        
        # Cache session data
        self.state_manager.set_session_data(user_id, {
            'session_id': session_id,
            'photo_file_id': photo_file_id,
            'created_at': datetime.now().isoformat(),
            'corrections_count': 0
        })
        
        logger.info(f"Created session {session_id} for user {user_id}")
        return session_id
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID"""
        return await self.db.get_session(session_id)
    
    async def get_active_session(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get active session for user"""
        # Try cache first
        cached = self.state_manager.get_session_data(user_id)
        if cached and 'session_id' in cached:
            session = await self.db.get_session(cached['session_id'])
            if session and session['status'] != 'completed':
                return session
        
        # Fallback to database
        return await self.db.get_active_session(user_id)
    
    async def update_session(self, session_id: str, **kwargs) -> bool:
        """Update session data"""
        return await self.db.update_session(session_id, **kwargs)
    
    async def save_initial_analysis(self, session_id: str, analysis: Dict[str, Any]) -> bool:
        """Save initial analysis to session"""
        return await self.update_session(
            session_id,
            initial_analysis=analysis,
            status='pending'
        )
    
    async def get_current_analysis(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get current analysis (corrected if exists, otherwise initial)"""
        session = await self.get_session(session_id)
        if not session:
            return None
        
        # Return corrected analysis if exists, otherwise initial
        if session.get('corrected_analysis'):
            return session['corrected_analysis']
        return session.get('initial_analysis')
    
    async def save_correction(self, session_id: str, correction_text: str,
                             corrected_analysis: Dict[str, Any]) -> bool:
        """Save correction and updated analysis"""
        session = await self.get_session(session_id)
        if not session:
            return False
        
        # Get current corrections (parse JSON if string)
        corrections = session.get('corrections')
        if corrections is None:
            corrections = []
        elif isinstance(corrections, str):
            import json
            try:
                corrections = json.loads(corrections)
            except:
                corrections = []
        
        corrections.append({
            'text': correction_text,
            'timestamp': datetime.now().isoformat()
        })
        
        # Update session
        return await self.update_session(
            session_id,
            corrected_analysis=corrected_analysis,
            corrections=corrections,
            correction_count=len(corrections)
        )
    
    async def complete_session(self, session_id: str, final_analysis: Dict[str, Any]) -> bool:
        """Mark session as completed"""
        return await self.update_session(
            session_id,
            final_analysis=final_analysis,
            status='completed',
            confirmed_at=datetime.now()
        )
    
    async def cancel_session(self, user_id: int) -> bool:
        """Cancel active session for user"""
        session = await self.get_active_session(user_id)
        if not session:
            return False
        
        await self.update_session(session['session_id'], status='cancelled')
        self.state_manager.clear_session_data(user_id)
        
        logger.info(f"Cancelled session for user {user_id}")
        return True
    
    async def cleanup_expired(self) -> int:
        """Cleanup expired sessions"""
        return await self.db.delete_expired_sessions()
    
    def get_corrections_count(self, user_id: int) -> int:
        """Get number of corrections made in current session"""
        cached = self.state_manager.get_session_data(user_id)
        if cached:
            return cached.get('corrections_count', 0)
        return 0
    
    def increment_corrections(self, user_id: int):
        """Increment corrections counter"""
        cached = self.state_manager.get_session_data(user_id)
        if cached:
            cached['corrections_count'] = cached.get('corrections_count', 0) + 1
            self.state_manager.set_session_data(user_id, cached)
