from fastapi import BackgroundTasks, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from cab.helpers import populate_cache
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
    PATH = "notifications"

    @app.get(f"/{PATH}")
    async def notifications():
        """View current announcements."""

        announcements = AnnouncementModel.all_pks()

        data = [AnnouncementModel.get(ann) for ann in announcements]
        sorted_data = sorted(data, key=lambda ann: ann.id, reverse=True)

        return {"status": 200, "message": "OK", "data": sorted_data}

    @app.get(f"/{PATH}/" "{announcement_id}")
    async def notification_detail(announcement_id: int):
        """View a specific announcement."""

        announcements = AnnouncementModel.all_pks()

        announcement = None
        for ann in announcements:
            model = AnnouncementModel.get(ann)
            if model.id == announcement_id:
                announcement = model
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
