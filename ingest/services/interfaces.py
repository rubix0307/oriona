from __future__ import annotations
from typing import Protocol, Iterable
from ingest.models import Site, Article
from ingest.parsers.factroom.interfaces import FeedCard
from ingest.parsers.factroom.types import ParsedArticle
from ingest.services.types import FeedPersistStats, ArticlePersistStats


class FeedCardPersistProtocol(Protocol):
    def save_one(self, site: Site, card: FeedCard) -> tuple[Article, bool]:
        ...

    def save_many(self, site: Site, cards: list[FeedCard]) -> FeedPersistStats:
        ...


class ArticlePersistInterface(Protocol):
    def save_one(self, site: Site, parsed: ParsedArticle) -> tuple[Article, bool]:
        ...

    def save_many(self, site: Site, items: Iterable[ParsedArticle]) -> ArticlePersistStats:
        ...
