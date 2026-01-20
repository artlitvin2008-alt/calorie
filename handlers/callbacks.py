"""
Callback query handlers for inline buttons
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from core.state_machine import UserState
from utils.keyboards import parse_callback_data
from utils.formatters import format_error
from handlers.meal_confirmation import confirm_and_save_meal
import config

logger = logging.getLogger(__name__)


async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main callback query router"""
    query = update.callback_query
    await query.answer()  # Acknowledge the callback
    
    user_id = update.effective_user.id
    callback_data = query.data
    
    logger.info(f"User {user_id} pressed button: {callback_data}")
    
    # Parse callback data
    action, value = parse_callback_data(callback_data)
    
    # Route to appropriate handler
    if action == "goal":
        await handle_goal_callback(update, context, value)
    elif action == "gender":
        await handle_gender_callback(update, context, value)
    elif action == "confirm":
        await handle_confirm_callback(update, context, value)
    elif action == "cancel":
        await handle_cancel_callback(update, context, value)
    elif action == "meal":
        await handle_meal_type_callback(update, context, value)
    elif action == "edit":
        await handle_edit_callback(update, context, value)
    else:
        logger.warning(f"Unknown callback action: {action}")
        await query.edit_message_text(
            "❌ Неизвестное действие. Попробуй ещё раз.",
            parse_mode=ParseMode.MARKDOWN
        )


async def handle_goal_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, goal: str):
    """Handle goal selection callback"""
    query = update.callback_query
    user_id = update.effective_user.id
    state_manager = context.bot_data['state_manager']
    
    # Get setup data
    setup_data = state_manager.get_session_data(user_id) or {}
    
    # Save goal
    setup_data['goal'] = goal
    setup_data['setup_step'] = 'current_weight'
    state_manager.set_session_data(user_id, setup_data)
    
    # Update message
    goal_names = {
        'weight_loss': '🎯 Похудение',
        'muscle_gain': '💪 Набор массы',
        'maintenance': '⚖️ Поддержание'
    }
    
    await query.edit_message_text(
        f"✅ Выбрано: {goal_names.get(goal, goal)}\n\n"
        f"{config.MESSAGES['setup_weight']}",
        parse_mode=ParseMode.MARKDOWN
    )
    
    logger.info(f"User {user_id} selected goal: {goal}")


async def handle_gender_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, gender: str):
    """Handle gender selection callback and complete registration"""
    query = update.callback_query
    user_id = update.effective_user.id
    state_manager = context.bot_data['state_manager']
    user_manager = context.bot_data['user_manager']
    
    # Get setup data
    setup_data = state_manager.get_session_data(user_id) or {}
    
    # Check if all data is collected
    required_fields = ['goal', 'current_weight', 'target_weight', 'height', 'age']
    if not all(field in setup_data for field in required_fields):
        await query.edit_message_text(
            "❌ Ошибка: не все данные собраны. Начни заново с /setup",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Save all data to database
    await user_manager.set_goals(
        user_id=user_id,
        goal=setup_data['goal'],
        current_weight=setup_data['current_weight'],
        target_weight=setup_data['target_weight'],
        height=setup_data['height'],
        age=setup_data['age'],
        gender=gender
    )
    
    # Get updated user data
    user = await user_manager.db.get_user(user_id)
    
    # Send completion message
    gender_names = {'male': '👨 Мужской', 'female': '👩 Женский'}
    
    message = config.MESSAGES['setup_complete'].format(
        goal=config.GOAL_NAMES.get(user['goal'], user['goal']),
        current_weight=user['current_weight'],
        target_weight=user['target_weight'],
        height=user['height'],
        age=user['age'],
        daily_calories=user['daily_calories'],
        protein_goal=user['protein_goal'],
        fat_goal=user['fat_goal'],
        carbs_goal=user['carbs_goal']
    )
    
    await query.edit_message_text(
        f"✅ Выбрано: {gender_names.get(gender, gender)}\n\n{message}",
        parse_mode=ParseMode.MARKDOWN
    )
    
    # Reset state
    await state_manager.set_state(user_id, UserState.IDLE, validate=False)
    state_manager.clear_session_data(user_id)
    
    logger.info(f"User {user_id} completed registration with gender: {gender}")


async def handle_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, item: str):
    """Handle confirmation callbacks"""
    query = update.callback_query
    user_id = update.effective_user.id
    state_manager = context.bot_data['state_manager']
    session_manager = context.bot_data['session_manager']
    user_manager = context.bot_data['user_manager']
    
    if item == "analysis":
        # Confirm and save food analysis
        await confirm_and_save_meal(update, context, query)
    
    else:
        await query.edit_message_text(
            f"✅ Подтверждено: {item}",
            parse_mode=ParseMode.MARKDOWN
        )


async def handle_cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, item: str):
    """Handle cancellation callbacks"""
    query = update.callback_query
    user_id = update.effective_user.id
    state_manager = context.bot_data['state_manager']
    session_manager = context.bot_data['session_manager']
    
    # Cancel any active session
    await session_manager.cancel_session(user_id)
    
    # Reset state
    await state_manager.reset_state(user_id)
    
    # Clear session data
    state_manager.clear_session_data(user_id)
    
    await query.edit_message_text(
        config.MESSAGES['cancelled'],
        parse_mode=ParseMode.MARKDOWN
    )
    
    logger.info(f"User {user_id} cancelled: {item}")


async def handle_meal_type_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, meal_type: str):
    """Handle meal type selection"""
    query = update.callback_query
    user_id = update.effective_user.id
    state_manager = context.bot_data['state_manager']
    
    # Save meal type to session data
    session_data = state_manager.get_session_data(user_id) or {}
    session_data['meal_type'] = meal_type
    state_manager.set_session_data(user_id, session_data)
    
    meal_names = {
        'breakfast': '🌅 Завтрак',
        'lunch': '🌞 Обед',
        'dinner': '🌆 Ужин',
        'snack': '🍎 Перекус'
    }
    
    await query.edit_message_text(
        f"✅ Выбрано: {meal_names.get(meal_type, meal_type)}",
        parse_mode=ParseMode.MARKDOWN
    )
    
    logger.info(f"User {user_id} selected meal type: {meal_type}")


async def handle_edit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, item: str):
    """Handle edit callbacks"""
    query = update.callback_query
    user_id = update.effective_user.id
    state_manager = context.bot_data['state_manager']
    
    if item == "text":
        # Switch to correction mode
        await state_manager.set_state(user_id, UserState.WAITING_CORRECTION)
        
        await query.edit_message_text(
            "✏️ **Режим исправлений**\n\n"
            "Напиши, что нужно исправить:\n\n"
            "Примеры:\n"
            "• \"нет хлеба\" - убрать компонент\n"
            "• \"добавь салат 100г\" - добавить\n"
            "• \"это курица, а не свинина\" - изменить\n"
            "• \"500г\" - изменить общий вес на 500г\n\n"
            "Или используй /cancel для отмены.",
            parse_mode=ParseMode.MARKDOWN
        )
        
        logger.info(f"User {user_id} entered correction mode")
    
    else:
        await query.edit_message_text(
            f"✏️ Редактирование: {item}",
            parse_mode=ParseMode.MARKDOWN
        )
