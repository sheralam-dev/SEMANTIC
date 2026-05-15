'''
conn.py — SQLite Connection Layer
Purpose: manage database lifecycle and access.

Initializes SQLite database
Handles connections (singleton or pooled)
Applies pragmas for performance
Loads extensions (e.g., sqlite_vec)

Key functions:

get_connection() -> sqlite3.Connection
init_db()
close_connection()

Important settings:

PRAGMA journal_mode=WAL
PRAGMA synchronous=NORMAL
PRAGMA temp_store=MEMORY

Notes:

keep one shared connection per thread
enable foreign keys if needed
'''
import sqlite3
import sqlite_vec
from pathlib import Path


conn: sqlite3.Connection = None

def init_db(drop_tables: bool=False, vector_len: int=768):
    conn = get_connection()
    if drop_tables:
        conn.execute("DROP TABLE IF EXISTS files")
        conn.execute("DROP TABLE IF EXISTS files_vector") 
    # Minimal files table
    conn.execute("""
    CREATE TABLE IF NOT EXISTS files (
        path TEXT PRIMARY KEY,
        name TEXT
    )
    """)
    # Vector table (unique name)
    conn.execute(f"""
    CREATE VIRTUAL TABLE IF NOT EXISTS files_vector USING vec0(
        name TEXT PRIMARY KEY,
        embedding float[{vector_len}] distance_metric=cosine
    );
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_files_name ON files(name)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_files_path ON files(path)")
    conn.commit()


def get_connection() -> sqlite3.Connection:
    global conn
    # 1. Create a connection (using :memory: for a quick test)
    # conn = sqlite3.connect(":memory:")
    BASE_DIR = Path(__file__).resolve().parent
    conn = sqlite3.connect(BASE_DIR.parent.parent / "data" / "files.conn")
    # 2. Enable extension loading and load sqlite-vec
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    return conn


def close_connection() -> None:
    conn.close()


