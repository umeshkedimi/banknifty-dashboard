from kiteconnect import KiteTicker
from dotenv import load_dotenv
from app.services.access_token import getAccessToken
import os
import asyncio
import json
import logging
from datetime import datetime
import nest_asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from app.main import connections

load_dotenv()
nest_asyncio.apply()

API_KEY = os.getenv("API_KEY")
ACCESS_TOKEN = getAccessToken()
BANKNIFTY_TOKEN = 260105

kws = KiteTicker(API_KEY, ACCESS_TOKEN)

logger.info(f"Initialized with API_KEY: {API_KEY[:4]}... and ACCESS_TOKEN: {ACCESS_TOKEN[:4]}...")

async def send_to_connections(data):
    if not connections:
        logger.warning("No active WebSocket connections")
        return
        
    current_connections = connections.copy()
    logger.info(f"Sending data to {len(current_connections)} connections")
    
    for conn in current_connections:
        try:
            await conn.send_json(data)
            logger.debug("Data sent successfully")
        except Exception as e:
            logger.error(f"Error sending data: {str(e)}")
            if conn in connections:
                connections.remove(conn)

def on_ticks(ws, ticks):
    logger.info(f"Received ticks: {json.dumps(ticks, default=str)}")
    
    for tick in ticks:
        try:
            if 'last_price' not in tick:
                logger.warning(f"Missing last_price in tick data: {tick}")
                continue
                
            data = {
                "price": tick["last_price"],
                "timestamp": datetime.now().isoformat(),
                "token": BANKNIFTY_TOKEN,
                "type": "tick_data"
            }
            logger.info(f"Processed tick: {data}")
            
            loop = asyncio.get_event_loop()
            loop.run_until_complete(send_to_connections(data))
            
        except Exception as e:
            logger.error(f"Error processing tick: {str(e)}")

def on_connect(ws, response):
    logger.info(f"KiteTicker connected with response: {response}")
    ws.subscribe([BANKNIFTY_TOKEN])
    ws.set_mode(ws.MODE_FULL, [BANKNIFTY_TOKEN])
    logger.info(f"Subscribed to BANKNIFTY_TOKEN: {BANKNIFTY_TOKEN}")

def on_close(ws, code, reason):
    logger.warning(f"KiteTicker connection closed: {code} - {reason}")
    try:
        ws.connect(threaded=True)
        logger.info("Reconnection successful")
    except Exception as e:
        logger.error(f"Reconnection failed: {str(e)}")

def on_error(ws, code, reason):
    logger.error(f"KiteTicker error: {code} - {reason}")
    try:
        ws.connect(threaded=True)
        logger.info("Reconnection after error successful")
    except Exception as e:
        logger.error(f"Reconnection failed: {str(e)}")

async def start_kite_ws():
    try:
        logger.info("Starting KiteTicker...")
        kws.on_ticks = on_ticks
        kws.on_connect = on_connect
        kws.on_close = on_close
        kws.on_error = on_error
        kws.connect(threaded=True)
        logger.info("KiteTicker started successfully")

        while True:
            await asyncio.sleep(1)
    except Exception as e:
        logger.error(f"Error in KiteTicker: {str(e)}")

if __name__ == "__main__":
    asyncio.run(start_kite_ws())