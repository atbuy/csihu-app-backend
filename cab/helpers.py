import time
import urllib
from dataclasses import dataclass
from typing import List

import requests
import urllib3
from bs4 import BeautifulSoup
from bs4.element import Tag
from selenium import webdriver
from selenium.webdriver.common.by import By

from cab.models import AnnouncementModel
from cab.settings import Settings, get_settings

# Disable InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@dataclass
class Announcement:
    """Announcement dataclass."""

    id: int
    title: str
    description: str
    link: str
    date: str = ""
    author: str = ""

    def keys(self):
        return self.__dict__.keys()

    def __getitem__(self, key: str):
        return getattr(self, key.lower())


def parse_feed(current_id: int = -1) -> List[Announcement]:
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


def get_webdriver() -> webdriver.Remote:
    """Initialize a new webdriver."""

    settings = get_settings()

    options = webdriver.ChromeOptions()
    options.headless = True

    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-mipmap-generation")
    options.add_argument("--disable-extensions")
    options.add_argument("--dns-prefetch-disable")
    options.add_argument("--single-process")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--remote-debugging-port=9222")

    # Setup remove host path
    host = settings.web_driver.host
    port = settings.web_driver.port
    remote = f"http://{host}:{port}/wd/hub"

    return webdriver.Remote(remote, options=options)


def parse_announcements(announcements: list[Announcement], existing_ids: list[int]) -> list[Announcement]:
    """Parse each announcement separately and get extra info."""

    driver = get_webdriver()

    settings: Settings = get_settings()
    base_url = settings.ann.base_announcement_url

    out = []
    for ann in announcements:
        if ann.id in existing_ids:
            continue

        url = f"{base_url}?id={ann.id}"

        # Go to page and wait for Javascript to load
        print("Getting page", url)
        driver.get(url)
        time.sleep(1.5)
        print("Got page", url)

        body_element = driver.find_element(By.CLASS_NAME, "ql-editor")
        header_element = driver.find_element(
            By.XPATH, '//span[@style="color: #888888;"]'
        )

        text = body_element.get_attribute("innerText")
        header = header_element.get_attribute("innerText")

        date, author = str(header).split("-")
        date = date.strip()
        author = author.strip()

        new_ann = Announcement(ann.id, ann.title, text, ann.link, date, author)
        out.append(new_ann)

    driver.close()
    driver.quit()

    return out


def populate_cache(ids: list[int]) -> None:
    """Background job to populate Redis cache."""

    feed = parse_feed()
    announcements = parse_announcements(feed, ids)

    for ann in announcements:
        if ann.id in ids:
            continue

        model = AnnouncementModel(**ann)
        model.save()

        print(f"Saved model {ann}")
