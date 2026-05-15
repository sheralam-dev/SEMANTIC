# import mimetypes
from pathlib import Path
from typing import Dict

from app.storage.models import File


def path_to_file(path: Path) -> Dict:
    """
    Extract lightweight file metadata for indexing.
    """
    return File(
        path=str(path),
        name=path.stem.lower(),
    )



def row_to_file(row, score: float=None) -> File:
    """Convert a database row to a File object."""
    return File(
        path=row[0],
        name=row[1],
        score=score,
    )