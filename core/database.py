"""
Database layer with async SQLite support
"""
import aiosqlite
import logging
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class Database:
    """Async database wrapper for SQLite"""
    
    def __init__(self, db_path: str = "data/database.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    async def initialize(self):
        """Initialize database with all tables"""
        async with aiosqlite.connect(self.db_path) as db:
            await self._create_tables(db)
            await self._create_indexes(db)
            await db.commit()
        logger.info("Database initialized successfully")
    
    async def _create_tables(self, db: aiosqlite.Connection):
        """Create all tables"""
        
        # Users table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                current_state TEXT DEFAULT 'idle',
                
                -- Goals
                goal TEXT DEFAULT 'weight_loss',
                target_weight REAL,
                start_weight REAL,
                current_weight REAL,
                height INTEGER,
                age INTEGER,
                gender TEXT,
                
                -- Calculated
                daily_calories INTEGER,
                protein_goal INTEGER,
                fat_goal INTEGER,
                carbs_goal INTEGER,
                
                -- Settings
                notifications_enabled BOOLEAN DEFAULT TRUE,
                quiet_hours_start TIME DEFAULT '22:00',
                quiet_hours_end TIME DEFAULT '07:00',
                language TEXT DEFAULT 'ru',
                
                -- Stats
                streak_days INTEGER DEFAULT 0,
                total_workouts INTEGER DEFAULT 0,
                total_meals_logged INTEGER DEFAULT 0,
                
                last_activity TIMESTAMP
            )
        """)
        
        # Meal sessions table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS meal_sessions (
                session_id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                photo_file_id TEXT,
                
                -- Analysis stages (stored as JSON)
                initial_analysis TEXT,
                corrected_analysis TEXT,
                final_analysis TEXT,
                corrections TEXT,
                
                -- Status
                status TEXT DEFAULT 'pending',
                correction_count INTEGER DEFAULT 0,
                confirmed_at TIMESTAMP,
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Meals table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS meals (
                meal_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_id TEXT,
                
                dish_name TEXT,
                meal_type TEXT,
                photo_file_id TEXT,
                components TEXT,
                
                total_weight INTEGER,
                total_calories INTEGER,
                protein_g INTEGER,
                fat_g INTEGER,
                carbs_g INTEGER,
                
                health_score INTEGER,
                confidence_avg REAL,
                corrections_count INTEGER DEFAULT 0,
                
                eaten_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (session_id) REFERENCES meal_sessions(session_id)
            )
        """)
        
        # Food components table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS food_components (
                component_id INTEGER PRIMARY KEY AUTOINCREMENT,
                meal_id INTEGER NOT NULL,
                
                name TEXT NOT NULL,
                weight_g INTEGER,
                calories INTEGER,
                protein_g INTEGER,
                fat_g INTEGER,
                carbs_g INTEGER,
                confidence REAL,
                
                FOREIGN KEY (meal_id) REFERENCES meals(meal_id)
            )
        """)
        
        # Water logs table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS water_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount_ml INTEGER,
                logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Workout plans table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS workout_plans (
                plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                
                plan_name TEXT,
                start_date DATE,
                end_date DATE,
                frequency_per_week INTEGER,
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Workouts table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS workouts (
                workout_id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_id INTEGER,
                user_id INTEGER NOT NULL,
                
                workout_date DATE,
                exercises TEXT,
                duration_minutes INTEGER,
                completed BOOLEAN DEFAULT FALSE,
                
                FOREIGN KEY (plan_id) REFERENCES workout_plans(plan_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Daily stats table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS daily_stats (
                stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date DATE NOT NULL,
                
                calories_consumed INTEGER DEFAULT 0,
                protein_consumed INTEGER DEFAULT 0,
                fat_consumed INTEGER DEFAULT 0,
                carbs_consumed INTEGER DEFAULT 0,
                
                water_ml INTEGER DEFAULT 0,
                steps INTEGER DEFAULT 0,
                
                meals_count INTEGER DEFAULT 0,
                workouts_count INTEGER DEFAULT 0,
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                UNIQUE(user_id, date)
            )
        """)
        
        # Contracts table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS contracts (
                contract_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                
                contract_type TEXT,
                start_date DATE,
                end_date DATE,
                goal_description TEXT,
                
                penalty_type TEXT,
                penalty_details TEXT,
                witness_username TEXT,
                
                active BOOLEAN DEFAULT TRUE,
                violations_count INTEGER DEFAULT 0,
                last_violation DATE,
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Checkins table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS checkins (
                checkin_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                
                morning_mood INTEGER,
                morning_goal TEXT,
                morning_weight REAL,
                morning_time TIMESTAMP,
                
                evening_completed BOOLEAN,
                evening_reflection TEXT,
                evening_mood INTEGER,
                evening_time TIMESTAMP,
                
                checkin_date DATE,
                
                UNIQUE(user_id, checkin_date),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Weight history table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS weight_history (
                record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                weight REAL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Typical dishes table (for realistic comparison)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS typical_dishes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dish_name TEXT NOT NULL,
                category TEXT NOT NULL,
                source TEXT,
                
                -- Nutrition per 100g
                calories_per_100g REAL NOT NULL,
                protein_per_100g REAL NOT NULL,
                fat_per_100g REAL NOT NULL,
                carbs_per_100g REAL NOT NULL,
                
                -- Additional metrics
                sodium_per_100g REAL,
                sugar_per_100g REAL,
                saturated_fat_per_100g REAL,
                fiber_per_100g REAL,
                
                -- Typical portion
                typical_weight_g INTEGER,
                health_score INTEGER,
                
                -- Metadata
                description TEXT,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        logger.info("All tables created")
    
    async def _create_indexes(self, db: aiosqlite.Connection):
        """Create indexes for performance"""
        await db.execute("CREATE INDEX IF NOT EXISTS idx_users_state ON users(current_state)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_meals_user_date ON meals(user_id, eaten_at)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user_status ON meal_sessions(user_id, status)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_checkins_user_date ON checkins(user_id, checkin_date)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_weight_history_user ON weight_history(user_id, recorded_at)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_dishes_category ON typical_dishes(category)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_dishes_name ON typical_dishes(dish_name)")
        logger.info("Indexes created")
    
    # ==================== USER METHODS ====================
    
    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM users WHERE user_id = ?",
                (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
    
    async def create_user(self, user_id: int, username: str = None, 
                         first_name: str = None, last_name: str = None) -> bool:
        """Create new user"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO users (user_id, username, first_name, last_name)
                    VALUES (?, ?, ?, ?)
                """, (user_id, username, first_name, last_name))
                await db.commit()
            logger.info(f"User {user_id} created")
            return True
        except aiosqlite.IntegrityError:
            logger.warning(f"User {user_id} already exists")
            return False
    
    async def update_user(self, user_id: int, **kwargs) -> bool:
        """Update user fields"""
        if not kwargs:
            return False
        
        fields = ", ".join(f"{k} = ?" for k in kwargs.keys())
        values = list(kwargs.values()) + [user_id]
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                f"UPDATE users SET {fields} WHERE user_id = ?",
                values
            )
            await db.commit()
        
        logger.info(f"User {user_id} updated: {kwargs.keys()}")
        return True
    
    async def update_user_state(self, user_id: int, state: str):
        """Update user state"""
        await self.update_user(user_id, current_state=state, last_activity=datetime.now())
    
    # ==================== SESSION METHODS ====================
    
    async def create_session(self, session_id: str, user_id: int, 
                            photo_file_id: str, expires_in_minutes: int = 30) -> bool:
        """Create new meal session"""
        expires_at = datetime.now() + timedelta(minutes=expires_in_minutes)
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO meal_sessions 
                (session_id, user_id, photo_file_id, expires_at)
                VALUES (?, ?, ?, ?)
            """, (session_id, user_id, photo_file_id, expires_at))
            await db.commit()
        
        logger.info(f"Session {session_id} created for user {user_id}")
        return True
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM meal_sessions WHERE session_id = ?",
                (session_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if not row:
                    return None
                
                session = dict(row)
                # Parse JSON fields
                for field in ['initial_analysis', 'corrected_analysis', 'final_analysis']:
                    if session.get(field):
                        session[field] = json.loads(session[field])
                
                return session
    
    async def get_active_session(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get active session for user"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM meal_sessions 
                WHERE user_id = ? AND status != 'completed' AND expires_at > ?
                ORDER BY created_at DESC LIMIT 1
            """, (user_id, datetime.now())) as cursor:
                row = await cursor.fetchone()
                if not row:
                    return None
                
                session = dict(row)
                # Parse JSON fields
                for field in ['initial_analysis', 'corrected_analysis', 'final_analysis']:
                    if session.get(field):
                        session[field] = json.loads(session[field])
                
                return session
    
    async def update_session(self, session_id: str, **kwargs) -> bool:
        """Update session fields"""
        if not kwargs:
            return False
        
        # Convert dict/list fields to JSON
        for key in ['initial_analysis', 'corrected_analysis', 'final_analysis', 'corrections']:
            if key in kwargs and kwargs[key] is not None:
                kwargs[key] = json.dumps(kwargs[key], ensure_ascii=False)
        
        fields = ", ".join(f"{k} = ?" for k in kwargs.keys())
        values = list(kwargs.values()) + [session_id]
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                f"UPDATE meal_sessions SET {fields} WHERE session_id = ?",
                values
            )
            await db.commit()
        
        logger.info(f"Session {session_id} updated")
        return True
    
    async def delete_expired_sessions(self) -> int:
        """Delete expired sessions"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "DELETE FROM meal_sessions WHERE expires_at < ?",
                (datetime.now(),)
            )
            await db.commit()
            deleted = cursor.rowcount
        
        if deleted > 0:
            logger.info(f"Deleted {deleted} expired sessions")
        return deleted
    
    # ==================== MEAL METHODS ====================
    
    async def create_meal(self, user_id: int, session_id: str,
                         total_calories: int, protein_g: int,
                         fat_g: int, carbs_g: int,
                         meal_type: str = None) -> int:
        """Create meal record"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO meals 
                (user_id, session_id, meal_type, total_calories, protein_g, fat_g, carbs_g)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, session_id, meal_type, total_calories, protein_g, fat_g, carbs_g))
            await db.commit()
            meal_id = cursor.lastrowid
        
        # Update user stats
        await self.update_user(user_id, total_meals_logged=f"total_meals_logged + 1")
        
        logger.info(f"Meal {meal_id} created for user {user_id}")
        return meal_id
    
    async def get_meals_today(self, user_id: int) -> List[Dict[str, Any]]:
        """Get today's meals for user"""
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM meals 
                WHERE user_id = ? AND eaten_at >= ?
                ORDER BY eaten_at DESC
            """, (user_id, today_start)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def get_meals_history(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get meal history for user"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM meals 
                WHERE user_id = ?
                ORDER BY eaten_at DESC
                LIMIT ?
            """, (user_id, limit)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def get_daily_calories(self, user_id: int) -> int:
        """Get total calories consumed today"""
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT SUM(total_calories) as total
                FROM meals 
                WHERE user_id = ? AND eaten_at >= ?
            """, (user_id, today_start)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row[0] else 0
    
    async def save_meal(self, meal_data: Dict[str, Any]) -> int:
        """
        Save complete meal with all details
        
        Args:
            meal_data: Dictionary with meal information
        
        Returns:
            meal_id of saved meal
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO meals 
                (user_id, session_id, dish_name, meal_type, photo_file_id,
                 components, total_weight, total_calories, protein_g, fat_g, carbs_g,
                 health_score, confidence_avg, corrections_count, eaten_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                meal_data['user_id'],
                meal_data['session_id'],
                meal_data['dish_name'],
                meal_data['meal_type'],
                meal_data['photo_file_id'],
                json.dumps(meal_data['components'], ensure_ascii=False),
                meal_data['total_weight'],
                meal_data['total_calories'],
                meal_data['protein_g'],
                meal_data['fat_g'],
                meal_data['carbs_g'],
                meal_data['health_score'],
                meal_data['confidence_avg'],
                meal_data['corrections_count'],
                meal_data['eaten_at']
            ))
            await db.commit()
            meal_id = cursor.lastrowid
        
        # Update user stats
        await self.update_user(
            meal_data['user_id'],
            total_meals_logged=f"total_meals_logged + 1"
        )
        
        logger.info(f"Meal {meal_id} saved for user {meal_data['user_id']}")
        return meal_id
    
    # ==================== DAILY STATS METHODS ====================
    
    async def get_daily_stats(self, user_id: int, date: datetime.date) -> Optional[Dict[str, Any]]:
        """Get daily statistics for specific date"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM daily_stats
                WHERE user_id = ? AND date = ?
            """, (user_id, date)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
    
    async def create_daily_stats(
        self,
        user_id: int,
        date: datetime.date,
        calories_consumed: int = 0,
        protein_consumed: int = 0,
        fat_consumed: int = 0,
        carbs_consumed: int = 0,
        meals_count: int = 0
    ) -> bool:
        """Create daily statistics record"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO daily_stats
                (user_id, date, calories_consumed, protein_consumed, 
                 fat_consumed, carbs_consumed, meals_count)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, date, calories_consumed, protein_consumed,
                  fat_consumed, carbs_consumed, meals_count))
            await db.commit()
        
        logger.info(f"Daily stats created for user {user_id} on {date}")
        return True
    
    async def update_daily_stats(
        self,
        user_id: int,
        date: datetime.date,
        calories_consumed: int = None,
        protein_consumed: int = None,
        fat_consumed: int = None,
        carbs_consumed: int = None,
        meals_count: int = None,
        water_ml: int = None,
        steps: int = None,
        workouts_count: int = None
    ) -> bool:
        """Update daily statistics"""
        updates = []
        params = []
        
        if calories_consumed is not None:
            updates.append("calories_consumed = ?")
            params.append(calories_consumed)
        if protein_consumed is not None:
            updates.append("protein_consumed = ?")
            params.append(protein_consumed)
        if fat_consumed is not None:
            updates.append("fat_consumed = ?")
            params.append(fat_consumed)
        if carbs_consumed is not None:
            updates.append("carbs_consumed = ?")
            params.append(carbs_consumed)
        if meals_count is not None:
            updates.append("meals_count = ?")
            params.append(meals_count)
        if water_ml is not None:
            updates.append("water_ml = ?")
            params.append(water_ml)
        if steps is not None:
            updates.append("steps = ?")
            params.append(steps)
        if workouts_count is not None:
            updates.append("workouts_count = ?")
            params.append(workouts_count)
        
        if not updates:
            return False
        
        params.extend([user_id, date])
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(f"""
                UPDATE daily_stats
                SET {', '.join(updates)}
                WHERE user_id = ? AND date = ?
            """, params)
            await db.commit()
        
        logger.info(f"Daily stats updated for user {user_id} on {date}")
        return True
    
    # ==================== UTILITY METHODS ====================
    
    async def cleanup(self):
        """Cleanup expired data"""
        deleted = await self.delete_expired_sessions()
        logger.info(f"Cleanup completed: {deleted} sessions deleted")
    
    # ==================== TYPICAL DISHES METHODS ====================
    
    async def get_typical_dishes(self, category: str = None) -> List[Dict[str, Any]]:
        """Get typical dishes, optionally filtered by category"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            if category:
                query = "SELECT * FROM typical_dishes WHERE category = ?"
                params = (category,)
            else:
                query = "SELECT * FROM typical_dishes"
                params = ()
            
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def search_typical_dishes(self, dish_name: str) -> List[Dict[str, Any]]:
        """Search typical dishes by name"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM typical_dishes 
                WHERE dish_name LIKE ?
                ORDER BY dish_name
            """, (f"%{dish_name}%",)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def add_typical_dish(self, dish_data: Dict[str, Any]) -> int:
        """Add a typical dish to database"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO typical_dishes
                (dish_name, category, source, calories_per_100g, protein_per_100g,
                 fat_per_100g, carbs_per_100g, sodium_per_100g, sugar_per_100g,
                 saturated_fat_per_100g, fiber_per_100g, typical_weight_g,
                 health_score, description, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                dish_data['dish_name'],
                dish_data['category'],
                dish_data.get('source'),
                dish_data['calories_per_100g'],
                dish_data['protein_per_100g'],
                dish_data['fat_per_100g'],
                dish_data['carbs_per_100g'],
                dish_data.get('sodium_per_100g'),
                dish_data.get('sugar_per_100g'),
                dish_data.get('saturated_fat_per_100g'),
                dish_data.get('fiber_per_100g'),
                dish_data.get('typical_weight_g'),
                dish_data['health_score'],
                dish_data.get('description'),
                json.dumps(dish_data.get('tags', []), ensure_ascii=False)
            ))
            await db.commit()
            return cursor.lastrowid
    
    async def count_typical_dishes(self) -> int:
        """Count typical dishes in database"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM typical_dishes") as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0
