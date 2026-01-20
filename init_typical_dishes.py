"""
Initialize typical dishes database
"""
import asyncio
import logging
from core.database import Database
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Типичные блюда для сравнения
TYPICAL_DISHES = [
    # ==================== ФАСТФУД ====================
    {
        'dish_name': 'Бургер с говядиной',
        'category': 'fast_food',
        'source': 'mcdonalds',
        'calories_per_100g': 250,
        'protein_per_100g': 12,
        'fat_per_100g': 12,
        'carbs_per_100g': 26,
        'sodium_per_100g': 350,
        'sugar_per_100g': 5,
        'saturated_fat_per_100g': 4.5,
        'fiber_per_100g': 1.5,
        'typical_weight_g': 200,
        'health_score': 4,
        'description': 'Типичный фастфуд-бургер: жареная котлета, белая булочка, сыр, соус',
        'tags': ['fried', 'processed_bread', 'cheese', 'sauce', 'high_sodium']
    },
    {
        'dish_name': 'Чизбургер',
        'category': 'fast_food',
        'source': 'mcdonalds',
        'calories_per_100g': 280,
        'protein_per_100g': 13,
        'fat_per_100g': 14,
        'carbs_per_100g': 28,
        'sodium_per_100g': 400,
        'sugar_per_100g': 6,
        'saturated_fat_per_100g': 6,
        'fiber_per_100g': 1,
        'typical_weight_g': 180,
        'health_score': 3,
        'description': 'Бургер с двойным сыром, высокое содержание насыщенных жиров',
        'tags': ['fried', 'processed_bread', 'double_cheese', 'high_sodium', 'high_fat']
    },
    {
        'dish_name': 'Картофель фри',
        'category': 'fast_food',
        'source': 'mcdonalds',
        'calories_per_100g': 312,
        'protein_per_100g': 3.4,
        'fat_per_100g': 15,
        'carbs_per_100g': 41,
        'sodium_per_100g': 210,
        'sugar_per_100g': 0.3,
        'saturated_fat_per_100g': 2.3,
        'fiber_per_100g': 3.8,
        'typical_weight_g': 150,
        'health_score': 2,
        'description': 'Жареный картофель во фритюре, много масла и соли',
        'tags': ['fried', 'high_fat', 'high_carbs', 'processed']
    },
    {
        'dish_name': 'Пицца пепперони',
        'category': 'fast_food',
        'source': 'dominos',
        'calories_per_100g': 280,
        'protein_per_100g': 11,
        'fat_per_100g': 12,
        'carbs_per_100g': 33,
        'sodium_per_100g': 600,
        'sugar_per_100g': 4,
        'saturated_fat_per_100g': 5,
        'fiber_per_100g': 2,
        'typical_weight_g': 300,
        'health_score': 3,
        'description': 'Пицца с колбасой пепперони, сыром моцарелла, томатным соусом',
        'tags': ['processed_meat', 'cheese', 'white_flour', 'high_sodium']
    },
    
    # ==================== ЗДОРОВАЯ ЕДА ====================
    {
        'dish_name': 'Домашний бургер с курицей',
        'category': 'home_cooking',
        'source': 'healthy',
        'calories_per_100g': 180,
        'protein_per_100g': 20,
        'fat_per_100g': 8,
        'carbs_per_100g': 15,
        'sodium_per_100g': 200,
        'sugar_per_100g': 2,
        'saturated_fat_per_100g': 2,
        'fiber_per_100g': 3,
        'typical_weight_g': 250,
        'health_score': 7,
        'description': 'Полезная версия: куриная грудка на гриле, цельнозерновая булочка, много овощей',
        'tags': ['grilled', 'whole_grain', 'vegetables', 'lean_meat']
    },
    {
        'dish_name': 'Салат цезарь с курицей',
        'category': 'healthy',
        'source': 'restaurant',
        'calories_per_100g': 150,
        'protein_per_100g': 12,
        'fat_per_100g': 9,
        'carbs_per_100g': 8,
        'sodium_per_100g': 300,
        'sugar_per_100g': 2,
        'saturated_fat_per_100g': 2.5,
        'fiber_per_100g': 2,
        'typical_weight_g': 350,
        'health_score': 6,
        'description': 'Салат с курицей гриль, листьями салата, пармезаном, соусом цезарь',
        'tags': ['grilled', 'vegetables', 'cheese', 'sauce']
    },
    {
        'dish_name': 'Овсянка с фруктами',
        'category': 'healthy',
        'source': 'home_cooking',
        'calories_per_100g': 120,
        'protein_per_100g': 4,
        'fat_per_100g': 2.5,
        'carbs_per_100g': 22,
        'sodium_per_100g': 5,
        'sugar_per_100g': 8,
        'saturated_fat_per_100g': 0.5,
        'fiber_per_100g': 3.5,
        'typical_weight_g': 300,
        'health_score': 9,
        'description': 'Овсяная каша на воде с бананом, ягодами, орехами',
        'tags': ['whole_grain', 'fruits', 'nuts', 'low_fat', 'high_fiber']
    },
    {
        'dish_name': 'Греческий салат',
        'category': 'healthy',
        'source': 'restaurant',
        'calories_per_100g': 110,
        'protein_per_100g': 4,
        'fat_per_100g': 8,
        'carbs_per_100g': 6,
        'sodium_per_100g': 400,
        'sugar_per_100g': 3,
        'saturated_fat_per_100g': 3,
        'fiber_per_100g': 2,
        'typical_weight_g': 300,
        'health_score': 8,
        'description': 'Овощной салат с фетой, оливками, оливковым маслом',
        'tags': ['vegetables', 'cheese', 'olive_oil', 'mediterranean']
    },
    
    # ==================== ДОМАШНЯЯ ЕДА ====================
    {
        'dish_name': 'Пельмени со сметаной',
        'category': 'home_cooking',
        'source': 'traditional',
        'calories_per_100g': 250,
        'protein_per_100g': 11,
        'fat_per_100g': 10,
        'carbs_per_100g': 28,
        'sodium_per_100g': 300,
        'sugar_per_100g': 1,
        'saturated_fat_per_100g': 4,
        'fiber_per_100g': 1.5,
        'typical_weight_g': 280,
        'health_score': 5,
        'description': 'Традиционные пельмени с мясной начинкой и сметаной',
        'tags': ['meat', 'dough', 'sour_cream', 'boiled']
    },
    {
        'dish_name': 'Борщ с мясом',
        'category': 'home_cooking',
        'source': 'traditional',
        'calories_per_100g': 60,
        'protein_per_100g': 4,
        'fat_per_100g': 2.5,
        'carbs_per_100g': 6,
        'sodium_per_100g': 400,
        'sugar_per_100g': 3,
        'saturated_fat_per_100g': 1,
        'fiber_per_100g': 2,
        'typical_weight_g': 400,
        'health_score': 7,
        'description': 'Традиционный борщ со свеклой, капустой, мясом, сметаной',
        'tags': ['soup', 'vegetables', 'meat', 'traditional']
    },
    {
        'dish_name': 'Гречка с курицей',
        'category': 'home_cooking',
        'source': 'healthy',
        'calories_per_100g': 140,
        'protein_per_100g': 12,
        'fat_per_100g': 4,
        'carbs_per_100g': 18,
        'sodium_per_100g': 200,
        'sugar_per_100g': 0.5,
        'saturated_fat_per_100g': 1,
        'fiber_per_100g': 3,
        'typical_weight_g': 350,
        'health_score': 8,
        'description': 'Гречневая каша с отварной куриной грудкой',
        'tags': ['whole_grain', 'lean_meat', 'boiled', 'low_fat']
    },
    {
        'dish_name': 'Жареная картошка с мясом',
        'category': 'home_cooking',
        'source': 'traditional',
        'calories_per_100g': 200,
        'protein_per_100g': 8,
        'fat_per_100g': 10,
        'carbs_per_100g': 20,
        'sodium_per_100g': 250,
        'sugar_per_100g': 1,
        'saturated_fat_per_100g': 3,
        'fiber_per_100g': 2,
        'typical_weight_g': 350,
        'health_score': 4,
        'description': 'Картофель жареный на масле с кусочками мяса',
        'tags': ['fried', 'meat', 'high_fat', 'potatoes']
    },
    
    # ==================== ДЕСЕРТЫ ====================
    {
        'dish_name': 'Шоколадный торт',
        'category': 'dessert',
        'source': 'bakery',
        'calories_per_100g': 400,
        'protein_per_100g': 5,
        'fat_per_100g': 20,
        'carbs_per_100g': 50,
        'sodium_per_100g': 200,
        'sugar_per_100g': 35,
        'saturated_fat_per_100g': 12,
        'fiber_per_100g': 2,
        'typical_weight_g': 120,
        'health_score': 2,
        'description': 'Шоколадный торт с кремом, высокое содержание сахара и жира',
        'tags': ['sugar', 'chocolate', 'cream', 'high_fat', 'high_sugar']
    },
    {
        'dish_name': 'Мороженое',
        'category': 'dessert',
        'source': 'store',
        'calories_per_100g': 207,
        'protein_per_100g': 3.5,
        'fat_per_100g': 11,
        'carbs_per_100g': 24,
        'sodium_per_100g': 80,
        'sugar_per_100g': 21,
        'saturated_fat_per_100g': 7,
        'fiber_per_100g': 0.5,
        'typical_weight_g': 100,
        'health_score': 3,
        'description': 'Сливочное мороженое, много сахара и насыщенных жиров',
        'tags': ['sugar', 'cream', 'frozen', 'high_sugar']
    },
    
    # ==================== НАПИТКИ ====================
    {
        'dish_name': 'Кока-кола',
        'category': 'drinks',
        'source': 'store',
        'calories_per_100g': 42,
        'protein_per_100g': 0,
        'fat_per_100g': 0,
        'carbs_per_100g': 10.6,
        'sodium_per_100g': 10,
        'sugar_per_100g': 10.6,
        'saturated_fat_per_100g': 0,
        'fiber_per_100g': 0,
        'typical_weight_g': 330,
        'health_score': 1,
        'description': 'Газированный напиток с высоким содержанием сахара',
        'tags': ['sugar', 'carbonated', 'no_nutrients']
    },
    {
        'dish_name': 'Апельсиновый сок',
        'category': 'drinks',
        'source': 'store',
        'calories_per_100g': 45,
        'protein_per_100g': 0.7,
        'fat_per_100g': 0.2,
        'carbs_per_100g': 10,
        'sodium_per_100g': 1,
        'sugar_per_100g': 8.5,
        'saturated_fat_per_100g': 0,
        'fiber_per_100g': 0.2,
        'typical_weight_g': 250,
        'health_score': 5,
        'description': 'Натуральный апельсиновый сок, содержит витамин C',
        'tags': ['juice', 'vitamin_c', 'natural_sugar']
    },
    
    # ==================== ЗАКУСКИ ====================
    {
        'dish_name': 'Чипсы картофельные',
        'category': 'snacks',
        'source': 'store',
        'calories_per_100g': 536,
        'protein_per_100g': 6.6,
        'fat_per_100g': 35,
        'carbs_per_100g': 49,
        'sodium_per_100g': 500,
        'sugar_per_100g': 3,
        'saturated_fat_per_100g': 3.1,
        'fiber_per_100g': 4.4,
        'typical_weight_g': 50,
        'health_score': 1,
        'description': 'Жареные картофельные чипсы, очень высокая калорийность',
        'tags': ['fried', 'high_fat', 'high_sodium', 'processed']
    },
    {
        'dish_name': 'Орехи миндаль',
        'category': 'snacks',
        'source': 'healthy',
        'calories_per_100g': 579,
        'protein_per_100g': 21,
        'fat_per_100g': 50,
        'carbs_per_100g': 22,
        'sodium_per_100g': 1,
        'sugar_per_100g': 4,
        'saturated_fat_per_100g': 3.8,
        'fiber_per_100g': 12.5,
        'typical_weight_g': 30,
        'health_score': 8,
        'description': 'Миндаль, богат белком, полезными жирами, витамином E',
        'tags': ['nuts', 'protein', 'healthy_fats', 'fiber', 'vitamin_e']
    },
    
    # ==================== ЗАВТРАКИ ====================
    {
        'dish_name': 'Яичница с беконом',
        'category': 'breakfast',
        'source': 'home_cooking',
        'calories_per_100g': 220,
        'protein_per_100g': 14,
        'fat_per_100g': 17,
        'carbs_per_100g': 2,
        'sodium_per_100g': 450,
        'sugar_per_100g': 0.5,
        'saturated_fat_per_100g': 5,
        'fiber_per_100g': 0,
        'typical_weight_g': 200,
        'health_score': 5,
        'description': 'Жареные яйца с беконом, высокое содержание белка и жира',
        'tags': ['fried', 'eggs', 'bacon', 'high_protein', 'high_sodium']
    },
    {
        'dish_name': 'Блины с медом',
        'category': 'breakfast',
        'source': 'home_cooking',
        'calories_per_100g': 227,
        'protein_per_100g': 6,
        'fat_per_100g': 7,
        'carbs_per_100g': 35,
        'sodium_per_100g': 250,
        'sugar_per_100g': 15,
        'saturated_fat_per_100g': 2,
        'fiber_per_100g': 1,
        'typical_weight_g': 200,
        'health_score': 4,
        'description': 'Блины на молоке с медом, много быстрых углеводов',
        'tags': ['fried', 'white_flour', 'sugar', 'high_carbs']
    },
]


async def init_dishes():
    """Initialize typical dishes in database"""
    db = Database(config.DATABASE_PATH)
    await db.initialize()
    
    # Check if already populated
    count = await db.count_typical_dishes()
    if count > 0:
        logger.info(f"Database already has {count} dishes")
        response = input("Do you want to add more dishes? (y/n): ")
        if response.lower() != 'y':
            return
    
    # Add dishes
    logger.info(f"Adding {len(TYPICAL_DISHES)} typical dishes...")
    
    for dish in TYPICAL_DISHES:
        try:
            dish_id = await db.add_typical_dish(dish)
            logger.info(f"✅ Added: {dish['dish_name']} (ID: {dish_id}, Score: {dish['health_score']}/10)")
        except Exception as e:
            logger.error(f"❌ Failed to add {dish['dish_name']}: {e}")
    
    # Show summary
    total = await db.count_typical_dishes()
    logger.info(f"\n✅ Total dishes in database: {total}")
    
    # Show by category
    categories = {}
    all_dishes = await db.get_typical_dishes()
    for dish in all_dishes:
        cat = dish['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    logger.info("\n📊 Dishes by category:")
    for cat, count in categories.items():
        logger.info(f"  {cat}: {count}")


if __name__ == '__main__':
    asyncio.run(init_dishes())
