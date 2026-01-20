"""
Клиент для работы с OpenRouter API
"""
import base64
import json
import logging
from io import BytesIO
from typing import Optional, Dict, Any

import aiohttp
from PIL import Image

from config import (
    OPENROUTER_API_KEY,
    OPENROUTER_API_URL,
    MODEL_NAME,
    SYSTEM_PROMPT,
    MAX_PHOTO_SIZE_MB
)
from validator import FoodAnalysisValidator

logger = logging.getLogger(__name__)


class OpenRouterClient:
    """Клиент для взаимодействия с OpenRouter API"""
    
    def __init__(self):
        self.api_key = OPENROUTER_API_KEY
        self.api_url = OPENROUTER_API_URL
        self.model = MODEL_NAME
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/food-analyzer-bot",
            "X-Title": "Food Analyzer Bot"
        }
        self.validator = FoodAnalysisValidator()
    
    async def compress_image_if_needed(self, image_bytes: bytes) -> bytes:
        """
        Сжимает изображение, если оно превышает максимальный размер
        
        Args:
            image_bytes: Байты изображения
            
        Returns:
            Сжатые байты изображения
        """
        size_mb = len(image_bytes) / (1024 * 1024)
        
        if size_mb <= MAX_PHOTO_SIZE_MB:
            return image_bytes
        
        logger.info(f"Сжатие изображения: {size_mb:.2f} MB -> целевой размер: {MAX_PHOTO_SIZE_MB} MB")
        
        # Открываем изображение
        image = Image.open(BytesIO(image_bytes))
        
        # Конвертируем в RGB если необходимо
        if image.mode in ('RGBA', 'LA', 'P'):
            image = image.convert('RGB')
        
        # Уменьшаем качество постепенно
        quality = 85
        while quality > 20:
            output = BytesIO()
            image.save(output, format='JPEG', quality=quality, optimize=True)
            compressed_bytes = output.getvalue()
            
            new_size_mb = len(compressed_bytes) / (1024 * 1024)
            if new_size_mb <= MAX_PHOTO_SIZE_MB:
                logger.info(f"Изображение сжато до {new_size_mb:.2f} MB с качеством {quality}")
                return compressed_bytes
            
            quality -= 10
        
        # Если все еще слишком большое, уменьшаем разрешение
        max_dimension = 1920
        if max(image.size) > max_dimension:
            ratio = max_dimension / max(image.size)
            new_size = tuple(int(dim * ratio) for dim in image.size)
            image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            output = BytesIO()
            image.save(output, format='JPEG', quality=85, optimize=True)
            compressed_bytes = output.getvalue()
            
            logger.info(f"Изображение уменьшено до {new_size} и сжато до {len(compressed_bytes) / (1024 * 1024):.2f} MB")
            return compressed_bytes
        
        return image_bytes
    
    def image_to_base64(self, image_bytes: bytes) -> str:
        """
        Конвертирует изображение в base64
        
        Args:
            image_bytes: Байты изображения
            
        Returns:
            Base64 строка
        """
        return base64.b64encode(image_bytes).decode('utf-8')
    
    async def analyze_food_image(self, image_bytes: bytes) -> Optional[Dict[str, Any]]:
        """
        Анализирует изображение еды через OpenRouter API
        
        Args:
            image_bytes: Байты изображения
            
        Returns:
            Словарь с результатами анализа или None в случае ошибки
        """
        try:
            # Сжимаем изображение если необходимо
            image_bytes = await self.compress_image_if_needed(image_bytes)
            
            # Конвертируем в base64
            base64_image = self.image_to_base64(image_bytes)
            
            # Детальный промпт для пользователя
            user_prompt = """ПРОАНАЛИЗИРУЙ ЭТУ ФОТОГРАФИЮ ЕДЫ МАКСИМАЛЬНО ТОЧНО:

ОБЯЗАТЕЛЬНЫЕ ТРЕБОВАНИЯ:
1. Найди ВСЕ компоненты на фото (включая хлеб, соусы, напитки, гарниры)
2. Оцени вес КАЖДОГО компонента отдельно (используй вилку ~17см, ложку ~15см для масштаба)
3. Для КАЖДОГО компонента рассчитай калорийность, белки, жиры, углеводы
4. Используй ТОЧНЫЕ названия (не "суп", а "мясной суп с капустой")
5. Если видишь хлеб — ОБЯЗАТЕЛЬНО включи в расчёт!

ВАЖНО: Верни ответ СТРОГО в JSON формате без дополнительного текста."""
            
            # Формируем запрос
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": user_prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "temperature": 0.1,  # Минимальная креативность для точности
                "max_tokens": 2000
            }
            
            # Отправляем запрос
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"OpenRouter API error: {response.status} - {error_text}")
                        return None
                    
                    result = await response.json()
                    
                    # Извлекаем текст ответа
                    if 'choices' not in result or len(result['choices']) == 0:
                        logger.error("Нет ответа от API")
                        return None
                    
                    content = result['choices'][0]['message']['content']
                    logger.info(f"Получен ответ от API: {content[:200]}...")
                    
                    # Парсим JSON из ответа
                    # Убираем markdown блоки если есть
                    content = content.replace('```json', '').replace('```', '')
                    
                    # Ищем JSON в ответе
                    json_start = content.find('{')
                    json_end = content.rfind('}') + 1
                    
                    if json_start == -1 or json_end == 0:
                        logger.error("JSON не найден в ответе")
                        return None
                    
                    json_str = content[json_start:json_end]
                    
                    # Пытаемся распарсить JSON
                    try:
                        parsed_data = json.loads(json_str)
                    except json.JSONDecodeError as e:
                        logger.error(f"Ошибка парсинга JSON: {e}")
                        logger.error(f"Проблемный JSON: {json_str[:500]}...")
                        
                        # Пытаемся очистить JSON от комментариев и лишних символов
                        import re
                        # Удаляем комментарии
                        json_str = re.sub(r'//.*?\n', '\n', json_str)
                        json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
                        # Удаляем trailing commas
                        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
                        
                        try:
                            parsed_data = json.loads(json_str)
                            logger.info("JSON успешно распарсен после очистки")
                        except json.JSONDecodeError as e2:
                            logger.error(f"Не удалось распарсить JSON даже после очистки: {e2}")
                            return None
                    
                    # Валидация обязательных полей
                    required_fields = [
                        'dish_name', 'weight_grams', 'calories_per_100g',
                        'calories_total', 'protein_g', 'fat_g', 'carbs_g',
                        'health_score', 'detailed_analysis', 'recommendations',
                        'portion_advice'
                    ]
                    
                    for field in required_fields:
                        if field not in parsed_data:
                            logger.warning(f"Отсутствует обязательное поле: {field}, добавляем значение по умолчанию")
                            # Добавляем значения по умолчанию для отсутствующих полей
                            if field == 'warnings':
                                parsed_data[field] = []
                            elif field == 'components':
                                parsed_data[field] = []
                            elif field in ['detailed_analysis', 'recommendations', 'portion_advice']:
                                parsed_data[field] = "Информация недоступна"
                            else:
                                parsed_data[field] = 0
                    
                    # Валидируем результат
                    validated_data = self.validator.validate(parsed_data)
                    
                    return validated_data
                    
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON: {e}")
            return None
        except aiohttp.ClientError as e:
            logger.error(f"Ошибка сети: {e}")
            return None
        except Exception as e:
            logger.error(f"Неожиданная ошибка: {e}", exc_info=True)
            return None
