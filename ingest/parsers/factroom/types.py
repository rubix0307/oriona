from datetime import datetime
from typing import Optional, TypedDict
from dataclasses import dataclass
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
        if self.image_preview:
            self.image_preview = normalize_url(self.image_preview)

    def __repr__(self):
        url = self.url
        title = self.title
        image_preview = self.image_preview
        return f'<{self.__class__.__name__} {title=}, {url=},  {image_preview=}>'

class PaginationInfo(TypedDict):
    current: int
    total: int
    next: Optional[int]
    next_url: Optional[str]
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
        if self.url:
            self.url = normalize_url(self.url)

