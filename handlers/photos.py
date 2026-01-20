"""
Photo message handlers
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from core.state_machine import UserState
from modules.nutrition.photo_analyzer import PhotoAnalyzer
from modules.nutrition.dish_comparator import DishComparator
from utils.formatters import format_preliminary_analysis, format_error, format_dish_comparison
from utils.keyboards import create_analysis_actions_keyboard
import config

logger = logging.getLogger(__name__)


async def handle_photo_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo messages"""
    user_id = update.effective_user.id
    user_manager = context.bot_data['user_manager']
    state_manager = context.bot_data['state_manager']
    session_manager = context.bot_data['session_manager']
    
    # Check if user is registered
    is_registered = await user_manager.is_registered(user_id)
    
    if not is_registered:
        await update.message.reply_text(
            config.MESSAGES['error_no_profile'],
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Check current state
    current_state = await state_manager.get_state(user_id)
    
    if current_state not in [UserState.IDLE, UserState.WAITING_FOR_PHOTO]:
        await update.message.reply_text(
            "⚠️ Сначала завершите текущее действие или используйте /cancel",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Send analyzing message
    status_message = await update.message.reply_text(
        config.MESSAGES['analyzing'],
        parse_mode=ParseMode.MARKDOWN
    )
    
    try:
        # Get photo
        photo = update.message.photo[-1]  # Highest quality
        photo_file_id = photo.file_id
        
        logger.info(f"User {user_id} sent photo: {photo_file_id}")
        
        # Download photo
        file = await context.bot.get_file(photo_file_id)
        photo_bytes = await file.download_as_bytearray()
        
        logger.info(f"Photo downloaded: {len(photo_bytes)} bytes")
        
        # Update status
        await status_message.edit_text(
            "🔍 Распознаю компоненты...",
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Create session
        session_id = await session_manager.create_session(user_id, photo_file_id)
        
        # Set state to analyzing
        await state_manager.set_state(user_id, UserState.ANALYZING_PHOTO)
        
        # Analyze photo
        photo_analyzer = PhotoAnalyzer(use_mock=config.USE_MOCK_API)
        analysis_result = await photo_analyzer.analyze_photo(bytes(photo_bytes))
        
        if analysis_result is None:
            await status_message.edit_text(
                format_error('api_error'),
                parse_mode=ParseMode.MARKDOWN
            )
            await state_manager.reset_state(user_id)
            await session_manager.cancel_session(user_id)
            return
        
        # Compare with typical dishes
        database = context.bot_data['database']
        dish_comparator = DishComparator(database)
        
        # Find similar dishes
        similar_dishes = await dish_comparator.find_similar_dishes(analysis_result, limit=3)
        
        # Calculate realism and adjust health score
        if similar_dishes:
            comparison_result = await dish_comparator.calculate_realism_score(
                analysis_result,
                similar_dishes
            )
            
            # Adjust health score based on comparison
            adjusted_score, explanation = await dish_comparator.adjust_health_score(
                analysis_result,
                similar_dishes
            )
            
            # Update analysis with adjusted score
            original_score = analysis_result.get('health_score', 5)
            analysis_result['health_score'] = adjusted_score
            analysis_result['health_score_adjusted'] = True
            analysis_result['health_score_original'] = original_score
            analysis_result['health_score_explanation'] = explanation
            
            # Add comparison data
            analysis_result['comparison'] = comparison_result
            
            logger.info(
                f"Health score adjusted: {original_score} -> {adjusted_score} "
                f"(based on '{similar_dishes[0]['dish_name']}')"
            )
        
        # Save initial analysis
        await session_manager.save_initial_analysis(session_id, analysis_result)
        
        # Update status
        await status_message.edit_text(
            "🧮 Рассчитываю калории...",
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Format and display preliminary analysis
        message = format_preliminary_analysis(analysis_result)
        
        # Add comparison section if available
        if similar_dishes and 'comparison' in analysis_result:
            comparison_message = format_dish_comparison(
                analysis_result,
                analysis_result['comparison']
            )
            message += comparison_message
        
        # Set state to waiting confirmation
        await state_manager.set_state(user_id, UserState.WAITING_CONFIRMATION)
        
        # Send analysis with action buttons
        await status_message.edit_text(
            message,
            reply_markup=create_analysis_actions_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )
        
        logger.info(f"Analysis sent to user {user_id}")
        
    except Exception as e:
        logger.error(f"Error processing photo: {e}", exc_info=True)
        try:
            await status_message.edit_text(
                format_error('photo_error'),
                parse_mode=ParseMode.MARKDOWN
            )
        except:
            await update.message.reply_text(
                format_error('photo_error'),
                parse_mode=ParseMode.MARKDOWN
            )
        
        # Reset state
        await state_manager.reset_state(user_id)
        await session_manager.cancel_session(user_id)
