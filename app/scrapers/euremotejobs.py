import httpx
from bs4 import BeautifulSoup
from app.scrapers.base import BaseScraper

URL = "https://euremotejobs.com/jobs/"


class EURemoteJobsScraper(BaseScraper):
    source_name = "euremotejobs"

    async def fetch(self) -> list[dict]:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(URL, headers={"User-Agent": "JobLens/1.0"})
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        listings = soup.select("a.job-card-link")

        raw = []
        for a in listings:
            title_tag = a.select_one("h2.job-title")
            company_tag = a.select_one("div.company-name")
            location_tag = a.select_one("div.meta-item.meta-location")

            # Location div contains an <img> — get only the text node
            location = ""
            if location_tag:
                location = location_tag.get_text(strip=True)

            raw.append({
                "title": title_tag.get_text(strip=True) if title_tag else "",
                "company": company_tag.get_text(strip=True) if company_tag else "",
                "location": location or "Europe",
                "url": a.get("href", ""),
                "date_posted": "",
            })
        return raw

    def normalize(self, raw: list[dict]) -> list[dict]:
        jobs = []
        for item in raw:
            if not item.get("title") or not item.get("url"):
                continue
            jobs.append({
                "title": item["title"],
                "company": item.get("company", ""),
                "location": item.get("location", "Europe"),
                "url": item["url"],
                "source": self.source_name,
                "description": "",
                "date_posted": item.get("date_posted", ""),
                "tags": "",
            })
        return jobs
