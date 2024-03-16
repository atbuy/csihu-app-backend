import urllib
from dataclasses import dataclass
from typing import List

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from cab.settings import Settings, get_settings


@dataclass
class Announcement:
    """Announcement dataclass."""

    id: int
    title: str
    description: str
    link: str

    def keys(self):
        return self.__dict__.keys()

    def __getitem__(self, key: str):
        return getattr(self, key.lower())


async def parse_feed(current_id: int = -1) -> List[Announcement]:
    """Parse RSS feed and return announcements."""

    # Get RSS feed
    settings: Settings = get_settings()
    feed_url = settings.ann.feed_url
    headers = {"Referer": settings.ann.base_url}
    feed = requests.get(feed_url, headers=headers, verify=False)
    soup = BeautifulSoup(feed.text, "xml")

    # Parse all announcements
    out = []
    items = soup.find_all("item")
    for item in items:
        item: Tag

        # Parse attributes
        title = item.find("title").text
        description = item.find("description").text
        description = description.replace("....", "").replace("...", "")
        link = item.find("link").text
        id = int(link.split("id=")[-1])

        # URL Decode text
        title = urllib.parse.unquote(title)
        description = urllib.parse.unquote(description)

        # No need to parse announcements
        # that have already been sent
        if id <= current_id:
            break

        # Create object and append to output
        ann = Announcement(id, title, description, link)
        out.append(ann)

    return out
