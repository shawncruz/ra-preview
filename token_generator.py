from spotify_service import SpotifyService

def handle(event, context):
    SpotifyService().generate_access_token()

if __name__ == "__main__":
    handle({}, {})
