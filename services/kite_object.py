from access_token import getAccessToken
from kiteconnect import KiteConnect
from dotenv import load_dotenv
import os


def get_kite_object():
    """
    This function initializes the KiteConnect object with the access token.
    It loads environment variables from a .env file and returns the KiteConnect object.
    """
    load_dotenv()
    api_key = os.getenv("API_KEY")
    access_token = getAccessToken()
    kite = KiteConnect(api_key=api_key)
    kite.set_access_token(access_token)
    return kite