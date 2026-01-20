"""
Главный файл Telegram-бота для анализа фотографий еды
"""
import logging
import sys

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters
)

from config import TELEGRAM_BOT_TOKEN
from handlers import (
    start_command,
    help_command,
    handle_photo,
    handle_text,
    error_handler
)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Главная функция запуска бота"""
    logger.info("Запуск бота...")
    
    try:
        # Создаем приложение
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        # Регистрируем обработчики команд
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        
        # Регистрируем обработчик фотографий
        application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
        
        # Регистрируем обработчик текстовых сообщений
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
        
        # Регистрируем обработчик ошибок
        application.add_error_handler(error_handler)
        
        logger.info("Бот успешно запущен и готов к работе!")
        
        # Запускаем бота
        application.run_polling(allowed_updates=["message"])
        
    except Exception as e:
        logger.error(f"Критическая ошибка при запуске бота: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
