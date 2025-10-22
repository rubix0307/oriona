from typing import Protocol, Iterable
from bs4 import BeautifulSoup
from ingest.parsers.factroom.types import FeedCard
from ingest.parsers.interfaces import HasUrl

class FeedCardParser(Protocol):
    def parse_many(self, soup: BeautifulSoup, base_url: str) -> list[FeedCard]:
        ...

class DuplicateChecker(Protocol):
    def __call__(self, cards: Iterable[HasUrl]) -> bool:
        ...
