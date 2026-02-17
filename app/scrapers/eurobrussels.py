import httpx                                                                       
from bs4 import BeautifulSoup                                                    
from app.scrapers.base import BaseScraper                                          
                                                                                    
URL = "https://www.eurobrussels.com/jobs"


class EuroBrusselsScraper(BaseScraper):
    source_name = "eurobrussels"

    async def fetch(self) -> list[dict]:
        async with httpx.AsyncClient() as client:
            response = await client.get(URL, headers={"User-Agent": "JobLens/1.0"})
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        listings = soup.select("ul.searchList li.premiumJobContainer")

        raw = []
        for li in listings:
            link_tag = li.select_one("h3 a") or li.select_one("a")
            raw.append({                                                           
                  "title": link_tag.get_text(strip=True) if link_tag else "",        
                  "url": link_tag["href"] if link_tag else "",
                  "company": li.select_one("div.companyName").get_text(strip=True) if
   li.select_one("div.companyName") else "",
                  "location": li.select_one("div.location").get_text(strip=True) if
  li.select_one("div.location") else "",
              })
        return raw

    def normalize(self, raw: list[dict]) -> list[dict]:
        jobs = []
        for item in raw:
            url = item.get("url", "")
            if url and not url.startswith("http"):
                url = f"https://www.eurobrussels.com{url}"

            jobs.append({
                  "title": item.get("title", ""),
                  "company": item.get("company", ""),
                  "location": item.get("location", ""),
                  "url": url,
                  "source": self.source_name,
                  "description": "",
                  "date_posted": "",
                  "tags": "",
              })
        return jobs