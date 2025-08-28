from __future__ import annotations
from typing import TypedDict


class FeedPersistStats(TypedDict):
    total_input: int
    total_unique: int
    created: int
    updated: int

class ArticlePersistStats(TypedDict):
    total_input: int
    total_unique: int
    created: int
    updated: int
    content_created: int
    content_updated: int