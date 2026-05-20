from pathlib import Path
from typing import Iterator, List, Optional, Set

from app.storage.models import File
from app.storage.repository import insert_files


IGNORE_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", "$RECYCLE.BIN", "System Volume Information"}

def batch_scan(paths: List[str], batch_size: int = 1000, extensions: Optional[Set[str]] = None):
    # Convert list to set for O(1) lookups and normalize to lowercase
    ext_filter = {e.lower().lstrip('.') for e in extensions} if extensions else None
    batch = []
    for file in _scan(paths, ext_filter):
        batch.append(file)
        if len(batch) >= batch_size:
            insert_files(batch)
            batch.clear()
    if batch: # remaining batches
        insert_files(batch)


def _scan(str_paths: List[str], ext_filter: Optional[Set[str]]) -> Iterator[File]:
    for base_str_path in str_paths:
        yield from _safe_recursive_scan(Path(base_str_path), ext_filter)


def _safe_recursive_scan(base_path: Path, ext_filter: Optional[Set[str]]) -> Iterator[File]:
    # 1. Immediate Skip for known problematic system folders
    if base_path.name in IGNORE_DIRS:
        return
    try:
        # Use iterdir() so we can wrap the access in a try-block
        for path in base_path.iterdir():
            try:
                if path.is_dir():
                    yield from _safe_recursive_scan(path, ext_filter)
                else:
                    # Extension check
                    if ext_filter and path.suffix.lower().lstrip('.') not in ext_filter:
                        continue
                    yield File(file_path=path)
            except (PermissionError, OSError):
                # This catches errors on individual files or subfolders
                continue
    except (PermissionError, OSError):
        # This catches errors when trying to list the parent folder itself
        return

