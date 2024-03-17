from fastapi import FastAPI
from redis_om import HashModel

from cab.helpers import Announcement, parse_feed
from cab.settings import get_settings

app = FastAPI()
settings = get_settings()


class AnnouncementModel(HashModel):
    id: int
    title: str
    description: str
    link: str

    @classmethod
    def from_announcement(ann: Announcement) -> "AnnouncementModel":
        """Create model from Announcement."""

        return AnnouncementModel(**ann)


class Notifications:
    PATH = "notifications"

    @app.get(f"/{PATH}")
    async def notifications():
        """View current announcements."""

        announcements = AnnouncementModel.all_pks()

        data = [AnnouncementModel.get(ann) for ann in announcements]

        return {"status": 200, "message": "OK", "data": data}

    @app.post(f"/{PATH}/cache")
    async def notifications_cache():
        """Parse announcements feed and cache them in Redis."""

        announcements = AnnouncementModel.all_pks()
        data = [AnnouncementModel.get(ann) for ann in announcements]
        ids = [ann.id for ann in data]

        feed = await parse_feed()

        for ann in feed:
            if ann.id in ids:
                continue

            model = AnnouncementModel(**ann)
            model.save()

        return {"status": 200, "message": "OK", "data": None}


def main():
    """Initialize application."""

    Notifications()


if __name__ == "__main__":
    main()
