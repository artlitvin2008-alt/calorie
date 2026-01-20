# 🛠️ Telegram Fitness Coach Bot - Developer Guide

## 📋 Table of Contents
- [Architecture](#architecture)
- [Setup](#setup)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [API Integration](#api-integration)
- [Testing](#testing)
- [Deployment](#deployment)

## 🏗️ Architecture

### Tech Stack
- **Python:** 3.9+
- **Framework:** python-telegram-bot (async)
- **Database:** SQLite + aiosqlite
- **AI:** OpenRouter API (qwen-2-vl-7b)
- **Image:** PIL/Pillow

### Design Patterns
- **State Machine:** User flow control
- **Session Management:** Tracking analysis sessions
- **Repository Pattern:** Database abstraction
- **Async/Await:** Throughout the codebase

### Core Components

```
┌─────────────────┐
│  Telegram Bot   │
└────────┬────────┘
         │
    ┌────▼────┐
    │ Handlers│
    └────┬────┘
         │
    ┌────▼────────────────┐
    │  State Machine      │
    │  Session Manager    │
    │  User Manager       │
    └────┬────────────────┘
         │
    ┌────▼────┐
    │Database │
    └─────────┘
```

## 🚀 Setup

### Prerequisites
```bash
python 3.9+
pip
virtualenv (recommended)
```

### Installation

1. Clone repository
```bash
git clone <repo>
cd calories
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure environment
```bash
cp .env.example .env
# Edit .env with your tokens
```

Required in `.env`:
```
TELEGRAM_BOT_TOKEN=your_bot_token
OPENROUTER_API_KEY=your_api_key
USE_MOCK_API=false
```

5. Initialize database
```bash
python init_db.py
```

6. Run bot
```bash
python main_new.py
```

## 📁 Project Structure

```
calories/
├── core/                    # Core business logic
│   ├── database.py         # Database wrapper (500+ lines)
│   ├── state_machine.py    # State management
│   ├── session_manager.py  # Session tracking
│   └── user_manager.py     # User operations
│
├── handlers/               # Telegram handlers
│   ├── commands.py         # Command handlers
│   ├── registration.py     # User registration
│   ├── callbacks.py        # Button callbacks
│   ├── photos.py           # Photo analysis
│   ├── corrections.py      # Text corrections
│   └── meal_confirmation.py # Meal saving
│
├── modules/nutrition/      # Nutrition logic
│   ├── photo_analyzer.py   # AI photo analysis
│   ├── calorie_calculator.py # Calorie calculations
│   └── correction_parser.py  # Correction parsing
│
├── utils/                  # Utilities
│   ├── validators.py       # Input validation
│   ├── formatters.py       # Message formatting (400+ lines)
│   ├── keyboards.py        # Inline keyboards
│   └── display_helpers.py  # Display utilities
│
├── tests/                  # Test suite
│   ├── test_database.py
│   ├── test_state_machine.py
│   ├── test_validators.py
│   ├── test_calorie_calculator.py
│   ├── test_correction_flow.py
│   ├── test_full_flow.py
│   └── test_edge_cases.py
│
├── data/                   # Data directory
│   └── database.db         # SQLite database
│
├── main_new.py            # Bot entry point
├── config.py              # Configuration
├── init_db.py             # Database initialization
└── requirements.txt       # Dependencies
```

## 🗄️ Database Schema

### Tables (12 total)

#### users
```sql
user_id INTEGER PRIMARY KEY
username, first_name, last_name
goal, current_weight, target_weight
height, age, gender
daily_calories, protein_goal, fat_goal, carbs_goal
```

#### meal_sessions
```sql
session_id TEXT PRIMARY KEY
user_id, photo_file_id
initial_analysis, corrected_analysis, final_analysis (JSON)
corrections (JSON)
status, correction_count
created_at, expires_at
```

#### meals
```sql
meal_id INTEGER PRIMARY KEY
user_id, session_id
dish_name, meal_type, photo_file_id
components (JSON)
total_weight, total_calories
protein_g, fat_g, carbs_g
health_score, confidence_avg
corrections_count
eaten_at
```

#### daily_stats
```sql
stat_id INTEGER PRIMARY KEY
user_id, date
calories_consumed, protein_consumed
fat_consumed, carbs_consumed
water_ml, steps
meals_count, workouts_count
```

## 🤖 API Integration

### OpenRouter API

**Endpoint:** `https://openrouter.ai/api/v1/chat/completions`

**Model:** `qwen/qwen-2-vl-7b-instruct:free`

**Request:**
```python
{
    "model": "qwen/qwen-2-vl-7b-instruct:free",
    "messages": [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Analyze this food"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]
        }
    ],
    "temperature": 0.1,
    "max_tokens": 2000
}
```

**Response:**
```json
{
    "dish_name": "Пельмени со сметаной",
    "components": [
        {
            "name": "Пельмени",
            "weight_g": 250,
            "calories": 625,
            "protein_g": 30,
            "fat_g": 25,
            "carbs_g": 70,
            "confidence": 0.85
        }
    ],
    "weight_grams": 280,
    "calories_total": 685,
    "health_score": 5
}
```

### Mock Mode

For testing without API calls:
```python
USE_MOCK_API=true
```

Returns predefined analysis data.

## 🧪 Testing

### Run all tests
```bash
pytest tests/
```

### Run specific test
```bash
python test_full_flow.py
python test_edge_cases.py
```

### Test Coverage
- Unit tests: 46+
- Integration tests: 2
- Edge case tests: 1

### Test Categories

**Unit Tests:**
- Database operations
- State transitions
- Validators
- Calorie calculations

**Integration Tests:**
- Full user flow
- End-to-end scenarios

**Edge Cases:**
- Invalid inputs
- Extreme values
- Error scenarios

## 🚀 Deployment

### Production Checklist

- [ ] Set `USE_MOCK_API=false`
- [ ] Configure real API keys
- [ ] Set up logging
- [ ] Configure database backups
- [ ] Set up monitoring
- [ ] Configure error alerts

### Running in Production

**Option 1: systemd service**
```bash
sudo systemctl start fitness-bot
sudo systemctl enable fitness-bot
```

**Option 2: Docker**
```bash
docker build -t fitness-bot .
docker run -d fitness-bot
```

**Option 3: Screen/tmux**
```bash
screen -S bot
python main_new.py
# Ctrl+A, D to detach
```

### Monitoring

Check logs:
```bash
tail -f bot.log
```

Check process:
```bash
ps aux | grep main_new.py
```

## 🔧 Configuration

### config.py

Key settings:
```python
SESSION_TIMEOUT_MINUTES = 30
MAX_CORRECTIONS = 3
MAX_PHOTO_SIZE_MB = 5
MIN_CONFIDENCE = 0.4
```

### Environment Variables

```bash
TELEGRAM_BOT_TOKEN=required
OPENROUTER_API_KEY=required
USE_MOCK_API=false
```

## 📊 Performance

### Metrics
- Photo analysis: 5-10 sec
- Correction: <1 sec
- Database query: <50ms
- Meal save: <100ms

### Optimization Tips
- Use indexes on frequently queried columns
- Cache user data in memory
- Batch database operations
- Compress images before sending to API

## 🐛 Debugging

### Enable debug logging
```python
logging.basicConfig(level=logging.DEBUG)
```

### Common Issues

**Issue:** Bot not responding
```bash
# Check if running
ps aux | grep main_new.py

# Check logs
tail -f bot.log
```

**Issue:** Database locked
```bash
# Check connections
lsof data/database.db

# Restart bot
```

**Issue:** API errors
```bash
# Check API key
echo $OPENROUTER_API_KEY

# Test API manually
curl -X POST https://openrouter.ai/api/v1/chat/completions
```

## 🤝 Contributing

### Code Style
- Follow PEP 8
- Use type hints
- Write docstrings
- Add tests for new features

### Git Workflow
```bash
git checkout -b feature/new-feature
# Make changes
git commit -m "Add new feature"
git push origin feature/new-feature
# Create PR
```

## 📝 License

MIT License

## 📧 Contact

Issues: GitHub Issues
Docs: This file

---

**Version:** 1.0 MVP  
**Last Updated:** 2026-01-20
