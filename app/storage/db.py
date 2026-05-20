import sqlite3
import sqlite_vec
from pathlib import Path
from app.utils.paths import DB_PATH

_conn: sqlite3.Connection = None

def get_connection() -> sqlite3.Connection:
    global _conn
    if _conn is not None:
        return _conn
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
    db = get_connection()
    if drop_tables:
        db.execute("DROP TABLE IF EXISTS files_vector") 
    db.execute(
        f"""
        CREATE VIRTUAL TABLE IF NOT EXISTS files_vector USING vec0(
            path TEXT,
            embedding float[{vector_len}] distance_metric=cosine
        )
        """
    )
    db.commit()


def close_connection() -> None:
    global _conn
    if _conn:
        _conn.close()
        _conn = None
