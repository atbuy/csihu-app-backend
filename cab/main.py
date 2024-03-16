from typing import Dict

from fastapi import FastAPI

from cab.helpers import Announcement
from cab.settings import get_settings

app = FastAPI()
settings = get_settings()


ANNOUNCEMENTS: Dict[int, Announcement] = {}


@app.get("/notifications")
async def notifications():
    return {"message": "Hello, World"}
