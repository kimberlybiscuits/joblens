import asyncio                                                                                                                             
import sqlite3                                                                                                                             
from apscheduler.schedulers.background import BackgroundScheduler                                                                          
from app.database import get_db                                                                                                            
from app.scrapers.remoteok import RemoteOKScraper
from app.scrapers.eurobrussels import EuroBrusselsScraper
from app.scrapers.hn import HNScraper
from app.scrapers.eucareers import EUCareersScraper
from app.scrapers.euremotejobs import EURemoteJobsScraper
from app.scrapers.impactpool import ImpactPoolScraper

# All active scrapers — add new ones here as we build them.
SCRAPERS = [
    RemoteOKScraper(),
    EuroBrusselsScraper(),
    HNScraper(),
    EUCareersScraper(),
    EURemoteJobsScraper(),
    ImpactPoolScraper(),
]


def save_jobs(jobs: list[dict]):
    """Save a list of normalised jobs to the database."""
    conn = get_db()
    saved = 0
    for job in jobs:
        try:
            conn.execute(
                """INSERT OR IGNORE INTO jobs
                    (title, company, location, url, source, description, date_posted, tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (job["title"], job["company"], job["location"], job["url"],
                job["source"], job["description"], job["date_posted"], job["tags"]),
            )
            saved += 1
        except Exception as e:
            print(f"Skipped job: {e}")
    conn.commit()
    conn.close()
    return saved


def fetch_all_jobs():
    """Run all scrapers and save results. Called by the scheduler and the manual trigger."""
    print("Running scheduled fetch...")

    # APScheduler runs in a background thread, not an async context.
    # asyncio.run() lets us call our async scrapers from that sync thread.
    async def _run():
        for scraper in SCRAPERS:
            try:
                raw = await scraper.fetch()
                jobs = scraper.normalize(raw)
                saved = save_jobs(jobs)
                print(f"  {scraper.source_name}: {saved} jobs saved")
            except Exception as e:
                print(f"  {scraper.source_name} failed: {e}")

    asyncio.run(_run())


# BackgroundScheduler runs in a separate thread alongside the FastAPI app.
# It won't block web requests while scraping.
scheduler = BackgroundScheduler()
scheduler.add_job(fetch_all_jobs, "interval", hours=12, id="fetch_jobs")