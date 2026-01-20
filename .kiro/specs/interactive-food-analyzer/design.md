# Design Document

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Telegram Bot API                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   Bot Application Layer                      │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────┐    │
│  │  Handlers  │  │   States   │  │  Callback Handlers │    │
│  └────────────┘  └────────────┘  └────────────────────┘    │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                    Core Services Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ State Manager│  │ User Manager │  │ Session Manager  │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   Business Logic Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  Nutrition   │  │   Workout    │  │   Motivation     │  │
│  │   Module     │  │   Module     │  │     Module       │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │  Analytics   │  │   Support    │                        │
│  │   Module     │  │   Module     │                        │
│  └──────────────┘  └──────────────┘                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                    Data Access Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   Database   │  │    Cache     │  │   File Storage   │  │
│  │   (SQLite)   │  │  (In-Memory) │  │     (Photos)     │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   External Services                          │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │  OpenRouter  │  │   Telegram   │                        │
│  │     API      │  │   File API   │                        │
│  └──────────────┘  └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

### Module Structure

#### 1. Core Module
**Purpose:** Foundation services for user management, state management, and session handling

**Components:**
- `UserManager`: CRUD operations for user profiles
- `StateManager`: State machine implementation for user workflows
- `SessionManager`: Active session tracking and timeout management

#### 2. Nutrition Module
**Purpose:** Food analysis, meal tracking, and calorie calculation

**Components:**
- `PhotoAnalyzer`: AI-powered food recognition via OpenRouter
- `CorrectionParser`: Natural language processing for user corrections
- `MealTracker`: Daily meal logging and history
- `WaterTracker`: Water intake monitoring
- `CalorieCalculator`: Nutritional value computation

#### 3. Workout Module
**Purpose:** Personalized workout generation and progress tracking

**Components:**
- `WorkoutGenerator`: Creates customized workout plans
- `ExerciseLibrary`: Database of exercises with metadata
- `ProgressTracker`: Tracks weights, reps, and improvements
- `WorkoutScheduler`: Manages workout calendar

#### 4. Motivation Module
**Purpose:** User commitment, accountability, and anti-fail mechanisms

**Components:**
- `ContractManager`: Creates and enforces user commitments
- `CheckinSystem`: Daily morning/evening check-ins
- `AntiFail`: Crisis intervention and support protocols
- `PenaltyEngine`: Applies consequences for violations

#### 5. Analytics Module
**Purpose:** Progress visualization, pattern detection, and predictions

**Components:**
- `ProgressVisualizer`: Generates charts and graphs
- `PatternDetector`: Identifies behavioral patterns
- `GoalPredictor`: Estimates goal achievement timeline
- `ReportGenerator`: Weekly/monthly summary reports

#### 6. Support Module
**Purpose:** Education, notifications, and user assistance

**Components:**
- `EducationSystem`: Daily micro-lessons delivery
- `NotificationManager`: Scheduled reminders and alerts
- `KnowledgeBase`: FAQ and educational content
- `DataExporter`: User data export functionality

## State Machine Design

### User States

```python
class UserState(Enum):
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
```

### State Transitions

```
IDLE
  ├─> REGISTERING (on /start, first time)
  ├─> WAITING_FOR_PHOTO (on photo received)
  ├─> CONFIGURING_WORKOUT (on /workout)
  ├─> CREATING_CONTRACT (on /create_contract)
  └─> DOING_CHECKIN (on scheduled time)

WAITING_FOR_PHOTO
  └─> ANALYZING_PHOTO (photo received)

ANALYZING_PHOTO
  └─> WAITING_CONFIRMATION (analysis complete)

WAITING_CONFIRMATION
  ├─> IDLE (on confirm button)
  └─> WAITING_CORRECTION (on text message)

WAITING_CORRECTION
  ├─> IDLE (on confirm after correction)
  ├─> WAITING_CORRECTION (on additional correction)
  └─> IDLE (after 3 corrections, forced)
```

## Database Schema

### Tables Overview

```sql
-- Core tables
users
user_sessions

-- Nutrition tables
meal_sessions
meals
food_components
water_logs

-- Workout tables
workout_plans
workouts
exercises
exercise_logs

-- Motivation tables
contracts
checkins
penalties

-- Analytics tables
weight_history
progress_photos
reports

-- Support tables
lessons_delivered
notifications_sent
```

### Detailed Schema

#### users table
```sql
CREATE TABLE users (
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
);
```

#### meal_sessions table
```sql
CREATE TABLE meal_sessions (
    session_id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    photo_file_id TEXT,
    photo_base64 TEXT,
    
    -- Analysis stages
    initial_analysis JSON,
    corrected_analysis JSON,
    final_analysis JSON,
    
    -- Status
    status TEXT DEFAULT 'pending',
    corrections_count INTEGER DEFAULT 0,
    confirmed_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

#### meals table
```sql
CREATE TABLE meals (
    meal_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_id TEXT,
    
    meal_type TEXT,
    total_calories INTEGER,
    protein_g INTEGER,
    fat_g INTEGER,
    carbs_g INTEGER,
    
    eaten_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (session_id) REFERENCES meal_sessions(session_id)
);
```

#### contracts table
```sql
CREATE TABLE contracts (
    contract_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    
    contract_type TEXT,
    start_date DATE,
    end_date DATE,
    goal_description TEXT,
    
    penalty_type TEXT,
    penalty_details JSON,
    witness_username TEXT,
    
    active BOOLEAN DEFAULT TRUE,
    violations_count INTEGER DEFAULT 0,
    last_violation DATE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

#### checkins table
```sql
CREATE TABLE checkins (
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
);
```

## API Integration Design

### OpenRouter API Client

```python
class OpenRouterClient:
    """Client for OpenRouter API interactions"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = "qwen/qwen-2-vl-7b-instruct:free"
    
    async def analyze_food_photo(
        self, 
        photo_base64: str,
        mode: str = "initial"
    ) -> dict:
        """
        Analyze food photo
        
        Args:
            photo_base64: Base64 encoded image
            mode: "initial" or "correction"
        
        Returns:
            Analysis result with components
        """
        pass
    
    async def parse_correction(
        self,
        correction_text: str,
        current_analysis: dict
    ) -> dict:
        """
        Parse user correction using AI
        
        Args:
            correction_text: User's correction message
            current_analysis: Current analysis state
        
        Returns:
            Parsed corrections with actions
        """
        pass
```

### Prompts Design

#### Initial Analysis Prompt
```python
INITIAL_ANALYSIS_PROMPT = """
Ты - эксперт по питанию. Проанализируй фото еды и верни JSON:

{
  "components": [
    {
      "name": "точное название блюда",
      "weight_g": примерный_вес,
      "confidence": 0.0-1.0,
      "category": "main/side/drink/bread/sauce"
    }
  ],
  "total_weight_g": общий_вес,
  "assumptions": [
    "предположение о составе",
    "предположение о приготовлении"
  ]
}

ВАЖНО:
- Найди ВСЕ компоненты (включая хлеб, соусы, напитки)
- Используй столовые приборы для оценки размера
- Будь консервативен в оценках веса
- Указывай confidence < 0.6 если не уверен
"""
```

#### Correction Parsing Prompt
```python
CORRECTION_PROMPT = """
Пользователь внес правки: "{correction_text}"

Текущий анализ:
{current_analysis}

Определи какие действия нужно выполнить и верни JSON:

{
  "corrections": [
    {
      "action": "remove|modify|add",
      "target": "название_компонента",
      "new_value": "новое_значение (для modify/add)",
      "weight_g": вес (для add)
    }
  ]
}

Правила:
- "нет X", "убери X" → remove
- "добавь X" → add
- "это Y, а не X" → modify
- "X больше/меньше" → modify weight
"""
```

## Component Interactions

### Nutrition Flow

```
User sends photo
    ↓
PhotoAnalyzer.analyze()
    ↓
OpenRouterClient.analyze_food_photo()
    ↓
Store in meal_sessions (status: pending)
    ↓
Display preliminary analysis + button
    ↓
User clicks confirm OR sends correction
    ↓
If correction:
    CorrectionParser.parse()
    ↓
    Apply corrections
    ↓
    Update meal_sessions
    ↓
    Display updated analysis + button
    ↓
If confirm:
    CalorieCalculator.calculate()
    ↓
    Store in meals table
    ↓
    Display final analysis
```

### Workout Flow

```
User requests workout
    ↓
WorkoutGenerator.generate()
    ↓
Collect user preferences
    ↓
Query ExerciseLibrary
    ↓
Create workout plan
    ↓
Store in workout_plans
    ↓
Display today's workout
    ↓
User logs completion
    ↓
ProgressTracker.log()
    ↓
Update exercise_logs
    ↓
Analyze progress
    ↓
Suggest weight increases
```

### Contract Flow

```
User creates contract
    ↓
ContractManager.create()
    ↓
Select contract type
    ↓
Choose penalty
    ↓
Store in contracts
    ↓
Daily monitoring
    ↓
CheckinSystem checks compliance
    ↓
If violation:
    PenaltyEngine.apply()
    ↓
    Notify user
    ↓
    Update violations_count
```

## Error Handling Strategy

### Error Categories

1. **User Errors**
   - Invalid input
   - Missing required data
   - Out of sequence actions

2. **System Errors**
   - Database connection failures
   - API timeouts
   - State corruption

3. **External Errors**
   - OpenRouter API failures
   - Telegram API issues
   - Network problems

### Error Handling Patterns

```python
class ErrorHandler:
    """Centralized error handling"""
    
    @staticmethod
    async def handle_user_error(error: UserError, update: Update):
        """Send helpful message to user"""
        await update.message.reply_text(
            f"❌ {error.message}\n\n"
            f"💡 {error.suggestion}"
        )
    
    @staticmethod
    async def handle_api_error(error: APIError, retry_count: int):
        """Retry with exponential backoff"""
        if retry_count < 3:
            await asyncio.sleep(2 ** retry_count)
            return True  # Retry
        return False  # Give up
    
    @staticmethod
    async def handle_system_error(error: SystemError):
        """Log and notify admin"""
        logger.critical(f"System error: {error}")
        # Send alert to admin
```

## Performance Considerations

### Caching Strategy

```python
class CacheManager:
    """In-memory cache for active sessions"""
    
    def __init__(self):
        self.sessions = {}  # user_id -> session_data
        self.ttl = 1800  # 30 minutes
    
    def get_session(self, user_id: int) -> Optional[dict]:
        """Get active session from cache"""
        pass
    
    def set_session(self, user_id: int, data: dict):
        """Store session in cache"""
        pass
    
    def cleanup_expired(self):
        """Remove expired sessions"""
        pass
```

### Database Optimization

- Indexes on frequently queried columns
- Prepared statements for common queries
- Connection pooling
- Batch inserts for analytics

```sql
-- Performance indexes
CREATE INDEX idx_users_state ON users(current_state);
CREATE INDEX idx_meals_user_date ON meals(user_id, eaten_at);
CREATE INDEX idx_sessions_user_status ON meal_sessions(user_id, status);
CREATE INDEX idx_checkins_user_date ON checkins(user_id, checkin_date);
```

## Security Considerations

### Data Protection

1. **API Keys**: Store in environment variables, never in code
2. **User Data**: Encrypt sensitive information
3. **Photos**: Auto-delete after 7 days
4. **Database**: Regular backups, transaction safety

### Input Validation

```python
class Validator:
    """Input validation utilities"""
    
    @staticmethod
    def validate_weight(weight: float) -> bool:
        """Validate weight is reasonable"""
        return 30 <= weight <= 300
    
    @staticmethod
    def validate_calories(calories: int) -> bool:
        """Validate calorie count"""
        return 0 <= calories <= 10000
    
    @staticmethod
    def sanitize_text(text: str) -> str:
        """Remove potentially harmful content"""
        return text.strip()[:1000]
```

## Deployment Architecture

### Production Setup

```
┌─────────────────────────────────────┐
│         Load Balancer (nginx)       │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      Bot Application (Python)       │
│  ┌──────────────────────────────┐  │
│  │  Main Process (polling)      │  │
│  └──────────────────────────────┘  │
│  ┌──────────────────────────────┐  │
│  │  Background Jobs (scheduler) │  │
│  └──────────────────────────────┘  │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      SQLite Database (persistent)   │
└─────────────────────────────────────┘
```

### Monitoring

- Application logs (rotating files)
- Error tracking (Sentry or similar)
- Performance metrics (response times)
- User activity metrics

## Testing Strategy

### Unit Tests
- Individual component testing
- Mock external dependencies
- Test edge cases

### Integration Tests
- Full workflow testing
- Database interactions
- API integrations

### End-to-End Tests
- Simulate real user interactions
- Test complete flows
- Verify state transitions

## Configuration Management

```python
# config.py
class Config:
    # Telegram
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    
    # OpenRouter
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
    OPENROUTER_MODEL = 'qwen/qwen-2-vl-7b-instruct:free'
    
    # Database
    DATABASE_PATH = 'data/database.db'
    
    # Session
    SESSION_TIMEOUT = 1800  # 30 minutes
    MAX_CORRECTIONS = 3
    
    # Notifications
    MORNING_CHECKIN_TIME = '08:00'
    EVENING_CHECKIN_TIME = '21:00'
    WATER_REMINDER_INTERVAL = 7200  # 2 hours
    
    # Limits
    MAX_PHOTO_SIZE_MB = 5
    MAX_COMPONENTS = 10
    MIN_CONFIDENCE = 0.4
```

This design provides a solid foundation for implementing the fitness coach bot with all required modules and proper separation of concerns.
