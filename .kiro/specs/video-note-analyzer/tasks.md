# Implementation Plan: Video Note Analyzer

## Overview

Реализация анализа видео-кружков для Telegram бота подсчета калорий. Фича добавляет возможность анализировать еду через короткие видео с извлечением кадров, транскрипцией речи и мультимодальным AI анализом.

**Подход к реализации:**
- Инкрементальная разработка по фазам (MVP → полная функциональность)
- Использование существующей архитектуры (SessionManager, StateManager, форматтеры)
- Property-based тесты для критических компонентов
- Graceful degradation при ошибках

## Tasks

- [ ] 1. Setup project structure and dependencies
  - Add opencv-python to requirements.txt
  - Create handlers/video_notes.py
  - Create modules/nutrition/frame_extractor.py
  - Create modules/nutrition/audio_transcriber.py
  - Create modules/nutrition/video_note_analyzer.py
  - Create utils/temp_storage.py
  - Add configuration constants to config.py
  - _Requirements: All_

- [ ] 2. Implement temporary file management
  - [ ] 2.1 Create TempStorage utility class
    - Implement unique file ID generation
    - Implement file path management with session IDs
    - Implement cleanup methods for individual files and sessions
    - Add scheduled cleanup for orphaned files
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_
  
  - [ ]* 2.2 Write property test for unique file identifiers
    - **Property 18: Resource Cleanup**
    - **Validates: Requirements 9.5**
    - Test that concurrent sessions generate unique file IDs without conflicts

- [ ] 3. Implement FrameExtractor (Phase 2)
  - [ ] 3.1 Create FrameExtractor class with OpenCV
    - Implement video opening and metadata extraction
    - Implement frame interval calculation (duration / 6)
    - Implement frame extraction at calculated timestamps
    - Save frames as JPEG with unique names
    - Handle partial extraction failures gracefully
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [ ]* 3.2 Write property test for frame extraction count
    - **Property 3: Frame Extraction Count and Spacing**
    - **Validates: Requirements 2.1, 2.2**
    - Test that exactly 5 frames are extracted at correct intervals for any video duration
  
  - [ ]* 3.3 Write property test for frame format
    - **Property 4: Frame Format Compatibility**
    - **Validates: Requirements 2.3**
    - Test that all extracted frames are in JPEG or PNG format
  
  - [ ]* 3.4 Write unit tests for FrameExtractor
    - Test extraction with valid video
    - Test extraction with very short video (< 1 second)
    - Test extraction with corrupted video
    - Test partial extraction when some frames fail
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [ ] 4. Implement AudioTranscriber with mock mode (Phase 1)
  - [ ] 4.1 Create AudioTranscriber class with mock implementation
    - Implement __init__ with use_mock parameter
    - Implement mock transcription returning predefined Russian text
    - Add audio extraction placeholder (returns None in mock mode)
    - Add error handling that returns None gracefully
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_
  
  - [ ]* 4.2 Write property test for mock mode behavior
    - **Property 7: Mock Mode Behavior**
    - **Validates: Requirements 3.6**
    - Test that mock mode never calls external services and always returns mock data
  
  - [ ]* 4.3 Write unit tests for AudioTranscriber
    - Test mock mode returns predefined text
    - Test mock mode doesn't call external services
    - Test error handling returns None
    - _Requirements: 3.6, 3.4, 3.5_

- [ ] 5. Checkpoint - Ensure frame extraction and mock transcription work
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 6. Implement VideoNoteAnalyzer with mock mode (Phase 1)
  - [ ] 6.1 Create MockVideoNoteAnalyzer class
    - Implement analyze_video_note returning predefined mock data
    - Include transcription_used flag based on input
    - Return realistic food analysis data
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
  
  - [ ]* 6.2 Write unit tests for MockVideoNoteAnalyzer
    - Test returns valid analysis structure
    - Test transcription_used flag is set correctly
    - Test all required fields are present
    - _Requirements: 4.1, 4.4, 4.5_

- [ ] 7. Implement VideoNoteAnalyzer with real API (Phase 3)
  - [ ] 7.1 Create VideoNoteAnalyzer class with OpenRouter integration
    - Implement prompt preparation with frames and transcription
    - Implement image encoding to base64
    - Implement multimodal API request to OpenRouter
    - Use model: qwen/qwen-2-vl-7b-instruct:free
    - Implement retry logic (up to 2 retries with exponential backoff)
    - Implement response parsing (JSON and text fallback)
    - Implement numeric validation (non-negative values)
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [ ]* 7.2 Write property test for API retry logic
    - **Property 10: API Retry Logic**
    - **Validates: Requirements 4.6**
    - Test that failed API calls are retried exactly 2 times before failing
  
  - [ ]* 7.3 Write property test for numeric validation
    - **Property 13: Numeric Validation**
    - **Validates: Requirements 5.5**
    - Test that all numeric values in parsed results are non-negative
  
  - [ ]* 7.4 Write property test for graceful degradation
    - **Property 8: Graceful Degradation on Transcription Failure**
    - **Validates: Requirements 3.4, 3.5, 4.5, 8.3**
    - Test that analysis proceeds with visual-only mode when transcription is None or empty
  
  - [ ]* 7.5 Write unit tests for VideoNoteAnalyzer
    - Test analysis with frames only (no transcription)
    - Test analysis with frames + transcription
    - Test JSON response parsing
    - Test text fallback parsing
    - Test API error handling
    - Test retry logic
    - _Requirements: 4.1, 4.4, 4.5, 4.6, 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 8. Extend result formatting for video notes
  - [ ] 8.1 Add video note formatting to utils/formatters.py
    - Create format_video_note_analysis function
    - Include transcription usage indicator
    - Reuse existing formatting components
    - Add video-specific emoji and messaging
    - Ensure Telegram markdown compatibility
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_
  
  - [ ]* 8.2 Write property test for result formatting
    - **Property 14: Result Formatting Completeness**
    - **Validates: Requirements 6.1, 6.2, 6.3, 6.5**
    - Test that formatted output contains all required elements for any analysis data
  
  - [ ]* 8.3 Write property test for transcription indicator
    - **Property 15: Transcription Usage Indicator**
    - **Validates: Requirements 6.4**
    - Test that transcription indicator appears when transcription was used
  
  - [ ]* 8.4 Write unit tests for video note formatting
    - Test formatting with all fields present
    - Test formatting with transcription indicator
    - Test formatting without transcription
    - Test markdown syntax
    - Test emoji presence
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 9. Implement VideoNoteHandler
  - [ ] 9.1 Create handle_video_note_message function
    - Check user registration
    - Check user state (IDLE or WAITING_FOR_PHOTO)
    - Send status message "Обрабатываю видео..."
    - Download video to temp storage
    - Create session via SessionManager
    - Set state to ANALYZING_VIDEO
    - Extract frames via FrameExtractor
    - Transcribe audio via AudioTranscriber
    - Analyze via VideoNoteAnalyzer (use mock or real based on config)
    - Format results via format_video_note_analysis
    - Save initial analysis to session
    - Set state to WAITING_CONFIRMATION
    - Send results with action buttons
    - Cleanup temp files
    - Handle errors at each stage with appropriate user messages
    - _Requirements: 1.1, 1.2, 1.4, 8.1, 8.2, 8.3, 8.4, 8.5, 9.1, 9.2, 9.3, 9.4_
  
  - [ ]* 9.2 Write property test for video note acceptance
    - **Property 1: Video Note Acceptance**
    - **Validates: Requirements 1.1**
    - Test that all valid video notes from registered users are accepted
  
  - [ ]* 9.3 Write property test for video download
    - **Property 2: Video Download Completion**
    - **Validates: Requirements 1.2, 9.5**
    - Test that downloaded videos have unique identifiers and exist in temp storage
  
  - [ ]* 9.4 Write property test for error notifications
    - **Property 17: Error Notification**
    - **Validates: Requirements 8.1, 8.2, 8.4, 8.5**
    - Test that all error types result in user notification and error logging
  
  - [ ]* 9.5 Write unit tests for VideoNoteHandler
    - Test user registration check
    - Test state validation
    - Test session creation
    - Test download error handling
    - Test frame extraction error handling
    - Test API error handling
    - Test cleanup on success
    - Test cleanup on error
    - _Requirements: 1.1, 1.2, 1.4, 8.1, 8.2, 8.3, 8.4, 8.5, 9.4_

- [ ] 10. Checkpoint - Ensure end-to-end flow works with mock data
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 11. Register video note handler in bot
  - [ ] 11.1 Add video note handler to main bot application
    - Import handle_video_note_message
    - Register handler with application.add_handler
    - Add VIDEO_NOTE message type filter
    - Ensure handler priority is correct
    - _Requirements: 1.1_
  
  - [ ]* 11.2 Write integration test for handler registration
    - Test video note messages are routed to handler
    - Test handler is called with correct parameters
    - _Requirements: 1.1_

- [ ] 12. Implement database integration for video notes
  - [ ] 12.1 Extend session model to support video notes
    - Add video_file_id field to sessions table
    - Add source_type field ('video_note' vs 'photo')
    - Add transcription field for storing transcribed text
    - Update SessionManager to handle video note sessions
    - _Requirements: 10.1, 10.4_
  
  - [ ]* 12.2 Write property test for integration consistency
    - **Property 19: Integration Consistency**
    - **Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5**
    - Test that video analysis data format matches photo analysis format
  
  - [ ]* 12.3 Write unit tests for database integration
    - Test video note session creation
    - Test source_type is set correctly
    - Test transcription is stored
    - Test data format matches photo analysis
    - _Requirements: 10.1, 10.4_

- [ ] 13. Implement correction support for video notes
  - [ ] 13.1 Extend correction handlers to support video notes
    - Verify correction flow works with video note sessions
    - Ensure correction buttons appear after video analysis
    - Ensure corrections recalculate totals
    - Ensure corrections are saved to database
    - _Requirements: 7.1, 7.2, 7.3, 7.4_
  
  - [ ]* 13.2 Write property test for correction flow
    - **Property 16: Correction Flow Consistency**
    - **Validates: Requirements 7.1, 7.2, 7.3, 7.4**
    - Test that correction flow is identical for video and photo analysis
  
  - [ ]* 13.3 Write unit tests for video note corrections
    - Test correction options are displayed
    - Test corrections modify data correctly
    - Test totals are recalculated
    - Test corrections are saved to database
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [ ] 14. Add configuration and feature flags
  - [ ] 14.1 Add video note configuration to config.py
    - Add VIDEO_NOTE_ENABLED flag
    - Add VIDEO_NOTE_TEMP_DIR path
    - Add VIDEO_NOTE_MAX_SIZE_MB limit
    - Add VIDEO_NOTE_FRAME_COUNT setting
    - Add USE_MOCK_TRANSCRIPTION flag
    - Add TRANSCRIPTION_LANGUAGE setting
    - Add OPENROUTER_VIDEO_MODEL setting
    - Add OPENROUTER_MAX_RETRIES setting
    - _Requirements: All_

- [ ] 15. Checkpoint - Ensure all features work end-to-end
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 16. Add monitoring and logging
  - [ ] 16.1 Add comprehensive logging to all components
    - Log video processing start/completion
    - Log frame extraction metrics
    - Log transcription success/failure
    - Log API call metrics
    - Log cleanup operations
    - Use appropriate log levels (INFO, WARNING, ERROR, DEBUG)
    - _Requirements: 8.5_
  
  - [ ]* 16.2 Write unit tests for logging
    - Test all major operations are logged
    - Test error details are logged
    - Test log levels are appropriate
    - _Requirements: 8.5_

- [ ] 17. Add error messages to config
  - [ ] 17.1 Add user-friendly error messages to config.py
    - Add message for video download failure
    - Add message for frame extraction failure
    - Add message for transcription failure (with visual-only note)
    - Add message for API failure
    - Add message for parsing failure
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [ ] 18. Final integration and testing
  - [ ] 18.1 Run full integration test suite
    - Test end-to-end with mock data
    - Test end-to-end with real OpenCV but mock API
    - Test correction flow
    - Test database integration
    - Test cleanup on success and error
    - _Requirements: All_
  
  - [ ]* 18.2 Run all property-based tests
    - Verify all 19 properties pass with 100+ iterations
    - Fix any failures discovered
    - _Requirements: All_

- [ ] 19. Documentation and deployment preparation
  - [ ] 19.1 Update README with video note feature
    - Document new dependencies (opencv-python)
    - Document configuration options
    - Document usage instructions
    - Document limitations and known issues
    - _Requirements: All_

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Phase 1 (MVP) includes tasks 1-6, 8-11, 14, 17 with mock implementations
- Phase 2 adds real frame extraction (task 3)
- Phase 3 adds real API integration (task 7)
- Phase 4 (optional) would add real audio transcription (requires extending task 4)
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- Checkpoints ensure incremental validation
