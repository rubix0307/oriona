from abc import ABC, abstractmethod
from typing import List, Optional, Protocol
from dataclasses import dataclass
from bs4 import BeautifulSoup
from ingest.services.common import normalize_url


@dataclass
class ParsedCategory:
    name: str
    url: str
    parent_url: Optional[str] = None

    def __post_init__(self):
        self.name = self.name.strip()
        self.url = normalize_url(self.url)
        if self.parent_url:
            self.parent_url = normalize_url(self.parent_url)

@dataclass
class FeedCard:
    url: str
    title: Optional[str] = None
    image_preview: Optional[str] = None

    def __repr__(self):
        url = self.url
        title = self.title
        image_preview = self.image_preview
        return f'<{self.__class__.__name__} {title=}, {url=},  {image_preview=}>'

class CategoryParser(ABC):
    @abstractmethod
    def parse(self, html: str) -> List[ParsedCategory]:
        ...

class FeedCardParser(Protocol):
    def parse_many(self, soup: BeautifulSoup, base_url: str) -> list[FeedCard]:
        ...
