import sqlite3
import sqlite_vec
from pathlib import Path
from app.utils.paths import DB_PATH

_conn: sqlite3.Connection = None

def get_connection() -> sqlite3.Connection:
    global _conn
    if _conn is not None:
        return _conn
    print(f'[db] {DB_PATH = }')
    _conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    _conn.enable_load_extension(True)
    sqlite_vec.load(_conn)
    _conn.enable_load_extension(False)
    
    # Performance Pragmas
    _conn.execute("PRAGMA journal_mode=WAL")
    _conn.execute("PRAGMA synchronous=NORMAL")
    _conn.execute("PRAGMA foreign_keys=ON")
    
    return _conn

def init_db(drop_tables: bool = False, vector_len: int = 384):
    print(f'[db] {vector_len = }')
    db = get_connection()
    if drop_tables:
        db.execute("DROP TABLE IF EXISTS files")
        db.execute("DROP TABLE IF EXISTS files_vector") 

    # Standard table for metadata
    db.execute("""
    CREATE TABLE IF NOT EXISTS files (
        path TEXT PRIMARY KEY,
        name TEXT
    )""")
    db.execute("CREATE INDEX IF NOT EXISTS idx_files_name ON files(name)")

    # Vector table (vec0 does not support PRIMARY KEY or standard INDEX)
    db.execute(f"""
    CREATE VIRTUAL TABLE IF NOT EXISTS files_vector USING vec0(
        name TEXT,
        embedding float[{vector_len}] distance_metric=cosine
    )""")
    db.commit()

def close_connection() -> None:
    global _conn
    if _conn:
        _conn.close()
        _conn = None
