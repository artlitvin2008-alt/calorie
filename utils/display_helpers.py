"""
Display helpers for better UX
"""
from typing import Dict, Any, List


def format_component_compact(comp: Dict[str, Any], index: int) -> str:
    """Format single component in compact view"""
    name = comp.get('name', 'Неизвестно')
    weight = comp.get('weight_g', 0)
    calories = comp.get('calories', 0)
    confidence = comp.get('confidence', 0)
    
    # Confidence emoji
    if confidence >= 0.8:
        emoji = "✅"
    elif confidence >= 0.6:
        emoji = "⚠️"
    else:
        emoji = "❓"
    
    return f"{index}. {emoji} {name} ({weight}г, {calories} ккал)"


def format_component_detailed(comp: Dict[str, Any], index: int) -> str:
    """Format single component in detailed view"""
    name = comp.get('name', 'Неизвестно')
    weight = comp.get('weight_g', 0)
    calories = comp.get('calories', 0)
    protein = comp.get('protein_g', 0)
    fat = comp.get('fat_g', 0)
    carbs = comp.get('carbs_g', 0)
    confidence = comp.get('confidence', 0)
    
    # Confidence emoji and text
    if confidence >= 0.8:
        conf_emoji = "✅"
        conf_text = "уверен"
    elif confidence >= 0.6:
        conf_emoji = "⚠️"
        conf_text = "вероятно"
    else:
        conf_emoji = "❓"
        conf_text = "не уверен"
    
    lines = [
        f"{index}. {conf_emoji} **{name}**",
        f"   📊 Вес: ~{weight}г",
        f"   🔥 Калории: ~{calories} ккал"
    ]
    
    # Add macros if available
    if protein or fat or carbs:
        lines.append(f"   🥚 Б: {protein}г | 🥑 Ж: {fat}г | 🌾 У: {carbs}г")
    
    # Add confidence
    lines.append(f"   💭 {conf_text} ({int(confidence * 100)}%)")
    
    return "\n".join(lines)


def format_totals_summary(analysis: Dict[str, Any]) -> str:
    """Format totals summary"""
    total_weight = analysis.get('weight_grams', 0)
    total_calories = analysis.get('calories_total', 0)
    total_protein = analysis.get('protein_g', 0)
    total_fat = analysis.get('fat_g', 0)
    total_carbs = analysis.get('carbs_g', 0)
    
    lines = [
        "**📊 Итого:**",
        f"⚖️ Вес: {total_weight}г",
        f"🔥 Калории: {total_calories} ккал",
        f"🥚 Белки: {total_protein}г | 🥑 Жиры: {total_fat}г | 🌾 Углеводы: {total_carbs}г"
    ]
    
    return "\n".join(lines)


def format_warnings_list(warnings: List[str], max_warnings: int = 3) -> str:
    """Format warnings list"""
    if not warnings:
        return ""
    
    lines = ["⚠️ **Предупреждения:**"]
    for warning in warnings[:max_warnings]:
        lines.append(f"• {warning}")
    
    if len(warnings) > max_warnings:
        lines.append(f"• ...и ещё {len(warnings) - max_warnings}")
    
    return "\n".join(lines)


def format_instructions() -> str:
    """Format user instructions"""
    return """**Что дальше?**

✅ Всё верно? Нажми кнопку ниже

✏️ Нужно исправить? Напиши:
• "нет хлеба" - убрать компонент
• "добавь салат 100г" - добавить
• "это курица, а не свинина" - изменить"""


def create_separator(length: int = 30, char: str = "─") -> str:
    """Create visual separator"""
    return char * length


def format_health_score_visual(score: int) -> str:
    """Format health score with visual indicator"""
    # Ensure score is integer
    score = int(round(score))
    score = max(1, min(10, score))  # Clamp to 1-10
    
    filled = "🟢" * score
    empty = "⚪" * (10 - score)
    
    if score >= 8:
        text = "Отлично!"
    elif score >= 6:
        text = "Хорошо"
    elif score >= 4:
        text = "Средне"
    else:
        text = "Не очень"
    
    return f"{filled}{empty} {score}/10 - {text}"


def format_calorie_density_indicator(calories_per_100g: float) -> str:
    """Format calorie density indicator"""
    if calories_per_100g < 100:
        emoji = "🟢"
        text = "Низкая калорийность"
    elif calories_per_100g < 200:
        emoji = "🟡"
        text = "Средняя калорийность"
    elif calories_per_100g < 300:
        emoji = "🟠"
        text = "Высокая калорийность"
    else:
        emoji = "🔴"
        text = "Очень высокая калорийность"
    
    return f"{emoji} {calories_per_100g:.0f} ккал/100г - {text}"
