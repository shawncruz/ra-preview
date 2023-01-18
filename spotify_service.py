import os

import spotipy
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


class SpotifyService:
    def __init__(self) -> None:
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                scope=scope,
                client_id=SPOTIPY_CLIENT_ID,
                client_secret=SPOTIPY_CLIENT_SECRET,
                redirect_uri=SPOTIPY_REDIRECT_URI,
                cache_handler=CacheFileHandler(username=SPOTIPY_USERNAME),
            )
        )

    def generate_access_token(self):
        self.sp.auth_manager.get_access_token(as_dict=False)
        ra_preview_table.put_item(
            Item={
                "type": "token",
                "value": self.sp.auth_manager.cache_handler.get_cached_token(),
            }
        )

    def update_playlist(self, artist_names, start_date, end_date):
        artist_ids = []
        for artist_name in artist_names:
            results = self.sp.search(
                artist_name, limit=1, offset=0, type="artist", market=None
            )
            if (
                results["artists"]["items"]
                and results["artists"]["items"][0]["name"].casefold()
                == artist_name.casefold()
            ):
                artist_ids.append(results["artists"]["items"][0]["id"])

        top_track_ids = []
        for artist_id in artist_ids:
            top_tracks_reponse = self.sp.artist_top_tracks(artist_id)
            if top_tracks_reponse["tracks"] and top_tracks_reponse["tracks"][0]:
                top_track_ids.append(
                    top_tracks_reponse["tracks"][0]["id"]
                )

        # FIXME: This playlist ID should be dynamic, based on region
        self.sp.playlist_replace_items("73p99duLkd9Cu5zNuUfcEU", top_track_ids)
        self.sp.playlist_change_details(
            "73p99duLkd9Cu5zNuUfcEU",
            name=None,
            public=None,
            collaborative=None,
            description=f"Preview of all songs from artists playing in NYC between {start_date.strftime('%D')}-{end_date.strftime('%D')}",
        )
