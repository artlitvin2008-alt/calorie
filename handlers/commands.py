"""
Command handlers for the bot
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from core.state_machine import UserState
from utils.keyboards import create_goal_keyboard
from utils.formatters import (
    format_goal_name,
    format_daily_summary,
    format_meals_history,
    format_daily_progress
)
import config

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user_id = update.effective_user.id
    username = update.effective_user.username
    first_name = update.effective_user.first_name
    last_name = update.effective_user.last_name
    
    # Get managers from context
    user_manager = context.bot_data['user_manager']
    state_manager = context.bot_data['state_manager']
    
    # Get or create user
    user = await user_manager.get_or_create_user(
        user_id, username, first_name, last_name
    )
    
    # Check if user is registered
    is_registered = await user_manager.is_registered(user_id)
    
    if is_registered:
        # Welcome back message
        message = config.MESSAGES['welcome_back'].format(
            name=first_name or username or "друг",
            goal=format_goal_name(user.get('goal', '')),
            current_weight=user.get('current_weight', 0),
            target_weight=user.get('target_weight', 0),
            daily_calories=user.get('daily_calories', 0)
        )
        await state_manager.set_state(user_id, UserState.IDLE, validate=False)
    else:
        # New user welcome
        message = config.MESSAGES['welcome']
        await state_manager.set_state(user_id, UserState.IDLE, validate=False)
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    logger.info(f"User {user_id} started bot (registered: {is_registered})")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    await update.message.reply_text(
        config.MESSAGES['help'],
        parse_mode=ParseMode.MARKDOWN
    )
    logger.info(f"User {update.effective_user.id} requested help")


async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /profile command"""
    user_id = update.effective_user.id
    user_manager = context.bot_data['user_manager']
    
    # Check if user is registered
    is_registered = await user_manager.is_registered(user_id)
    
    if not is_registered:
        await update.message.reply_text(
            config.MESSAGES['error_no_profile'],
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Get profile summary
    summary = await user_manager.get_profile_summary(user_id)
    
    if summary:
        await update.message.reply_text(summary, parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text(
            config.MESSAGES['error_general'],
            parse_mode=ParseMode.MARKDOWN
        )
    
    logger.info(f"User {user_id} viewed profile")


async def setup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /setup command - start profile setup"""
    user_id = update.effective_user.id
    state_manager = context.bot_data['state_manager']
    
    # Set state to registering
    await state_manager.set_state(user_id, UserState.REGISTERING, validate=False)
    
    # Initialize setup data
    state_manager.set_session_data(user_id, {
        'setup_step': 'goal'
    })
    
    # Send goal selection with inline buttons
    await update.message.reply_text(
        config.MESSAGES['setup_start'],
        reply_markup=create_goal_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )
    
    logger.info(f"User {user_id} started setup")


async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /today command - show today's statistics"""
    user_id = update.effective_user.id
    user_manager = context.bot_data['user_manager']
    db = context.bot_data['database']
    
    # Check if user is registered
    is_registered = await user_manager.is_registered(user_id)
    
    if not is_registered:
        await update.message.reply_text(
            config.MESSAGES['error_no_profile'],
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Get user and daily stats
    user = await user_manager.db.get_user(user_id)
    from datetime import datetime
    daily_stats = await db.get_daily_stats(user_id, datetime.now().date())
    
    # Format and send
    message = format_daily_progress(user, daily_stats)
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    logger.info(f"User {user_id} viewed today's stats")


async def meals_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /meals command - show meal history"""
    user_id = update.effective_user.id
    user_manager = context.bot_data['user_manager']
    db = context.bot_data['database']
    
    # Check if user is registered
    is_registered = await user_manager.is_registered(user_id)
    
    if not is_registered:
        await update.message.reply_text(
            config.MESSAGES['error_no_profile'],
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Get meal history
    meals = await db.get_meals_history(user_id, limit=10)
    
    # Format and send
    message = format_meals_history(meals)
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    logger.info(f"User {user_id} viewed meal history")


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /cancel command - cancel current action"""
    user_id = update.effective_user.id
    state_manager = context.bot_data['state_manager']
    session_manager = context.bot_data['session_manager']
    
    # Cancel any active session
    await session_manager.cancel_session(user_id)
    
    # Reset state
    await state_manager.reset_state(user_id)
    
    # Clear session data
    state_manager.clear_session_data(user_id)
    
    await update.message.reply_text(
        config.MESSAGES['cancelled'],
        parse_mode=ParseMode.MARKDOWN
    )
    
    logger.info(f"User {user_id} cancelled action")


async def analyze_video_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /analyze_video command - start video note analysis"""
    user_id = update.effective_user.id
    user_manager = context.bot_data['user_manager']
    
    # Check if user is registered
    is_registered = await user_manager.is_registered(user_id)
    
    if not is_registered:
        await update.message.reply_text(
            config.MESSAGES['error_no_profile'],
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Send instructions
    await update.message.reply_text(
        "🎥 *Режим анализа видео-кружка*\n\n"
        "Запиши видео-кружок (до 60 сек), где:\n"
        "1️⃣ Покажи еду со всех сторон\n"
        "2️⃣ Расскажи, что это и примерный вес\n\n"
        "Я сделаю скриншоты и учту твой голос! 🎤\n\n"
        "_Просто нажми на кнопку видео-кружка в Telegram и запиши видео._",
        parse_mode=ParseMode.MARKDOWN
    )
    
    logger.info(f"User {user_id} requested video analysis")
