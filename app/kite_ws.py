from kiteconnect import KiteTicker
from dotenv import load_dotenv
import os
import asyncio

from app.main import connections
from app.services.access_token import getAccessToken

load_dotenv()

API_KEY = os.getenv("API_KEY")
ACCESS_TOKEN = getAccessToken()
BANKNIFTY_TOKEN = 260105

kws = KiteTicker(API_KEY, ACCESS_TOKEN)

print("API_KEY:", API_KEY)
print("ACCESS_TOKEN:", ACCESS_TOKEN)

def on_ticks(ws, ticks):
    for tick in ticks:
        try:
            data = {
                "price": tick.get("last_price"),
                "timestamp": tick.get("timestamp").isoformat() if tick.get("timestamp") else None,
                "token": BANKNIFTY_TOKEN
            }
            print(f"Bank Nifty Tick: {data}")
            
            current_connections = connections.copy()
            
            for conn in current_connections:
                try:
                    asyncio.create_task(conn.send_json(data))
                except Exception as e:
                    print(f"Error sending tick: {str(e)}")
                    if conn in connections:
                        connections.remove(conn)
        except Exception as e:
            print(f"Error processing tick: {str(e)}")

def on_connect(ws, response):
    print("KiteTicker connected")
    ws.subscribe([BANKNIFTY_TOKEN])
    ws.set_mode(ws.MODE_FULL, [BANKNIFTY_TOKEN])

def on_error(ws, code, reason):
    print(f"KiteTicker Error: {code} - {reason}")
    try:
        ws.connect(threaded=True)
    except Exception as e:
        print(f"Reconnection failed: {str(e)}")

def on_close(ws, code, reason):
    print(f"KiteTicker closed: {code} - {reason}")
    try:
        ws.connect(threaded=True)
    except Exception as e:
        print(f"Reconnection failed: {str(e)}")

def start_kite_ws():
    try:
        print("Starting KiteTicker...")
        kws.on_ticks = on_ticks
        kws.on_connect = on_connect
        kws.on_error = on_error
        kws.on_close = on_close
        kws.connect(threaded=True)
        print("KiteTicker started successfully")
    except Exception as e:
        print(f"Error starting KiteTicker: {str(e)}")

if __name__ == "__main__":
    start_kite_ws()