import os

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import CacheFileHandler
import boto3

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_USERNAME = os.getenv("SPOTIFY_USERNAME")
SPOTIFY_REDIRECT_URI = "http://127.0.0.1:9090"

dynamodb = boto3.resource("dynamodb")
ra_preview_table = dynamodb.Table("ra-preview")
scope = "playlist-modify-public"

def handle(event, context):
    cache_handler = CacheFileHandler(username=SPOTIFY_USERNAME)

    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            scope=scope,
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=SPOTIFY_REDIRECT_URI,
            cache_handler=cache_handler,
        )
    )

    ra_preview_table.put_item(
        Item={"type": "token", "value": cache_handler.get_cached_token()}
    )


if __name__ == "__main__":
    handle({}, {})
