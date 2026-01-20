"""
Intelligent keyframe extraction from video
Selects best frames based on quality metrics
"""

import cv2
import numpy as np
import logging
from typing import List, Tuple
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


class KeyFrameExtractor:
    """Extracts and enhances key frames from video"""
    
    def __init__(self, target_frames: int = 5):
        """
        Initialize keyframe extractor
        
        Args:
            target_frames: Number of best frames to extract (default: 5)
        """
        self.target_frames = target_frames
    
    async def process(self, video_path: str) -> List[bytes]:
        """
        Extract and enhance key frames from video
        
        Algorithm:
        1. Decode video and get all frames
        2. Skip first 1-3 seconds (to avoid face/front camera)
        3. Score each frame by:
           - Sharpness (Laplacian variance)
           - Brightness (not too dark/bright)
           - Change from previous frame (different angles)
        4. Select top-N frames by combined score
        5. Apply light enhancement (denoise, contrast)
        6. Return list of enhanced frames as bytes
        
        Args:
            video_path: Path to video file
        
        Returns:
            List of enhanced frame images as bytes
        """
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                logger.error(f"Failed to open video: {video_path}")
                return []
            
            # Get video properties
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            duration = total_frames / fps if fps > 0 else 0
            
            logger.info(f"Video: {total_frames} frames, {fps} fps, {duration:.1f}s")
            
            # Calculate skip duration based on video length
            # Short videos (< 5s): skip 1s
            # Medium videos (5-10s): skip 2s
            # Long videos (> 10s): skip 3s
            if duration < 5:
                skip_seconds = 1.0
            elif duration < 10:
                skip_seconds = 2.0
            else:
                skip_seconds = 3.0
            
            skip_frames = int(skip_seconds * fps)
            logger.info(f"Skipping first {skip_seconds}s ({skip_frames} frames) to avoid face/front camera")
            
            # Extract and score frames (starting after skip)
            frames_with_scores = []
            prev_frame = None
            frame_idx = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Skip first N frames
                if frame_idx < skip_frames:
                    frame_idx += 1
                    continue
                
                # Calculate frame quality score
                score = self._calculate_frame_score(frame, prev_frame)
                frames_with_scores.append((frame_idx, frame, score))
                
                prev_frame = frame
                frame_idx += 1
            
            cap.release()
            
            if not frames_with_scores:
                logger.warning(f"No frames after skipping {skip_seconds}s - video too short?")
                return []
            
            # Sort by score and select top N frames
            frames_with_scores.sort(key=lambda x: x[2], reverse=True)
            best_frames = frames_with_scores[:self.target_frames]
            
            # Sort selected frames by original order (chronological)
            best_frames.sort(key=lambda x: x[0])
            
            logger.info(f"Selected {len(best_frames)} best frames from {len(frames_with_scores)} (after skipping {skip_frames})")
            
            # Enhance and convert to bytes
            enhanced_frames = []
            for idx, frame, score in best_frames:
                enhanced = self._enhance_frame(frame)
                _, buffer = cv2.imencode('.jpg', enhanced, [cv2.IMWRITE_JPEG_QUALITY, 90])
                enhanced_frames.append(buffer.tobytes())
                logger.info(f"Frame {idx}: score={score:.3f}")
            
            return enhanced_frames
            
        except Exception as e:
            logger.error(f"Error extracting keyframes: {e}", exc_info=True)
            return []
    
    def _calculate_frame_score(self, frame: np.ndarray, prev_frame: np.ndarray = None) -> float:
        """
        Calculate quality score for a frame (0 to 1)
        
        Metrics:
        - Sharpness: Higher is better (Laplacian variance)
        - Brightness: Avoid too dark/bright (optimal around 128)
        - Change: Different from previous frame (new angle)
        
        Args:
            frame: Current frame
            prev_frame: Previous frame for change detection
        
        Returns:
            Combined quality score (0-1)
        """
        # Convert to grayscale for analysis
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # 1. Sharpness (Laplacian variance)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sharpness = laplacian.var()
        # Normalize (typical range: 0-1000)
        sharpness_score = min(sharpness / 500.0, 1.0)
        
        # 2. Brightness (optimal around 128)
        brightness = np.mean(gray)
        brightness_score = 1.0 - abs(brightness - 128) / 128.0
        
        # 3. Texture (food usually has texture)
        # Use standard deviation as texture indicator
        texture = np.std(gray)
        texture_score = min(texture / 50.0, 1.0)
        
        # 4. Change from previous frame
        change_score = 0.5  # Default if no previous frame
        if prev_frame is not None:
            prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
            # Calculate absolute difference
            diff = cv2.absdiff(gray, prev_gray)
            change = np.mean(diff)
            # Normalize (typical range: 0-50)
            change_score = min(change / 25.0, 1.0)
        
        # Combined score with weights
        score = (
            sharpness_score * 0.4 +
            brightness_score * 0.2 +
            texture_score * 0.2 +
            change_score * 0.2
        )
        
        return score
    
    def _enhance_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Apply light enhancement to frame
        
        Enhancements:
        - Slight contrast increase
        - Light denoising
        - Slight sharpening
        
        All in moderation to avoid artifacts!
        
        Args:
            frame: Input frame
        
        Returns:
            Enhanced frame
        """
        # 1. Light denoising
        denoised = cv2.fastNlMeansDenoisingColored(frame, None, 3, 3, 7, 21)
        
        # 2. Increase contrast slightly (CLAHE)
        lab = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        
        # 3. Slight sharpening (unsharp mask)
        gaussian = cv2.GaussianBlur(enhanced, (0, 0), 2.0)
        enhanced = cv2.addWeighted(enhanced, 1.5, gaussian, -0.5, 0)
        
        return enhanced
