import httpx
from bs4 import BeautifulSoup
from app.scrapers.base import BaseScraper

BASE_URL = "https://www.impactpool.org"
JOBS_URL = f"{BASE_URL}/jobs"
MAX_PAGES = 10


class ImpactPoolScraper(BaseScraper):
    source_name = "impactpool"

    async def fetch(self) -> list[dict]:
        raw = []
        async with httpx.AsyncClient(follow_redirects=True) as client:
            for page in range(1, MAX_PAGES + 1):
                url = JOBS_URL if page == 1 else f"{BASE_URL}/search?page={page}&per_page=40"
                response = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "html.parser")
                cards = soup.select("div.job")

                if not cards:
                    break

                for card in cards:
                    link = card.select_one("a[href]")
                    title_tag = card.select_one("div[type='cardTitle']")
                    org_tag = card.select_one("div[type='bodyEmphasis']")
                    location_tags = card.select("div[type='bodyEmphasis']")

                    # First bodyEmphasis is org, second contains location
                    org = org_tag.get_text(strip=True) if org_tag else ""
                    location = location_tags[1].get_text(strip=True) if len(location_tags) > 1 else ""

                    raw.append({
                        "title": title_tag.get_text(strip=True) if title_tag else "",
                        "company": org,
                        "location": location,
                        "url": link["href"] if link else "",
                    })
        return raw

    def normalize(self, raw: list[dict]) -> list[dict]:
        jobs = []
        for item in raw:
            if not item.get("title") or not item.get("url"):
                continue
            url = item["url"]
            if not url.startswith("http"):
                url = f"{BASE_URL}{url}"
            jobs.append({
                "title": item["title"],
                "company": item.get("company", ""),
                "location": item.get("location", ""),
                "url": url,
                "source": self.source_name,
                "description": "",
                "date_posted": "",
                "tags": "",
            })
        return jobs
