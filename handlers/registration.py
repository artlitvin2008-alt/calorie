"""
Registration flow handler
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from core.state_machine import UserState
from utils.keyboards import create_goal_keyboard, create_gender_keyboard
import config

logger = logging.getLogger(__name__)


async def handle_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle registration flow"""
    user_id = update.effective_user.id
    text = update.message.text.strip().lower()
    
    state_manager = context.bot_data['state_manager']
    user_manager = context.bot_data['user_manager']
    
    # Get current setup data
    setup_data = state_manager.get_session_data(user_id) or {}
    step = setup_data.get('setup_step')
    
    # Skip goal and gender - they use inline buttons now
    if step == 'current_weight':
        await handle_weight_input(update, context, text, setup_data)
    elif step == 'target_weight':
        await handle_target_input(update, context, text, setup_data)
    elif step == 'height':
        await handle_height_input(update, context, text, setup_data)
    elif step == 'age':
        await handle_age_input(update, context, text, setup_data)


# Goal selection now handled by callback in handlers/callbacks.py


async def handle_weight_input(update: Update, context: ContextTypes.DEFAULT_TYPE,
                              text: str, setup_data: dict):
    """Handle current weight input"""
    user_id = update.effective_user.id
    state_manager = context.bot_data['state_manager']
    
    try:
        weight = float(text.replace(',', '.'))
        
        if weight < 30 or weight > 300:
            await update.message.reply_text(
                "❌ Вес должен быть от 30 до 300 кг. Попробуй ещё раз.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Save weight
        setup_data['current_weight'] = weight
        setup_data['setup_step'] = 'target_weight'
        state_manager.set_session_data(user_id, setup_data)
        
        await update.message.reply_text(
            config.MESSAGES['setup_target'],
            parse_mode=ParseMode.MARKDOWN
        )
        
        logger.info(f"User {user_id} entered weight: {weight}")
        
    except ValueError:
        await update.message.reply_text(
            "❌ Неверный формат. Введи число, например: 75",
            parse_mode=ParseMode.MARKDOWN
        )


async def handle_target_input(update: Update, context: ContextTypes.DEFAULT_TYPE,
                              text: str, setup_data: dict):
    """Handle target weight input"""
    user_id = update.effective_user.id
    state_manager = context.bot_data['state_manager']
    
    try:
        target = float(text.replace(',', '.'))
        
        if target < 30 or target > 300:
            await update.message.reply_text(
                "❌ Вес должен быть от 30 до 300 кг. Попробуй ещё раз.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Save target
        setup_data['target_weight'] = target
        setup_data['setup_step'] = 'height'
        state_manager.set_session_data(user_id, setup_data)
        
        await update.message.reply_text(
            config.MESSAGES['setup_height'],
            parse_mode=ParseMode.MARKDOWN
        )
        
        logger.info(f"User {user_id} entered target: {target}")
        
    except ValueError:
        await update.message.reply_text(
            "❌ Неверный формат. Введи число, например: 70",
            parse_mode=ParseMode.MARKDOWN
        )


async def handle_height_input(update: Update, context: ContextTypes.DEFAULT_TYPE,
                              text: str, setup_data: dict):
    """Handle height input"""
    user_id = update.effective_user.id
    state_manager = context.bot_data['state_manager']
    
    try:
        height = int(text)
        
        if height < 100 or height > 250:
            await update.message.reply_text(
                "❌ Рост должен быть от 100 до 250 см. Попробуй ещё раз.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Save height
        setup_data['height'] = height
        setup_data['setup_step'] = 'age'
        state_manager.set_session_data(user_id, setup_data)
        
        await update.message.reply_text(
            config.MESSAGES['setup_age'],
            parse_mode=ParseMode.MARKDOWN
        )
        
        logger.info(f"User {user_id} entered height: {height}")
        
    except ValueError:
        await update.message.reply_text(
            "❌ Неверный формат. Введи число, например: 175",
            parse_mode=ParseMode.MARKDOWN
        )


async def handle_age_input(update: Update, context: ContextTypes.DEFAULT_TYPE,
                          text: str, setup_data: dict):
    """Handle age input and show gender selection"""
    user_id = update.effective_user.id
    state_manager = context.bot_data['state_manager']
    
    try:
        age = int(text)
        
        if age < 10 or age > 100:
            await update.message.reply_text(
                "❌ Возраст должен быть от 10 до 100 лет. Попробуй ещё раз.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Save age
        setup_data['age'] = age
        setup_data['setup_step'] = 'gender'
        state_manager.set_session_data(user_id, setup_data)
        
        # Show gender selection with inline buttons
        await update.message.reply_text(
            config.MESSAGES['setup_gender'],
            reply_markup=create_gender_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )
        
        logger.info(f"User {user_id} entered age: {age}")
        
    except ValueError:
        await update.message.reply_text(
            "❌ Неверный формат. Введи число, например: 28",
            parse_mode=ParseMode.MARKDOWN
        )


# Gender selection now handled by callback in handlers/callbacks.py
