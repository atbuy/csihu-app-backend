from typing import Dict

from fastapi import FastAPI

from cab.helpers import Announcement
from cab.settings import Settings

app = FastAPI()
settings = Settings()


ANNOUNCEMENTS: Dict[int, Announcement] = {}


@app.get("/notifications")
async def notifications():
    return {"message": "Hello, World"}
