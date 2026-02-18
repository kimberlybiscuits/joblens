import httpx         
import html                                                                                                                      
from datetime import datetime                                                                                                              
from app.scrapers.base import BaseScraper   
from bs4 import BeautifulSoup                                                                                                
                                                                                                                                            
# HN doesn't have an official search API, so we use Algolia — HN's search engine.                                                        
# It lets us find threads by keyword, which is how we locate the latest hiring post.
HN_SEARCH_URL = "https://hn.algolia.com/api/v1/search"

# The official HN Firebase API — used to fetch individual items (threads, comments).
# The {} is a placeholder we fill in with .format(id) when making a request.
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"


class HNScraper(BaseScraper):
    source_name = "hn_hiring"

    async def _get_latest_thread_id(self, client: httpx.AsyncClient) -> int | None:
        """Find the most recent 'Ask HN: Who is Hiring?' thread ID."""
        # We pass the client in rather than creating a new one here — this lets us
        # reuse the same HTTP connection across multiple requests in fetch(), which
        # is faster and more efficient than opening a new connection each time.
        params = {
            "query": "Ask HN: Who is Hiring?",
            "tags": "ask_hn",   # limit results to Ask HN posts only
            "hitsPerPage": 5,
        }
        resp = await client.get(HN_SEARCH_URL, params=params)
        resp.raise_for_status()

        hits = resp.json().get("hits", [])
        if not hits:
            return None

        # Algolia returns results sorted by recency — so the first hit is the
        # latest hiring thread. objectID is the HN item ID we need.
        return int(hits[0]["objectID"])

    async def fetch(self) -> list[dict]:
        # A single AsyncClient is created here and passed into helper methods.
        # This is the "connection reuse" pattern — one client, many requests.
        async with httpx.AsyncClient() as client:
            thread_id = await self._get_latest_thread_id(client)
            if not thread_id:
                return []

            # Fetch the thread itself — we don't need the post body, just the
            # list of top-level comment IDs stored in the "kids" field.
            resp = await client.get(HN_ITEM_URL.format(thread_id))
            resp.raise_for_status()
            thread = resp.json()

            # "kids" is HN's name for direct child comments. Each is an item ID.
            # We cap at 100 to avoid hammering the API — a typical thread has 400+.
            comment_ids = thread.get("kids", [])[:100]

            # Fetch each comment individually — the HN API doesn't support
            # bulk fetching, so we loop and make one request per comment.
            raw = []
            for comment_id in comment_ids:
                r = await client.get(HN_ITEM_URL.format(comment_id))
                if r.status_code == 200:
                    item = r.json()
                    # Skip deleted or flagged comments — they have no useful content.
                    if item and not item.get("deleted") and not item.get("dead"):
                        raw.append(item)

        return raw

    def normalize(self, raw: list[dict]) -> list[dict]:
        jobs = []
        for item in raw:
            text = item.get("text", "") or ""

            # HN comment text comes as HTML. Paragraphs are separated by <p> tags.
            # The first paragraph is usually the job summary, e.g.:
            # "Acme Corp | Software Engineer | Remote | Full-time"
            first_line = text.split("<p>")[0].strip()
            first_line = BeautifulSoup(first_line, "html.parser").get_text()                                                                           
            first_line = html.unescape(first_line)

            if '|' not in first_line:
                continue
            
            jobs.append({
                "title": first_line[:200],
                "company": "",   # too varied to parse reliably — left blank for now
                "location": "",
                "url": f"https://news.ycombinator.com/item?id={item.get('id')}",
                "source": self.source_name,
                "description": text,   # raw HTML — can strip tags in the UI later
                # item["time"] is a Unix timestamp (seconds since 1970-01-01).
                # utcfromtimestamp() converts it to a readable date string.
                "date_posted": datetime.utcfromtimestamp(
                    item.get("time", 0)
                ).strftime("%Y-%m-%d"),
                "tags": "",
            })
        return jobs