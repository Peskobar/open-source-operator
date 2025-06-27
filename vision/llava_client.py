import os
from typing import List, Optional
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

AVAILABLE_MODELS = {
    "llava-next": "liuhaotian/llava-next-13b-v1.1",
    "fuyu-8b": "adept/fuyu-8b",
    "gpt-4o-vision": "openai/gpt-4o-vision"
}

class VisionModel:
    """Wrapper na modele wizji/tekstu z opcjonalną kwantyzacją."""

    def __init__(self, model_name: str, checkpoint_path: Optional[str] = None):
        if checkpoint_path:
            model_id = checkpoint_path
        else:
            if model_name not in AVAILABLE_MODELS:
                raise ValueError(f"Nieznany model: {model_name}")
            model_id = AVAILABLE_MODELS[model_name]
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            device_map="auto",
            torch_dtype=torch.float16,
            load_in_4bit=True
        )

    def generate(self, prompt: str, image_path: str) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        with open(image_path, "rb") as f:
            image = f.read()
        # uproszczony interfejs multimodalny
        output = self.model.generate(**inputs, images=[image], max_new_tokens=64)
        return self.tokenizer.decode(output[0], skip_special_tokens=True)

    def describe(self, image_path: str) -> str:
        """Skrócony opis obrazu"""
        return self.generate("Describe the image", image_path)
