# Frontend 4 Operator

This folder provides an experimental dashboard that merges ideas from the three proposal archives. It exposes a minimal vanilla JavaScript app with optional 3D and voice features. The dashboard can be served by a FastAPI backend and communicates via WebSockets.

## Features
- Real-time metrics and agent status via `/ws` WebSocket
- Voice command button using the Web Speech API
- Simple 3D canvas powered by Three.js (placeholder for WebXR)
- Responsive CSS layout with CSS variables

## Running
1. Install Python requirements:
   ```bash
   pip install fastapi uvicorn
   ```
2. Start the FastAPI server (`fastapi_app.py` example below):
   ```bash
   uvicorn fastapi_app:app --reload --port 7860
   ```
3. Open `index.html` in your browser or let FastAPI serve static files from this directory.

## Example FastAPI Backend
```python
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
import json, asyncio

app = FastAPI(title="Open Operator API")
app.mount("/", StaticFiles(directory="frontend4_operator", html=True), name="static")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = {"metrics": {"active_agents": 1}, "agents": [{"name": "demo", "status": "running"}]}
        await websocket.send_text(json.dumps(data))
        await asyncio.sleep(1)
```
