"""
Message formatting utilities
"""
from typing import Dict, Any, List
from datetime import datetime
import config
from utils.display_helpers import (
    format_component_detailed,
    format_totals_summary,
    format_warnings_list,
    format_instructions,
    create_separator,
    format_health_score_visual,
    format_calorie_density_indicator
)


def format_goal_name(goal: str) -> str:
    """Format goal name with emoji"""
    return config.GOAL_NAMES.get(goal, goal)


def format_weight_progress(current: float, target: float) -> str:
    """Format weight progress"""
    diff = current - target
    if diff > 0:
        return f"📉 Осталось сбросить: {diff:.1f} кг"
    elif diff < 0:
        return f"📈 Осталось набрать: {abs(diff):.1f} кг"
    else:
        return f"🎯 Цель достигнута!"


def format_calories_progress(consumed: int, target: int) -> str:
    """Format calorie progress"""
    remaining = target - consumed
    percentage = (consumed / target * 100) if target > 0 else 0
    
    if remaining > 0:
        emoji = "✅" if percentage < 90 else "⚠️"
        return f"{emoji} Съедено: {consumed}/{target} ккал (осталось {remaining} ккал)"
    else:
        return f"🔴 Превышение: {consumed}/{target} ккал (+{abs(remaining)} ккал)"


def format_macros_progress(consumed: int, target: int, name: str) -> str:
    """Format macro progress"""
    percentage = (consumed / target * 100) if target > 0 else 0
    bar = create_progress_bar(percentage)
    
    return f"{name}: {consumed}/{target}г {bar} {percentage:.0f}%"


def create_progress_bar(percentage: float, length: int = 10) -> str:
    """Create visual progress bar"""
    filled = int(percentage / 100 * length)
    empty = length - filled
    return "█" * filled + "░" * empty


def create_confidence_bar(confidence: float) -> str:
    """Create confidence indicator bar"""
    percentage = confidence * 100
    if percentage >= 80:
        return f"{'█' * 8}{'░' * 2} {percentage:.0f}%"
    elif percentage >= 60:
        return f"{'█' * 6}{'░' * 4} {percentage:.0f}%"
    elif percentage >= 40:
        return f"{'█' * 4}{'░' * 6} {percentage:.0f}%"
    else:
        return f"{'█' * 2}{'░' * 8} {percentage:.0f}%"


def format_confidence_text(confidence: float) -> str:
    """Format confidence as text with emoji"""
    if confidence >= 0.8:
        return "✅ Уверен"
    elif confidence >= 0.6:
        return "⚠️ Вероятно"
    elif confidence >= 0.4:
        return "❓ Не уверен"
    else:
        return "❌ Сомнительно"


def format_meal_summary(meal: Dict[str, Any]) -> str:
    """Format single meal summary"""
    eaten_at = meal.get('eaten_at', '')
    if isinstance(eaten_at, str):
        try:
            dt = datetime.fromisoformat(eaten_at)
            time_str = dt.strftime('%H:%M')
        except:
            time_str = eaten_at
    else:
        time_str = str(eaten_at)
    
    meal_type = meal.get('meal_type', 'Приём пищи')
    calories = meal.get('total_calories', 0)
    protein = meal.get('protein_g', 0)
    fat = meal.get('fat_g', 0)
    carbs = meal.get('carbs_g', 0)
    
    return f"""🕐 {time_str} - {meal_type}
🔥 {calories} ккал | 🥚 {protein}г | 🥑 {fat}г | 🌾 {carbs}г"""


def format_daily_summary(progress: Dict[str, Any]) -> str:
    """Format daily progress summary"""
    consumed = progress.get('consumed_calories', 0)
    target = progress.get('target_calories', 0)
    remaining = progress.get('remaining_calories', 0)
    
    protein = progress.get('protein', {})
    fat = progress.get('fat', {})
    carbs = progress.get('carbs', {})
    
    meals_count = progress.get('meals_count', 0)
    
    message = f"""📊 **Статистика за сегодня**

🍽️ Приёмов пищи: {meals_count}

{format_calories_progress(consumed, target)}

**БЖУ:**
🥚 {format_macros_progress(protein.get('consumed', 0), protein.get('target', 0), 'Белки')}
🥑 {format_macros_progress(fat.get('consumed', 0), fat.get('target', 0), 'Жиры')}
🌾 {format_macros_progress(carbs.get('consumed', 0), carbs.get('target', 0), 'Углеводы')}
"""
    
    if remaining > 0:
        message += f"\n💡 Можешь съесть ещё {remaining} ккал"
    elif remaining < 0:
        message += f"\n⚠️ Превышение на {abs(remaining)} ккал"
    else:
        message += f"\n🎯 Идеально! Норма выполнена"
    
    return message


def format_preliminary_analysis(analysis: Dict[str, Any]) -> str:
    """Format preliminary analysis with components"""
    components = analysis.get('components', [])
    
    if not components:
        return "❌ Не удалось распознать компоненты блюда"
    
    # Header with dish name
    dish_name = analysis.get('dish_name', 'Блюдо')
    message = f"🔍 **Анализ фото**\n\n"
    message += f"🍽️ **{dish_name}**\n\n"
    
    # Components with detailed info
    message += "**Компоненты:**\n\n"
    
    for i, comp in enumerate(components, 1):
        message += format_component_detailed(comp, i) + "\n\n"
    
    # Separator
    message += create_separator() + "\n"
    
    # Totals
    message += format_totals_summary(analysis) + "\n"
    
    # Calorie density indicator
    calories_per_100g = analysis.get('calories_per_100g', 0)
    if calories_per_100g > 0:
        message += f"\n{format_calorie_density_indicator(calories_per_100g)}\n"
    
    # Health score if available
    health_score = analysis.get('health_score')
    if health_score:
        message += f"\n⭐ Полезность: {format_health_score_visual(health_score)}\n"
    
    # Show warnings if any
    warnings = analysis.get('warnings', [])
    if warnings:
        message += f"\n{format_warnings_list(warnings)}\n"
    
    # Separator
    message += f"\n{create_separator()}\n"
    
    # Instructions
    message += format_instructions()
    
    return message


def format_final_analysis(analysis: Dict[str, Any], user_progress: Dict[str, Any]) -> str:
    """Format final analysis with recommendations"""
    dish_name = analysis.get('dish_name', 'Блюдо')
    total_calories = analysis.get('calories_total', 0)
    protein = analysis.get('protein_g', 0)
    fat = analysis.get('fat_g', 0)
    carbs = analysis.get('carbs_g', 0)
    health_score = analysis.get('health_score', 5)
    
    message = f"""✅ **Анализ сохранён!**

🍽️ **{dish_name}**

**Пищевая ценность:**
🔥 Калории: {total_calories} ккал
🥚 Белки: {protein} г
🥑 Жиры: {fat} г
🌾 Углеводы: {carbs} г
⭐ Полезность: {health_score}/10

"""
    
    # Add daily progress
    consumed = user_progress.get('consumed_calories', 0)
    target = user_progress.get('target_calories', 0)
    remaining = user_progress.get('remaining_calories', 0)
    
    message += f"**Сегодня:**\n"
    message += f"{format_calories_progress(consumed, target)}\n\n"
    
    # Add recommendations
    recommendations = analysis.get('recommendations', '')
    if recommendations:
        message += f"💡 **Рекомендации:**\n{recommendations}\n\n"
    
    # Add portion advice
    portion_advice = analysis.get('portion_advice', '')
    if portion_advice:
        message += f"📏 **Совет:**\n{portion_advice}"
    
    return message


def format_meals_history(meals: List[Dict[str, Any]]) -> str:
    """Format meals history"""
    if not meals:
        return "📭 История пуста. Отправь фото еды для анализа!"
    
    message = "📜 **История приёмов пищи**\n\n"
    
    current_date = None
    for meal in meals:
        eaten_at = meal.get('eaten_at', '')
        if isinstance(eaten_at, str):
            try:
                dt = datetime.fromisoformat(eaten_at)
                date_str = dt.strftime('%d.%m.%Y')
                
                if date_str != current_date:
                    current_date = date_str
                    message += f"\n📅 **{date_str}**\n"
                
                message += format_meal_summary(meal) + "\n"
            except:
                message += format_meal_summary(meal) + "\n"
        else:
            message += format_meal_summary(meal) + "\n"
    
    return message


def format_error(error_type: str, details: str = "") -> str:
    """Format error message"""
    errors = {
        'api_error': "❌ Ошибка при обращении к API анализа. Попробуй позже.",
        'photo_error': "❌ Не удалось обработать фото. Попробуй другое фото.",
        'parse_error': "❌ Не удалось распознать блюдо. Попробуй более чёткое фото.",
        'session_expired': "⏱️ Сессия истекла. Отправь фото заново.",
        'invalid_input': "❌ Неверный формат. Попробуй ещё раз.",
        'no_session': "❌ Нет активной сессии. Отправь фото для анализа.",
        'correction_error': config.MESSAGES.get('correction_error', "❌ Ошибка при применении коррекции."),
        'save_error': "❌ Ошибка при сохранении. Попробуй ещё раз.",
    }
    
    message = errors.get(error_type, config.MESSAGES['error_general'])
    
    if details:
        message += f"\n\n{details}"
    
    return message



def format_meal_saved(meal_data: Dict[str, Any], user: Dict[str, Any], daily_stats: Dict[str, Any]) -> str:
    """Format meal saved confirmation message"""
    dish_name = meal_data.get('dish_name', 'Блюдо')
    calories = meal_data.get('total_calories', 0)
    protein = meal_data.get('protein_g', 0)
    fat = meal_data.get('fat_g', 0)
    carbs = meal_data.get('carbs_g', 0)
    
    # Daily progress
    daily_calories = user.get('daily_calories', 2000)
    consumed = daily_stats.get('calories_consumed', 0) if daily_stats else calories
    remaining = daily_calories - consumed
    percentage = (consumed / daily_calories * 100) if daily_calories > 0 else 0
    
    # Progress bar
    progress_bar = create_progress_bar(percentage)
    
    # Status emoji
    if percentage < 90:
        status_emoji = "✅"
        status_text = "В пределах нормы"
    elif percentage <= 110:
        status_emoji = "🎯"
        status_text = "Цель достигнута!"
    else:
        status_emoji = "⚠️"
        status_text = "Превышение нормы"
    
    message = f"""✅ **Приём пищи сохранён!**

🍽️ {dish_name}

📊 **Добавлено:**
🔥 Калории: {calories} ккал
🥚 Белки: {protein}г | 🥑 Жиры: {fat}г | 🌾 Углеводы: {carbs}г

──────────────────────────────
📈 **Прогресс за сегодня:**

{progress_bar} {percentage:.0f}%

🔥 {consumed}/{daily_calories} ккал"""
    
    if remaining > 0:
        message += f"\n💡 Осталось: {remaining} ккал"
    else:
        message += f"\n⚠️ Превышение: {abs(remaining)} ккал"
    
    message += f"\n\n{status_emoji} {status_text}"
    
    # Meal count
    if daily_stats:
        meals_count = daily_stats.get('meals_count', 1)
        message += f"\n🍽️ Приёмов пищи сегодня: {meals_count}"
    
    return message


def format_daily_progress(user: Dict[str, Any], daily_stats: Dict[str, Any]) -> str:
    """Format daily progress summary"""
    if not daily_stats:
        return "📊 Сегодня ещё нет данных."
    
    # Goals
    daily_calories = user.get('daily_calories', 2000)
    protein_goal = user.get('protein_goal', 150)
    fat_goal = user.get('fat_goal', 65)
    carbs_goal = user.get('carbs_goal', 200)
    
    # Consumed
    calories_consumed = daily_stats.get('calories_consumed', 0)
    protein_consumed = daily_stats.get('protein_consumed', 0)
    fat_consumed = daily_stats.get('fat_consumed', 0)
    carbs_consumed = daily_stats.get('carbs_consumed', 0)
    meals_count = daily_stats.get('meals_count', 0)
    
    # Percentages
    cal_pct = (calories_consumed / daily_calories * 100) if daily_calories > 0 else 0
    prot_pct = (protein_consumed / protein_goal * 100) if protein_goal > 0 else 0
    fat_pct = (fat_consumed / fat_goal * 100) if fat_goal > 0 else 0
    carbs_pct = (carbs_consumed / carbs_goal * 100) if carbs_goal > 0 else 0
    
    message = f"""📊 **Прогресс за сегодня**

🍽️ Приёмов пищи: {meals_count}

🔥 **Калории:**
{create_progress_bar(cal_pct)} {cal_pct:.0f}%
{calories_consumed}/{daily_calories} ккал

🥚 **Белки:**
{create_progress_bar(prot_pct)} {prot_pct:.0f}%
{protein_consumed}/{protein_goal}г

🥑 **Жиры:**
{create_progress_bar(fat_pct)} {fat_pct:.0f}%
{fat_consumed}/{fat_goal}г

🌾 **Углеводы:**
{create_progress_bar(carbs_pct)} {carbs_pct:.0f}%
{carbs_consumed}/{carbs_goal}г"""
    
    return message


def format_dish_comparison(
    user_analysis: Dict[str, Any],
    comparison_result: Dict[str, Any]
) -> str:
    """
    Format comparison with typical dishes
    
    Args:
        user_analysis: User's food analysis
        comparison_result: Result from DishComparator.calculate_realism_score()
    
    Returns:
        Formatted comparison message
    """
    closest_match = comparison_result.get('closest_match')
    
    if not closest_match:
        return ""
    
    deviations = comparison_result.get('deviations', [])
    warnings = comparison_result.get('warnings', [])
    realism_score = comparison_result.get('realism_score', 0.5)
    
    # Header
    message = "\n🔍 **СРАВНЕНИЕ С ТИПИЧНЫМИ БЛЮДАМИ:**\n\n"
    
    # Closest match info
    dish_name = closest_match['dish_name']
    source = closest_match.get('source', '')
    category = closest_match['category']
    typical_score = closest_match['health_score']
    similarity = closest_match['similarity']['total_score']
    
    source_text = f" ({source})" if source else ""
    message += f"Ваше блюдо похоже на:\n"
    message += f"🍔 **{dish_name}**{source_text}\n"
    message += f"📊 Сходство: {similarity * 100:.0f}%\n"
    message += f"⭐ Типичная оценка: {typical_score}/10\n\n"
    
    # Deviations
    if deviations:
        message += "📊 **Отличия от типичного блюда:**\n"
        
        for dev in deviations:
            metric = dev['metric']
            user_val = dev['user']
            typical_val = dev['typical']
            diff_pct = dev['diff_percent']
            
            # Emoji based on metric
            emoji_map = {
                'calories': '🔥',
                'protein': '🥚',
                'fat': '🥑',
                'carbs': '🌾'
            }
            emoji = emoji_map.get(metric, '📊')
            
            # Status emoji based on difference
            if abs(diff_pct) < 10:
                status = "✅"
            elif abs(diff_pct) < 20:
                status = "⚠️"
            else:
                status = "❌"
            
            # Format metric name
            metric_names = {
                'calories': 'Калории',
                'protein': 'Белки',
                'fat': 'Жиры',
                'carbs': 'Углеводы'
            }
            metric_name = metric_names.get(metric, metric)
            
            # Format difference
            if diff_pct > 0:
                diff_text = f"+{diff_pct:.0f}%"
            else:
                diff_text = f"{diff_pct:.0f}%"
            
            message += f"{status} {emoji} {metric_name}: {user_val} vs {typical_val} ({diff_text})\n"
        
        message += "\n"
    
    # Context analysis
    message += "📝 **КОНТЕКСТ:**\n"
    
    # Category-specific context
    category_contexts = {
        'fast_food': "Это фастфуд: жареное мясо + белая булочка + сыр. Даже с хорошими компонентами, КОМБИНАЦИЯ делает блюдо менее полезным.",
        'healthy': "Здоровая комбинация ингредиентов: цельнозерновые продукты, нежирное мясо, овощи.",
        'dessert': "Десерт с высоким содержанием сахара и жиров. Употреблять в ограниченных количествах.",
        'home_cooking': "Домашняя еда. Полезность зависит от способа приготовления и ингредиентов.",
        'breakfast': "Завтрак. Важен баланс белков, жиров и углеводов для энергии на день.",
        'snacks': "Перекус. Выбирай варианты с белком и клетчаткой, избегай пустых калорий.",
        'drinks': "Напиток. Обращай внимание на содержание сахара."
    }
    
    context_text = category_contexts.get(category, "Обычное блюдо.")
    message += f"{context_text}\n\n"
    
    # Warnings
    if warnings:
        message += "⚠️ **ЗАМЕЧАНИЯ:**\n"
        for warning in warnings:
            message += f"• {warning}\n"
        message += "\n"
    
    # Realism indicator
    if realism_score < 0.5:
        message += "❓ **Реалистичность анализа:** Низкая. Возможны неточности в распознавании.\n"
    elif realism_score < 0.7:
        message += "⚠️ **Реалистичность анализа:** Средняя. Проверь данные.\n"
    else:
        message += "✅ **Реалистичность анализа:** Высокая. Данные соответствуют типичным значениям.\n"
    
    return message


def format_video_note_analysis(analysis: Dict[str, Any]) -> str:
    """Format video note analysis with transcription indicator"""
    components = analysis.get('components', [])
    
    if not components:
        return "❌ Не удалось распознать компоненты блюда"
    
    # Header with video indicator
    dish_name = analysis.get('dish_name', 'Блюдо')
    message = f"🎥 **Анализ видео-кружка**\n\n"
    
    # Transcription indicator
    transcription = analysis.get('audio_transcription', '')
    transcription_used = analysis.get('transcription_used', False)
    
    if transcription and transcription_used:
        message += f"🎤 _Учтена голосовая информация:_\n"
        message += f"_{transcription}_\n\n"
    elif not transcription:
        message += f"ℹ️ _Анализ только по видео (без голоса)_\n\n"
    
    message += f"🍽️ **{dish_name}**\n\n"
    
    # Components with detailed info
    message += "**Компоненты:**\n\n"
    
    for i, comp in enumerate(components, 1):
        message += format_component_detailed(comp, i) + "\n\n"
    
    # Separator
    message += create_separator() + "\n"
    
    # Totals
    message += format_totals_summary(analysis) + "\n"
    
    # Calorie density indicator
    calories_per_100g = analysis.get('calories_per_100g', 0)
    if calories_per_100g > 0:
        message += f"\n{format_calorie_density_indicator(calories_per_100g)}\n"
    
    # Health score if available
    health_score = analysis.get('health_score')
    if health_score:
        message += f"\n⭐ Полезность: {format_health_score_visual(health_score)}\n"
    
    # Show warnings if any
    warnings = analysis.get('warnings', [])
    if warnings:
        message += f"\n{format_warnings_list(warnings)}\n"
    
    # Separator
    message += f"\n{create_separator()}\n"
    
    # Instructions
    message += format_instructions()
    
    return message
