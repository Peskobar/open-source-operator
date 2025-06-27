import json
import os
import logging
from typing import Dict

class VisionSFTConverter:
    """Convert processed vision data to SFT training format"""

    def __init__(self, config: Dict):
        self.config = config
        log_dir = self.config.get('log_dir', 'logs/converter')
        os.makedirs(log_dir, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def convert_to_sft_format(self, processed_data: Dict) -> Dict:
        planning_samples = []
        for item in processed_data.get('planning_data', []):
            planning_samples.append({
                'prompt': item['instruction'],
                'image': item['observation'],
                'action': item['action']
            })
        grounding_samples = []
        for item in processed_data.get('grounding_data', []):
            grounding_samples.append({
                'image': item['screenshot'],
                'action': item['action'],
                'coordinates': item['coordinates']
            })
        return {'planning': planning_samples, 'grounding': grounding_samples}

    def save_sft_data(self, sft_data: Dict, output_dir: str):
        os.makedirs(output_dir, exist_ok=True)
        planning_path = os.path.join(output_dir, 'vision_planning.jsonl')
        grounding_path = os.path.join(output_dir, 'vision_grounding.jsonl')

        with open(planning_path, 'w', encoding='utf-8') as f:
            for sample in sft_data['planning']:
                f.write(json.dumps(sample, ensure_ascii=False) + '\n')
        with open(grounding_path, 'w', encoding='utf-8') as f:
            for sample in sft_data['grounding']:
                f.write(json.dumps(sample, ensure_ascii=False) + '\n')
        logging.info(
            f"Saved {len(sft_data['planning'])} planning samples to {planning_path}")
        logging.info(
            f"Saved {len(sft_data['grounding'])} grounding samples to {grounding_path}")
