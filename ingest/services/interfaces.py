from __future__ import annotations
from typing import Protocol
from ingest.models import Site, Article
from ingest.parsers.factroom.interfaces import FeedCard
from ingest.services.types import FeedPersistStats


class FeedCardPersistProtocol(Protocol):
    def save_one(self, site: Site, card: FeedCard) -> tuple[Article, bool]:
        ...

    def save_many(self, site: Site, cards: list[FeedCard]) -> FeedPersistStats:
        ...