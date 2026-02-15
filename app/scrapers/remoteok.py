import httpx
from app.scrapers.base import BaseScraper

API_URL = "https://remoteok.com/api"


class RemoteOKScraper(BaseScraper):
    source_name = "remoteok"

    async def fetch(self) -> list[dict]:
        async with httpx.AsyncClient() as client:
            response = await client.get(API_URL, headers={"User-Agent": "JobLens/1.0"})
            response.raise_for_status()
            data = response.json()
        # First item is a metadata/legal notice, skip it
        return data[1:]

    def normalize(self, raw: list[dict]) -> list[dict]:
        jobs = []
        for item in raw:
            jobs.append({
                "title": item.get("position", ""),
                "company": item.get("company", ""),
                "location": item.get("location", "Remote"),
                "url": f"https://remoteok.com/remote-jobs/{item.get('id', '')}",
                "source": self.source_name,
                "description": item.get("description", ""),
                "date_posted": item.get("date", ""),
                "tags": ",".join(item.get("tags", [])),
            })
        return jobs