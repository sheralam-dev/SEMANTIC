from pathlib import Path
from typing import List
# from datetime import datetime

from app.storage.db import get_connection
from app.storage.models import File
from app.search.embedding_model_onnx import embed_batch, embed_query, embed_text


def search_similar_files(user_input: str, top_k: int, max_distance: float=0.55) -> List[File]:
    """Return most similar files based on vector distance."""
    # today = datetime.now().strftime('%Y-%m-%d')
    query = f"Represent this sentence for searching relevant passages:  {user_input}"
    query_vector = embed_query(query)
    db = get_connection()
    with db:
        rows = db.execute("SELECT path, distance FROM files_vector WHERE embedding MATCH ? ORDER BY distance ASC LIMIT ?", (query_vector, top_k)).fetchall()
    # print(f'{max_distance = }')
    # print([round(row[1], 3) for row in rows if row[1] < max_distance])
    return [
        File(file_path=Path(Path(row[0])), score=row[1])
        for row in rows
        if row[1] < max_distance
    ]


def insert_file(file: File):
    """Insert a single file into the database."""
    db = get_connection()
    try:
        with db:
            db.execute("INSERT OR IGNORE INTO files_vector(path, embedding) VALUES (?, ?)", (file.path, embed_text(file.get_phrase())))
    except Exception as e:
        db.rollback()


def insert_files(files: List[File]):
    """Insert multiple files and their embeddings in batches."""
    db = get_connection()
    try:
        with db:
            if not files: return
            # create dict of files with paths as keys
            unique_files = {file.path: file for file in files}
            paths = list(unique_files.keys())
            placeholders = ','.join(['?'] * len(paths))
            existing = db.execute(f"SELECT path FROM files_vector WHERE path IN ({placeholders})", paths).fetchall()
            existing_paths = {row[0] for row in existing}
            missing_files = [file for path, file in unique_files.items() if path not in existing_paths]
            if not missing_files: return
            phrases = [file.get_phrase() for file in missing_files]
            embeddings = embed_batch(phrases)
            insert_data = [(file.path, emb) for file, emb in zip(missing_files, embeddings)]
            db.executemany("INSERT OR IGNORE INTO files_vector (path, embedding) VALUES (?, ?)", insert_data)
    except Exception as e:
        db.rollback()
        raise e


def delete_file(path: str):
    """Delete a file by its path."""
    db = get_connection()
    try:
        with db:
            db.execute("DELETE FROM files_vector WHERE path = ?", (path,))
    except Exception as e:
        db.rollback()
        raise e


def update_file_path(old_path: Path, new_path: Path):
    """Update a file's path."""
    new_file = File(new_path)
    embedding = embed_text(new_file.get_phrase())
    db = get_connection()
    try:
        with db:
            db.execute("DELETE FROM files_vector WHERE path = ?", (str(old_path),))
            db.execute("INSERT OR IGNORE INTO files_vector(path, embedding) VALUES (?, ?)", (new_file.path, embedding))
    except Exception as e:
        db.rollback()
        raise e


def count_files() -> int:
    """Count total number of files."""
    db = get_connection()
    return db.execute("SELECT COUNT(*) FROM files_vector").fetchone()[0]


