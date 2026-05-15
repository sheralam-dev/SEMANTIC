'''
models.py — Data Schema Definitions
Purpose: define structure of stored data.

Main model: File

Fields:

id: int (primary key)
path: str (unique)
name: str
extension: str
size: int
created_at: float
modified_at: float
embedding: vector (optional)

Optional:

content_preview: str
mime_type: str

Implementation styles:

simple dataclass
or lightweight ORM-like structure

Notes:

keep schema minimal for speed
index path, name, modified_at
'''

from dataclasses import dataclass
from typing import Optional


@dataclass
class File:
    path: str
    name: str
    score: Optional[float] = None