# Requirements Document

## Introduction

Fitness AI Coach Telegram Mini App (TMA) - это полноценный frontend-клиент к существующему Telegram боту для анализа питания. Проект реализует гибридную архитектуру, где бот и Mini App работают параллельно, используя общий Backend API и базу данных. Пользователи могут выбирать между быстрыми командами в чате бота и расширенным интерфейсом Mini App.

## Glossary

- **TMA (Telegram Mini App)**: Веб-приложение, встроенное в Telegram, работающее через WebView
- **Backend_API**: REST API на FastAPI, обслуживающий запросы от бота и TMA
- **Bot**: Существующий Telegram бот на Python (aiogram)
- **PhotoAnalyzer**: Существующий модуль для анализа фотографий еды через AI
- **VideoAnalyzer**: Существующий модуль для анализа видео-кружков
- **SessionManager**: Существующий модуль для управления сессиями пользователей
- **Meal**: Запись о приёме пищи в базе данных
- **initData**: Данные аутентификации от Telegram WebApp SDK
- **Dashboard**: Главный экран TMA с обзором дневной статистики
- **DiaryPage**: Страница дневника питания с историей приёмов пищи
- **AnalyticsPage**: Страница с графиками и аналитикой
- **ProfilePage**: Страница профиля и настроек пользователя

## Requirements

### Requirement 1: Backend API Infrastructure

**User Story:** As a system architect, I want a unified Backend API, so that both the bot and TMA can access the same business logic and data.

#### Acceptance Criteria

1. THE Backend_API SHALL be implemented using FastAPI framework
2. THE Backend_API SHALL use aiosqlite for asynchronous database operations
3. THE Backend_API SHALL enable CORS for requests from TMA domain
4. THE Backend_API SHALL import and use existing modules (PhotoAnalyzer, VideoAnalyzer, SessionManager)
5. THE Backend_API SHALL expose REST endpoints under /api/* path prefix
6. THE Backend_API SHALL run on port 8000 independently from the Bot

### Requirement 2: Authentication and Authorization

**User Story:** As a user, I want secure authentication when using the Mini App, so that my data is protected.

#### Acceptance Criteria

1. WHEN a TMA request is received, THE Backend_API SHALL validate Telegram WebApp initData signature
2. THE Backend_API SHALL extract user_id from validated initData
3. IF initData validation fails, THEN THE Backend_API SHALL return 401 Unauthorized error
4. THE Backend_API SHALL use the bot token secret for signature validation
5. THE Backend_API SHALL create a dependency function for protected routes

### Requirement 3: User Profile Management

**User Story:** As a user, I want to view and edit my profile settings, so that I can customize my fitness goals.

#### Acceptance Criteria

1. WHEN a GET /api/user/profile request is received, THE Backend_API SHALL return user profile data including goals, height, weight, and notification preferences
2. WHEN a PATCH /api/user/profile request is received, THE Backend_API SHALL update user profile fields
3. THE Backend_API SHALL validate profile data before updating
4. WHEN a GET /api/user/stats/today request is received, THE Backend_API SHALL return daily statistics including consumed calories, protein, fats, carbs, and progress percentage
5. THE Backend_API SHALL calculate statistics from meals table for the current date

### Requirement 4: Nutrition Data Management

**User Story:** As a user, I want to add meals through photo analysis, so that I can track my nutrition easily.

#### Acceptance Criteria

1. WHEN a POST /api/nutrition/analyze-photo request with image file is received, THE Backend_API SHALL invoke PhotoAnalyzer module
2. THE Backend_API SHALL store uploaded photo in uploads/ directory
3. THE Backend_API SHALL save photo path in database
4. THE Backend_API SHALL return analysis results including ingredients, calories, and macronutrients
5. WHEN a POST /api/nutrition/meals request is received, THE Backend_API SHALL create a new meal record
6. WHEN a PATCH /api/nutrition/meals/{meal_id} request is received, THE Backend_API SHALL update meal data with corrections
7. WHEN a DELETE /api/nutrition/meals/{meal_id} request is received, THE Backend_API SHALL delete the meal record
8. WHEN a GET /api/nutrition/meals request with date parameter is received, THE Backend_API SHALL return meals for specified date grouped by meal time

### Requirement 5: Analytics and Insights

**User Story:** As a user, I want to see analytics and trends, so that I can understand my nutrition patterns.

#### Acceptance Criteria

1. WHEN a GET /api/analytics/weight request with period parameter is received, THE Backend_API SHALL return weight data for the specified period (week, month, year)
2. WHEN a GET /api/analytics/calories request with period parameter is received, THE Backend_API SHALL return calorie consumption data for the specified period
3. THE Backend_API SHALL aggregate data from meals table for analytics
4. THE Backend_API SHALL calculate daily averages and trends
5. THE Backend_API SHALL return data in format suitable for chart visualization

### Requirement 6: Frontend Application Structure

**User Story:** As a developer, I want a well-structured React application, so that the codebase is maintainable and scalable.

#### Acceptance Criteria

1. THE TMA SHALL be built using React 18 with TypeScript
2. THE TMA SHALL use Vite as build tool
3. THE TMA SHALL use Tailwind CSS for styling
4. THE TMA SHALL integrate Telegram WebApp SDK
5. THE TMA SHALL use Zustand for state management
6. THE TMA SHALL use React Router for navigation
7. THE TMA SHALL use recharts library for data visualization

### Requirement 7: Dashboard Interface

**User Story:** As a user, I want to see my daily progress on the main screen, so that I can quickly understand my current status.

#### Acceptance Criteria

1. WHEN the Dashboard loads, THE TMA SHALL display user greeting with name
2. THE TMA SHALL display circular progress chart showing calorie and macronutrient consumption
3. THE TMA SHALL display list of recent meals with timestamps
4. THE TMA SHALL display "Add Meal" button prominently
5. WHEN daily goal is reached, THE TMA SHALL display congratulatory message
6. THE TMA SHALL fetch data from GET /api/user/stats/today endpoint
7. THE TMA SHALL refresh data when user navigates back to Dashboard

### Requirement 8: Meal Addition Flow

**User Story:** As a user, I want multiple ways to add meals, so that I can choose the most convenient method.

#### Acceptance Criteria

1. WHEN "Add Meal" button is clicked, THE TMA SHALL display modal with three options: Camera, Gallery, Manual
2. WHEN Camera option is selected, THE TMA SHALL open camera interface for photo capture
3. WHEN Gallery option is selected, THE TMA SHALL open file picker for image selection
4. WHEN Manual option is selected, THE TMA SHALL display form for manual meal entry
5. WHEN photo is captured or selected, THE TMA SHALL upload it to POST /api/nutrition/analyze-photo
6. WHEN analysis completes, THE TMA SHALL display confirmation screen with detected ingredients
7. THE TMA SHALL provide sliders for adjusting ingredient weights
8. WHEN user confirms, THE TMA SHALL send data to POST /api/nutrition/meals
9. WHEN meal is saved, THE TMA SHALL close modal and refresh Dashboard

### Requirement 9: Diary Interface

**User Story:** As a user, I want to view my meal history, so that I can track what I've eaten.

#### Acceptance Criteria

1. WHEN DiaryPage loads, THE TMA SHALL display meals for current date
2. THE TMA SHALL provide date switcher for navigating between dates
3. THE TMA SHALL group meals by meal time (breakfast, lunch, dinner, snacks)
4. THE TMA SHALL display meal details including photo, ingredients, calories, and macronutrients
5. WHEN user swipes left on meal, THE TMA SHALL reveal delete button
6. WHEN delete is confirmed, THE TMA SHALL send DELETE /api/nutrition/meals/{meal_id}
7. THE TMA SHALL fetch data from GET /api/nutrition/meals?date=YYYY-MM-DD endpoint
8. WHEN date changes, THE TMA SHALL reload meals for new date

### Requirement 10: Analytics Interface

**User Story:** As a user, I want to see charts and trends, so that I can analyze my nutrition patterns over time.

#### Acceptance Criteria

1. WHEN AnalyticsPage loads, THE TMA SHALL display tabs for different chart types
2. THE TMA SHALL display weight trend chart using data from GET /api/analytics/weight
3. THE TMA SHALL display calorie consumption chart using data from GET /api/analytics/calories
4. THE TMA SHALL provide period selector (week, month, year)
5. WHEN period changes, THE TMA SHALL reload chart data
6. THE TMA SHALL display insights section with AI-generated recommendations
7. THE TMA SHALL use recharts library for rendering charts
8. THE TMA SHALL format chart data for optimal visualization

### Requirement 11: Profile and Settings Interface

**User Story:** As a user, I want to manage my profile and settings, so that I can customize the app to my needs.

#### Acceptance Criteria

1. WHEN ProfilePage loads, THE TMA SHALL fetch data from GET /api/user/profile
2. THE TMA SHALL display editable form with fields for goals, height, weight, age, gender
3. THE TMA SHALL provide toggle for notification preferences
4. WHEN user saves changes, THE TMA SHALL send PATCH /api/user/profile
5. THE TMA SHALL validate form data before submission
6. THE TMA SHALL display success message after successful update
7. THE TMA SHALL provide "Chat with Trainer" section linking to POST /api/ai/chat

### Requirement 12: Camera Capture Component

**User Story:** As a user, I want to take photos directly in the app, so that I can quickly add meals without leaving the interface.

#### Acceptance Criteria

1. WHEN CameraCapture component mounts, THE TMA SHALL request camera permissions
2. THE TMA SHALL display live camera preview
3. THE TMA SHALL provide capture button for taking photo
4. WHEN photo is captured, THE TMA SHALL display preview with retake and confirm options
5. WHEN confirmed, THE TMA SHALL convert photo to file format suitable for upload
6. THE TMA SHALL handle camera permission denial gracefully
7. THE TMA SHALL work on both iOS and Android devices

### Requirement 13: Theme Support

**User Story:** As a user, I want the app to match my Telegram theme, so that the experience is consistent.

#### Acceptance Criteria

1. WHEN TMA initializes, THE TMA SHALL detect theme from Telegram.WebApp.colorScheme
2. THE TMA SHALL apply light or dark theme based on detected scheme
3. THE TMA SHALL use CSS variables for theme colors
4. WHEN Telegram theme changes, THE TMA SHALL update app theme accordingly
5. THE TMA SHALL ensure all UI components support both themes
6. THE TMA SHALL maintain readability in both light and dark modes

### Requirement 14: Progressive Web App Features

**User Story:** As a user, I want to add the app to my home screen, so that I can access it quickly.

#### Acceptance Criteria

1. THE TMA SHALL include manifest.json with app metadata
2. THE manifest SHALL specify app name, icons, theme colors, and display mode
3. THE TMA SHALL provide icons in sizes 192x192 and 512x512
4. THE TMA SHALL be installable on iOS and Android home screens
5. WHERE service worker is implemented, THE TMA SHALL support offline mode for cached data

### Requirement 15: Data Synchronization

**User Story:** As a user, I want my data to be synchronized between bot and Mini App, so that I have consistent experience across interfaces.

#### Acceptance Criteria

1. WHEN meal is added through Bot, THE TMA SHALL reflect changes on next data fetch
2. WHEN meal is added through TMA, THE Bot SHALL have access to updated data
3. THE TMA SHALL implement polling mechanism for data updates
4. THE TMA SHALL poll for updates every 30 seconds when Dashboard is active
5. WHERE WebSocket is implemented, THE TMA SHALL receive real-time updates

### Requirement 16: Video Note Analysis

**User Story:** As a user, I want to analyze video notes in the Mini App, so that I can use all bot features in the TMA interface.

#### Acceptance Criteria

1. THE TMA SHALL provide interface for recording short videos
2. WHEN video is recorded, THE TMA SHALL upload it to POST /api/nutrition/analyze-video
3. THE Backend_API SHALL invoke VideoAnalyzer module for video processing
4. THE Backend_API SHALL return analysis results similar to photo analysis
5. THE TMA SHALL handle video recording on both iOS and Android

### Requirement 17: Error Handling and User Feedback

**User Story:** As a user, I want clear feedback when errors occur, so that I understand what went wrong and how to fix it.

#### Acceptance Criteria

1. WHEN API request fails, THE TMA SHALL display user-friendly error message
2. WHEN network is unavailable, THE TMA SHALL display offline indicator
3. WHEN photo upload fails, THE TMA SHALL allow retry
4. WHEN form validation fails, THE TMA SHALL highlight invalid fields with error messages
5. THE TMA SHALL display loading indicators during async operations
6. THE Backend_API SHALL return structured error responses with error codes and messages

### Requirement 18: Deployment and Infrastructure

**User Story:** As a system administrator, I want clear deployment setup, so that the application can be hosted reliably.

#### Acceptance Criteria

1. THE Bot SHALL run on port 3001 as existing implementation
2. THE Backend_API SHALL run on port 8000 independently
3. THE deployment SHALL use Nginx as reverse proxy for both services
4. THE TMA frontend SHALL be built as static files using npm run build
5. THE TMA static files SHALL be hosted on Vercel, Netlify, or server directory
6. THE TMA URL SHALL be configured in bot settings via @BotFather
7. THE deployment SHALL support HTTPS for secure communication

### Requirement 19: File Storage

**User Story:** As a system architect, I want efficient file storage, so that uploaded photos and videos are managed properly.

#### Acceptance Criteria

1. THE Backend_API SHALL store uploaded files in uploads/ directory on server
2. THE Backend_API SHALL generate unique filenames for uploaded files
3. THE Backend_API SHALL store file paths in database meals table
4. THE Backend_API SHALL serve uploaded files through static file endpoint
5. WHERE S3 integration is implemented, THE Backend_API SHALL support cloud storage

### Requirement 20: Performance and Optimization

**User Story:** As a user, I want fast and responsive interface, so that I can use the app efficiently.

#### Acceptance Criteria

1. THE TMA SHALL load initial view within 2 seconds on 3G connection
2. THE TMA SHALL implement lazy loading for route components
3. THE TMA SHALL optimize images before upload to reduce file size
4. THE TMA SHALL cache API responses where appropriate
5. THE Backend_API SHALL respond to requests within 500ms for non-AI operations
6. THE Backend_API SHALL implement request timeout of 30 seconds for AI operations
