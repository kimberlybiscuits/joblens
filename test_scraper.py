import asyncio
from app.scrapers.remoteok import RemoteOKScraper
from app.database import get_db, init_db


async def main():
    # 1. Fetch and normalize
    scraper = RemoteOKScraper()
    print("Fetching jobs from RemoteOK...")
    raw = await scraper.fetch()
    print(f"Got {len(raw)} raw jobs")

    jobs = scraper.normalize(raw)
    print(f"Normalized {len(jobs)} jobs")
    print(f"First job: {jobs[0]['title']} at {jobs[0]['company']}")

# Fetch EuroBrussels
    from app.scrapers.eurobrussels import EuroBrusselsScraper
    eb_scraper = EuroBrusselsScraper()
    print("Fetching jobs from EuroBrussels...")
    eb_raw = await eb_scraper.fetch()
    print(f"Got {len(eb_raw)} raw jobs")

    eb_jobs = eb_scraper.normalize(eb_raw)
    print(f"Normalized {len(eb_jobs)} jobs")
    jobs = jobs + eb_jobs

# Fetch HN Who's Hiring
    from app.scrapers.hn import HNScraper
    hn_scraper = HNScraper()
    print("Fetching jobs from HN Who's Hiring...")
    hn_raw = await hn_scraper.fetch()
    print(f"Got {len(hn_raw)} raw comments")

    hn_jobs = hn_scraper.normalize(hn_raw)
    print(f"Normalized {len(hn_jobs)} jobs")
    jobs = jobs + hn_jobs

    # 2. Save to DB
    init_db()
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
            print(f"Skipped: {e}")
    conn.commit()
    conn.close()
    print(f"Saved {saved} jobs to the database!")


asyncio.run(main())