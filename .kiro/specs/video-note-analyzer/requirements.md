# Requirements Document: Video Note Analyzer

## Introduction

Эта фича добавляет возможность анализа еды через видео-кружки (Video Note) в Telegram боте для подсчета калорий. Пользователь записывает короткое видео, показывая еду с разных сторон и проговаривая дополнительную информацию. Бот извлекает кадры из видео, транскрибирует речь и отправляет все данные в AI для комплексного анализа.

## Glossary

- **Video_Note**: Круглое видео сообщение в Telegram длительностью до 60 секунд
- **Frame_Extractor**: Компонент для извлечения кадров из видео
- **Audio_Transcriber**: Компонент для преобразования речи в текст
- **Video_Note_Handler**: Обработчик входящих видео-кружков
- **Multimodal_Analyzer**: Компонент для анализа изображений и текста через AI
- **Result_Formatter**: Компонент для форматирования результатов анализа
- **Mock_Mode**: Режим тестирования без реальной транскрипции

## Requirements

### Requirement 1: Video Note Reception

**User Story:** Как пользователь, я хочу отправить видео-кружок с едой боту, чтобы получить анализ калорий и БЖУ на основе визуальной и голосовой информации.

#### Acceptance Criteria

1. WHEN a user sends a Video_Note to the bot, THE Video_Note_Handler SHALL accept and process the message
2. WHEN a Video_Note is received, THE System SHALL download the video file to temporary storage
3. WHEN a Video_Note exceeds 60 seconds, THE System SHALL process it normally as Telegram enforces this limit
4. IF a Video_Note download fails, THEN THE System SHALL notify the user with an error message and continue operation

### Requirement 2: Frame Extraction

**User Story:** Как система, я хочу извлечь ключевые кадры из видео, чтобы AI мог проанализировать еду с разных ракурсов.

#### Acceptance Criteria

1. WHEN a video file is available, THE Frame_Extractor SHALL extract exactly 5 frames at equal time intervals
2. WHEN extracting frames, THE Frame_Extractor SHALL calculate intervals as video_duration divided by 6 to get 5 evenly spaced frames
3. WHEN a frame is extracted, THE System SHALL save it in a format compatible with the AI API (JPEG or PNG)
4. IF frame extraction fails for any frame, THEN THE System SHALL attempt to extract remaining frames and proceed with available frames
5. WHEN all frames are extracted, THE System SHALL store them in temporary storage with unique identifiers

### Requirement 3: Audio Transcription

**User Story:** Как система, я хочу транскрибировать речь из видео, чтобы учесть голосовую информацию пользователя при анализе еды.

#### Acceptance Criteria

1. WHEN a video file is available, THE Audio_Transcriber SHALL extract the audio track from the video
2. WHEN audio is extracted, THE Audio_Transcriber SHALL send it to the transcription service for speech-to-text conversion
3. WHEN transcribing, THE Audio_Transcriber SHALL specify Russian language as the primary language
4. IF audio extraction fails, THEN THE System SHALL proceed with visual analysis only and notify the user
5. IF transcription returns empty text, THEN THE System SHALL proceed with visual analysis only
6. WHERE Mock_Mode is enabled, THE Audio_Transcriber SHALL return predefined mock transcription text without calling external services

### Requirement 4: Multimodal Analysis

**User Story:** Как система, я хочу отправить кадры и транскрипцию в AI, чтобы получить точный анализ еды с учетом визуальной и текстовой информации.

#### Acceptance Criteria

1. WHEN frames and transcription are ready, THE Multimodal_Analyzer SHALL prepare a request with all frames and transcription text
2. WHEN preparing the request, THE Multimodal_Analyzer SHALL format the prompt to request food identification, weight estimation, calories, and macronutrients
3. WHEN sending to OpenRouter API, THE Multimodal_Analyzer SHALL use the model qwen/qwen-2-vl-7b-instruct:free
4. WHEN transcription text is available, THE Multimodal_Analyzer SHALL include it in the prompt with context that it contains user's voice description
5. WHEN transcription text is empty, THE Multimodal_Analyzer SHALL proceed with visual-only analysis
6. IF the API request fails, THEN THE System SHALL retry up to 2 times before notifying the user of the error

### Requirement 5: Result Parsing

**User Story:** Как система, я хочу извлечь структурированные данные из ответа AI, чтобы показать пользователю информацию о калориях и БЖУ.

#### Acceptance Criteria

1. WHEN AI response is received, THE System SHALL parse the response to extract JSON data with food items
2. WHEN parsing, THE System SHALL extract for each food item: name, weight, calories, protein, fat, and carbohydrates
3. IF the response does not contain valid JSON, THEN THE System SHALL attempt to extract structured data from text format
4. IF parsing fails completely, THEN THE System SHALL notify the user that analysis could not be completed
5. WHEN parsing succeeds, THE System SHALL validate that numeric values are non-negative

### Requirement 6: Result Formatting and Display

**User Story:** Как пользователь, я хочу увидеть результат анализа в читаемом формате, чтобы понять состав и калорийность моей еды.

#### Acceptance Criteria

1. WHEN parsed data is available, THE Result_Formatter SHALL format the output with food names, weights, calories, and macronutrients
2. WHEN formatting, THE Result_Formatter SHALL include appropriate emoji for visual clarity
3. WHEN displaying results, THE System SHALL show total calories and total macronutrients as a summary
4. WHEN transcription was used, THE System SHALL indicate in the message that voice information was considered
5. WHEN sending the formatted result, THE System SHALL use Telegram markdown formatting for readability

### Requirement 7: Correction Support

**User Story:** Как пользователь, я хочу иметь возможность скорректировать результаты анализа видео-кружка, чтобы уточнить данные о еде.

#### Acceptance Criteria

1. WHEN analysis results are displayed, THE System SHALL provide correction options similar to photo analysis
2. WHEN a user requests correction, THE System SHALL allow modification of food items, weights, and macronutrients
3. WHEN corrections are applied, THE System SHALL recalculate totals and update the display
4. WHEN corrections are saved, THE System SHALL store the corrected data in the database

### Requirement 8: Error Handling and Graceful Degradation

**User Story:** Как система, я хочу корректно обрабатывать ошибки на каждом этапе, чтобы пользователь получил максимально возможный результат даже при частичных сбоях.

#### Acceptance Criteria

1. IF video download fails, THEN THE System SHALL notify the user and request to try again
2. IF frame extraction fails completely, THEN THE System SHALL notify the user that video processing failed
3. IF audio transcription fails, THEN THE System SHALL proceed with visual-only analysis and inform the user
4. IF AI analysis fails after retries, THEN THE System SHALL notify the user with a clear error message
5. WHEN any error occurs, THE System SHALL log the error details for debugging while showing user-friendly messages

### Requirement 9: Resource Management

**User Story:** Как система, я хочу эффективно управлять временными файлами, чтобы не засорять хранилище и избежать утечек ресурсов.

#### Acceptance Criteria

1. WHEN video processing is complete, THE System SHALL delete the downloaded video file from temporary storage
2. WHEN frame extraction is complete, THE System SHALL delete extracted frame files after AI analysis
3. WHEN audio extraction is complete, THE System SHALL delete the extracted audio file after transcription
4. IF processing is interrupted by an error, THEN THE System SHALL still attempt to clean up temporary files
5. THE System SHALL use unique identifiers for temporary files to avoid conflicts between concurrent requests

### Requirement 10: Integration with Existing Flow

**User Story:** Как пользователь, я хочу чтобы анализ видео-кружков работал так же, как анализ фото, чтобы иметь единообразный опыт использования бота.

#### Acceptance Criteria

1. WHEN video analysis is complete, THE System SHALL store results in the same database format as photo analysis
2. WHEN displaying results, THE System SHALL use the same formatting style as photo analysis results
3. WHEN corrections are requested, THE System SHALL use the same correction flow as photo analysis
4. WHEN saving to history, THE System SHALL mark entries as originating from video analysis for future reference
5. THE System SHALL support the same user commands and interactions for video analysis as for photo analysis

## Notes

- Фаза 1 реализации будет использовать Mock_Mode для транскрипции
- OpenCV (cv2) будет использоваться для работы с видео
- OpenRouter API поддерживает мультимодальные запросы с несколькими изображениями
- Временные файлы должны храниться в директории, доступной для чтения/записи
- Транскрипция может быть неточной при фоновом шуме - это ожидаемое поведение
