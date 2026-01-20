"""
Audio context parser - extracts food hypotheses from speech
"""

import re
import logging
import subprocess
import tempfile
import aiohttp
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class AudioContextParser:
    """Parses audio transcription to extract food hypotheses"""
    
    def __init__(self, config=None, use_mock: bool = False):
        """
        Initialize audio context parser
        
        Args:
            config: Configuration object with API keys
            use_mock: Use mock transcription (False by default - use real)
        """
        self.use_mock = use_mock
        self.config = config
        self.api_url = "https://openrouter.ai/api/v1/audio/transcriptions"
    
    async def extract_hypothesis(self, video_path: str) -> Dict[str, Any]:
        """
        Extract audio, transcribe, and parse food hypotheses
        
        Returns:
        {
            'transcription': 'пюре думаю 500г и два куска хлеба',
            'hypothesis': {
                'primary_dish': {
                    'name': 'пюре',
                    'weight_guess': {'value': 500, 'unit': 'г', 'confidence': 0.7}
                },
                'secondary_items': [
                    {'name': 'хлеб', 'quantity': '2 куска', 'confidence': 0.8}
                ],
                'mentioned_items': ['чай'],
                'cooking_style': None,
                'certainty_words': ['думаю']
            }
        }
        """
        if self.use_mock:
            return self._get_mock_hypothesis()
        
        try:
            # 1. Extract audio from video using ffmpeg
            audio_path = await self._extract_audio(video_path)
            if not audio_path:
                logger.warning("Failed to extract audio, using empty transcription")
                return self._get_mock_hypothesis()
            
            try:
                # 2. Transcribe audio to text
                transcription = await self._transcribe_audio(audio_path)
                logger.info(f"Transcription: {transcription}")
                
                # 3. Parse text to structured hypothesis
                if transcription:
                    hypothesis = self._parse_food_hypothesis(transcription)
                else:
                    hypothesis = self._get_mock_hypothesis()['hypothesis']
                
                return {
                    'transcription': transcription,
                    'hypothesis': hypothesis
                }
                
            finally:
                # Clean up audio file
                Path(audio_path).unlink(missing_ok=True)
                
        except Exception as e:
            logger.error(f"Error extracting hypothesis: {e}", exc_info=True)
            return self._get_mock_hypothesis()
    
    async def _extract_audio(self, video_path: str) -> Optional[str]:
        """
        Extract audio from video using ffmpeg
        
        Args:
            video_path: Path to video file
        
        Returns:
            Path to extracted audio file (mp3) or None on error
        """
        try:
            # Check if ffmpeg is available
            try:
                subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
            except FileNotFoundError:
                logger.warning("ffmpeg not found. Install with: brew install ffmpeg")
                logger.warning("Falling back to mock transcription")
                return None
            
            # Create temporary file for audio
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_audio:
                audio_path = tmp_audio.name
            
            # Use ffmpeg to extract audio
            # -vn: no video
            # -acodec libmp3lame: encode to mp3
            # -ar 16000: sample rate 16kHz (good for speech)
            # -ac 1: mono audio
            # -b:a 64k: bitrate 64kbps (sufficient for speech)
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vn',  # No video
                '-acodec', 'libmp3lame',
                '-ar', '16000',  # 16kHz sample rate
                '-ac', '1',  # Mono
                '-b:a', '64k',  # 64kbps bitrate
                '-y',  # Overwrite output file
                audio_path
            ]
            
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.error(f"ffmpeg error: {result.stderr.decode()}")
                return None
            
            # Check if file was created and has content
            if Path(audio_path).exists() and Path(audio_path).stat().st_size > 0:
                logger.info(f"Audio extracted: {Path(audio_path).stat().st_size} bytes")
                return audio_path
            else:
                logger.error("Audio file is empty or not created")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("ffmpeg timeout")
            return None
        except Exception as e:
            logger.error(f"Error extracting audio: {e}", exc_info=True)
            return None
    
    async def _transcribe_audio(self, audio_path: str) -> str:
        """
        Transcribe audio to text using Groq API (Whisper)
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            Transcribed text or empty string on error
        """
        try:
            # Check if Groq API key is available
            groq_api_key = getattr(self.config, 'GROQ_API_KEY', None)
            
            if not groq_api_key:
                logger.warning("GROQ_API_KEY not set - skipping audio transcription")
                logger.info("To enable transcription, get free API key from: https://console.groq.com")
                return ""
            
            # Read audio file
            with open(audio_path, 'rb') as f:
                audio_data = f.read()
            
            # Prepare multipart form data for Groq API
            form = aiohttp.FormData()
            form.add_field('file', audio_data, filename='audio.mp3', content_type='audio/mpeg')
            form.add_field('model', 'whisper-large-v3')
            form.add_field('language', 'ru')  # Russian language
            form.add_field('response_format', 'json')
            
            headers = {
                "Authorization": f"Bearer {groq_api_key}",
            }
            
            # Make API request to Groq
            groq_url = "https://api.groq.com/openai/v1/audio/transcriptions"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    groq_url,
                    data=form,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Groq transcription API error {response.status}: {error_text}")
                        return ""
                    
                    result = await response.json()
                    transcription = result.get('text', '')
                    
                    logger.info(f"Transcription successful: {len(transcription)} characters")
                    return transcription.strip()
                    
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}", exc_info=True)
            return ""
    
    def _get_mock_hypothesis(self) -> Dict[str, Any]:
        """Mock hypothesis for Phase 1 testing"""
        return {
            'transcription': '',  # Empty for now
            'hypothesis': {
                'primary_dish': None,
                'secondary_items': [],
                'mentioned_items': [],
                'cooking_style': None,
                'certainty_words': []
            }
        }
    
    def _parse_food_hypothesis(self, text: str) -> Dict[str, Any]:
        """
        Parse text into structured food hypothesis
        
        Extracts:
        - Dish names (пюре, суп, котлета)
        - Weights and quantities (500г, 2 куска, стакан)
        - Cooking styles (жареный, варёный)
        - Certainty words (думаю, точно, примерно)
        
        Args:
            text: Transcribed text
        
        Returns:
            Structured hypothesis dict
        """
        text_lower = text.lower()
        
        # Extract weights
        weight_pattern = r'(\d+)\s*(г|грам|грамм|кг|кило)'
        weights = re.findall(weight_pattern, text_lower)
        
        # Extract quantities
        quantity_pattern = r'(\d+)\s*(куск|кусок|шт|штук|ломтик|ломтика)'
        quantities = re.findall(quantity_pattern, text_lower)
        
        # Extract certainty words
        certainty_words = []
        certainty_patterns = ['думаю', 'наверное', 'примерно', 'около', 'может быть', 'точно', 'уверен']
        for word in certainty_patterns:
            if word in text_lower:
                certainty_words.append(word)
        
        # Extract cooking styles
        cooking_styles = []
        style_patterns = ['жареный', 'жареная', 'варёный', 'варёная', 'тушёный', 'тушёная', 
                         'печёный', 'печёная', 'запечённый', 'запечённая']
        for style in style_patterns:
            if style in text_lower:
                cooking_styles.append(style)
        
        # Common food names (simple dictionary for now)
        food_names = ['пюре', 'суп', 'каша', 'салат', 'котлета', 'курица', 'рыба', 
                     'мясо', 'овощи', 'хлеб', 'рис', 'макароны', 'гречка']
        
        mentioned_foods = []
        for food in food_names:
            if food in text_lower:
                mentioned_foods.append(food)
        
        # Build hypothesis
        hypothesis = {
            'primary_dish': None,
            'secondary_items': [],
            'mentioned_items': mentioned_foods,
            'cooking_style': cooking_styles[0] if cooking_styles else None,
            'certainty_words': certainty_words
        }
        
        # Try to identify primary dish (first mentioned food)
        if mentioned_foods:
            primary_food = mentioned_foods[0]
            weight_guess = None
            
            if weights:
                value, unit = weights[0]
                # Calculate confidence based on certainty words
                confidence = 0.5 if certainty_words else 0.7
                weight_guess = {
                    'value': int(value),
                    'unit': unit,
                    'confidence': confidence
                }
            
            hypothesis['primary_dish'] = {
                'name': primary_food,
                'weight_guess': weight_guess
            }
            
            # Secondary items are other mentioned foods
            for food in mentioned_foods[1:]:
                item = {'name': food, 'confidence': 0.6}
                
                # Try to match with quantities
                if quantities:
                    qty, unit = quantities[0]
                    item['quantity'] = f"{qty} {unit}"
                    quantities = quantities[1:]  # Remove used quantity
                
                hypothesis['secondary_items'].append(item)
        
        return hypothesis
