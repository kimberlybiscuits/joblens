import httpx                                                                                                                               
from bs4 import BeautifulSoup
from app.scrapers.base import BaseScraper                                                                                                  
                                                                                                                                            
# Both pages use the same table structure, so one scraper handles both.                                                                    
URLS = [
    "https://eu-careers.europa.eu/en/non-permanent-contract-ec",
    "https://eu-careers.europa.eu/en/temporary-agents-other-institutions-vacancies",
]

BASE_URL = "https://eu-careers.europa.eu"


class EUCareersScraper(BaseScraper):
    source_name = "eu_careers"

    async def fetch(self) -> list[dict]:
        raw = []
        async with httpx.AsyncClient() as client:
            for url in URLS:
                response = await client.get(url, headers={"User-Agent": "JobLens/1.0"})
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")

                # Each page has one table of vacancies — skip the header row.
                rows = soup.select("table tr")[1:]
                for row in rows:
                    cells = row.find_all("td")
                    if len(cells) < 5:
                        continue

                    link = cells[0].find("a")
                    raw.append({
                        "title": link.get_text(strip=True) if link else "",
                        "url": link["href"] if link else "",
                        "institution": cells[2].get_text(strip=True),
                        "location": cells[3].get_text(strip=True),
                        "deadline": cells[-1].get_text(strip=True),
                    })
        return raw

    def normalize(self, raw: list[dict]) -> list[dict]:
        jobs = []
        for item in raw:
            url = item.get("url", "")
            if url and not url.startswith("http"):
                url = f"{BASE_URL}{url}"

            jobs.append({
                "title": item.get("title", ""),
                "company": item.get("institution", ""),
                "location": item.get("location", ""),
                "url": url,
                "source": self.source_name,
                "description": "",
                "date_posted": "",
                "tags": item.get("deadline", ""),  # deadline stored in tags for now
            })
        return jobs