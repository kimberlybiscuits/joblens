import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]


class Connection:
    """Wraps psycopg2 to keep the same conn.execute().fetchall() interface as sqlite3."""

    def __init__(self):
        self._conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        self._cur = self._conn.cursor()

    def execute(self, query, params=()):
        self._cur.execute(query, params)
        return self._cur

    def commit(self):
        self._conn.commit()

    def close(self):
        self._cur.close()
        self._conn.close()


def get_db() -> Connection:
    return Connection()


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sources (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            url TEXT,
            last_fetched TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            company TEXT,
            location TEXT,
            url TEXT UNIQUE,
            source TEXT,
            description TEXT,
            date_posted TIMESTAMP,
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS search_queries (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            keywords TEXT,
            filters TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id SERIAL PRIMARY KEY,
            name TEXT,
            email TEXT,
            current_title TEXT,
            years_experience INTEGER,
            skills TEXT,
            education TEXT,
            languages TEXT,
            location_preference TEXT,
            open_to_remote BOOLEAN DEFAULT TRUE,
            bio TEXT,
            preferred_titles TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS saved_jobs (
            id SERIAL PRIMARY KEY,
            job_id INTEGER UNIQUE NOT NULL,
            status TEXT DEFAULT 'saved',
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES jobs(id)
        )
    """)
    conn.commit()
    conn.close()
