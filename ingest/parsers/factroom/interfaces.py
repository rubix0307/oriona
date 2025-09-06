
from typing import Protocol, Iterable
from bs4 import BeautifulSoup
from ingest.parsers.factroom.types import ParsedCategory, FeedCard


class FeedCardParser(Protocol):
    def parse_many(self, soup: BeautifulSoup, base_url: str) -> list[FeedCard]:
        ...
