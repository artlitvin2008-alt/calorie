"""
Correction handlers for user text corrections
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from core.state_machine import UserState
from modules.nutrition.ai_correction_handler import AICorrectionHandler
from modules.nutrition.correction_parser import CorrectionParser
from utils.formatters import format_preliminary_analysis, format_error
from utils.keyboards import create_analysis_actions_keyboard
import config

logger = logging.getLogger(__name__)

# Use AI correction by default, fallback to rule-based parser
USE_AI_CORRECTION = True


async def handle_correction_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user correction text input"""
    user_id = update.effective_user.id
    correction_text = update.message.text.strip()
    
    state_manager = context.bot_data['state_manager']
    session_manager = context.bot_data['session_manager']
    
    # Verify state
    current_state = await state_manager.get_state(user_id)
    
    if current_state != UserState.WAITING_CORRECTION:
        await update.message.reply_text(
            "⚠️ Сейчас не ожидается коррекция. Отправь фото для анализа.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Get active session
    session = await session_manager.get_active_session(user_id)
    
    if not session:
        await update.message.reply_text(
            format_error('no_session'),
            parse_mode=ParseMode.MARKDOWN
        )
        await state_manager.reset_state(user_id)
        return
    
    session_id = session['session_id']
    
    # Check correction limit
    correction_count = session.get('correction_count', 0)
    
    if correction_count >= config.MAX_CORRECTIONS:
        await update.message.reply_text(
            f"⚠️ Достигнут лимит коррекций ({config.MAX_CORRECTIONS}).\n\n"
            "Ты можешь:\n"
            "• Подтвердить текущий анализ\n"
            "• Отменить и начать заново с /cancel",
            parse_mode=ParseMode.MARKDOWN
        )
        # Return to confirmation state
        await state_manager.set_state(user_id, UserState.WAITING_CONFIRMATION)
        return
    
    # Send processing message
    status_message = await update.message.reply_text(
        "⏳ Применяю коррекцию...",
        parse_mode=ParseMode.MARKDOWN
    )
    
    try:
        # Get current analysis
        current_analysis = await session_manager.get_current_analysis(session_id)
        
        if not current_analysis:
            await status_message.edit_text(
                format_error('no_session'),
                parse_mode=ParseMode.MARKDOWN
            )
            await state_manager.reset_state(user_id)
            return
        
        # Try AI correction first, fallback to rule-based parser
        if USE_AI_CORRECTION:
            logger.info(f"Using AI correction for: {correction_text}")
            ai_handler = AICorrectionHandler()
            success, updated_analysis, error_message = await ai_handler.apply_correction(
                correction_text,
                current_analysis
            )
            
            # If AI fails, try rule-based parser as fallback
            if not success:
                logger.warning(f"AI correction failed, trying rule-based parser: {error_message}")
                parser = CorrectionParser()
                success, updated_analysis, error_message = parser.parse_correction(
                    correction_text,
                    current_analysis
                )
        else:
            # Use rule-based parser directly
            logger.info(f"Using rule-based parser for: {correction_text}")
            parser = CorrectionParser()
            success, updated_analysis, error_message = parser.parse_correction(
                correction_text,
                current_analysis
            )
        
        if not success:
            # Show error and ask for another correction
            error_text = f"❌ {error_message}\n\n"
            error_text += "Попробуй ещё раз или используй /cancel для отмены.\n\n"
            error_text += "**Примеры коррекций:**\n"
            error_text += "• \"500г\" - изменить общий вес\n"
            error_text += "• \"нет хлеба\" - убрать компонент\n"
            error_text += "• \"добавь салат 100г\" - добавить\n"
            error_text += "• \"говядины 150г\" - изменить вес компонента\n"
            error_text += "• \"это курица, а не свинина\" - изменить название\n"
            
            await status_message.edit_text(
                error_text,
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Save updated analysis
        await session_manager.save_correction(
            session_id,
            correction_text,
            updated_analysis
        )
        
        # Increment correction count
        new_count = correction_count + 1
        
        # Format updated analysis
        message = format_preliminary_analysis(updated_analysis)
        
        # Add correction info
        corrections_left = config.MAX_CORRECTIONS - new_count
        correction_info = f"\n\n✅ Коррекция применена"
        
        # Show what was changed if AI provided description
        if 'correction_applied' in updated_analysis:
            correction_info += f": {updated_analysis['correction_applied']}"
        
        correction_info += f"\n(Осталось коррекций: {corrections_left})"
        
        # Return to confirmation state
        await state_manager.set_state(user_id, UserState.WAITING_CONFIRMATION)
        
        # Send updated analysis
        await status_message.edit_text(
            message + correction_info,
            reply_markup=create_analysis_actions_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )
        
        logger.info(
            f"User {user_id} applied correction #{new_count}: {correction_text[:50]}"
        )
        
    except Exception as e:
        logger.error(f"Error processing correction: {e}", exc_info=True)
        await status_message.edit_text(
            format_error('correction_error'),
            parse_mode=ParseMode.MARKDOWN
        )
        # Return to confirmation state
        await state_manager.set_state(user_id, UserState.WAITING_CONFIRMATION)


async def show_correction_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show correction examples and help"""
    parser = CorrectionParser()
    help_text = (
        "📝 **Как исправить анализ**\n\n"
        f"{parser.get_correction_examples()}\n\n"
        "💡 **Советы:**\n"
        "• Пиши просто и понятно\n"
        "• Указывай вес для новых компонентов\n"
        f"• Максимум {config.MAX_CORRECTIONS} коррекции на анализ\n\n"
        "Используй /cancel для отмены."
    )
    
    await update.message.reply_text(
        help_text,
        parse_mode=ParseMode.MARKDOWN
    )
