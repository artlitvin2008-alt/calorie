"""
Keyboard utilities for inline and reply keyboards
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from typing import List, Tuple


def create_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Create confirmation keyboard for food analysis"""
    keyboard = [
        [InlineKeyboardButton("✅ Подтвердить", callback_data="confirm_analysis")]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_goal_keyboard() -> InlineKeyboardMarkup:
    """Create goal selection keyboard"""
    keyboard = [
        [InlineKeyboardButton("🎯 Похудение", callback_data="goal_weight_loss")],
        [InlineKeyboardButton("💪 Набор массы", callback_data="goal_muscle_gain")],
        [InlineKeyboardButton("⚖️ Поддержание", callback_data="goal_maintenance")]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_gender_keyboard() -> InlineKeyboardMarkup:
    """Create gender selection keyboard"""
    keyboard = [
        [InlineKeyboardButton("👨 Мужской", callback_data="gender_male")],
        [InlineKeyboardButton("👩 Женский", callback_data="gender_female")]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_meal_type_keyboard() -> InlineKeyboardMarkup:
    """Create meal type selection keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("🌅 Завтрак", callback_data="meal_breakfast"),
            InlineKeyboardButton("🌞 Обед", callback_data="meal_lunch")
        ],
        [
            InlineKeyboardButton("🌆 Ужин", callback_data="meal_dinner"),
            InlineKeyboardButton("🍎 Перекус", callback_data="meal_snack")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_yes_no_keyboard(yes_data: str, no_data: str) -> InlineKeyboardMarkup:
    """Create yes/no keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Да", callback_data=yes_data),
            InlineKeyboardButton("❌ Нет", callback_data=no_data)
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_cancel_keyboard() -> InlineKeyboardMarkup:
    """Create cancel keyboard"""
    keyboard = [
        [InlineKeyboardButton("❌ Отменить", callback_data="cancel_action")]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_analysis_actions_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard with analysis actions"""
    keyboard = [
        [InlineKeyboardButton("✅ Всё верно, подтвердить", callback_data="confirm_analysis")],
        [InlineKeyboardButton("✏️ Исправить текстом", callback_data="edit_text")],
        [InlineKeyboardButton("❌ Отменить анализ", callback_data="cancel_analysis")]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_correction_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for correction flow"""
    keyboard = [
        [InlineKeyboardButton("✅ Подтвердить", callback_data="confirm_analysis")],
        [InlineKeyboardButton("❌ Отменить", callback_data="cancel_analysis")]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Create main menu reply keyboard"""
    keyboard = [
        [KeyboardButton("📊 Сегодня"), KeyboardButton("👤 Профиль")],
        [KeyboardButton("🍽️ История"), KeyboardButton("⚙️ Настройки")],
        [KeyboardButton("❓ Помощь")]
    ]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )


def remove_keyboard() -> dict:
    """Remove keyboard"""
    return {"remove_keyboard": True}


# Callback data parsers
def parse_callback_data(data: str) -> Tuple[str, str]:
    """
    Parse callback data into action and value
    
    Examples:
        "goal_weight_loss" -> ("goal", "weight_loss")
        "confirm_analysis" -> ("confirm", "analysis")
        "gender_male" -> ("gender", "male")
    """
    parts = data.split("_", 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return parts[0], ""


def build_callback_data(action: str, value: str = "") -> str:
    """
    Build callback data from action and value
    
    Examples:
        ("goal", "weight_loss") -> "goal_weight_loss"
        ("confirm", "analysis") -> "confirm_analysis"
    """
    if value:
        return f"{action}_{value}"
    return action
