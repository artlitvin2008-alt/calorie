"""
Обработчики команд и сообщений Telegram бота
"""
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from api_client import OpenRouterClient
from config import (
    WELCOME_MESSAGE,
    HELP_MESSAGE,
    ANALYZING_MESSAGE,
    ERROR_NO_PHOTO,
    ERROR_POOR_QUALITY,
    ERROR_API,
    ERROR_GENERAL,
    CACHE_TIMEOUT_SECONDS
)

logger = logging.getLogger(__name__)

# Кэш для хранения результатов анализа
analysis_cache: Dict[str, Dict[str, Any]] = {}

# Инициализация клиента API
api_client = OpenRouterClient()


def get_cache_key(file_unique_id: str) -> str:
    """Генерирует ключ кэша для файла"""
    return hashlib.md5(file_unique_id.encode()).hexdigest()


def get_from_cache(cache_key: str) -> Any:
    """Получает результат из кэша, если он не устарел"""
    if cache_key in analysis_cache:
        cached_data = analysis_cache[cache_key]
        if datetime.now() - cached_data['timestamp'] < timedelta(seconds=CACHE_TIMEOUT_SECONDS):
            logger.info(f"Результат найден в кэше: {cache_key}")
            return cached_data['result']
        else:
            # Удаляем устаревший кэш
            del analysis_cache[cache_key]
    return None


def save_to_cache(cache_key: str, result: Dict[str, Any]):
    """Сохраняет результат в кэш"""
    analysis_cache[cache_key] = {
        'result': result,
        'timestamp': datetime.now()
    }
    logger.info(f"Результат сохранен в кэш: {cache_key}")


def format_analysis_message(data: Dict[str, Any]) -> str:
    """
    Форматирует результаты анализа в красивое сообщение
    
    Args:
        data: Словарь с результатами анализа
        
    Returns:
        Отформатированное сообщение
    """
    message = f"""🍽️ *Название:* {data['dish_name']}

⚖️ *Общий вес:* {data['weight_grams']} г

🔥 *Калорийность:* {data['calories_total']} ккал ({data['calories_per_100g']:.0f} ккал/100г)

*Состав БЖУ:*
🥚 Белки: {data['protein_g']} г
🥑 Жиры: {data['fat_g']} г
🌾 Углеводы: {data['carbs_g']} г

⭐ *Полезность:* {data['health_score']}/10"""

    # Добавляем детализацию по компонентам, если есть
    if 'components' in data and data['components']:
        message += "\n\n📊 *Детализация:*"
        for comp in data['components']:
            comp_name = comp.get('name', 'Неизвестно')
            comp_weight = comp.get('weight_grams', 0)
            comp_calories = comp.get('calories', 0)
            message += f"\n• {comp_name}: {comp_weight}г, {comp_calories} ккал"
    
    # Добавляем анализ
    message += f"\n\n📋 *Анализ:*\n{data['detailed_analysis']}"
    
    # Добавляем предупреждения, если есть
    if 'warnings' in data and data['warnings']:
        message += "\n\n⚠️ *Предупреждения:*"
        for warning in data['warnings']:
            message += f"\n{warning}"
    
    # Добавляем рекомендации
    message += f"\n\n💡 *Рекомендации для похудения:*\n{data['recommendations']}"
    
    # Добавляем совет по порции
    message += f"\n\n📏 *Совет по порции:*\n{data['portion_advice']}"
    
    return message


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    logger.info(f"Пользователь {update.effective_user.id} запустил бота")
    await update.message.reply_text(WELCOME_MESSAGE)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    logger.info(f"Пользователь {update.effective_user.id} запросил помощь")
    await update.message.reply_text(HELP_MESSAGE)


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик фотографий
    """
    user_id = update.effective_user.id
    logger.info(f"Получено фото от пользователя {user_id}")
    
    try:
        # Проверяем наличие фото
        if not update.message.photo:
            await update.message.reply_text(ERROR_NO_PHOTO)
            return
        
        # Отправляем сообщение о начале анализа
        status_message = await update.message.reply_text(ANALYZING_MESSAGE)
        
        # Получаем фото максимального качества (последнее в списке)
        photo = update.message.photo[-1]
        file_unique_id = photo.file_unique_id
        
        # Проверяем кэш
        cache_key = get_cache_key(file_unique_id)
        cached_result = get_from_cache(cache_key)
        
        if cached_result:
            # Используем кэшированный результат
            formatted_message = format_analysis_message(cached_result)
            await status_message.edit_text(
                formatted_message,
                parse_mode=ParseMode.MARKDOWN
            )
            logger.info(f"Отправлен кэшированный результат пользователю {user_id}")
            return
        
        # Скачиваем фото
        file = await context.bot.get_file(photo.file_id)
        image_bytes = await file.download_as_bytearray()
        
        logger.info(f"Фото скачано: {len(image_bytes)} байт")
        
        # Анализируем фото через API
        result = await api_client.analyze_food_image(bytes(image_bytes))
        
        if result is None:
            await status_message.edit_text(ERROR_POOR_QUALITY)
            logger.warning(f"Не удалось проанализировать фото от пользователя {user_id}")
            return
        
        # Сохраняем в кэш
        save_to_cache(cache_key, result)
        
        # Форматируем и отправляем результат
        formatted_message = format_analysis_message(result)
        await status_message.edit_text(
            formatted_message,
            parse_mode=ParseMode.MARKDOWN
        )
        
        logger.info(f"Анализ успешно отправлен пользователю {user_id}")
        
    except Exception as e:
        logger.error(f"Ошибка при обработке фото: {e}", exc_info=True)
        try:
            await status_message.edit_text(ERROR_GENERAL)
        except:
            await update.message.reply_text(ERROR_GENERAL)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    logger.info(f"Получено текстовое сообщение от пользователя {update.effective_user.id}")
    await update.message.reply_text(
        "📸 Пожалуйста, отправьте фото блюда для анализа.\n\n"
        "Используйте /help для получения инструкций."
    )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Ошибка при обработке обновления: {context.error}", exc_info=context.error)
    
    if update and update.effective_message:
        await update.effective_message.reply_text(ERROR_GENERAL)
