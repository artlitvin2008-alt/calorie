"""
Video analyzer - analyzes frames with audio hypothesis context
"""

import base64
import json
import re
import logging
import aiohttp
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class VideoAnalyzer:
    """Analyzes video frames using audio hypothesis as context"""
    
    def __init__(self, config):
        """
        Initialize video analyzer
        
        Args:
            config: Configuration object with API keys
        """
        self.config = config
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "google/gemini-2.0-flash-exp:free"  # Alternative free model
    
    async def analyze_frames(self, frames: List[bytes], audio_hypothesis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze frames using audio hypothesis as priority context
        
        Instead of asking "What's in the photo?", we ask:
        "User said it's 'mashed potatoes, ~500g, bread'.
        1. Confirm if it's really mashed potatoes.
        2. Estimate weight of potatoes in photo.
        3. Find bread if present.
        4. Find everything else in the photo."
        
        Args:
            frames: List of frame images as bytes
            audio_hypothesis: Structured hypothesis from audio
        
        Returns:
            List of analysis results for each frame
        """
        system_prompt = self._build_system_prompt(audio_hypothesis)
        
        results = []
        for i, frame in enumerate(frames):
            frame_result = await self._analyze_single_frame(
                frame, 
                system_prompt, 
                i, 
                len(frames),
                audio_hypothesis
            )
            if frame_result:
                results.append(frame_result)
        
        return results
    
    def _build_system_prompt(self, hypothesis: Dict[str, Any]) -> str:
        """
        Build prompt tailored to verify hypothesis
        
        Args:
            hypothesis: Audio hypothesis dict
        
        Returns:
            System prompt string
        """
        transcription = hypothesis.get('transcription', '')
        hyp = hypothesis.get('hypothesis', {})
        
        primary_dish = hyp.get('primary_dish')
        secondary_items = hyp.get('secondary_items', [])
        
        if not primary_dish and not transcription:
            # No audio context - use generic prompt
            return """ТЫ — ЭКСПЕРТНЫЙ АНАЛИЗАТОР ЕДЫ.

ЗАДАЧА: Проанализируй фото еды максимально точно.

ТРЕБОВАНИЯ:
1. Определи ВСЕ компоненты на фото
2. Оцени вес КАЖДОГО компонента
3. Рассчитай калории, белки, жиры, углеводы
4. Используй точные названия блюд

Верни результат в JSON формате."""
        
        # Build hypothesis-aware prompt
        prompt = f"""ТЫ — ПОМОЩНИК, ПРОВЕРЯЮЩИЙ ГИПОТЕЗУ ПОЛЬЗОВАТЕЛЯ.

ПОЛЬЗОВАТЕЛЬ СКАЗАЛ: "{transcription}"
"""
        
        if primary_dish:
            dish_name = primary_dish.get('name', 'неизвестно')
            weight_guess = primary_dish.get('weight_guess')
            
            prompt += f"\nИЗ ЭТОГО МЫ ИЗВЛЕКЛИ ГИПОТЕЗУ:\n"
            prompt += f"Основное блюдо: {dish_name}\n"
            
            if weight_guess:
                prompt += f"Примерный вес: {weight_guess['value']}{weight_guess['unit']}\n"
            
            if secondary_items:
                items_str = ", ".join([item['name'] for item in secondary_items])
                prompt += f"Дополнительно: {items_str}\n"
        
        prompt += """
ТВОЯ ЗАДАЧА:
1. ПОДТВЕРДИТЬ или ОПРОВЕРГНУТЬ гипотезу по фото
2. Если подтверждается — УТОЧНИТЬ детали (точный вес, БЖУ)
3. Если нет — сказать, что на фото НА САМОМ ДЕЛЕ
4. Найти ВСЁ, что есть на фото, даже если не упомянуто

БУДЬ КРИТИЧЕН! Если видишь "пюре", но оно жидкое как суп — укажи это.
Если видишь "салат", но пользователь сказал "торт" — исправь ошибку.

ФОРМАТ ОТВЕТА (строго JSON):
{
  "hypothesis_confirmed": true/false,
  "actual_dish": "название того, что на самом деле на фото",
  "components": [
    {
      "name": "компонент",
      "weight_g": 200,
      "calories": 150,
      "protein_g": 10,
      "fat_g": 5,
      "carbs_g": 20,
      "confidence": 0.85,
      "matches_hypothesis": true/false
    }
  ],
  "discrepancies": ["что не совпало с гипотезой"],
  "additional_items": ["что нашли, но не было упомянуто"]
}"""
        
        return prompt
    
    async def _analyze_single_frame(
        self, 
        frame: bytes, 
        system_prompt: str, 
        frame_idx: int, 
        total_frames: int,
        audio_hypothesis: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze single frame with API
        
        Args:
            frame: Frame image as bytes
            system_prompt: System prompt with hypothesis
            frame_idx: Index of this frame
            total_frames: Total number of frames
            audio_hypothesis: Audio hypothesis for context
        
        Returns:
            Analysis result dict or None on error
        """
        try:
            # Convert frame to base64
            base64_image = base64.b64encode(frame).decode('utf-8')
            
            # Build user prompt
            user_prompt = f"""Это кадр {frame_idx + 1} из {total_frames} из видео.
Проанализируй этот кадр согласно инструкциям."""
            
            # Prepare API request
            headers = {
                "Authorization": f"Bearer {self.config.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/food-analyzer-bot",
                "X-Title": "Food Analyzer Bot - Frame Analysis"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
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
                "max_tokens": 1500
            }
            
            # Make API call
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"API error {response.status}: {error_text}")
                        return None
                    
                    data = await response.json()
                    
                    if 'choices' not in data or len(data['choices']) == 0:
                        logger.error("No response from API")
                        return None
                    
                    content = data['choices'][0]['message']['content']
                    logger.info(f"Frame {frame_idx} analysis: {content[:150]}...")
                    
                    # Parse JSON response
                    result = self._parse_json_response(content)
                    
                    if result:
                        result['frame_index'] = frame_idx
                        result['frame_total'] = total_frames
                    
                    return result
                    
        except Exception as e:
            logger.error(f"Error analyzing frame {frame_idx}: {e}", exc_info=True)
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
            
            # Try to clean JSON
            json_str = re.sub(r'//.*?\n', '\n', json_str)
            json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
            json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
            
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                logger.error("Failed to parse JSON even after cleaning")
                return None
