import os

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import CacheFileHandler
import boto3
import json
import decimal

SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_USERNAME = os.getenv("SPOTIPY_USERNAME")
SPOTIPY_REDIRECT_URI = "http://127.0.0.1:9090"

dynamodb = boto3.resource("dynamodb")
ra_preview_table = dynamodb.Table("ra-preview")
scope = "playlist-modify-public"


# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


class SpotifyService:
    def __init__(self, restore_access_token=True) -> None:
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                scope=scope,
                client_id=SPOTIPY_CLIENT_ID,
                client_secret=SPOTIPY_CLIENT_SECRET,
                redirect_uri=SPOTIPY_REDIRECT_URI,
                cache_handler=CacheFileHandler(
                    cache_path=f"/tmp/.cache-{SPOTIPY_USERNAME}",
                    encoder_cls=DecimalEncoder,
                ),
            )
        )
        if restore_access_token:
            self._restore_access_token()

    def generate_access_token(self):
        self.sp.auth_manager.get_access_token(as_dict=False)
        ra_preview_table.put_item(
            Item={
                "type": "token",
                "value": self.sp.auth_manager.cache_handler.get_cached_token(),
            }
        )

    def _restore_access_token(self):
        entry = ra_preview_table.get_item(
            Key={"type": "token"}, AttributesToGet=["value"]
        )
        if "Item" not in entry:
            print("Token not found in db")
            return
        token = entry["Item"]["value"]
        self.sp.auth_manager.cache_handler.save_token_to_cache(token)

    # TODO: Move to util
    def chunk(self, c, n):
        for i in range(0, len(c), n):
            yield c[i : i + n]

    def update_playlist(self, artist_names, start_date, end_date):
        artist_ids = set()
        for artist_name in set(artist_names):
            results = self.sp.search(
                artist_name, limit=1, offset=0, type="artist", market=None
            )
            if (
                results["artists"]["items"]
                and results["artists"]["items"][0]["name"].casefold()
                == artist_name.casefold()
            ):
                artist_ids.add(results["artists"]["items"][0]["id"])

        top_track_ids = set()
        for artist_id in artist_ids:
            top_tracks_reponse = self.sp.artist_top_tracks(artist_id)
            if top_tracks_reponse["tracks"] and top_tracks_reponse["tracks"][0]:
                top_track_ids.add(top_tracks_reponse["tracks"][0]["id"])

        # FIXME: This playlist ID should be dynamic, based on region

        # FIXME: Hack to clear playlist, then update with multiple update request chunks
        self.sp.playlist_replace_items("73p99duLkd9Cu5zNuUfcEU", [top_track_ids.pop()])

        for track_id_chunk in self.chunk(list(top_track_ids), 100):
            self.sp.playlist_add_items("73p99duLkd9Cu5zNuUfcEU", track_id_chunk)

        self.sp.playlist_change_details(
            "73p99duLkd9Cu5zNuUfcEU",
            name=None,
            public=None,
            collaborative=None,
            description=f"Preview of top songs from artists playing upcoming shows in NYC between {start_date.strftime('%D')}-{end_date.strftime('%D')}. Based on data from Resident Advisor's events. Updated daily.",
        )
