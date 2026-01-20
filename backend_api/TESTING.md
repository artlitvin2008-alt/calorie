# Backend API Testing Guide

## Quick Start

### 1. Start the API

```bash
# Option 1: Using run script
./backend_api/run.sh

# Option 2: Direct Python
python -m backend_api.main

# Option 3: With uvicorn
uvicorn backend_api.main:app --reload --port 8000
```

### 2. Run Basic Tests

```bash
# Make sure API is running first
python backend_api/test_api.py
```

### 3. Open Swagger UI

Navigate to: http://localhost:8000/docs

## Manual Testing

### Health Check

```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Fitness AI Coach API",
  "version": "1.0.0"
}
```

### Test CORS

```bash
curl -X OPTIONS http://localhost:8000/api/health \
  -H "Origin: http://localhost:5173" \
  -v
```

Should see CORS headers in response.

### Test Authentication (Missing Header)

```bash
curl http://localhost:8000/api/user/profile
```

Expected response (401):
```json
{
  "error_code": "MISSING_INIT_DATA",
  "message": "X-Telegram-Init-Data header is required"
}
```

### Test with Valid initData

You need to get initData from Telegram WebApp. For testing, you can use the auth verification endpoint:

```bash
curl -X POST http://localhost:8000/api/auth/verify \
  -H "Content-Type: application/json" \
  -d '{"init_data": "YOUR_INIT_DATA_HERE"}'
```

## Running Unit Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest backend_api/tests/ -v

# Run specific test file
pytest backend_api/tests/test_auth.py -v

# Run with coverage
pytest --cov=backend_api backend_api/tests/
```

## Testing Endpoints

### User Endpoints

```bash
# Get user profile (requires auth)
curl http://localhost:8000/api/user/profile \
  -H "X-Telegram-Init-Data: YOUR_INIT_DATA"

# Update user profile
curl -X PATCH http://localhost:8000/api/user/profile \
  -H "X-Telegram-Init-Data: YOUR_INIT_DATA" \
  -H "Content-Type: application/json" \
  -d '{
    "height": 175,
    "weight": 75,
    "age": 28
  }'

# Get today's stats
curl http://localhost:8000/api/user/stats/today \
  -H "X-Telegram-Init-Data: YOUR_INIT_DATA"
```

### Nutrition Endpoints

```bash
# Analyze photo
curl -X POST http://localhost:8000/api/nutrition/analyze-photo \
  -H "X-Telegram-Init-Data: YOUR_INIT_DATA" \
  -F "file=@path/to/food_photo.jpg"

# Create meal
curl -X POST http://localhost:8000/api/nutrition/meals \
  -H "X-Telegram-Init-Data: YOUR_INIT_DATA" \
  -H "Content-Type: application/json" \
  -d '{
    "meal_time": "lunch",
    "ingredients": [
      {
        "name": "Chicken breast",
        "weight": 150,
        "calories": 165,
        "protein": 31,
        "fats": 3.6,
        "carbs": 0
      }
    ]
  }'

# Get meals
curl http://localhost:8000/api/nutrition/meals \
  -H "X-Telegram-Init-Data: YOUR_INIT_DATA"

# Get meals for specific date
curl "http://localhost:8000/api/nutrition/meals?date=2024-01-20" \
  -H "X-Telegram-Init-Data: YOUR_INIT_DATA"

# Update meal
curl -X PATCH http://localhost:8000/api/nutrition/meals/1 \
  -H "X-Telegram-Init-Data: YOUR_INIT_DATA" \
  -H "Content-Type: application/json" \
  -d '{
    "dish_name": "Updated meal name"
  }'

# Delete meal
curl -X DELETE http://localhost:8000/api/nutrition/meals/1 \
  -H "X-Telegram-Init-Data: YOUR_INIT_DATA"
```

### Analytics Endpoints

```bash
# Get weight analytics
curl "http://localhost:8000/api/analytics/weight?period=week" \
  -H "X-Telegram-Init-Data: YOUR_INIT_DATA"

# Get calorie analytics
curl "http://localhost:8000/api/analytics/calories?period=month" \
  -H "X-Telegram-Init-Data: YOUR_INIT_DATA"
```

## Common Issues

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Database Not Found

```bash
# Initialize database
python init_db.py
```

### Missing Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt
pip install -r backend_api/requirements.txt
```

## Next Steps

1. ✅ All endpoints return proper responses
2. ✅ CORS headers are present
3. ✅ Authentication works correctly
4. ✅ Error responses are structured
5. ✅ Swagger UI is accessible

Ready to proceed to Phase 2: Frontend Development!
