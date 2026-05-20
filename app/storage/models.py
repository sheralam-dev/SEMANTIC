from dataclasses import dataclass
from functools import wraps
from pathlib import Path
from typing import Optional
from datetime import datetime


def format_datetime(fmt="%d-%b-%y %I:%M %p"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            timestamp = func(*args, **kwargs)
            dt = datetime.fromtimestamp(timestamp)
            # Use lstrip to safely remove leading zero from the hour
            # This avoids the platform-specific %-I vs %#I issue
            formatted = dt.strftime(fmt)
            return formatted.replace(" 0", " ") 
        return wrapper
    return decorator


@dataclass
class File:

    file_path: Path
    score: Optional[float] = None

    @property
    def name(self):
        return self.file_path.name
    
    @property
    def path(self):
        return str(self.file_path)
    
    @property
    def path_parent(self):
        return str(self.file_path.parent)
    
    @property
    def extension(self):
        return self.file_path.suffix
    
    @property
    def file_size(self):
        return self.file_path.stat().st_size
    
    @property
    @format_datetime()
    def date_created(self):
        return self.file_path.stat().st_birthtime
    
    @property
    @format_datetime()
    def date_modified(self):
        return self.file_path.stat().st_mtime
    
    def get_phrase(self):
        clean_name = self.name.replace('_', ' ').replace('-', ' ')
        phrase = phrase = f"{self.name} {self.extension} ({self.path})"
        # print(phrase)
        return phrase