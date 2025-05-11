from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi import Request
from typing import List

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")
connections: List[WebSocket] = []

@app.get("/")
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws/ticks")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)
    try:
        # Send initial connection confirmation
        await websocket.send_json({"status": "connected"})
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connections.remove(websocket)
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        if websocket in connections:
            connections.remove(websocket)