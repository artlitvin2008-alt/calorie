"""
Correction parser for user text corrections
Will be fully implemented on Day 7-8
"""
import logging
from typing import Dict, Any, List, Optional, Tuple
from utils.validators import CorrectionValidator

logger = logging.getLogger(__name__)


class CorrectionParser:
    """Parses user corrections to food analysis"""
    
    def __init__(self):
        """Initialize correction parser"""
        self.validator = CorrectionValidator()
    
    def parse_correction(
        self,
        correction_text: str,
        current_analysis: Dict[str, Any]
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Parse user correction text
        
        Args:
            correction_text: User's correction message
            current_analysis: Current analysis data
        
        Returns:
            (success, updated_analysis, error_message)
        
        Example corrections:
            "нет хлеба" -> remove bread component
            "добавь салат 100г" -> add salad 100g
            "это курица, а не свинина" -> modify component
        """
        # Validate correction
        is_valid, error = self.validator.validate_correction(correction_text)
        if not is_valid:
            return False, None, error
        
        # Detect correction type
        action_type, details = self.validator.detect_correction_type(correction_text)
        
        if action_type is None:
            return False, None, "Не удалось распознать коррекцию"
        
        # Apply correction
        try:
            if action_type == 'remove':
                updated = self._apply_remove(current_analysis, details)
            elif action_type == 'add':
                updated = self._apply_add(current_analysis, details)
            elif action_type == 'modify':
                updated = self._apply_modify(current_analysis, details)
            elif action_type == 'change_weight':
                updated = self._apply_weight_change(current_analysis, details)
            else:
                return False, None, f"Неизвестный тип коррекции: {action_type}"
            
            return True, updated, None
            
        except Exception as e:
            logger.error(f"Error applying correction: {e}", exc_info=True)
            return False, None, f"Ошибка при применении коррекции: {str(e)}"
    
    def _apply_remove(
        self,
        analysis: Dict[str, Any],
        details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Remove component from analysis
        
        Args:
            analysis: Current analysis
            details: Correction details with 'item' key
        
        Returns:
            Updated analysis
        """
        item_to_remove = details['item'].lower()
        components = analysis.get('components', [])
        
        # Find and remove matching component
        updated_components = []
        removed = False
        
        for comp in components:
            comp_name = comp.get('name', '').lower()
            if item_to_remove not in comp_name and comp_name not in item_to_remove:
                updated_components.append(comp)
            else:
                removed = True
                logger.info(f"Removed component: {comp.get('name')}")
        
        if not removed:
            logger.warning(f"Component not found for removal: {item_to_remove}")
        
        # Recalculate totals
        analysis['components'] = updated_components
        return self._recalculate_totals(analysis)
    
    def _apply_add(
        self,
        analysis: Dict[str, Any],
        details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Add component to analysis
        
        Args:
            analysis: Current analysis
            details: Correction details with 'item' and optional 'weight' keys
        
        Returns:
            Updated analysis
        """
        item_name = details['item']
        weight = details.get('weight', 100)  # Default 100g
        
        # Estimate calories (simplified - will improve on Day 7)
        estimated_calories = int(weight * 2)  # Rough estimate: 200 kcal/100g
        
        new_component = {
            'name': item_name.capitalize(),
            'weight_g': weight,
            'calories': estimated_calories,
            'protein_g': int(estimated_calories * 0.15 / 4),  # ~15% protein
            'fat_g': int(estimated_calories * 0.30 / 9),      # ~30% fat
            'carbs_g': int(estimated_calories * 0.55 / 4),    # ~55% carbs
            'confidence': 0.5  # Lower confidence for user-added items
        }
        
        components = analysis.get('components', [])
        components.append(new_component)
        analysis['components'] = components
        
        logger.info(f"Added component: {item_name} ({weight}g)")
        
        # Recalculate totals
        return self._recalculate_totals(analysis)
    
    def _apply_modify(
        self,
        analysis: Dict[str, Any],
        details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Modify component in analysis
        
        Args:
            analysis: Current analysis
            details: Correction details with 'old_item' and 'new_item' keys
        
        Returns:
            Updated analysis
        """
        old_item = details['old_item'].lower()
        new_item = details['new_item']
        
        components = analysis.get('components', [])
        modified = False
        
        for comp in components:
            comp_name = comp.get('name', '').lower()
            if old_item in comp_name or comp_name in old_item:
                # Keep weight and calories, just change name
                comp['name'] = new_item.capitalize()
                comp['confidence'] = 0.7  # Moderate confidence for modified items
                modified = True
                logger.info(f"Modified component: {comp_name} -> {new_item}")
                break
        
        if not modified:
            logger.warning(f"Component not found for modification: {old_item}")
        
        analysis['components'] = components
        return analysis
    
    def _apply_weight_change(
        self,
        analysis: Dict[str, Any],
        details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Change total weight of the dish (scales all components proportionally)
        
        Args:
            analysis: Current analysis
            details: Correction details with 'weight' key (new total weight in grams)
        
        Returns:
            Updated analysis
        """
        new_total_weight = details['weight']
        current_total_weight = analysis.get('weight_grams', 0)
        
        if current_total_weight == 0:
            logger.error("Cannot change weight: current weight is 0")
            return analysis
        
        # Calculate scaling factor
        scale_factor = new_total_weight / current_total_weight
        
        logger.info(f"Changing total weight: {current_total_weight}g -> {new_total_weight}g (scale: {scale_factor:.2f})")
        
        # Scale all components
        components = analysis.get('components', [])
        for comp in components:
            comp['weight_g'] = int(comp.get('weight_g', 0) * scale_factor)
            comp['calories'] = int(comp.get('calories', 0) * scale_factor)
            comp['protein_g'] = round(comp.get('protein_g', 0) * scale_factor, 1)
            comp['fat_g'] = round(comp.get('fat_g', 0) * scale_factor, 1)
            comp['carbs_g'] = round(comp.get('carbs_g', 0) * scale_factor, 1)
        
        analysis['components'] = components
        
        # Recalculate totals
        return self._recalculate_totals(analysis)
    
    def _recalculate_totals(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recalculate total values from components
        
        Args:
            analysis: Analysis with components
        
        Returns:
            Analysis with updated totals
        """
        components = analysis.get('components', [])
        
        total_weight = sum(c.get('weight_g', 0) for c in components)
        total_calories = sum(c.get('calories', 0) for c in components)
        total_protein = sum(c.get('protein_g', 0) for c in components)
        total_fat = sum(c.get('fat_g', 0) for c in components)
        total_carbs = sum(c.get('carbs_g', 0) for c in components)
        
        calories_per_100g = (total_calories / total_weight * 100) if total_weight > 0 else 0
        
        analysis.update({
            'weight_grams': total_weight,
            'calories_total': total_calories,
            'calories_per_100g': round(calories_per_100g, 1),
            'protein_g': total_protein,
            'fat_g': total_fat,
            'carbs_g': total_carbs
        })
        
        return analysis
    
    def get_correction_examples(self) -> str:
        """Get examples of valid corrections"""
        return """Примеры коррекций:

**Убрать компонент:**
• "нет хлеба"
• "убери салат"
• "без соуса"

**Добавить компонент:**
• "добавь салат 100г"
• "есть ещё хлеб 50г"
• "плюс огурец"

**Изменить компонент:**
• "это курица, а не свинина"
• "не говядина, а индейка"

**Изменить общий вес:**
• "500г" (изменить общий вес на 500г)
• "вес 300г"
"""
