import time
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

MODEL_PATH = "models/llm"

def main():
    tok = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        device_map="auto",
        torch_dtype="auto",
        load_in_4bit=True,
    )
    pipe = pipeline("text-generation", model=model, tokenizer=tok)
    prompts = ["Hello world" for _ in range(10)]
    start = time.time()
    for p in prompts:
        pipe(p, max_new_tokens=10)
    end = time.time()
    print("LLM throughput", len(prompts) / (end - start), "req/s")


if __name__ == "__main__":
    main()
