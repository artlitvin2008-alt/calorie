# Requirements Document

## Introduction

Комплексный Telegram-бот фитнес-коуч, который помогает пользователям достигать целей по снижению веса или набору мышечной массы через:
- Интерактивный анализ питания с фотографий (AI-powered)
- Персонализированные тренировочные планы
- Систему мотивации и контроля (контракты, чекины)
- Аналитику прогресса и предсказание достижения целей
- Обучающую систему и поддержку

Бот использует state machine для управления взаимодействием, SQLite для персистентности данных и OpenRouter API для AI-анализа.

## Glossary

**CORE COMPONENTS:**
- **Bot**: Telegram-бот фитнес-коуч
- **User**: Пользователь Telegram с целями по фитнесу
- **Session**: Активная сессия взаимодействия (анализ еды, тренировка, чекин)
- **State_Manager**: Компонент управления состояниями пользователя
- **Database**: SQLite база данных для всех данных бота

**NUTRITION MODULE:**
- **AI_Analyzer**: Компонент анализа изображений еды через OpenRouter API
- **Preliminary_Analysis**: Первичный результат анализа с компонентами и уверенностью
- **Final_Analysis**: Финальный результат с калориями, БЖУ и рекомендациями
- **Food_Component**: Распознанный компонент еды (название, вес, уверенность)
- **Correction**: Пользовательская коррекция (add, remove, modify)
- **Meal_Tracker**: Трекер приемов пищи и дневник питания
- **Water_Tracker**: Трекер потребления воды

**WORKOUT MODULE:**
- **Workout_Generator**: Генератор персонализированных тренировок
- **Exercise**: Упражнение из библиотеки (название, описание, мышцы, сложность)
- **Workout_Plan**: План тренировок на период
- **Progress_Tracker**: Трекер прогресса по упражнениям и весам

**MOTIVATION MODULE:**
- **Contract**: Обязательство пользователя с условиями и штрафами
- **Checkin**: Ежедневный чекин (утренний/вечерний)
- **Anti_Fail_Protocol**: Протокол предотвращения срывов
- **Penalty**: Штраф за нарушение контракта

**ANALYTICS MODULE:**
- **Progress_Visualizer**: Визуализация прогресса (графики, тренды)
- **Pattern_Detector**: Детектор паттернов поведения
- **Goal_Predictor**: Предсказатель достижения целей
- **Report**: Отчет (недельный/месячный)

## Requirements

### PRIORITY 1: CORE FUNCTIONALITY

### Requirement 1: User Registration and Profile Management

**User Story:** Как новый пользователь, я хочу зарегистрироваться и настроить свой профиль, чтобы получать персонализированные рекомендации.

#### Acceptance Criteria

1. WHEN a User sends /start command for the first time, THEN THE Bot SHALL create a new user record in Database
2. WHEN creating a user profile, THEN THE Bot SHALL collect: goal (weight_loss/muscle_gain), current_weight, target_weight, height, age, gender
3. WHEN a User sends /profile command, THEN THE Bot SHALL display current profile information including progress statistics
4. WHEN a User sends /setup command, THEN THE Bot SHALL allow updating profile settings
5. WHEN profile is created, THEN THE Bot SHALL calculate daily calorie target based on user parameters

### Requirement 2: Photo Reception and Processing

**User Story:** Как пользователь, я хочу отправить фото еды боту, чтобы получить анализ содержимого блюда.

#### Acceptance Criteria

1. WHEN a User sends a photo to the Bot, THEN THE Bot SHALL accept the photo and create a new Session
2. WHEN a User sends a photo while in state waiting_for_photo, THEN THE Bot SHALL process the photo with AI_Analyzer
3. IF a User sends non-photo content while in state waiting_for_photo, THEN THE Bot SHALL respond with an error message requesting a photo
4. WHEN a photo is received, THEN THE Bot SHALL transition the Session state to waiting_confirmation
5. WHEN processing a photo, THEN THE Bot SHALL use OpenRouter API with model qwen/qwen-2-vl-7b-instruct:free

### Requirement 2: Preliminary Analysis Generation

**User Story:** Как пользователь, я хочу видеть предварительный анализ моей еды, чтобы понять, что бот распознал на фото.

#### Acceptance Criteria

1. WHEN AI_Analyzer completes image analysis, THEN THE Bot SHALL generate a Preliminary_Analysis containing a list of Food_Components
2. WHEN generating Preliminary_Analysis, THEN THE Bot SHALL include name, estimated weight, and confidence level for each Food_Component
3. WHEN displaying Preliminary_Analysis, THEN THE Bot SHALL format the results as a readable message with component details
4. WHEN displaying Preliminary_Analysis, THEN THE Bot SHALL include an inline button labeled "✅ Подтвердить"
5. WHEN Preliminary_Analysis is displayed, THEN THE Bot SHALL store the analysis data in the Session

### Requirement 3: Confirmation and Correction Flow

**User Story:** Как пользователь, я хочу подтвердить или скорректировать результаты анализа, чтобы получить точную информацию о моей еде.

#### Acceptance Criteria

1. WHEN a User clicks the "✅ Подтвердить" button, THEN THE Bot SHALL transition the Session to completed state and generate Final_Analysis
2. WHEN a User sends text while in state waiting_confirmation, THEN THE Bot SHALL treat the text as a Correction and transition to waiting_correction state
3. WHEN processing a Correction, THEN THE Correction_Parser SHALL parse the text to identify action type (add, remove, modify) and target component
4. WHEN a Correction is parsed, THEN THE Bot SHALL apply the changes to the Preliminary_Analysis
5. WHEN a Correction is applied, THEN THE Bot SHALL display the updated Preliminary_Analysis with the "✅ Подтвердить" button
6. WHEN a Session has 3 correction cycles, THEN THE Bot SHALL automatically proceed to Final_Analysis regardless of further corrections

### Requirement 4: Correction Parsing

**User Story:** Как пользователь, я хочу использовать естественный язык для коррекций, чтобы легко исправлять ошибки анализа.

#### Acceptance Criteria

1. WHEN Correction_Parser receives text containing "нет" or "убери" followed by a food name, THEN THE Parser SHALL identify it as a remove action
2. WHEN Correction_Parser receives text containing "добавь" or "есть" followed by a food name, THEN THE Parser SHALL identify it as an add action
3. WHEN Correction_Parser receives text with a food name followed by descriptive words, THEN THE Parser SHALL identify it as a modify action
4. WHEN Correction_Parser identifies an action, THEN THE Parser SHALL extract the target food component name
5. IF Correction_Parser cannot parse the text, THEN THE Bot SHALL respond with a helpful error message and examples

### Requirement 5: Final Analysis Generation

**User Story:** Как пользователь, я хочу получить детальный анализ калорий и БЖУ, чтобы контролировать свое питание.

#### Acceptance Criteria

1. WHEN generating Final_Analysis, THEN THE Bot SHALL calculate total calories for all confirmed Food_Components
2. WHEN generating Final_Analysis, THEN THE Bot SHALL calculate total protein, fats, and carbohydrates in grams
3. WHEN generating Final_Analysis, THEN THE Bot SHALL include personalized recommendations for weight loss
4. WHEN Final_Analysis is generated, THEN THE Bot SHALL display the results in a formatted message
5. WHEN Final_Analysis is complete, THEN THE Bot SHALL save the analysis to Database history

### Requirement 6: Session State Management

**User Story:** Как система, я хочу управлять состояниями пользовательских сессий, чтобы корректно обрабатывать взаимодействия.

#### Acceptance Criteria

1. WHEN a new User interaction begins, THEN THE State_Manager SHALL initialize a Session in waiting_for_photo state
2. WHEN a Session transitions between states, THEN THE State_Manager SHALL update the Session state in Database
3. WHEN a Session is inactive for 30 minutes, THEN THE State_Manager SHALL expire the Session and reset User to waiting_for_photo state
4. WHEN a Session is active, THEN THE State_Manager SHALL maintain the Session data in memory cache
5. THE State_Manager SHALL support four states: waiting_for_photo, waiting_confirmation, waiting_correction, completed

### Requirement 7: Data Persistence

**User Story:** Как система, я хочу сохранять сессии и историю анализов, чтобы обеспечить надежность и возможность просмотра истории.

#### Acceptance Criteria

1. WHEN a Session is created or updated, THEN THE Database SHALL persist the Session data to SQLite
2. WHEN Final_Analysis is generated, THEN THE Database SHALL save the analysis to user history table
3. WHEN retrieving Session data, THEN THE Database SHALL return the most recent Session for the User
4. WHEN storing Food_Components, THEN THE Database SHALL preserve name, weight, confidence level, and modification history
5. THE Database SHALL maintain separate tables for active sessions and completed analysis history

### Requirement 8: Error Handling

**User Story:** Как пользователь, я хочу получать понятные сообщения об ошибках, чтобы знать, как исправить проблему.

#### Acceptance Criteria

1. IF OpenRouter API request fails, THEN THE Bot SHALL retry up to 3 times with exponential backoff
2. IF OpenRouter API fails after retries, THEN THE Bot SHALL notify the User with a friendly error message
3. IF a Session timeout occurs, THEN THE Bot SHALL notify the User and reset to waiting_for_photo state
4. IF an invalid Correction is received, THEN THE Bot SHALL provide examples of valid correction formats
5. IF maximum correction cycles (3) is reached, THEN THE Bot SHALL inform the User and proceed to Final_Analysis

### Requirement 9: API Integration

**User Story:** Как система, я хочу интегрироваться с внешними API, чтобы обеспечить функциональность анализа изображений.

#### Acceptance Criteria

1. WHEN making OpenRouter API requests, THEN THE AI_Analyzer SHALL use the provided OPENROUTER_API_KEY
2. WHEN analyzing images, THEN THE AI_Analyzer SHALL use model qwen/qwen-2-vl-7b-instruct:free
3. WHEN sending images to OpenRouter, THEN THE AI_Analyzer SHALL format the request according to OpenRouter API specifications
4. WHEN receiving OpenRouter responses, THEN THE AI_Analyzer SHALL parse the response to extract Food_Components
5. WHEN initializing the Bot, THEN THE Bot SHALL use the provided TELEGRAM_BOT_TOKEN for authentication

### Requirement 10: User Interface

**User Story:** Как пользователь, я хочу иметь интуитивный интерфейс с кнопками, чтобы легко взаимодействовать с ботом.

#### Acceptance Criteria

1. WHEN displaying Preliminary_Analysis, THEN THE Bot SHALL use Telegram inline keyboard with a confirmation button
2. WHEN a User clicks an inline button, THEN THE Bot SHALL handle the callback and update the message
3. WHEN displaying analysis results, THEN THE Bot SHALL use clear formatting with emojis for readability
4. WHEN showing error messages, THEN THE Bot SHALL include helpful instructions for next steps
5. WHEN the Bot starts, THEN THE Bot SHALL send a welcome message explaining how to use the bot


### PRIORITY 2: WORKOUT MODULE

### Requirement 11: Workout Plan Generation

**User Story:** Как пользователь, я хочу получать персонализированные тренировочные планы, чтобы эффективно достигать своих фитнес-целей.

#### Acceptance Criteria

1. WHEN a User requests workout plan, THEN THE Bot SHALL collect information about: equipment availability, fitness level, training goal
2. WHEN generating workout plan, THEN THE Workout_Generator SHALL select appropriate exercises from Exercise library
3. WHEN creating workout, THEN THE Bot SHALL specify sets, reps, and rest periods for each Exercise
4. WHEN a User sends /workout_today command, THEN THE Bot SHALL display today's scheduled workout
5. WHEN workout is generated, THEN THE Bot SHALL save the Workout_Plan to Database

### Requirement 12: Workout Progress Tracking

**User Story:** Как пользователь, я хочу отслеживать выполнение тренировок и прогресс по весам, чтобы видеть свое развитие.

#### Acceptance Criteria

1. WHEN a User completes an exercise, THEN THE Bot SHALL allow marking it as completed with used weight
2. WHEN tracking progress, THEN THE Progress_Tracker SHALL store weight used for each exercise over time
3. WHEN a User requests progress, THEN THE Bot SHALL display weight progression graphs for exercises
4. WHEN detecting consistent progress, THEN THE Bot SHALL suggest increasing weights
5. WHEN a User misses scheduled workout, THEN THE Bot SHALL send reminder notification

### PRIORITY 3: MOTIVATION MODULE

### Requirement 13: Contract System

**User Story:** Как пользователь, я хочу заключить контракт с обязательствами и штрафами, чтобы повысить свою мотивацию и дисциплину.

#### Acceptance Criteria

1. WHEN a User sends /create_contract command, THEN THE Bot SHALL offer contract types: beginner, intermediate, hardcore
2. WHEN creating Contract, THEN THE Bot SHALL allow selecting penalty type: physical, financial, social
3. WHEN Contract is created, THEN THE Bot SHALL store contract details including start_date, end_date, and penalty_details
4. WHEN a User violates Contract terms, THEN THE Bot SHALL apply specified Penalty
5. WHEN Contract period ends, THEN THE Bot SHALL generate completion report with violations count

### Requirement 14: Daily Check-ins

**User Story:** Как пользователь, я хочу делать ежедневные чекины утром и вечером, чтобы отслеживать свое состояние и рефлексировать.

#### Acceptance Criteria

1. WHEN time is 8:00 AM, THEN THE Bot SHALL send morning Checkin request asking for mood (1-5) and daily goal
2. WHEN time is 9:00 PM, THEN THE Bot SHALL send evening Checkin request asking for goal completion and reflection
3. WHEN a User completes Checkin, THEN THE Bot SHALL save responses to Database with checkin_date
4. WHEN analyzing Checkin text, THEN THE Bot SHALL detect mood patterns and trigger warnings
5. WHEN a User misses Checkin, THEN THE Bot SHALL send reminder after 1 hour

### Requirement 15: Anti-Fail Protocols

**User Story:** Как пользователь, я хочу получать поддержку в моменты слабости, чтобы не сорваться с диеты или тренировок.

#### Acceptance Criteria

1. WHEN a User sends message containing trigger words ("сорвусь", "хочу сладкого"), THEN THE Bot SHALL activate Anti_Fail_Protocol
2. WHEN protocol is activated, THEN THE Bot SHALL guide User through STOP process: pause, analyze, alternative, decision
3. WHEN User is in crisis, THEN THE Bot SHALL offer alternative actions from Database
4. WHEN detecting pattern of failures, THEN THE Bot SHALL suggest adjusting goals or Contract
5. WHEN User successfully resists temptation, THEN THE Bot SHALL provide positive reinforcement

### PRIORITY 4: ANALYTICS MODULE

### Requirement 16: Progress Visualization

**User Story:** Как пользователь, я хочу видеть визуализацию своего прогресса, чтобы оставаться мотивированным и понимать динамику изменений.

#### Acceptance Criteria

1. WHEN a User sends /progress command, THEN THE Progress_Visualizer SHALL generate weight change graph
2. WHEN displaying progress, THEN THE Bot SHALL show trends and predictions for goal achievement
3. WHEN a User uploads progress photos, THEN THE Bot SHALL store them with timestamps for before/after comparison
4. WHEN generating visualization, THEN THE Bot SHALL use matplotlib or similar library to create graphs
5. WHEN progress is positive, THEN THE Bot SHALL highlight achievements and milestones

### Requirement 17: Reports and Analytics

**User Story:** Как пользователь, я хочу получать периодические отчеты о своей активности, чтобы анализировать паттерны и улучшать результаты.

#### Acceptance Criteria

1. WHEN Sunday arrives, THEN THE Bot SHALL generate weekly Report with: weight change, average calories, workout count, consistency score
2. WHEN month ends, THEN THE Bot SHALL generate monthly Report with achievements, problems, and recommendations
3. WHEN generating Report, THEN THE Pattern_Detector SHALL identify patterns: failure days, overeating times, mood-food correlations
4. WHEN a User requests /report command, THEN THE Bot SHALL display most recent weekly Report
5. WHEN patterns are detected, THEN THE Bot SHALL provide actionable insights and suggestions

### PRIORITY 5: SUPPORT MODULE

### Requirement 18: Education System

**User Story:** Как пользователь, я хочу получать образовательный контент о питании и тренировках, чтобы лучше понимать процесс трансформации.

#### Acceptance Criteria

1. WHEN a User is registered for 1+ days, THEN THE Bot SHALL send daily micro-lesson (21 lessons total)
2. WHEN a User sends /knowledge command, THEN THE Bot SHALL display knowledge base with topics
3. WHEN a User asks question, THEN THE Bot SHALL search knowledge base and provide relevant answer
4. WHEN sending lessons, THEN THE Bot SHALL cover topics: calorie deficit, macros, training principles, recovery
5. WHEN lesson is sent, THEN THE Bot SHALL mark it as delivered in Database

### Requirement 19: Notifications and Reminders

**User Story:** Как пользователь, я хочу получать напоминания о важных действиях, чтобы не забывать пить воду, есть вовремя и тренироваться.

#### Acceptance Criteria

1. WHEN 2 hours pass since last water log, THEN THE Bot SHALL send water reminder
2. WHEN meal time arrives (breakfast/lunch/dinner), THEN THE Bot SHALL send meal reminder
3. WHEN a User enables motivational quotes, THEN THE Bot SHALL send one quote per day
4. WHEN time is between 10 PM and 7 AM, THEN THE Bot SHALL NOT send notifications (quiet hours)
5. WHEN a User sends /settings command, THEN THE Bot SHALL allow configuring notification preferences

### Requirement 20: Data Export and Privacy

**User Story:** Как пользователь, я хочу иметь возможность экспортировать свои данные и контролировать приватность, чтобы владеть своей информацией.

#### Acceptance Criteria

1. WHEN a User sends /export command, THEN THE Bot SHALL generate CSV/JSON file with all user data
2. WHEN exporting data, THEN THE Bot SHALL include: meals, workouts, checkins, weight history, contracts
3. WHEN a User requests data deletion, THEN THE Bot SHALL remove all user data from Database
4. WHEN storing sensitive data, THEN THE Bot SHALL ensure data is not shared with third parties
5. WHEN a User views privacy policy, THEN THE Bot SHALL display clear information about data usage
