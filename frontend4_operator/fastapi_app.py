from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
import asyncio, json

app = FastAPI(title="Open Operator API")
app.mount("/", StaticFiles(directory=".", html=True), name="static")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = {
            "metrics": {"active_agents": 1, "success_rate": 0.95},
            "agents": [
                {"name": "demo-agent", "status": "running"}
            ]
        }
        await websocket.send_text(json.dumps(data))
        await asyncio.sleep(1)
