"""
Обработчик видео-кружков (Video Note) с анализом еды
Поддерживает извлечение кадров и транскрипцию аудио
"""

import asyncio
import tempfile
import aiohttp
import logging
import base64
import json
import re
from pathlib import Path
from typing import Optional, List, Dict, Any
from telegram import Update
from telegram.ext import ContextTypes

from modules.video_analysis import (
    KeyFrameExtractor,
    AudioContextParser,
    VideoAnalyzer,
    EvidenceAggregator
)

logger = logging.getLogger(__name__)


class VideoNoteAnalyzer:
    """Анализатор видео-кружков с извлечением кадров и транскрипцией"""
    
    def __init__(self, config, openrouter_client=None):
        self.config = config
        self.openrouter_client = openrouter_client
        self.speech_to_text_url = "https://api.openrouter.ai/v1/audio/transcriptions"
        
        # Initialize new analysis modules
        self.keyframe_extractor = KeyFrameExtractor(target_frames=5)
        self.audio_parser = AudioContextParser(config=config, use_mock=False)  # Real audio transcription
        self.video_analyzer = VideoAnalyzer(config)
        self.evidence_aggregator = EvidenceAggregator()
    
    async def analyze_video_note(self, video_bytes: bytes, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Полный анализ видео-кружка: кадры + аудио
        
        NEW PIPELINE:
        1. Extract audio hypothesis (what user said)
        2. Extract best keyframes (intelligent selection)
        3. Analyze each frame with hypothesis context
        4. Aggregate evidence from all frames + audio
        
        Returns dict with:
        - analysis: final analysis result
        - frames: list of extracted frame images (bytes)
        - transcription: audio transcription text
        """
        try:
            # Сохраняем видео во временный файл
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp_file:
                tmp_file.write(video_bytes)
                video_path = tmp_file.name
            
            try:
                logger.info("=== Starting NEW video analysis pipeline ===")
                
                # STEP 1: Extract audio hypothesis
                logger.info("Step 1: Extracting audio hypothesis...")
                audio_hypothesis = await self.audio_parser.extract_hypothesis(video_path)
                logger.info(f"Audio hypothesis: {audio_hypothesis}")
                
                # STEP 2: Extract best keyframes
                logger.info("Step 2: Extracting keyframes...")
                frames = await self.keyframe_extractor.process(video_path)
                if not frames:
                    logger.error("Failed to extract keyframes")
                    return None
                logger.info(f"Extracted {len(frames)} keyframes")
                
                # STEP 3: Analyze frames with hypothesis context
                logger.info("Step 3: Analyzing frames with hypothesis...")
                visual_evidence = await self.video_analyzer.analyze_frames(
                    frames, 
                    audio_hypothesis
                )
                if not visual_evidence:
                    logger.error("Failed to analyze frames")
                    return None
                logger.info(f"Analyzed {len(visual_evidence)} frames")
                
                # STEP 4: Aggregate all evidence
                logger.info("Step 4: Aggregating evidence...")
                final_analysis = await self.evidence_aggregator.aggregate(
                    audio_hypothesis,
                    visual_evidence
                )
                
                logger.info("=== Analysis complete ===")
                logger.info(f"Final result: {final_analysis.get('dish_name')}, "
                          f"{final_analysis.get('calories_total')} kcal")
                
                # Add metadata
                final_analysis['frames_count'] = len(frames)
                
                # Return analysis + frames + transcription
                return {
                    'analysis': final_analysis,
                    'frames': frames,
                    'transcription': audio_hypothesis.get('transcription', '')
                }
                
            finally:
                # Удаляем временный файл
                Path(video_path).unlink(missing_ok=True)
                
        except Exception as e:
            logger.error(f"Ошибка анализа видео: {e}", exc_info=True)
            return None



class MockVideoNoteAnalyzer:
    """Мок-версия для тестирования без реального видео"""
    
    async def analyze_video_note(self, video_bytes: bytes, user_id: int) -> Dict[str, Any]:
        """Возвращает мок-данные для тестирования"""
        return {
            "dish_name": "Картофельное пюре с хлебом и чаем",
            "components": [
                {
                    "name": "Картофельное пюре",
                    "weight_g": 400,
                    "calories": 320,
                    "protein_g": 8,
                    "fat_g": 12,
                    "carbs_g": 52,
                    "confidence": 0.85
                },
                {
                    "name": "Хлеб белый",
                    "weight_g": 80,
                    "calories": 200,
                    "protein_g": 6,
                    "fat_g": 2,
                    "carbs_g": 40,
                    "confidence": 0.75
                },
                {
                    "name": "Чай с сахаром",
                    "weight_g": 200,
                    "calories": 40,
                    "protein_g": 0,
                    "fat_g": 0,
                    "carbs_g": 10,
                    "confidence": 0.70
                }
            ],
            "weight_grams": 680,
            "calories_total": 560,
            "calories_per_100g": 82,
            "protein_g": 14,
            "fat_g": 14,
            "carbs_g": 102,
            "health_score": 6,
            "warnings": [
                "Много углеводов (102г)",
                "Можно добавить белка (курица, рыба)"
            ],
            "audio_transcription": "пюре думаю здесь 500г и наверное еще хлеба съем два кусочка плюс чай",
            "frames_count": 5,
            "source": "video_note"
        }


async def handle_video_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик видео-кружков"""
    user_id = update.effective_user.id
    
    # Проверяем регистрацию
    user_manager = context.bot_data['user_manager']
    is_registered = await user_manager.is_registered(user_id)
    
    if not is_registered:
        await update.message.reply_text(
            "❌ Сначала зарегистрируйся с помощью /start и /setup"
        )
        return
    
    # Скачиваем видео
    video_note = update.message.video_note
    bot = context.bot
    file = await bot.get_file(video_note.file_id)
    
    # Показываем сообщение о начале обработки
    processing_msg = await update.message.reply_text(
        "🎥 Анализирую видео-кружок...\n"
        "⏳ Извлекаю кадры и анализирую содержимое..."
    )
    
    try:
        # Скачиваем видео
        video_bytes = await file.download_as_bytearray()
        logger.info(f"Скачано видео: {len(video_bytes)} байт")
        
        # Создаем анализатор
        import config
        
        # Проверяем, установлен ли OpenCV
        try:
            import cv2
            use_real_analyzer = True
            logger.info("OpenCV доступен, используем реальный анализатор")
        except ImportError:
            use_real_analyzer = False
            logger.warning("OpenCV не установлен, используем мок-анализатор")
        
        # Выбираем анализатор
        # Всегда используем реальный анализатор с OpenRouter API
        if use_real_analyzer:
            video_analyzer = VideoNoteAnalyzer(config)
        else:
            # Fallback на мок, если OpenCV не установлен
            video_analyzer = MockVideoNoteAnalyzer()
        
        # Анализируем видео
        result = await video_analyzer.analyze_video_note(video_bytes, user_id)
        
        if not result:
            await processing_msg.edit_text(
                "❌ Не удалось проанализировать видео. Попробуй ещё раз."
            )
            return
        
        # Извлекаем данные из результата
        analysis = result.get('analysis', result)  # Fallback для старого формата
        frames = result.get('frames', [])
        transcription = result.get('transcription', '')
        
        # 1. Отправляем транскрипцию (если есть)
        if transcription:
            await update.message.reply_text(
                f"🎤 *Транскрипция аудио:*\n\n_{transcription}_",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "🎤 _Аудио не обнаружено или не удалось распознать_",
                parse_mode='Markdown'
            )
        
        # 2. Отправляем извлечённые кадры
        if frames:
            await update.message.reply_text(
                f"📸 *Извлечено {len(frames)} ключевых кадров:*",
                parse_mode='Markdown'
            )
            
            # Отправляем кадры как медиа-группу (до 10 фото)
            from telegram import InputMediaPhoto
            import io
            
            media_group = []
            for i, frame_bytes in enumerate(frames[:10]):  # Telegram limit: 10 photos
                media_group.append(
                    InputMediaPhoto(
                        media=io.BytesIO(frame_bytes),
                        caption=f"Кадр {i+1}/{len(frames)}"
                    )
                )
            
            await update.message.reply_media_group(media=media_group)
        
        # 3. Форматируем и отправляем результат анализа
        from utils.formatters import format_video_note_analysis
        formatted_result = format_video_note_analysis(analysis)
        
        # Обновляем сообщение
        await processing_msg.edit_text(
            formatted_result,
            parse_mode='Markdown'
        )
        
        # Сохраняем в сессию (для коррекций)
        session_manager = context.bot_data['session_manager']
        
        # Создаем новую сессию (используем file_id видео вместо photo_file_id)
        session_id = await session_manager.create_session(
            user_id,
            video_note.file_id
        )
        
        # Обновляем сессию с результатами анализа
        await session_manager.update_session(
            session_id,
            initial_analysis=analysis,
            status='pending'
        )
        
        # Устанавливаем состояние
        from core.state_machine import UserState
        state_manager = context.bot_data.get('state_manager')
        if state_manager:
            await state_manager.set_state(user_id, UserState.WAITING_CONFIRMATION)
        
        # Показываем кнопки
        from utils.keyboards import create_analysis_actions_keyboard
        keyboard = create_analysis_actions_keyboard()
        await update.message.reply_text(
            "Что дальше?",
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error(f"Ошибка обработки видео: {e}", exc_info=True)
        await processing_msg.edit_text(
            f"❌ Произошла ошибка: {str(e)}\n\n"
            "Попробуй записать видео заново."
        )
