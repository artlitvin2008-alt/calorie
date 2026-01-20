"""
Photo analyzer using OpenRouter API
"""
import logging
import base64
import json
import re
from io import BytesIO
from typing import Dict, Any, Optional

import aiohttp
from PIL import Image

import config
from utils.validators import FoodAnalysisValidator

logger = logging.getLogger(__name__)


class PhotoAnalyzer:
    """Analyzes food photos using AI"""
    
    def __init__(self, use_mock: bool = False):
        """
        Initialize photo analyzer
        
        Args:
            use_mock: If True, use mock data instead of real API
        """
        self.use_mock = use_mock or config.USE_MOCK_API
        self.api_key = config.OPENROUTER_API_KEY
        self.api_url = config.OPENROUTER_API_URL
        self.model = config.MODEL_NAME
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/food-analyzer-bot",
            "X-Title": "Food Analyzer Bot"
        }
        self.validator = FoodAnalysisValidator()
    
    async def analyze_photo(self, photo_bytes: bytes) -> Optional[Dict[str, Any]]:
        """
        Analyze food photo and extract components
        
        Args:
            photo_bytes: Photo data as bytes
        
        Returns:
            Analysis result with components, or None on error
        """
        if self.use_mock:
            logger.info("Using mock analysis data")
            return self._get_mock_analysis()
        
        try:
            # Compress image if needed
            photo_bytes = await self._compress_image_if_needed(photo_bytes)
            
            # Convert to base64
            base64_image = self._image_to_base64(photo_bytes)
            
            # Create prompt
            user_prompt = self._create_analysis_prompt()
            
            # Make API request
            result = await self._call_api(base64_image, user_prompt)
            
            if result is None:
                logger.error("API returned None")
                return None
            
            # Validate result
            is_valid, warnings = self.validator.validate_analysis(result)
            if warnings:
                logger.warning(f"Validation warnings: {warnings}")
                result['warnings'] = warnings
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing photo: {e}", exc_info=True)
            return None
    
    async def _compress_image_if_needed(self, image_bytes: bytes) -> bytes:
        """Compress image if it exceeds max size"""
        size_mb = len(image_bytes) / (1024 * 1024)
        max_size = config.MAX_PHOTO_SIZE_MB
        
        if size_mb <= max_size:
            return image_bytes
        
        logger.info(f"Compressing image: {size_mb:.2f} MB -> target: {max_size} MB")
        
        # Open image
        image = Image.open(BytesIO(image_bytes))
        
        # Convert to RGB if needed
        if image.mode in ('RGBA', 'LA', 'P'):
            image = image.convert('RGB')
        
        # Reduce quality gradually
        quality = 85
        while quality > 20:
            output = BytesIO()
            image.save(output, format='JPEG', quality=quality, optimize=True)
            compressed_bytes = output.getvalue()
            
            new_size_mb = len(compressed_bytes) / (1024 * 1024)
            if new_size_mb <= max_size:
                logger.info(f"Image compressed to {new_size_mb:.2f} MB with quality {quality}")
                return compressed_bytes
            
            quality -= 10
        
        # If still too large, reduce resolution
        max_dimension = 1920
        if max(image.size) > max_dimension:
            ratio = max_dimension / max(image.size)
            new_size = tuple(int(dim * ratio) for dim in image.size)
            image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            output = BytesIO()
            image.save(output, format='JPEG', quality=85, optimize=True)
            compressed_bytes = output.getvalue()
            
            logger.info(f"Image resized to {new_size} and compressed to {len(compressed_bytes) / (1024 * 1024):.2f} MB")
            return compressed_bytes
        
        return image_bytes
    
    def _image_to_base64(self, image_bytes: bytes) -> str:
        """Convert image bytes to base64 string"""
        return base64.b64encode(image_bytes).decode('utf-8')
    
    def _create_analysis_prompt(self) -> str:
        """Create analysis prompt for API"""
        return """ПРОАНАЛИЗИРУЙ ЭТУ ФОТОГРАФИЮ ЕДЫ МАКСИМАЛЬНО ТОЧНО:

ОБЯЗАТЕЛЬНЫЕ ТРЕБОВАНИЯ:
1. Найди ВСЕ компоненты на фото (включая хлеб, соусы, напитки, гарниры)
2. Оцени вес КАЖДОГО компонента отдельно (используй вилку ~17см, ложку ~15см для масштаба)
3. Для КАЖДОГО компонента рассчитай калорийность, белки, жиры, углеводы
4. Используй ТОЧНЫЕ названия (не "суп", а "мясной суп с капустой")
5. Если видишь хлеб — ОБЯЗАТЕЛЬНО включи в расчёт!

ВАЖНО: Верни ответ СТРОГО в JSON формате без дополнительного текста."""
    
    async def _call_api(self, base64_image: str, user_prompt: str) -> Optional[Dict[str, Any]]:
        """Make API call to OpenRouter"""
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": config.SYSTEM_PROMPT
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
            "temperature": 0.1,
            "max_tokens": 2000
        }
        
        try:
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
                    
                    # Extract response
                    if 'choices' not in result or len(result['choices']) == 0:
                        logger.error("No response from API")
                        return None
                    
                    content = result['choices'][0]['message']['content']
                    logger.info(f"API response received: {content[:200]}...")
                    
                    # Parse JSON from response
                    parsed_data = self._parse_json_response(content)
                    
                    if parsed_data is None:
                        return None
                    
                    # Ensure required fields
                    parsed_data = self._ensure_required_fields(parsed_data)
                    
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
            # Remove comments
            json_str = re.sub(r'//.*?\n', '\n', json_str)
            json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
            # Remove trailing commas
            json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
            
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e2:
                logger.error(f"Failed to parse JSON even after cleaning: {e2}")
                return None
    
    def _ensure_required_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure all required fields are present"""
        required_fields = {
            'dish_name': 'Неизвестное блюдо',
            'weight_grams': 0,
            'calories_per_100g': 0,
            'calories_total': 0,
            'protein_g': 0,
            'fat_g': 0,
            'carbs_g': 0,
            'health_score': 5,
            'detailed_analysis': 'Информация недоступна',
            'recommendations': 'Информация недоступна',
            'portion_advice': 'Информация недоступна',
            'components': [],
            'warnings': []
        }
        
        for field, default_value in required_fields.items():
            if field not in data or data[field] is None:
                logger.warning(f"Missing field: {field}, using default")
                data[field] = default_value
        
        return data
    
    def _get_mock_analysis(self) -> Dict[str, Any]:
        """Get mock analysis for testing"""
        return {
            "components": [
                {
                    "name": "Пельмени",
                    "weight_g": 250,
                    "calories": 625,
                    "protein_g": 30,
                    "fat_g": 25,
                    "carbs_g": 70,
                    "confidence": 0.85
                },
                {
                    "name": "Сметана",
                    "weight_g": 30,
                    "calories": 60,
                    "protein_g": 2,
                    "fat_g": 3,
                    "carbs_g": 2,
                    "confidence": 0.90
                }
            ],
            "dish_name": "Пельмени со сметаной",
            "weight_grams": 280,
            "calories_total": 685,
            "calories_per_100g": 245,
            "protein_g": 32,
            "fat_g": 28,
            "carbs_g": 72,
            "health_score": 5,
            "detailed_analysis": "Блюдо содержит пельмени (250г) и сметану (30г). Высокое содержание жиров и углеводов.",
            "recommendations": "• Уменьши порцию на 20-30%\n• Замени сметану на греческий йогурт\n• Добавь овощной салат",
            "portion_advice": "Порция большая (280г). Попробуй уменьшить до 200г"
        }

