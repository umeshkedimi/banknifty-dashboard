from kiteconnect import KiteConnect
from urllib.parse import urlparse, parse_qs
import requests, pyotp
from dotenv import load_dotenv
import os

load_dotenv()

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
TOTP_TOKEN = os.getenv("TOTP_TOKEN")

kite = KiteConnect(api_key=API_KEY)

def getAccessToken():
    session = requests.Session()
    loginRes = session.post("https://kite.zerodha.com/api/login", {"user_id": USERNAME, "password": PASSWORD}).json()

    requestId = loginRes["data"]["request_id"]
    res = session.post("https://kite.zerodha.com/api/twofa", {"user_id": USERNAME, "request_id": requestId, "twofa_value": pyotp.TOTP(TOTP_TOKEN).now()})

    try:
        api_session = session.get(f"https://kite.trade/connect/login?api_key={API_KEY}")
        parsed = urlparse(api_session.url)
    except Exception as e:
        reqUrl = e.request.url
        parsed = urlparse(reqUrl)

    requestToken = parse_qs(parsed.query)["request_token"][0]
    accessToken = kite.generate_session(requestToken, api_secret=API_SECRET)["access_token"]
    return accessToken