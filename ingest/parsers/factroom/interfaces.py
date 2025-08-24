from abc import ABC, abstractmethod
from typing import Protocol
from bs4 import BeautifulSoup
from ingest.parsers.factroom.types import ParsedCategory, FeedCard


class CategoryParser(ABC):
    @abstractmethod
    def parse(self, html: str) -> list[ParsedCategory]:
        ...

class FeedCardParser(Protocol):
    def parse_many(self, soup: BeautifulSoup, base_url: str) -> list[FeedCard]:
        ...
