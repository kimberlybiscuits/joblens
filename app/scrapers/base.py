from abc import ABC, abstractmethod


class BaseScraper(ABC):
    """Every scraper must implement these two methods."""

    source_name: str  # e.g. "remoteok"

    @abstractmethod
    async def fetch(self) -> list[dict]:
        """Fetch raw job data from the source. Return a list of dicts."""
        ...

    @abstractmethod
    def normalize(self, raw: list[dict]) -> list[dict]:
        """Convert raw data into our common job schema:
        {title, company, location, url, source, description, date_posted, tags}
        """
        ...