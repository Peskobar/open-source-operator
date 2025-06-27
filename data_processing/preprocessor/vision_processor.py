from .base_processor import BaseProcessor
from typing import Dict, List
import os
import logging
import base64
from io import BytesIO
from PIL import Image

class VisionProcessor(BaseProcessor):
    """Process trajectory data for vision-based SFT"""

    def __init__(self, config: Dict):
        super().__init__(config)
        vision_cfg = config.get('vision', {})
        self.image_size = tuple(vision_cfg.get('image_size', [1024, 1024]))
        self.augmentation = vision_cfg.get('augmentation', False)

    def _process_image(self, image_path: str) -> str:
        """Load image, resize and return as base64 string"""
        if not image_path or not os.path.isfile(image_path):
            logging.warning(f"Image not found: {image_path}")
            return ""
        try:
            img = Image.open(image_path).convert('RGB')
            if self.image_size:
                img = img.resize(self.image_size)
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            return base64.b64encode(buffer.getvalue()).decode('utf-8')
        except Exception as e:
            logging.error(f"Failed to process image {image_path}: {e}")
            return ""

    def process(self, raw_data: List[Dict]) -> Dict:
        processed = {'planning_data': [], 'grounding_data': []}
        for item in raw_data:
            img_b64 = self._process_image(item.get('screenshot', ''))
            if not img_b64:
                continue
            planning_item = {
                'instruction': item.get('instruction', ''),
                'observation': img_b64,
                'action': item.get('action', '')
            }
            grounding_item = {
                'screenshot': img_b64,
                'action': item.get('action', ''),
                'coordinates': item.get('click_position')
            }
            processed['planning_data'].append(planning_item)
            processed['grounding_data'].append(grounding_item)
        return processed
