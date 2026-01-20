"""
Main bot application with new architecture
"""
import logging
import sys
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from telegram.constants import ParseMode

import config
from core.database import Database
from core.state_machine import StateManager, UserState
from core.session_manager import SessionManager
from core.user_manager import UserManager

from handlers.commands import (
    start_command,
    help_command,
    profile_command,
    setup_command,
    today_command,
    meals_command,
    cancel_command,
    analyze_video_command
)
from handlers.registration import handle_registration
from handlers.callbacks import handle_callback_query
from handlers.photos import handle_photo_message
from handlers.video_notes import handle_video_note
from handlers.corrections import handle_correction_text
from handlers.meal_confirmation import confirm_and_save_meal

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Route text messages based on user state"""
    user_id = update.effective_user.id
    state_manager = context.bot_data['state_manager']
    
    current_state = await state_manager.get_state(user_id)
    
    if current_state == UserState.REGISTERING:
        # Handle registration flow
        await handle_registration(update, context)
    elif current_state == UserState.WAITING_CORRECTION:
        # Handle correction input
        await handle_correction_text(update, context)
    else:
        # Default: suggest sending photo
        await update.message.reply_text(
            "📸 Отправь фото еды для анализа.\n\n"
            "Или используй команды:\n"
            "/profile - твой профиль\n"
            "/today - статистика за сегодня\n"
            "/help - помощь",
            parse_mode=ParseMode.MARKDOWN
        )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error: {context.error}", exc_info=context.error)
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            config.MESSAGES['error_general'],
            parse_mode=ParseMode.MARKDOWN
        )


async def post_init(application: Application):
    """Initialize bot components after application start"""
    logger.info("Initializing bot components...")
    
    # Initialize database
    db = Database(config.DATABASE_PATH)
    await db.initialize()
    
    # Initialize managers
    state_manager = StateManager(db)
    session_manager = SessionManager(db, state_manager)
    user_manager = UserManager(db)
    
    # Store in bot_data for access in handlers
    application.bot_data['database'] = db
    application.bot_data['state_manager'] = state_manager
    application.bot_data['session_manager'] = session_manager
    application.bot_data['user_manager'] = user_manager
    
    logger.info("✅ Bot components initialized")


async def cleanup(application: Application):
    """Cleanup on shutdown"""
    logger.info("Cleaning up...")
    
    db = application.bot_data.get('database')
    if db:
        await db.cleanup()
    
    logger.info("✅ Cleanup completed")


def main():
    """Main function"""
    logger.info("Starting bot...")
    
    try:
        # Create application
        application = (
            Application.builder()
            .token(config.TELEGRAM_BOT_TOKEN)
            .post_init(post_init)
            .post_shutdown(cleanup)
            .build()
        )
        
        # Register command handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("profile", profile_command))
        application.add_handler(CommandHandler("setup", setup_command))
        application.add_handler(CommandHandler("today", today_command))
        application.add_handler(CommandHandler("meals", meals_command))
        application.add_handler(CommandHandler("cancel", cancel_command))
        application.add_handler(CommandHandler("analyze_video", analyze_video_command))
        
        # Register message handlers
        application.add_handler(MessageHandler(filters.VIDEO_NOTE, handle_video_note))
        application.add_handler(MessageHandler(filters.PHOTO, handle_photo_message))
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_text_message
        ))
        
        # Register callback query handler
        application.add_handler(CallbackQueryHandler(handle_callback_query))
        
        # Register error handler
        application.add_error_handler(error_handler)
        
        logger.info("✅ Bot started successfully!")
        logger.info("Press Ctrl+C to stop")
        
        # Start polling
        application.run_polling(allowed_updates=["message", "callback_query"])
        
    except Exception as e:
        logger.error(f"Critical error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
