import sqlite3
from pathlib import Path

DB_PATH = Path("joblens.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets you access columns by name
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
          CREATE TABLE IF NOT EXISTS sources (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT UNIQUE NOT NULL,
              url TEXT,
              last_fetched TIMESTAMP
          );

          CREATE TABLE IF NOT EXISTS jobs (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              title TEXT NOT NULL,
              company TEXT,
              location TEXT,
              url TEXT UNIQUE,
              source TEXT,
              description TEXT,
              date_posted TIMESTAMP,
              tags TEXT,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
          );

          CREATE TABLE IF NOT EXISTS search_queries (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT NOT NULL,
              keywords TEXT,
              filters TEXT,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
          );
      """)
    conn.commit()
    conn.close()

