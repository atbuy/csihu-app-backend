from fastapi import BackgroundTasks, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from cab.helpers import get_all_announcements, populate_cache
from cab.models import AnnouncementModel
from cab.settings import get_settings

app = FastAPI()
settings = get_settings()


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Notifications:
    PATH = "csihu/notifications"

    @app.get(f"/{PATH}")
    async def notifications(amount: int = 100, offset: int = 0):
        """View current announcements.

        Sends the default amount of posts if no request parameters are given.
        If parameters are passed, the selection happens on the top <amount> items.
        """

        # Get sorted announcements
        announcements = get_all_announcements()

        # Safely keep only the `amount` announcements,
        # using the `offset` to get the next ones.
        data = []
        length = len(announcements)
        limit = min(length, offset + amount)
        base = min(offset, length)
        for i in range(base, limit):
            data.append(announcements[i])

        return {"status": 200, "message": "OK", "data": data}

    @app.get(f"/{PATH}/" "{announcement_id}")
    async def notification_detail(announcement_id: int):
        """View a specific announcement."""

        announcements = get_all_announcements()

        announcement = None
        for ann in announcements:
            if ann.id == announcement_id:
                announcement = ann
                break

        return {"status": 200, "message": "OK", "data": announcement}

    @app.post(f"/{PATH}/cache", status_code=202)
    async def notifications_cache(background_tasks: BackgroundTasks):
        """Parse announcements feed and cache them in Redis."""

        announcements = AnnouncementModel.all_pks()
        data = [AnnouncementModel.get(ann) for ann in announcements]
        ids = [ann.id for ann in data]

        background_tasks.add_task(populate_cache, ids)

        return {"status": 200, "message": "OK", "data": None}


def main():
    """Initialize application."""

    Notifications()


if __name__ == "__main__":
    main()
