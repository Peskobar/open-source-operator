import os
from typing import Literal

from transformers import AutoModelForCausalLM, AutoTokenizer
from PIL import Image

MODEL_PATHS = {
    "llava": "liuhaotian/llava-next-13b-v1.1",
    "fuyu": "adept/fuyu-8b",
}

_loaded = {}


def _load_model(model_key: str):
    if model_key in _loaded:
        return _loaded[model_key]
    name = MODEL_PATHS.get(model_key)
    tokenizer = AutoTokenizer.from_pretrained(name)
    model = AutoModelForCausalLM.from_pretrained(
        name,
        device_map="auto",
        load_in_4bit=True,
        trust_remote_code=True,
    )
    _loaded[model_key] = (model, tokenizer)
    return model, tokenizer


def describe_image(path: str, model: Literal["llava", "fuyu", "gpt4o"] = "llava") -> str:
    if model == "gpt4o":
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        with open(path, "rb") as f:
            b = f.read()
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": [{"type": "image", "image": b}, {"type": "text", "text": "co jest na obrazku"}]}],
        )
        return resp.choices[0].message.content
    model, tokenizer = _load_model(model)
    image = Image.open(path)
    prompt = "Describe the screenshot in detail."
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, images=[image], max_new_tokens=50)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)
