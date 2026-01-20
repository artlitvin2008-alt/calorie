# Implementation Plan: Fitness AI Coach Telegram Mini App

## Overview

This implementation plan breaks down the development of the Fitness AI Coach TMA into discrete, incremental tasks. The plan follows a 5-phase approach: Backend API foundation, Frontend scaffolding, Core functionality, Integration, and Polish. Each task builds on previous work, ensuring no orphaned code and continuous integration.

The implementation uses Python/FastAPI for the backend and TypeScript/React for the frontend, leveraging existing bot modules for business logic.

## Tasks

### Phase 1: Backend API Foundation

- [x] 1. Set up Backend API project structure and core configuration
  - Create backend_api/ directory with main.py, dependencies.py, models.py, utils.py
  - Initialize FastAPI application with CORS middleware
  - Configure aiosqlite database connection using existing database.py
  - Set up environment variables for bot token and allowed origins
  - Create basic health check endpoint GET /api/health
  - _Requirements: 1.1, 1.2, 1.3, 1.6_

- [ ] 2. Implement authentication system
  - [x] 2.1 Create Telegram WebApp initData validation function
    - Implement HMAC-SHA256 signature validation using bot token secret
    - Parse initData query string and extract user data
    - Create validate_init_data() function in dependencies.py
    - _Requirements: 2.1, 2.2, 2.4_
  
  - [ ]* 2.2 Write property test for authentication validation
    - **Property 3: Authentication Validation**
    - **Property 4: User ID Extraction**
    - Generate random valid and invalid initData
    - Test signature validation and user_id extraction
    - **Validates: Requirements 2.1, 2.2, 2.3**
  
  - [x] 2.3 Create authentication dependency for protected routes
    - Implement get_current_user() dependency function
    - Return 401 for invalid initData
    - Extract and return user_id for valid requests
    - _Requirements: 2.3, 2.5_

- [ ] 3. Implement user management endpoints
  - [x] 3.1 Create user router and Pydantic models
    - Create routers/user.py
    - Define UserProfile, UserProfileUpdate, DailyStats Pydantic models
    - Import existing SessionManager if needed
    - _Requirements: 3.1, 3.2, 3.4_
  
  - [x] 3.2 Implement GET /api/user/profile endpoint
    - Query users table by telegram_id
    - Return profile with all required fields
    - Handle user not found (404)
    - _Requirements: 3.1_
  
  - [x] 3.3 Implement PATCH /api/user/profile endpoint
    - Validate profile data (height, weight, age ranges)
    - Update user record in database
    - Return updated profile
    - _Requirements: 3.2, 3.3_
  
  - [ ]* 3.4 Write property tests for user profile operations
    - **Property 5: Profile Response Completeness**
    - **Property 6: Profile Update Round-Trip**
    - **Property 7: Profile Validation**
    - Test profile CRUD operations with random data
    - **Validates: Requirements 3.1, 3.2, 3.3**
  
  - [x] 3.5 Implement GET /api/user/stats/today endpoint
    - Query meals table for current date
    - Calculate sum of calories, protein, fats, carbs
    - Calculate progress percentages against goals
    - Return DailyStats model
    - _Requirements: 3.4, 3.5_
  
  - [ ]* 3.6 Write property test for stats calculation
    - **Property 8: Daily Stats Completeness**
    - **Property 9: Stats Calculation Correctness**
    - Generate random meal sets and verify calculations
    - **Validates: Requirements 3.4, 3.5**

- [ ] 4. Implement nutrition endpoints - photo analysis and meal CRUD
  - [x] 4.1 Create nutrition router and models
    - Create routers/nutrition.py
    - Define Meal, MealCreate, MealUpdate, AnalysisResult models
    - Import PhotoAnalyzer and VideoAnalyzer modules
    - _Requirements: 4.1, 4.4, 4.5_
  
  - [x] 4.2 Implement POST /api/nutrition/analyze-photo endpoint
    - Accept multipart/form-data with image file
    - Generate unique filename and save to uploads/ directory
    - Invoke PhotoAnalyzer.analyze() with image path
    - Return AnalysisResult with ingredients and nutrition
    - _Requirements: 4.1, 4.2, 4.3, 4.4_
  
  - [ ]* 4.3 Write property tests for photo upload and analysis
    - **Property 10: Photo Upload Persistence**
    - **Property 11: Analysis Response Completeness**
    - **Property 19: File Storage Uniqueness**
    - Test file storage and analysis result structure
    - **Validates: Requirements 4.2, 4.3, 4.4, 19.2**
  
  - [x] 4.4 Implement POST /api/nutrition/meals endpoint
    - Accept MealCreate model with ingredients and nutrition
    - Insert meal record into meals table
    - Return created Meal with ID
    - _Requirements: 4.5_
  
  - [x] 4.5 Implement GET /api/nutrition/meals endpoint with date filtering
    - Accept optional date query parameter (YYYY-MM-DD)
    - Query meals table filtered by date and user_id
    - Group meals by meal_time
    - Return array of Meal objects
    - _Requirements: 4.8_
  
  - [x] 4.6 Implement PATCH /api/nutrition/meals/{meal_id} endpoint
    - Accept MealUpdate model with corrections
    - Update meal record in database
    - Return updated Meal
    - _Requirements: 4.6_
  
  - [x] 4.7 Implement DELETE /api/nutrition/meals/{meal_id} endpoint
    - Delete meal record from database
    - Return 204 No Content on success
    - Return 404 if meal not found
    - _Requirements: 4.7_
  
  - [ ]* 4.8 Write property tests for meal CRUD operations
    - **Property 12: Meal Creation Round-Trip**
    - **Property 13: Meal Update Round-Trip**
    - **Property 14: Meal Deletion**
    - **Property 15: Meals Date Filtering**
    - **Property 16: Meals Grouping**
    - Test complete CRUD lifecycle with random data
    - **Validates: Requirements 4.5, 4.6, 4.7, 4.8**

- [ ] 5. Implement analytics endpoints
  - [x] 5.1 Create analytics router
    - Create routers/analytics.py
    - Define WeightData, CalorieData, AnalyticsPeriod models
    - _Requirements: 5.1, 5.2_
  
  - [x] 5.2 Implement GET /api/analytics/weight endpoint
    - Accept period query parameter (week, month, year)
    - Calculate date range based on period
    - Query meals/users table for weight data
    - Return array of date-weight pairs
    - _Requirements: 5.1_
  
  - [x] 5.3 Implement GET /api/analytics/calories endpoint
    - Accept period query parameter
    - Calculate date range based on period
    - Aggregate daily calorie consumption from meals
    - Calculate daily averages and trends
    - Return array of date-calories pairs
    - _Requirements: 5.2, 5.4_
  
  - [ ]* 5.4 Write property tests for analytics
    - **Property 17: Analytics Period Filtering**
    - **Property 18: Analytics Average Calculation**
    - Test period filtering and calculation accuracy
    - **Validates: Requirements 5.1, 5.2, 5.4**

- [ ] 6. Implement video analysis endpoint
  - [x] 6.1 Implement POST /api/nutrition/analyze-video endpoint
    - Accept multipart/form-data with video file
    - Generate unique filename and save to uploads/
    - Invoke VideoAnalyzer.analyze() with video path
    - Return AnalysisResult with same structure as photo analysis
    - _Requirements: 16.2, 16.3, 16.4_
  
  - [ ]* 6.2 Write property test for video analysis
    - **Property 22: Video Analysis Result Structure**
    - Verify video analysis returns same structure as photo
    - **Validates: Requirements 16.4**

- [ ] 7. Implement error handling and response formatting
  - [x] 7.1 Create error response models and exception handlers
    - Define ErrorResponse Pydantic model
    - Create custom exception classes
    - Implement FastAPI exception handlers
    - Format all errors with error_code and message
    - _Requirements: 17.6_
  
  - [ ]* 7.2 Write property test for error responses
    - **Property 21: Error Response Structure**
    - Test that all errors return structured responses
    - **Validates: Requirements 17.6**
  
  - [ ]* 7.3 Write unit tests for specific error cases
    - Test 401 for invalid auth
    - Test 404 for missing resources
    - Test 400 for validation errors
    - Test 500 for server errors
    - _Requirements: 17.6_

- [x] 8. Checkpoint - Backend API complete
  - Run all backend tests (unit and property-based)
  - Test all endpoints via Swagger UI at http://localhost:8000/docs
  - Verify CORS headers in responses
  - Ensure all tests pass, ask the user if questions arise

### Phase 2: Frontend Scaffolding

- [x] 9. Initialize frontend project and configure build tools
  - Create miniapp-frontend/ directory
  - Initialize Vite project with React and TypeScript template
  - Install dependencies: react-router-dom, zustand, recharts, tailwindcss
  - Configure Tailwind CSS with iOS-style design tokens
  - Set up vite.config.ts with proxy for API during development
  - _Requirements: 6.1, 6.2, 6.3, 6.7_

- [ ] 10. Set up Telegram WebApp SDK integration
  - [x] 10.1 Create Telegram WebApp type definitions
    - Create lib/telegram-webapp.d.ts with SDK types
    - Declare global Telegram object
    - _Requirements: 6.4_
  
  - [x] 10.2 Create Telegram SDK initialization
    - Add Telegram WebApp SDK script to index.html
    - Create useTelegramWebApp hook for SDK access
    - Initialize SDK in App.tsx
    - Extract initData for authentication
    - _Requirements: 6.4, 2.1_
  
  - [x] 10.3 Create theme detection and management
    - Create lib/theme.ts with theme utilities
    - Create themeStore.ts with Zustand
    - Detect colorScheme from Telegram.WebApp
    - Apply theme CSS variables
    - Listen for theme change events
    - _Requirements: 13.1, 13.2, 13.3, 13.4_
  
  - [ ]* 10.4 Write unit tests for theme detection
    - Test theme detection from colorScheme
    - Test theme change event handling
    - _Requirements: 13.1, 13.2, 13.4_

- [ ] 11. Create API client and state management
  - [x] 11.1 Create API client with authentication
    - Create lib/api.ts with axios or fetch wrapper
    - Add initData to all request headers
    - Implement request/response interceptors
    - Handle authentication errors (401)
    - _Requirements: 2.1, 17.1_
  
  - [x] 11.2 Create Zustand stores
    - Create store/userStore.ts for user profile and stats
    - Create store/mealsStore.ts for meals data
    - Implement actions for fetching and updating data
    - _Requirements: 6.5_
  
  - [ ]* 11.3 Write unit tests for API client
    - Test request header injection
    - Test error handling
    - Test response parsing
    - _Requirements: 17.1_

- [ ] 12. Set up routing and navigation
  - [x] 12.1 Configure React Router
    - Create App.tsx with BrowserRouter
    - Define routes for Dashboard, Diary, Analytics, Profile
    - Create navigation component with bottom tabs
    - _Requirements: 6.6_
  
  - [x] 12.2 Create page components scaffolding
    - Create pages/DashboardPage.tsx
    - Create pages/DiaryPage.tsx
    - Create pages/AnalyticsPage.tsx
    - Create pages/ProfilePage.tsx
    - Add basic layout and navigation
    - _Requirements: 7.1, 9.1, 10.1, 11.1_

- [ ] 13. Create base UI components
  - [ ] 13.1 Set up shadcn/ui components
    - Initialize shadcn/ui with iOS-style theme
    - Add Button, Card, Input, Modal components
    - Customize components for iOS aesthetic
    - _Requirements: 6.3_
  
  - [x] 13.2 Create loading and error components
    - Create LoadingSpinner component
    - Create ErrorMessage component
    - Create OfflineIndicator component
    - _Requirements: 17.1, 17.2, 17.5_
  
  - [ ]* 13.3 Write unit tests for UI components
    - Test component rendering
    - Test loading states
    - Test error states
    - _Requirements: 17.5_

### Phase 3: Core Functionality

- [x] 14. Implement Dashboard page
  - [x] 14.1 Create Dashboard data fetching and display
    - Fetch user stats from GET /api/user/stats/today
    - Display user greeting with first_name
    - Create ProgressChart component with circular progress
    - Display consumed vs goal for calories and macros
    - _Requirements: 7.1, 7.2, 7.6_
  
  - [x] 14.2 Create recent meals list
    - Fetch recent meals from GET /api/nutrition/meals
    - Create MealCard component
    - Display meal photo, time, calories
    - _Requirements: 7.3_
  
  - [x] 14.3 Implement data refresh on navigation
    - Use React Router navigation events
    - Refetch stats when returning to Dashboard
    - _Requirements: 7.7_
  
  - [ ]* 14.4 Write property tests for Dashboard
    - **Property 23: Dashboard User Greeting**
    - **Property 24: Dashboard Progress Chart**
    - **Property 25: Dashboard Meals Display**
    - **Property 26: Dashboard Data Refresh**
    - Test data display with random user data
    - **Validates: Requirements 7.1, 7.2, 7.3, 7.7**

- [-] 15. Implement meal addition flow - camera and photo upload
  - [x] 15.1 Create CameraCapture component
    - Request camera permissions on mount
    - Display live camera preview using getUserMedia
    - Implement capture button to take photo
    - Display preview with retake and confirm options
    - Convert captured photo to File/Blob
    - Handle permission denial gracefully
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6_
  
  - [ ]* 15.2 Write unit tests for CameraCapture
    - Test permission request
    - Test photo capture flow
    - Test permission denial handling
    - _Requirements: 12.1, 12.4, 12.6_
  
  - [x] 15.3 Create MealAddModal component
    - Display modal with three options: Camera, Gallery, Manual
    - Implement Camera option opening CameraCapture
    - Implement Gallery option with file input
    - Implement Manual option with form
    - _Requirements: 8.1, 8.2, 8.3, 8.4_
  
  - [ ]* 15.4 Write unit tests for MealAddModal
    - Test modal opening
    - Test option selection
    - Test modal closing
    - _Requirements: 8.1, 8.2, 8.3, 8.4_
  
  - [x] 15.5 Implement photo upload and analysis
    - Upload photo to POST /api/nutrition/analyze-photo
    - Display loading indicator during analysis
    - Handle upload errors with retry option
    - _Requirements: 8.5, 17.3, 17.5_
  
  - [ ]* 15.6 Write property tests for photo upload
    - **Property 27: Photo Upload Endpoint**
    - **Property 45: Image Optimization**
    - Test upload to correct endpoint
    - Test image optimization
    - **Validates: Requirements 8.5, 20.3**

- [-] 16. Implement meal confirmation and saving
  - [x] 16.1 Create MealConfirmation component
    - Display analysis results with detected ingredients
    - Create sliders for adjusting ingredient weights
    - Recalculate nutrition on weight changes
    - Display total calories and macros
    - _Requirements: 8.6, 8.7_
  
  - [x] 16.2 Implement meal save functionality
    - Send meal data to POST /api/nutrition/meals
    - Close modal on successful save
    - Refresh Dashboard with new meal
    - Display success message
    - _Requirements: 8.8, 8.9_
  
  - [ ]* 16.3 Write property tests for meal confirmation
    - **Property 28: Confirmation Screen Ingredients**
    - **Property 29: Meal Save Flow**
    - Test ingredient display and save flow
    - **Validates: Requirements 8.6, 8.9**

- [-] 17. Implement Diary page
  - [x] 17.1 Create DiaryPage with date navigation
    - Create DateSwitcher component for date selection
    - Fetch meals for selected date from GET /api/nutrition/meals
    - Display current date meals on initial load
    - Reload meals when date changes
    - _Requirements: 9.1, 9.2, 9.8_
  
  - [x] 17.2 Implement meals display with grouping
    - Group meals by meal_time (breakfast, lunch, dinner, snacks)
    - Display meal cards with photo, ingredients, nutrition
    - Show all required meal details
    - _Requirements: 9.3, 9.4_
  
  - [x] 17.3 Implement swipe-to-delete functionality
    - Add swipe gesture detection to meal cards
    - Reveal delete button on swipe left
    - Show confirmation dialog
    - Send DELETE request to /api/nutrition/meals/{meal_id}
    - Remove meal from display on success
    - _Requirements: 9.5, 9.6_
  
  - [ ]* 17.4 Write property tests for Diary page
    - **Property 30: Diary Meals Grouping**
    - **Property 31: Meal Details Display**
    - **Property 32: Diary Date Change**
    - Test meal grouping and display
    - **Validates: Requirements 9.3, 9.4, 9.8**
  
  - [ ]* 17.5 Write unit tests for swipe-to-delete
    - Test swipe gesture detection
    - Test delete confirmation
    - Test meal removal
    - _Requirements: 9.5_

- [-] 18. Implement Analytics page
  - [x] 18.1 Create AnalyticsPage with chart tabs
    - Create tab navigation for Weight and Calories charts
    - Create period selector (week, month, year)
    - Fetch data from GET /api/analytics/weight and /api/analytics/calories
    - Reload data when period changes
    - _Requirements: 10.1, 10.4, 10.5_
  
  - [x] 18.2 Implement chart visualization with recharts
    - Create WeightChart component using LineChart
    - Create CaloriesChart component using BarChart
    - Format data for recharts
    - Style charts for iOS aesthetic
    - _Requirements: 10.2, 10.3, 10.7, 10.8_
  
  - [x] 18.3 Create insights section
    - Display AI-generated recommendations
    - Show trends and patterns
    - _Requirements: 10.6_
  
  - [ ]* 18.4 Write property tests for Analytics page
    - **Property 33: Analytics Chart Rendering**
    - **Property 34: Analytics Period Change**
    - Test chart rendering and period changes
    - **Validates: Requirements 10.2, 10.3, 10.5**

- [-] 19. Implement Profile page
  - [x] 19.1 Create ProfilePage with form
    - Fetch profile from GET /api/user/profile
    - Display editable form with goals, height, weight, age, gender
    - Add toggle for notification preferences
    - _Requirements: 11.1, 11.2, 11.3_
  
  - [x] 19.2 Implement form validation and submission
    - Validate form data (ranges, required fields)
    - Highlight invalid fields with error messages
    - Prevent submission if validation fails
    - Send PATCH to /api/user/profile on save
    - Display success message after update
    - _Requirements: 11.4, 11.5, 11.6_
  
  - [x] 19.3 Add Chat with Trainer section
    - Create UI section linking to AI chat
    - Implement POST /api/ai/chat endpoint call
    - _Requirements: 11.7_
  
  - [ ]* 19.4 Write property tests for Profile page
    - **Property 35: Profile Form Fields**
    - **Property 36: Profile Form Validation**
    - Test form display and validation
    - **Validates: Requirements 11.2, 11.5**
  
  - [ ]* 19.5 Write unit test for success message
    - Test success message display after update
    - _Requirements: 11.6_

- [ ] 20. Checkpoint - Core functionality complete
  - Test complete meal addition flow end-to-end
  - Test diary navigation and meal deletion
  - Test analytics charts with different periods
  - Test profile editing and validation
  - Ensure all tests pass, ask the user if questions arise

### Phase 4: Integration and Synchronization

- [ ] 21. Implement video recording and analysis
  - [ ] 21.1 Create VideoRecorder component
    - Implement video recording interface
    - Use MediaRecorder API for recording
    - Limit recording duration to 30 seconds
    - Display recording indicator
    - _Requirements: 16.1_
  
  - [ ] 21.2 Implement video upload and analysis
    - Upload video to POST /api/nutrition/analyze-video
    - Display loading during analysis
    - Show results in same confirmation screen as photos
    - _Requirements: 16.2, 16.4_
  
  - [ ]* 21.3 Write property test for video upload
    - **Property 41: Video Upload Endpoint**
    - Test upload to correct endpoint
    - **Validates: Requirements 16.2**

- [ ] 22. Implement data synchronization between Bot and TMA
  - [ ] 22.1 Create polling mechanism for Dashboard
    - Implement setInterval for polling every 30 seconds
    - Fetch latest data when Dashboard is active
    - Stop polling when Dashboard is inactive
    - _Requirements: 15.3, 15.4_
  
  - [ ] 22.2 Test cross-interface synchronization
    - Add meal via Bot, verify it appears in TMA
    - Add meal via TMA, verify Bot can access it
    - _Requirements: 15.1, 15.2_
  
  - [ ]* 22.3 Write property test for data synchronization
    - **Property 40: Data Synchronization**
    - Test bidirectional sync between interfaces
    - **Validates: Requirements 15.1, 15.2**

- [ ] 23. Implement comprehensive error handling
  - [ ] 23.1 Add error boundaries and error states
    - Create ErrorBoundary component
    - Add error states to all pages
    - Display user-friendly error messages
    - _Requirements: 17.1_
  
  - [ ] 23.2 Implement offline detection
    - Listen for online/offline events
    - Display offline indicator when network unavailable
    - Cache last successful data
    - _Requirements: 17.2_
  
  - [ ] 23.3 Add form validation highlighting
    - Highlight invalid fields in red
    - Display inline error messages
    - Prevent submission until errors resolved
    - _Requirements: 17.4_
  
  - [ ]* 23.4 Write property tests for error handling
    - **Property 42: Error Message Display**
    - **Property 43: Form Validation Highlighting**
    - **Property 44: Loading Indicators**
    - Test error display and loading states
    - **Validates: Requirements 17.1, 17.4, 17.5**
  
  - [ ]* 23.5 Write unit tests for offline handling
    - Test offline indicator display
    - Test data caching
    - _Requirements: 17.2_

- [ ] 24. Checkpoint - Integration complete
  - Test video recording and analysis
  - Test data sync between Bot and TMA
  - Test error handling and offline mode
  - Verify all error states display correctly
  - Ensure all tests pass, ask the user if questions arise

### Phase 5: Polish and Deployment

- [ ] 25. Implement PWA features
  - [ ] 25.1 Create manifest.json
    - Define app name, short_name, description
    - Add icons (192x192, 512x512)
    - Set theme_color and background_color
    - Set display mode to standalone
    - _Requirements: 14.1, 14.2, 14.3_
  
  - [ ] 25.2 Create app icons
    - Design and export 192x192 icon
    - Design and export 512x512 icon
    - Add icons to public/ directory
    - _Requirements: 14.3_
  
  - [ ]* 25.3 Write unit tests for PWA manifest
    - Test manifest.json contains required fields
    - Test icons exist
    - _Requirements: 14.1, 14.2, 14.3_

- [ ] 26. Implement theme support and polish UI
  - [ ] 26.1 Finalize theme implementation
    - Ensure all components support light and dark themes
    - Test theme switching
    - Verify readability in both modes
    - _Requirements: 13.5, 13.6_
  
  - [ ]* 26.2 Write property tests for theme
    - **Property 37: Camera Photo Conversion**
    - **Property 38: Theme Detection**
    - **Property 39: Theme Change Response**
    - Test theme detection and changes
    - **Validates: Requirements 12.5, 13.2, 13.4**

- [ ] 27. Optimize performance
  - [ ] 27.1 Implement code splitting and lazy loading
    - Lazy load route components
    - Split vendor bundles
    - _Requirements: 20.2_
  
  - [ ] 27.2 Implement image optimization
    - Compress images before upload
    - Resize images to maximum dimensions
    - Convert to WebP format if supported
    - _Requirements: 20.3_
  
  - [ ] 27.3 Implement API response caching
    - Cache user profile data
    - Cache meals data with TTL
    - Invalidate cache on updates
    - _Requirements: 20.4_

- [ ] 28. Set up deployment configuration
  - [ ] 28.1 Configure backend deployment
    - Create Dockerfile for Backend API
    - Set up environment variables
    - Configure Nginx reverse proxy
    - Set up SSL certificates for HTTPS
    - _Requirements: 18.1, 18.2, 18.3, 18.7_
  
  - [ ] 28.2 Configure frontend deployment
    - Build frontend with npm run build
    - Configure deployment to Vercel/Netlify
    - Set up environment variables for API URL
    - Configure custom domain if needed
    - _Requirements: 18.4, 18.5_
  
  - [ ] 28.3 Configure Bot settings
    - Set Mini App URL in @BotFather
    - Configure Menu Button to open Mini App
    - Test Mini App opening from Telegram
    - _Requirements: 18.6_

- [ ] 29. Final testing and quality assurance
  - [ ]* 29.1 Run complete test suite
    - Run all backend unit and property tests
    - Run all frontend unit and property tests
    - Generate coverage reports
    - Ensure 80%+ code coverage
  
  - [ ]* 29.2 Run end-to-end tests
    - Test complete user flows
    - Test on iOS devices
    - Test on Android devices
    - Test in different Telegram clients
  
  - [ ] 29.3 Performance testing
    - Test load time on 3G connection
    - Test API response times
    - Verify performance requirements met
    - _Requirements: 20.1, 20.5, 20.6_

- [ ] 30. Final checkpoint - Project complete
  - All features implemented and tested
  - Backend API deployed and accessible
  - Frontend deployed and accessible via Telegram
  - Documentation updated
  - Ready for production use

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at major milestones
- Property tests validate universal correctness properties with minimum 100 iterations
- Unit tests validate specific examples, edge cases, and error conditions
- Backend uses Python with pytest and Hypothesis for property-based testing
- Frontend uses TypeScript with Vitest and fast-check for property-based testing
- All tasks build incrementally with no orphaned code
