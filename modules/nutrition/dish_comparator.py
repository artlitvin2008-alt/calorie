"""
Dish Comparator - compares user's food analysis with typical dishes
"""
import logging
import json
from typing import Dict, Any, List, Tuple, Optional
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class DishComparator:
    """Compares analyzed dishes with typical dishes from database"""
    
    def __init__(self, database):
        """
        Initialize comparator
        
        Args:
            database: Database instance
        """
        self.db = database
        
        # Category keywords for detection
        self.category_keywords = {
            'fast_food': [
                'бургер', 'гамбургер', 'чизбургер', 'картофель фри', 'фри',
                'пицца', 'хот-дог', 'наггетсы', 'крылышки', 'кфс', 'макдональдс',
                'жареная котлета', 'белая булочка', 'майонез', 'кетчуп'
            ],
            'healthy': [
                'салат', 'овощи', 'гриль', 'на пару', 'отварной', 'отварная',
                'цельнозерновой', 'цельнозерновая', 'фрукты', 'ягоды', 'орехи',
                'авокадо', 'киноа', 'брокколи', 'шпинат'
            ],
            'dessert': [
                'торт', 'пирожное', 'мороженое', 'шоколад', 'конфеты',
                'печенье', 'вафли', 'пончик', 'круассан', 'сладкое'
            ],
            'home_cooking': [
                'пельмени', 'вареники', 'борщ', 'суп', 'каша', 'гречка',
                'рис', 'макароны', 'котлета', 'тефтели', 'рагу', 'плов'
            ],
            'breakfast': [
                'яичница', 'омлет', 'блины', 'оладьи', 'сырники', 'каша',
                'мюсли', 'хлопья', 'тост', 'бутерброд'
            ],
            'snacks': [
                'чипсы', 'сухарики', 'орехи', 'семечки', 'попкорн',
                'батончик', 'крекер'
            ],
            'drinks': [
                'сок', 'кола', 'пепси', 'лимонад', 'напиток', 'смузи',
                'коктейль', 'чай', 'кофе'
            ]
        }
        
        # Unhealthy ingredient markers
        self.unhealthy_markers = {
            'fried': ['жареный', 'жареная', 'жареное', 'фри', 'во фритюре'],
            'processed_bread': ['белая булочка', 'белый хлеб', 'батон'],
            'processed_meat': ['колбаса', 'сосиски', 'бекон', 'ветчина'],
            'cheese': ['сыр плавленый', 'сыр чеддер'],
            'sauce': ['майонез', 'кетчуп', 'соус'],
            'high_sodium': ['соленый', 'соленая', 'маринованный'],
            'sugar': ['сахар', 'сладкий', 'сладкая', 'глазурь']
        }
    
    async def find_similar_dishes(
        self,
        user_analysis: Dict[str, Any],
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Find similar dishes from database
        
        Args:
            user_analysis: User's food analysis result
            limit: Maximum number of similar dishes to return
        
        Returns:
            List of similar dishes with similarity scores
        """
        dish_name = user_analysis.get('dish_name', '').lower()
        components = user_analysis.get('components', [])
        
        # Get all typical dishes
        all_dishes = await self.db.get_typical_dishes()
        
        if not all_dishes:
            logger.warning("No typical dishes in database")
            return []
        
        # Calculate similarity for each dish
        similarities = []
        for typical_dish in all_dishes:
            similarity = self._calculate_similarity(
                user_analysis,
                typical_dish,
                dish_name,
                components
            )
            
            if similarity['total_score'] > 0.2:  # Minimum threshold
                similarities.append({
                    **typical_dish,
                    'similarity': similarity
                })
        
        # Sort by similarity score
        similarities.sort(key=lambda x: x['similarity']['total_score'], reverse=True)
        
        return similarities[:limit]
    
    def _calculate_similarity(
        self,
        user_analysis: Dict[str, Any],
        typical_dish: Dict[str, Any],
        dish_name: str,
        components: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate similarity between user's dish and typical dish"""
        
        # 1. Name similarity (30% weight)
        name_score = self._name_similarity(dish_name, typical_dish['dish_name'].lower())
        
        # 2. Nutrition similarity (40% weight)
        nutrition_score = self._nutrition_similarity(user_analysis, typical_dish)
        
        # 3. Component similarity (30% weight)
        component_score = self._component_similarity(components, typical_dish)
        
        # Calculate weighted total
        total_score = (
            name_score * 0.3 +
            nutrition_score * 0.4 +
            component_score * 0.3
        )
        
        return {
            'name_score': name_score,
            'nutrition_score': nutrition_score,
            'component_score': component_score,
            'total_score': total_score
        }
    
    def _name_similarity(self, name1: str, name2: str) -> float:
        """Calculate name similarity using SequenceMatcher"""
        return SequenceMatcher(None, name1, name2).ratio()
    
    def _nutrition_similarity(
        self,
        user_analysis: Dict[str, Any],
        typical_dish: Dict[str, Any]
    ) -> float:
        """Calculate nutrition similarity"""
        
        # Get user's nutrition per 100g
        user_cal = user_analysis.get('calories_per_100g', 0)
        user_protein = user_analysis.get('protein_g', 0) / (user_analysis.get('weight_grams', 100) / 100)
        user_fat = user_analysis.get('fat_g', 0) / (user_analysis.get('weight_grams', 100) / 100)
        user_carbs = user_analysis.get('carbs_g', 0) / (user_analysis.get('weight_grams', 100) / 100)
        
        # Get typical dish nutrition per 100g
        typical_cal = typical_dish['calories_per_100g']
        typical_protein = typical_dish['protein_per_100g']
        typical_fat = typical_dish['fat_per_100g']
        typical_carbs = typical_dish['carbs_per_100g']
        
        # Calculate percentage differences
        cal_diff = abs(user_cal - typical_cal) / max(typical_cal, 1)
        protein_diff = abs(user_protein - typical_protein) / max(typical_protein, 1)
        fat_diff = abs(user_fat - typical_fat) / max(typical_fat, 1)
        carbs_diff = abs(user_carbs - typical_carbs) / max(typical_carbs, 1)
        
        # Average difference (lower is better)
        avg_diff = (cal_diff + protein_diff + fat_diff + carbs_diff) / 4
        
        # Convert to similarity score (0-1)
        similarity = max(0, 1 - avg_diff)
        
        return similarity
    
    def _component_similarity(
        self,
        components: List[Dict[str, Any]],
        typical_dish: Dict[str, Any]
    ) -> float:
        """Calculate component similarity based on tags"""
        
        # Get tags from typical dish
        tags_str = typical_dish.get('tags', '[]')
        if isinstance(tags_str, str):
            try:
                tags = json.loads(tags_str)
            except:
                tags = []
        else:
            tags = tags_str
        
        if not tags or not components:
            return 0.5  # Neutral score
        
        # Check how many tags match components
        matches = 0
        for tag in tags:
            for component in components:
                comp_name = component.get('name', '').lower()
                if tag in comp_name or any(keyword in comp_name for keyword in self._get_tag_keywords(tag)):
                    matches += 1
                    break
        
        # Calculate score
        score = matches / len(tags) if tags else 0
        return min(score, 1.0)
    
    def _get_tag_keywords(self, tag: str) -> List[str]:
        """Get keywords for a tag"""
        tag_keywords = {
            'fried': ['жареный', 'жареная', 'фри'],
            'grilled': ['гриль', 'на гриле'],
            'boiled': ['отварной', 'отварная', 'вареный'],
            'cheese': ['сыр'],
            'meat': ['мясо', 'говядина', 'свинина', 'курица'],
            'vegetables': ['овощи', 'салат', 'помидор', 'огурец'],
            'sauce': ['соус', 'майонез', 'кетчуп'],
            'bread': ['хлеб', 'булочка', 'батон']
        }
        return tag_keywords.get(tag, [tag])
    
    async def calculate_realism_score(
        self,
        user_analysis: Dict[str, Any],
        similar_dishes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate realism score based on comparison with typical dishes
        
        Returns:
            {
                'realism_score': 0.85,
                'closest_match': {...},
                'deviations': [...],
                'warnings': [...]
            }
        """
        if not similar_dishes:
            return {
                'realism_score': 0.5,
                'closest_match': None,
                'deviations': [],
                'warnings': ['Не найдено похожих блюд для сравнения']
            }
        
        closest = similar_dishes[0]
        
        # Calculate deviations
        deviations = self._calculate_deviations(user_analysis, closest)
        
        # Calculate realism score
        realism_score = self._calculate_realism(deviations, closest['similarity'])
        
        # Generate warnings
        warnings = self._generate_warnings(deviations, user_analysis, closest)
        
        return {
            'realism_score': realism_score,
            'closest_match': closest,
            'deviations': deviations,
            'warnings': warnings
        }
    
    def _calculate_deviations(
        self,
        user_analysis: Dict[str, Any],
        typical_dish: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Calculate deviations from typical dish"""
        
        deviations = []
        
        # Calories per 100g
        user_cal = user_analysis.get('calories_per_100g', 0)
        typical_cal = typical_dish['calories_per_100g']
        cal_diff = ((user_cal - typical_cal) / typical_cal * 100) if typical_cal > 0 else 0
        
        deviations.append({
            'metric': 'calories',
            'user': round(user_cal, 1),
            'typical': typical_cal,
            'diff_percent': round(cal_diff, 1)
        })
        
        # Protein per 100g
        user_protein = user_analysis.get('protein_g', 0) / (user_analysis.get('weight_grams', 100) / 100)
        typical_protein = typical_dish['protein_per_100g']
        protein_diff = ((user_protein - typical_protein) / typical_protein * 100) if typical_protein > 0 else 0
        
        deviations.append({
            'metric': 'protein',
            'user': round(user_protein, 1),
            'typical': typical_protein,
            'diff_percent': round(protein_diff, 1)
        })
        
        # Fat per 100g
        user_fat = user_analysis.get('fat_g', 0) / (user_analysis.get('weight_grams', 100) / 100)
        typical_fat = typical_dish['fat_per_100g']
        fat_diff = ((user_fat - typical_fat) / typical_fat * 100) if typical_fat > 0 else 0
        
        deviations.append({
            'metric': 'fat',
            'user': round(user_fat, 1),
            'typical': typical_fat,
            'diff_percent': round(fat_diff, 1)
        })
        
        # Carbs per 100g
        user_carbs = user_analysis.get('carbs_g', 0) / (user_analysis.get('weight_grams', 100) / 100)
        typical_carbs = typical_dish['carbs_per_100g']
        carbs_diff = ((user_carbs - typical_carbs) / typical_carbs * 100) if typical_carbs > 0 else 0
        
        deviations.append({
            'metric': 'carbs',
            'user': round(user_carbs, 1),
            'typical': typical_carbs,
            'diff_percent': round(carbs_diff, 1)
        })
        
        return deviations
    
    def _calculate_realism(
        self,
        deviations: List[Dict[str, Any]],
        similarity: Dict[str, float]
    ) -> float:
        """Calculate overall realism score"""
        
        # Check if deviations are within acceptable range
        acceptable_range = 20  # ±20%
        
        within_range = sum(
            1 for dev in deviations
            if abs(dev['diff_percent']) <= acceptable_range
        )
        
        deviation_score = within_range / len(deviations)
        
        # Combine with similarity score
        realism = (deviation_score * 0.6 + similarity['total_score'] * 0.4)
        
        return round(realism, 2)
    
    def _generate_warnings(
        self,
        deviations: List[Dict[str, Any]],
        user_analysis: Dict[str, Any],
        typical_dish: Dict[str, Any]
    ) -> List[str]:
        """Generate warnings based on deviations"""
        
        warnings = []
        
        for dev in deviations:
            metric = dev['metric']
            diff = dev['diff_percent']
            
            if abs(diff) > 30:
                if diff > 0:
                    warnings.append(
                        f"{metric.capitalize()} выше типичного на {abs(diff):.0f}%"
                    )
                else:
                    warnings.append(
                        f"{metric.capitalize()} ниже типичного на {abs(diff):.0f}%"
                    )
        
        return warnings
    
    async def adjust_health_score(
        self,
        user_analysis: Dict[str, Any],
        similar_dishes: List[Dict[str, Any]]
    ) -> Tuple[int, str]:
        """
        Adjust health score based on comparison with typical dishes
        
        Returns:
            (adjusted_score, explanation)
        """
        if not similar_dishes:
            return user_analysis.get('health_score', 5), "Нет данных для сравнения"
        
        original_score = user_analysis.get('health_score', 5)
        closest = similar_dishes[0]
        typical_score = closest['health_score']
        similarity_score = closest['similarity']['total_score']
        
        # If very similar to typical dish, use typical score
        if similarity_score > 0.7:
            # Weighted average: more weight to typical score
            adjusted = int(original_score * 0.3 + typical_score * 0.7)
            explanation = f"Скорректировано на основе сходства с '{closest['dish_name']}' (типичная оценка: {typical_score}/10)"
        
        # If moderately similar, adjust slightly
        elif similarity_score > 0.5:
            adjusted = int(original_score * 0.6 + typical_score * 0.4)
            explanation = f"Частично скорректировано на основе '{closest['dish_name']}'"
        
        # If not very similar, keep original but mention comparison
        else:
            adjusted = original_score
            explanation = f"Оценка сохранена (похоже на '{closest['dish_name']}', но есть отличия)"
        
        # Ensure score is in valid range
        adjusted = max(1, min(10, adjusted))
        
        return adjusted, explanation
    
    def detect_dish_category(self, user_analysis: Dict[str, Any]) -> str:
        """
        Detect dish category based on name and components
        
        Returns:
            Category name (fast_food, healthy, dessert, etc.)
        """
        dish_name = user_analysis.get('dish_name', '').lower()
        components = user_analysis.get('components', [])
        
        # Combine dish name and component names for analysis
        text = dish_name + ' ' + ' '.join(
            comp.get('name', '').lower() for comp in components
        )
        
        # Count matches for each category
        category_scores = {}
        for category, keywords in self.category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                category_scores[category] = score
        
        # Return category with highest score
        if category_scores:
            return max(category_scores.items(), key=lambda x: x[1])[0]
        
        return 'home_cooking'  # Default category
    
    def calculate_dish_context_score(self, components: List[Dict[str, Any]]) -> float:
        """
        Calculate context score based on combination of components
        
        Returns:
            Score from 0 to 1 (higher is healthier)
        """
        if not components:
            return 0.5
        
        # Combine all component names
        text = ' '.join(comp.get('name', '').lower() for comp in components)
        
        # Count unhealthy markers
        unhealthy_count = 0
        for marker_type, keywords in self.unhealthy_markers.items():
            if any(keyword in text for keyword in keywords):
                unhealthy_count += 1
        
        # Calculate score (more unhealthy markers = lower score)
        max_markers = len(self.unhealthy_markers)
        context_score = 1 - (unhealthy_count / max_markers)
        
        return round(context_score, 2)
