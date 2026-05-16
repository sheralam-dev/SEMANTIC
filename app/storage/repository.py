'''
repository.py — CRUD Operations
Purpose: abstraction over database queries.

All DB interactions go through this layer
Keeps SQL isolated from business logic

Core operations:

insert_file(file: File)
bulk_insert(files: list[File])
delete_file(path: str)
update_file_path(old_path: Path, new_path: Path)
get_file_by_path(path: str)
get_files_by_names(names: list[str])

Query helpers:

fetch_all(limit=50)
count_files()

Vector search:

search_by_vector(query_embedding, k) -> list[str]  (returns matching names)
search_files_by_vector(query_embedding, k) -> list[File]
insert_embedding(name, embedding)
delete_embedding(name)

Notes:

use prepared statements
batch inserts for performance
avoid heavy joins
return lightweight objects (not raw rows)
'''

import json
from pathlib import Path
from sqlite3 import Connection
from typing import List, Optional
from app.storage.db import get_connection
from app.storage.models import File
from app.search.embedding_model import embed_batch, embed_query, embed_text
from app.utils.metadata import row_to_file


def search_files_by_semilarity(query, k: int = 50) -> List[File]:
    """Search for similar files by vector embedding, returns list of File objects."""
    query_embedding = embed_query(query)
    names_n_score = _search_by_vector(query, query_embedding, k)
    return get_files_by_names(names_n_score=names_n_score)


def _search_by_vector(query, query_embedding: list[float], k: int = 50) -> List[str]:
    """Search for similar files by vector embedding, returns list of file names."""
    db = get_connection()
    cursor = db.execute("SELECT name, distance FROM files_vector WHERE embedding MATCH ? AND k = ? ORDER BY distance ASC", (query_embedding, k))
    rows = cursor.fetchall()
    # print(query.split(":")[1], " -> ", [row[0] + f' {row[1] :.3}' for row in rows if row[1] < 0.55])
    return [row for row in rows if row[1] < 0.6]
    # return rows


def insert_file(file: File):
    """Insert a single file into the database."""
    db = get_connection()
    try:
        db.execute("BEGIN TRANSACTION")
        db.execute("INSERT OR IGNORE INTO files (path, name) VALUES (?, ?)", (file.path, file.name))
        _insert_embedding(db, file.name)
        db.commit()
    except Exception as e:
        db.rollback()


def _insert_embedding(db: Connection, name: str):
    """Insert a vector embedding for a file name."""
    db.execute("INSERT OR IGNORE INTO files_vector(name, embedding) VALUES (?, ?)", (name, embed_text(name)))


def bulk_insert(files: List[File]):
    """Insert multiple files and their embeddings in batches."""
    db = get_connection()
    try:
        db.execute("BEGIN TRANSACTION")
        db.executemany("INSERT OR IGNORE INTO files (path, name) VALUES (?, ?)", [(f.path, f.name) for f in files])
        _bulk_insert_embedding(db, files)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e


def _bulk_insert_embedding(db: Connection, files: list[File]):
    unique_files = {f.name: f for f in files}
    names = list(unique_files.keys())
    placeholders = ','.join(['?'] * len(names))
    existing = db.execute(f"SELECT name FROM files_vector WHERE name IN ({placeholders})", names).fetchall()
    existing_names = {row[0] for row in existing}
    missing_files = [f for name, f in unique_files.items() if name not in existing_names]
    if missing_files:
        phrases = [f"This is a {f.path.split('.')[-1].upper()} file named {f.name}. It is stored at: {f.path}." for f in missing_files]
        embeddings = embed_batch(phrases)
        insert_data = [(f.name, emb) for f, emb in zip(missing_files, embeddings)]
        db.executemany("INSERT OR IGNORE INTO files_vector (name, embedding) VALUES (?, ?)", insert_data)




def delete_file(path: str):
    """Delete a file by its path."""
    db = get_connection()
    try:
        db.execute("BEGIN TRANSACTION")
        db.execute("DELETE FROM files WHERE path = ?", (path,))
        name = Path(path).name
        remains = db.execute("SELECT 1 FROM files WHERE name = ?", (name,)).fetchone()
        if not remains:
            _delete_embedding(db, name)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e


def _delete_embedding(db: Connection, name: str):
    db.execute("DELETE FROM files_vector WHERE name = ?", (name,))


def update_file_path(old_path: Path, new_path: Path):
    """Update a file's path."""
    db = get_connection()
    try:
        db.execute("BEGIN TRANSACTION")
        db.execute("UPDATE files SET path = ?, name = ? WHERE path = ?", (str(new_path), new_path.name, str(old_path)))
        _update_embedding(db, old_path, new_path)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e


def _update_embedding(db, old_path: Path, new_path: Path):
    db.execute("DELETE FROM files_vector WHERE name = ?", (old_path.name,))
    _insert_embedding(db, new_path.name)


def get_file_by_path(path: str) -> Optional[File]:
    """Get a file by its path."""
    db = get_connection()
    cursor = db.execute("SELECT path, name FROM files WHERE path = ?", (path,))
    row = cursor.fetchone()
    return row_to_file(row) if row else None


def get_files_by_names(names_n_score: List[tuple[str, float]]) -> List[File]:
    """Get files by their names."""
    if not names_n_score:
        return []
    db = get_connection()
    placeholders = ','.join('?' * len(names_n_score))
    names = [ns[0] for ns in names_n_score]
    cursor = db.execute(f"SELECT path, name FROM files WHERE name IN ({placeholders})", names)
    rows = cursor.fetchall() # row -> path, name
    mapping = dict(names_n_score)
    files = [row_to_file(row, mapping[row[1]]) for row in rows if row[1] in mapping]
    files.sort(key=lambda f: f.score, reverse=False) # lowest first
    return files


def fetch_all(limit: int = 50) -> List[File]:
    """Fetch files from the database."""
    db = get_connection()
    cursor = db.execute("SELECT path, name FROM files LIMIT ?", (limit,))
    return [row_to_file(r) for r in cursor.fetchall()]


def count_files() -> int:
    """Count total number of files."""
    db = get_connection()
    cursor = db.execute("SELECT COUNT(*) FROM files")
    return cursor.fetchone()[0]


