FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt && playwright install --with-deps
COPY . /app
COPY models /models
RUN python - <<'EOF'
import os
from transformers import AutoTokenizer, AutoModel
paths=['/models/llm','/models/vision']
for p in paths:
    if os.path.isdir(p) and os.listdir(p):
        AutoTokenizer.from_pretrained(p)
        AutoModel.from_pretrained(p)
EOF
CMD ["python", "app.py"]
