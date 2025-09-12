from datetime import datetime
from typing import Optional, TypedDict
from dataclasses import dataclass
from bs4 import BeautifulSoup
from ingest.parsers.exceptions import ParsedArticleError
from ingest.services.common import normalize_url

URL = str

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
    image_preview: Optional[URL] = None

    def __post_init__(self):
        if self.title:
            self.title = self.title.strip()

    def __repr__(self):
        url = self.url
        title = self.title
        image_preview = self.image_preview
        return f'<{self.__class__.__name__} {title=}, {url=},  {image_preview=}>'

@dataclass
class ParsedFeed:
    cards: list[FeedCard]
    html_soup: BeautifulSoup

@dataclass
class PaginationInfo:
    current: Optional[int] = None
    total: Optional[int] = None
    next: Optional[int] = None
    next_url: Optional[str] = None

@dataclass
class ContentInfo:
    content_html: Optional[str] = None
    content_text: Optional[str] = None


@dataclass
class Breadcrumb:
    name: str
    url: str

    def __post_init__(self):
        if self.url:
            self.url = normalize_url(self.url)


@dataclass
class ParsedArticle:
    url: str
    title: Optional[str] = None
    published_at: Optional[datetime] = None
    lead_image: Optional[str] = None
    breadcrumbs: list[Breadcrumb] = None
    content_html: Optional[str] = None
    content_text: Optional[str] = None

    def __post_init__(self):
        if self.title:
            self.title = self.title.strip()

    @property
    def ok(self) -> bool:
        return all([self.url, self.content_html, self.content_text])

    def raise_for_status(self):
        if not self.ok:
            raise ParsedArticleError()