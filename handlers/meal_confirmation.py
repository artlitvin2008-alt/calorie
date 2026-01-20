"""
Meal confirmation and saving handler
"""
import logging
from datetime import datetime
from typing import Dict, Any
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from core.state_machine import UserState
from utils.formatters import format_meal_saved, format_daily_progress, format_error
import config

logger = logging.getLogger(__name__)


async def confirm_and_save_meal(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    query=None
) -> bool:
    """
    Confirm and save meal analysis to database
    
    Args:
        update: Telegram update
        context: Bot context
        query: Callback query (if called from button)
    
    Returns:
        True if saved successfully, False otherwise
    """
    user_id = update.effective_user.id
    state_manager = context.bot_data['state_manager']
    session_manager = context.bot_data['session_manager']
    user_manager = context.bot_data['user_manager']
    db = context.bot_data['database']
    
    # Verify state
    current_state = await state_manager.get_state(user_id)
    
    if current_state != UserState.WAITING_CONFIRMATION:
        message = format_error('no_session')
        if query:
            await query.edit_message_text(message, parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
        return False
    
    # Get active session
    session = await session_manager.get_active_session(user_id)
    
    if not session:
        message = format_error('no_session')
        if query:
            await query.edit_message_text(message, parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
        return False
    
    session_id = session['session_id']
    
    try:
        # Get final analysis (corrected if exists, otherwise initial)
        final_analysis = await session_manager.get_current_analysis(session_id)
        
        if not final_analysis:
            message = format_error('no_session')
            if query:
                await query.edit_message_text(message, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            return False
        
        # Get user data for goals
        user = await user_manager.db.get_user(user_id)
        
        # Prepare meal data
        meal_data = {
            'user_id': user_id,
            'session_id': session_id,
            'dish_name': final_analysis.get('dish_name', 'Блюдо'),
            'meal_type': session.get('meal_type', 'snack'),  # Default to snack
            'photo_file_id': session.get('photo_file_id'),
            'components': final_analysis.get('components', []),
            'total_weight': final_analysis.get('weight_grams', 0),
            'total_calories': final_analysis.get('calories_total', 0),
            'protein_g': final_analysis.get('protein_g', 0),
            'fat_g': final_analysis.get('fat_g', 0),
            'carbs_g': final_analysis.get('carbs_g', 0),
            'health_score': final_analysis.get('health_score', 5),
            'confidence_avg': _calculate_avg_confidence(final_analysis),
            'corrections_count': session.get('correction_count', 0),
            'eaten_at': datetime.now()
        }
        
        # Save meal to database
        meal_id = await db.save_meal(meal_data)
        
        if not meal_id:
            raise Exception("Failed to save meal to database")
        
        logger.info(f"Meal saved: {meal_id} for user {user_id}")
        
        # Update daily statistics
        await _update_daily_stats(db, user_id, meal_data)
        
        # Complete session
        await session_manager.complete_session(session_id, final_analysis)
        
        # Reset state
        await state_manager.set_state(user_id, UserState.IDLE, validate=False)
        
        # Get updated daily stats
        daily_stats = await db.get_daily_stats(user_id, datetime.now().date())
        
        # Format success message
        message = format_meal_saved(meal_data, user, daily_stats)
        
        # Send message
        if query:
            await query.edit_message_text(message, parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
        
        # Check if goals achieved and send additional message
        if daily_stats:
            progress_message = await _check_goals_and_get_message(user, daily_stats)
            if progress_message:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=progress_message,
                    parse_mode=ParseMode.MARKDOWN
                )
        
        logger.info(f"User {user_id} confirmed and saved meal {meal_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving meal: {e}", exc_info=True)
        message = format_error('save_error', str(e))
        if query:
            await query.edit_message_text(message, parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
        
        # Reset state anyway
        await state_manager.reset_state(user_id)
        return False


def _calculate_avg_confidence(analysis: Dict[str, Any]) -> float:
    """Calculate average confidence from components"""
    components = analysis.get('components', [])
    if not components:
        return 0.0
    
    confidences = [c.get('confidence', 0.5) for c in components]
    return sum(confidences) / len(confidences)


async def _update_daily_stats(db, user_id: int, meal_data: Dict[str, Any]):
    """Update daily statistics with new meal"""
    today = datetime.now().date()
    
    # Get existing stats
    stats = await db.get_daily_stats(user_id, today)
    
    if stats:
        # Update existing stats
        await db.update_daily_stats(
            user_id=user_id,
            date=today,
            calories_consumed=stats['calories_consumed'] + meal_data['total_calories'],
            protein_consumed=stats['protein_consumed'] + meal_data['protein_g'],
            fat_consumed=stats['fat_consumed'] + meal_data['fat_g'],
            carbs_consumed=stats['carbs_consumed'] + meal_data['carbs_g'],
            meals_count=stats['meals_count'] + 1
        )
    else:
        # Create new stats
        await db.create_daily_stats(
            user_id=user_id,
            date=today,
            calories_consumed=meal_data['total_calories'],
            protein_consumed=meal_data['protein_g'],
            fat_consumed=meal_data['fat_g'],
            carbs_consumed=meal_data['carbs_g'],
            meals_count=1
        )
    
    logger.info(f"Daily stats updated for user {user_id}")


async def _check_goals_and_get_message(user: Dict[str, Any], daily_stats: Dict[str, Any]) -> str:
    """
    Check if user achieved goals and return motivational message
    
    Returns:
        Message string or empty string if no special message needed
    """
    if not user or not daily_stats:
        return ""
    
    calories_target = user.get('daily_calories', 2000)
    calories_consumed = daily_stats.get('calories_consumed', 0)
    calories_percentage = (calories_consumed / calories_target * 100) if calories_target > 0 else 0
    
    # Goal achieved (90-110% of target)
    if 90 <= calories_percentage <= 110:
        return (
            "🎯 **Отличная работа!**\n\n"
            f"Ты достиг дневной нормы калорий!\n"
            f"🔥 {calories_consumed}/{calories_target} ккал ({calories_percentage:.0f}%)\n\n"
            "Продолжай в том же духе! 💪"
        )
    
    # Approaching target (80-90%)
    elif 80 <= calories_percentage < 90:
        remaining = calories_target - calories_consumed
        return (
            "👍 **Хороший прогресс!**\n\n"
            f"Осталось ~{remaining} ккал до дневной нормы.\n"
            f"🔥 {calories_consumed}/{calories_target} ккал ({calories_percentage:.0f}%)"
        )
    
    # Over target (>110%)
    elif calories_percentage > 110:
        excess = calories_consumed - calories_target
        return (
            "⚠️ **Превышение нормы**\n\n"
            f"Ты превысил дневную норму на {excess} ккал.\n"
            f"🔥 {calories_consumed}/{calories_target} ккал ({calories_percentage:.0f}%)\n\n"
            "Не переживай! Завтра новый день. 😊"
        )
    
    # Still far from target (<80%)
    else:
        return ""
