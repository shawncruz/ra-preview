import os

from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import CacheFileHandler
import boto3

SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_USERNAME = os.getenv("SPOTIPY_USERNAME")
SPOTIPY_REDIRECT_URI = "http://127.0.0.1:9090"

dynamodb = boto3.resource("dynamodb")
ra_preview_table = dynamodb.Table("ra-preview")
scope = "playlist-modify-public"

def handle(event, context):
    cache_handler = CacheFileHandler(username=SPOTIPY_USERNAME)
    auth_manager = SpotifyOAuth(
        scope=scope,
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        cache_handler=cache_handler,
    )
    auth_manager.get_access_token(as_dict=False)
    ra_preview_table.put_item(
        Item={"type": "token", "value": cache_handler.get_cached_token()}
    )

if __name__ == "__main__":
    handle({}, {})
