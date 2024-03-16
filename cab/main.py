from typing import List

from fastapi import FastAPI

from cab.helpers import Announcement, parse_feed
from cab.settings import get_settings

app = FastAPI()
settings = get_settings()

ANNOUNCEMENTS: List[Announcement] = []


class Notifications:
    PATH = "notifications"

    @app.get(f"/{PATH}/cache")
    async def notifications_cache_view():
        """View current announcements."""

        return {"status": 200, "message": "OK", "data": ANNOUNCEMENTS}

    @app.post(f"/{PATH}")
    async def notifications():
        """Parse announcements feed and cache them."""

        global ANNOUNCEMENTS

        last_id = -1
        if len(ANNOUNCEMENTS) > 0:
            last_id = ANNOUNCEMENTS[-1].id

        feed = await parse_feed(last_id)

        ANNOUNCEMENTS = feed.copy()

        return {"status": 200, "message": "OK", "data": None}


def main():
    """Initialize paths."""

    Notifications()


if __name__ == "__main__":
    main()
