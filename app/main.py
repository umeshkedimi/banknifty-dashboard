from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi import Request
from typing import List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    logger.info(f"New WebSocket connection. Total connections: {len(connections)}")
    
    try:
        await websocket.send_json({"status": "connected"})
        logger.info("Sent initial connection confirmation")
        
        while True:
            try:
                data = await websocket.receive_text()
                if data == "ping":
                    await websocket.send_json({"status": "pong"})
            except Exception as e:
                logger.error(f"Error in websocket loop: {str(e)}")
                break
                
    except WebSocketDisconnect:
        logger.info("Client disconnected normally")
    except Exception as e:
        logger.error(f"Error in websocket connection: {str(e)}")
    finally:
        if websocket in connections:
            connections.remove(websocket)
            logger.info(f"Connection removed. Remaining: {len(connections)}")