from redis_om import HashModel


class AnnouncementModel(HashModel):
    id: int
    title: str
    description: str
    link: str
    date: str = ""
    author: str = ""

    @classmethod
    def from_announcement(ann) -> "AnnouncementModel":
        """Create model from Announcement."""

        return AnnouncementModel(**ann)
