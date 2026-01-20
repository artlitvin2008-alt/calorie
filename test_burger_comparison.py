"""
Test burger comparison with typical dishes
"""
import asyncio
import logging
from core.database import Database
from modules.nutrition.dish_comparator import DishComparator
from utils.formatters import format_dish_comparison
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Пример анализа бургера (как в промпте клиента)
BURGER_ANALYSIS = {
    "components": [
        {
            "name": "Говядина жареная",
            "weight_g": 100,
            "calories": 250,
            "protein_g": 25,
            "fat_g": 15,
            "carbs_g": 0,
            "confidence": 0.85
        },
        {
            "name": "Сыр твёрдый",
            "weight_g": 20,
            "calories": 80,
            "protein_g": 5,
            "fat_g": 6,
            "carbs_g": 0,
            "confidence": 0.90
        },
        {
            "name": "Булочка для бургера",
            "weight_g": 50,
            "calories": 140,
            "protein_g": 5,
            "fat_g": 3,
            "carbs_g": 23,
            "confidence": 0.85
        },
        {
            "name": "Томат",
            "weight_g": 20,
            "calories": 4,
            "protein_g": 0.2,
            "fat_g": 0,
            "carbs_g": 0.8,
            "confidence": 0.95
        },
        {
            "name": "Лук",
            "weight_g": 10,
            "calories": 4,
            "protein_g": 0.1,
            "fat_g": 0,
            "carbs_g": 0.9,
            "confidence": 0.90
        },
        {
            "name": "Салат",
            "weight_g": 20,
            "calories": 3,
            "protein_g": 0.3,
            "fat_g": 0,
            "carbs_g": 0.6,
            "confidence": 0.95
        }
    ],
    "dish_name": "Бургер с говядиной",
    "weight_grams": 220,
    "calories_total": 481,
    "calories_per_100g": 219,
    "protein_g": 35.6,
    "fat_g": 24,
    "carbs_g": 25.3,
    "health_score": 7,  # Завышенная оценка (должна быть 4-5)
    "detailed_analysis": "Бургер с говяжьей котлетой, сыром, овощами и булочкой",
    "recommendations": "Уменьши порцию на 20-30%",
    "portion_advice": "Порция стандартная"
}


async def test_burger_comparison():
    """Test burger comparison"""
    logger.info("=" * 60)
    logger.info("ТЕСТ: Сравнение бургера с типичными блюдами")
    logger.info("=" * 60)
    
    # Initialize database
    db = Database(config.DATABASE_PATH)
    await db.initialize()
    
    # Check if we have typical dishes
    count = await db.count_typical_dishes()
    logger.info(f"\n📊 Блюд в базе данных: {count}")
    
    if count == 0:
        logger.error("❌ База данных пуста! Запусти init_typical_dishes.py")
        return
    
    # Initialize comparator
    comparator = DishComparator(db)
    
    # Test 1: Find similar dishes
    logger.info("\n" + "=" * 60)
    logger.info("ТЕСТ 1: Поиск похожих блюд")
    logger.info("=" * 60)
    
    similar_dishes = await comparator.find_similar_dishes(BURGER_ANALYSIS, limit=3)
    
    logger.info(f"\nНайдено похожих блюд: {len(similar_dishes)}")
    
    for i, dish in enumerate(similar_dishes, 1):
        logger.info(f"\n{i}. {dish['dish_name']}")
        logger.info(f"   Категория: {dish['category']}")
        logger.info(f"   Источник: {dish.get('source', 'N/A')}")
        logger.info(f"   Health Score: {dish['health_score']}/10")
        logger.info(f"   Сходство: {dish['similarity']['total_score'] * 100:.1f}%")
        logger.info(f"   - По названию: {dish['similarity']['name_score'] * 100:.1f}%")
        logger.info(f"   - По питательности: {dish['similarity']['nutrition_score'] * 100:.1f}%")
        logger.info(f"   - По компонентам: {dish['similarity']['component_score'] * 100:.1f}%")
    
    # Test 2: Calculate realism score
    logger.info("\n" + "=" * 60)
    logger.info("ТЕСТ 2: Оценка реалистичности")
    logger.info("=" * 60)
    
    comparison_result = await comparator.calculate_realism_score(
        BURGER_ANALYSIS,
        similar_dishes
    )
    
    logger.info(f"\nРеалистичность: {comparison_result['realism_score']}")
    logger.info(f"\nОтклонения от типичного блюда:")
    
    for dev in comparison_result['deviations']:
        metric = dev['metric']
        user_val = dev['user']
        typical_val = dev['typical']
        diff = dev['diff_percent']
        
        logger.info(f"  {metric}: {user_val} vs {typical_val} ({diff:+.1f}%)")
    
    if comparison_result['warnings']:
        logger.info(f"\nПредупреждения:")
        for warning in comparison_result['warnings']:
            logger.info(f"  ⚠️ {warning}")
    
    # Test 3: Adjust health score
    logger.info("\n" + "=" * 60)
    logger.info("ТЕСТ 3: Корректировка health score")
    logger.info("=" * 60)
    
    original_score = BURGER_ANALYSIS['health_score']
    adjusted_score, explanation = await comparator.adjust_health_score(
        BURGER_ANALYSIS,
        similar_dishes
    )
    
    logger.info(f"\nОригинальная оценка: {original_score}/10")
    logger.info(f"Скорректированная оценка: {adjusted_score}/10")
    logger.info(f"Объяснение: {explanation}")
    
    # Test 4: Detect category
    logger.info("\n" + "=" * 60)
    logger.info("ТЕСТ 4: Определение категории")
    logger.info("=" * 60)
    
    category = comparator.detect_dish_category(BURGER_ANALYSIS)
    logger.info(f"\nОпределённая категория: {category}")
    
    # Test 5: Context score
    logger.info("\n" + "=" * 60)
    logger.info("ТЕСТ 5: Оценка контекста")
    logger.info("=" * 60)
    
    context_score = comparator.calculate_dish_context_score(BURGER_ANALYSIS['components'])
    logger.info(f"\nКонтекстная оценка: {context_score} (0-1, выше = здоровее)")
    
    # Test 6: Format comparison message
    logger.info("\n" + "=" * 60)
    logger.info("ТЕСТ 6: Форматирование сообщения")
    logger.info("=" * 60)
    
    # Update analysis with adjusted score
    BURGER_ANALYSIS['health_score'] = adjusted_score
    BURGER_ANALYSIS['health_score_original'] = original_score
    BURGER_ANALYSIS['comparison'] = comparison_result
    
    formatted_message = format_dish_comparison(BURGER_ANALYSIS, comparison_result)
    
    logger.info("\nФорматированное сообщение для пользователя:")
    logger.info("-" * 60)
    print(formatted_message)
    logger.info("-" * 60)
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("ИТОГИ ТЕСТА")
    logger.info("=" * 60)
    
    logger.info(f"\n✅ Найдено похожих блюд: {len(similar_dishes)}")
    logger.info(f"✅ Ближайшее совпадение: {similar_dishes[0]['dish_name']}")
    logger.info(f"✅ Health score: {original_score}/10 → {adjusted_score}/10")
    logger.info(f"✅ Категория: {category}")
    logger.info(f"✅ Реалистичность: {comparison_result['realism_score']}")
    
    # Check if goal achieved
    if adjusted_score <= 5:
        logger.info("\n🎯 ЦЕЛЬ ДОСТИГНУТА!")
        logger.info(f"   Бургер получил оценку {adjusted_score}/10 (не 7/10)")
        logger.info("   Система корректно определила, что это фастфуд")
    else:
        logger.warning("\n⚠️ ЦЕЛЬ НЕ ДОСТИГНУТА")
        logger.warning(f"   Бургер всё ещё имеет оценку {adjusted_score}/10")
        logger.warning("   Нужна дополнительная настройка алгоритма")
    
    logger.info("\n" + "=" * 60)


if __name__ == '__main__':
    asyncio.run(test_burger_comparison())
