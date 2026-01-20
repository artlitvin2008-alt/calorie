"""
AI-powered correction handler using OpenRouter API
"""
import logging
import json
import re
from typing import Dict, Any, Optional, Tuple
import aiohttp
import config

logger = logging.getLogger(__name__)


class AICorrectionHandler:
    """Handles corrections using AI to understand user intent"""
    
    def __init__(self):
        """Initialize AI correction handler"""
        self.api_key = config.OPENROUTER_API_KEY
        self.api_url = config.OPENROUTER_API_URL
        self.model = config.MODEL_NAME
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/food-analyzer-bot",
            "X-Title": "Food Analyzer Bot"
        }
    
    async def apply_correction(
        self,
        correction_text: str,
        current_analysis: Dict[str, Any]
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Apply correction using AI to understand user intent
        
        Args:
            correction_text: User's correction message (e.g., "500г", "нет хлеба")
            current_analysis: Current food analysis
        
        Returns:
            (success, updated_analysis, error_message)
        """
        try:
            # Create prompt for AI
            system_prompt = self._create_correction_system_prompt()
            user_prompt = self._create_correction_user_prompt(correction_text, current_analysis)
            
            # Call API
            result = await self._call_api(system_prompt, user_prompt)
            
            if result is None:
                return False, None, "Не удалось обработать коррекцию через AI"
            
            # Validate result
            if not self._validate_correction_result(result):
                return False, None, "AI вернул некорректные данные"
            
            # Merge with current analysis
            updated_analysis = self._merge_correction(current_analysis, result)
            
            logger.info(f"AI correction applied successfully: {correction_text}")
            
            return True, updated_analysis, None
            
        except Exception as e:
            logger.error(f"Error in AI correction: {e}", exc_info=True)
            return False, None, f"Ошибка при обработке коррекции: {str(e)}"
    
    def _create_correction_system_prompt(self) -> str:
        """Create system prompt for correction"""
        return """ТЫ — ЭКСПЕРТ ПО АНАЛИЗУ КОРРЕКЦИЙ ПОЛЬЗОВАТЕЛЯ.

ТВОЯ ЗАДАЧА: Понять, что хочет изменить пользователь в анализе еды, и вернуть ОБНОВЛЁННЫЙ анализ.

## ТИПЫ КОРРЕКЦИЙ:

### 1. ИЗМЕНЕНИЕ ОБЩЕГО ВЕСА
Примеры: "500г", "вес 300г", "порция 400 грамм"
Действие: Масштабируй ВСЕ компоненты пропорционально новому весу

### 2. УДАЛЕНИЕ КОМПОНЕНТА
Примеры: "нет хлеба", "убери салат", "без соуса"
Действие: Удали указанный компонент из списка

### 3. ДОБАВЛЕНИЕ КОМПОНЕНТА
Примеры: "добавь салат 100г", "есть ещё огурец", "плюс помидор 50г"
Действие: Добавь новый компонент с указанным весом (или 50г по умолчанию)

### 4. ИЗМЕНЕНИЕ КОМПОНЕНТА
Примеры: "это курица, а не свинина", "не говядина, а индейка"
Действие: Замени название компонента, сохранив вес

### 5. ИЗМЕНЕНИЕ ВЕСА КОМПОНЕНТА
Примеры: "говядины 150г", "булочка 80г", "сыра больше - 40г"
Действие: Измени вес указанного компонента

### 6. КОМПЛЕКСНЫЕ КОРРЕКЦИИ
Примеры: "Говядины 150г плюс там есть майонез"
Действие: Примени несколько изменений

## ВАЖНЫЕ ПРАВИЛА:

1. **СОХРАНЯЙ РЕАЛИСТИЧНОСТЬ**: Используй реальные значения калорий и БЖУ
2. **ПЕРЕСЧИТЫВАЙ ИТОГИ**: Всегда пересчитывай totals после изменений
3. **ПРОВЕРЯЙ ЛОГИКУ**: (Белки×4 + Жиры×9 + Углеводы×4) ≈ Калории
4. **МАСШТАБИРОВАНИЕ**: При изменении общего веса масштабируй ВСЕ компоненты пропорционально

## ФОРМАТ ОТВЕТА:

Верни ПОЛНЫЙ обновлённый анализ в JSON формате:

```json
{
  "components": [
    {
      "name": "название",
      "weight_g": число,
      "calories": число,
      "protein_g": число,
      "fat_g": число,
      "carbs_g": число,
      "confidence": 0.0-1.0
    }
  ],
  "dish_name": "название блюда",
  "weight_grams": общий_вес,
  "calories_total": сумма_калорий,
  "calories_per_100g": калории_на_100г,
  "protein_g": сумма_белков,
  "fat_g": сумма_жиров,
  "carbs_g": сумма_углеводов,
  "health_score": 1-10,
  "correction_applied": "описание что изменено"
}
```

ВАЖНО: Верни ТОЛЬКО JSON, без дополнительного текста!"""
    
    def _create_correction_user_prompt(
        self,
        correction_text: str,
        current_analysis: Dict[str, Any]
    ) -> str:
        """Create user prompt with current analysis and correction"""
        
        # Format current analysis
        components_text = "\n".join([
            f"- {comp['name']}: {comp['weight_g']}г, "
            f"{comp['calories']} ккал, "
            f"Б:{comp['protein_g']}г Ж:{comp['fat_g']}г У:{comp['carbs_g']}г"
            for comp in current_analysis.get('components', [])
        ])
        
        prompt = f"""ТЕКУЩИЙ АНАЛИЗ:

Блюдо: {current_analysis.get('dish_name', 'Неизвестно')}
Общий вес: {current_analysis.get('weight_grams', 0)}г
Калории: {current_analysis.get('calories_total', 0)} ккал
БЖУ: Б:{current_analysis.get('protein_g', 0)}г Ж:{current_analysis.get('fat_g', 0)}г У:{current_analysis.get('carbs_g', 0)}г

Компоненты:
{components_text}

──────────────────────────────

КОРРЕКЦИЯ ПОЛЬЗОВАТЕЛЯ: "{correction_text}"

──────────────────────────────

Верни ОБНОВЛЁННЫЙ анализ с учётом коррекции в JSON формате."""
        
        return prompt
    
    async def _call_api(self, system_prompt: str, user_prompt: str) -> Optional[Dict[str, Any]]:
        """Call OpenRouter API for correction"""
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            "temperature": 0.1,
            "max_tokens": 2000
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"OpenRouter API error: {response.status} - {error_text}")
                        return None
                    
                    result = await response.json()
                    
                    if 'choices' not in result or len(result['choices']) == 0:
                        logger.error("No response from API")
                        return None
                    
                    content = result['choices'][0]['message']['content']
                    logger.info(f"AI correction response: {content[:200]}...")
                    
                    # Parse JSON
                    parsed_data = self._parse_json_response(content)
                    
                    return parsed_data
                    
        except aiohttp.ClientError as e:
            logger.error(f"Network error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return None
    
    def _parse_json_response(self, content: str) -> Optional[Dict[str, Any]]:
        """Parse JSON from API response"""
        # Remove markdown blocks
        content = content.replace('```json', '').replace('```', '')
        
        # Find JSON in response
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        
        if json_start == -1 or json_end == 0:
            logger.error("JSON not found in response")
            return None
        
        json_str = content[json_start:json_end]
        
        # Try to parse JSON
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            logger.error(f"Problematic JSON: {json_str[:500]}...")
            
            # Try to clean JSON
            json_str = re.sub(r'//.*?\n', '\n', json_str)
            json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
            json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
            
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e2:
                logger.error(f"Failed to parse JSON even after cleaning: {e2}")
                return None
    
    def _validate_correction_result(self, result: Dict[str, Any]) -> bool:
        """Validate correction result from AI"""
        required_fields = [
            'components', 'dish_name', 'weight_grams', 'calories_total',
            'protein_g', 'fat_g', 'carbs_g'
        ]
        
        for field in required_fields:
            if field not in result:
                logger.error(f"Missing required field: {field}")
                return False
        
        if not isinstance(result['components'], list):
            logger.error("Components is not a list")
            return False
        
        if len(result['components']) == 0:
            logger.error("No components in result")
            return False
        
        return True
    
    def _merge_correction(
        self,
        original: Dict[str, Any],
        corrected: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge corrected data with original analysis"""
        
        # Start with original
        merged = original.copy()
        
        # Ensure all numeric values are proper types
        for comp in corrected['components']:
            comp['weight_g'] = int(round(comp.get('weight_g', 0)))
            comp['calories'] = int(round(comp.get('calories', 0)))
            comp['protein_g'] = round(comp.get('protein_g', 0), 1)
            comp['fat_g'] = round(comp.get('fat_g', 0), 1)
            comp['carbs_g'] = round(comp.get('carbs_g', 0), 1)
            comp['confidence'] = float(comp.get('confidence', 0.7))
        
        # Update with corrected values
        merged.update({
            'components': corrected['components'],
            'dish_name': corrected.get('dish_name', original.get('dish_name')),
            'weight_grams': int(round(corrected['weight_grams'])),
            'calories_total': int(round(corrected['calories_total'])),
            'calories_per_100g': round(corrected.get('calories_per_100g', 
                (corrected['calories_total'] / corrected['weight_grams'] * 100) if corrected['weight_grams'] > 0 else 0
            ), 1),
            'protein_g': round(corrected['protein_g'], 1),
            'fat_g': round(corrected['fat_g'], 1),
            'carbs_g': round(corrected['carbs_g'], 1),
            'health_score': int(round(corrected.get('health_score', original.get('health_score', 5))))
        })
        
        # Add correction metadata
        if 'correction_applied' in corrected:
            merged['correction_applied'] = corrected['correction_applied']
        
        # Preserve other fields from original
        for key in ['detailed_analysis', 'recommendations', 'portion_advice', 'warnings']:
            if key in original and key not in merged:
                merged[key] = original[key]
        
        return merged
