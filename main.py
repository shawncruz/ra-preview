from datetime import datetime, timedelta
from ra_service import RAService
from spotify_service import SpotifyService


def handle(event, context):
    ra_service = RAService()
    spotify_service = SpotifyService()
    # Potential Optimization: If this runs daily, then after the first run we should only be looking at the listings
    # one day after the previous end_date window. Downside here is that if events were added / removed, we will miss them.
    # For now, leave as is unless performance is severly impacted.
    start_date = datetime.utcnow()
    end_date = datetime.utcnow() + timedelta(weeks=2)
    artist_names = ra_service.get_artists(
        start_date=start_date,
        end_date=end_date,
    )
    spotify_service.update_playlist(
        artist_names=artist_names, start_date=start_date, end_date=end_date
    )

    return {}


if __name__ == "__main__":
    # Quick tests

    # Do nothing
    handle({}, {})
