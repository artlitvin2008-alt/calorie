"""
Валидатор результатов анализа еды
"""
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class FoodAnalysisValidator:
    """Класс для валидации результатов анализа еды"""
    
    # Минимальная калорийность для разных типов приёмов пищи
    MIN_CALORIES = {
        'breakfast': 200,
        'lunch': 400,
        'dinner': 300,
        'snack': 100
    }
    
    # Реалистичные соотношения БЖУ (в процентах от калорий)
    REALISTIC_RATIOS = {
        'protein': (10, 35),  # 10-35% от калорий
        'fat': (20, 40),      # 20-40% от калорий
        'carbs': (40, 65)     # 40-65% от калорий
    }
    
    def __init__(self):
        self.warnings = []
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Валидирует результаты анализа
        
        Args:
            data: Словарь с результатами анализа
            
        Returns:
            Обновлённый словарь с добавленными предупреждениями
        """
        self.warnings = []
        
        # Проверка 1: Минимальная калорийность
        self._check_minimum_calories(data)
        
        # Проверка 2: Соответствие БЖУ и калорий
        self._check_macros_consistency(data)
        
        # Проверка 3: Плотность калорий
        self._check_calorie_density(data)
        
        # Проверка 4: Реалистичность соотношений БЖУ
        self._check_macro_ratios(data)
        
        # Проверка 5: Наличие компонентов
        self._check_components(data)
        
        # Добавляем предупреждения к существующим
        if 'warnings' not in data:
            data['warnings'] = []
        
        data['warnings'].extend(self.warnings)
        
        # Удаляем дубликаты
        data['warnings'] = list(set(data['warnings']))
        
        logger.info(f"Валидация завершена. Найдено предупреждений: {len(self.warnings)}")
        
        return data
    
    def _check_minimum_calories(self, data: Dict[str, Any]):
        """Проверяет минимальную калорийность"""
        calories = data.get('calories_total', 0)
        
        # Предполагаем, что это обед (можно улучшить определением времени суток)
        min_calories = self.MIN_CALORIES['lunch']
        
        if calories < min_calories:
            self.warnings.append(
                f"⚠️ Слишком низкая калорийность ({calories} ккал). "
                f"Для полноценного приёма пищи ожидается минимум {min_calories} ккал. "
                f"Возможно, пропущены компоненты (хлеб, соусы, напитки)."
            )
    
    def _check_macros_consistency(self, data: Dict[str, Any]):
        """Проверяет соответствие БЖУ и общей калорийности"""
        total_calories = data.get('calories_total', 0)
        protein_g = data.get('protein_g', 0)
        fat_g = data.get('fat_g', 0)
        carbs_g = data.get('carbs_g', 0)
        
        # Рассчитываем калории из БЖУ
        protein_calories = protein_g * 4
        fat_calories = fat_g * 9
        carbs_calories = carbs_g * 4
        
        calculated_calories = protein_calories + fat_calories + carbs_calories
        
        # Допустимое отклонение 15%
        tolerance = total_calories * 0.15
        
        if abs(total_calories - calculated_calories) > tolerance:
            self.warnings.append(
                f"⚠️ Несоответствие в расчётах: заявлено {total_calories} ккал, "
                f"но по БЖУ получается {calculated_calories:.0f} ккал. "
                f"Разница: {abs(total_calories - calculated_calories):.0f} ккал."
            )
    
    def _check_calorie_density(self, data: Dict[str, Any]):
        """Проверяет плотность калорий"""
        calories_per_100g = data.get('calories_per_100g', 0)
        
        if calories_per_100g < 50:
            self.warnings.append(
                f"⚠️ Нереально низкая плотность калорий: {calories_per_100g:.0f} ккал/100г. "
                f"Возможно, неправильно оценён вес порции или пропущены калорийные компоненты."
            )
        elif calories_per_100g > 400:
            self.warnings.append(
                f"⚠️ Очень высокая плотность калорий: {calories_per_100g:.0f} ккал/100г. "
                f"Блюдо содержит много жиров (жареное, с соусами, сыром)."
            )
    
    def _check_macro_ratios(self, data: Dict[str, Any]):
        """Проверяет реалистичность соотношений БЖУ"""
        total_calories = data.get('calories_total', 0)
        
        if total_calories == 0:
            return
        
        protein_g = data.get('protein_g', 0)
        fat_g = data.get('fat_g', 0)
        carbs_g = data.get('carbs_g', 0)
        
        # Процент калорий от каждого макронутриента
        protein_percent = (protein_g * 4 / total_calories) * 100
        fat_percent = (fat_g * 9 / total_calories) * 100
        carbs_percent = (carbs_g * 4 / total_calories) * 100
        
        # Проверяем белки
        if protein_percent < self.REALISTIC_RATIOS['protein'][0]:
            self.warnings.append(
                f"⚠️ Слишком мало белка: {protein_percent:.1f}% от калорий "
                f"(норма {self.REALISTIC_RATIOS['protein'][0]}-{self.REALISTIC_RATIOS['protein'][1]}%)."
            )
        elif protein_percent > self.REALISTIC_RATIOS['protein'][1]:
            self.warnings.append(
                f"⚠️ Очень много белка: {protein_percent:.1f}% от калорий "
                f"(норма {self.REALISTIC_RATIOS['protein'][0]}-{self.REALISTIC_RATIOS['protein'][1]}%)."
            )
        
        # Проверяем жиры
        if fat_percent < self.REALISTIC_RATIOS['fat'][0]:
            self.warnings.append(
                f"⚠️ Слишком мало жиров: {fat_percent:.1f}% от калорий "
                f"(норма {self.REALISTIC_RATIOS['fat'][0]}-{self.REALISTIC_RATIOS['fat'][1]}%)."
            )
        elif fat_percent > self.REALISTIC_RATIOS['fat'][1]:
            self.warnings.append(
                f"⚠️ Очень много жиров: {fat_percent:.1f}% от калорий "
                f"(норма {self.REALISTIC_RATIOS['fat'][0]}-{self.REALISTIC_RATIOS['fat'][1]}%). "
                f"Возможно, блюдо жареное или с жирными соусами."
            )
        
        # Проверяем углеводы
        if carbs_percent < self.REALISTIC_RATIOS['carbs'][0]:
            self.warnings.append(
                f"⚠️ Слишком мало углеводов: {carbs_percent:.1f}% от калорий "
                f"(норма {self.REALISTIC_RATIOS['carbs'][0]}-{self.REALISTIC_RATIOS['carbs'][1]}%)."
            )
        elif carbs_percent > self.REALISTIC_RATIOS['carbs'][1]:
            self.warnings.append(
                f"⚠️ Очень много углеводов: {carbs_percent:.1f}% от калорий "
                f"(норма {self.REALISTIC_RATIOS['carbs'][0]}-{self.REALISTIC_RATIOS['carbs'][1]}%)."
            )
    
    def _check_components(self, data: Dict[str, Any]):
        """Проверяет наличие компонентов"""
        components = data.get('components', [])
        
        if not components:
            self.warnings.append(
                "⚠️ Не найдены отдельные компоненты блюда. "
                "Возможно, анализ неполный."
            )
            return
        
        # Проверяем, есть ли хлеб в компонентах
        has_bread = any(
            'хлеб' in comp.get('name', '').lower() or 
            'лепешка' in comp.get('name', '').lower() or
            'булка' in comp.get('name', '').lower()
            for comp in components
        )
        
        # Если калорийность высокая, но хлеба нет - возможно пропущен
        if not has_bread and data.get('calories_total', 0) > 600:
            self.warnings.append(
                "⚠️ Возможно, пропущен хлеб или другие мучные изделия. "
                "Проверьте края тарелки и стол."
            )
