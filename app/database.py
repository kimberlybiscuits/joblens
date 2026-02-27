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
                       
           CREATE TABLE IF NOT EXISTS profiles (                                                                                                                
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,                                                                                                                                       
                email TEXT,                                                                                                                                      
                current_title TEXT,
                years_experience INTEGER,
                skills TEXT,
                education TEXT,
                languages TEXT,
                location_preference TEXT,
                open_to_remote BOOLEAN DEFAULT 1,
                bio TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );            
      """)
       # Migrations — safe to run every time                                                                                                              
    try:
         conn.execute("ALTER TABLE profiles ADD COLUMN preferred_titles TEXT DEFAULT ''")
    except sqlite3.OperationalError:
          pass  # column already exists
    
    # Creates the saved_jobs table if it doesn't exist yet.                                                                                               
    # This is safe to run every time the app starts — CREATE TABLE IF NOT EXISTS                                                                    
    # means it's a no-op if the table is already there.                                                                                               
    try:
        conn.executescript("""                                                                                                                        
            CREATE TABLE IF NOT EXISTS saved_jobs (                                                                                                 
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER UNIQUE NOT NULL,
                status TEXT DEFAULT 'saved',
                notes TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_id) REFERENCES jobs(id)
            );
        """)
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()

