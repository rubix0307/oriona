from __future__ import annotations
from typing import Optional, Sequence, Callable
from bs4 import BeautifulSoup

from ingest.models import Site
from ingest.parsers.base import BaseParser
from ingest.parsers.factroom.interfaces import FeedCardParser
from ingest.parsers.factroom.parser_cards import (
    FeedCard,
    NewTextPostCardParser,
    PictureFactCardParser,
)
from ingest.parsers.factroom.types import URL, ParsedFeed
from ingest.services.common import normalize_url, is_site_root


class FactroomFeedParser(BaseParser):
    '''
    Parses a feed page and returns a list of FeedCard items.
    Uses multiple card parsers to cover different templates.
    '''
    def __init__(
        self,
        fetch_func: Optional[Callable[[str], str]] = None,
        card_parsers: Optional[Sequence[FeedCardParser]] = None,
    ):
        super().__init__(fetch_func=fetch_func)
        self.card_parsers: list[FeedCardParser] = list(card_parsers) if card_parsers else [
            NewTextPostCardParser(),
            PictureFactCardParser(),
        ]
        self.site = Site.objects.get(slug='factroom')

    def parse(self, url: URL) -> ParsedFeed:
        soup = self.fetch_soup(url=url)

        containers = soup.select('section.new-text-posts, div.feed-picture-fact-outer')
        scope = soup if not containers else BeautifulSoup(''.join(str(c) for c in containers), 'html.parser')

        items: list[FeedCard] = []
        seen: set[str] = set()

        for parser in self.card_parsers:
            for card in parser.parse_many(scope, self.site.base_url):
                if not card.url:
                    continue

                key = normalize_url(card.url)
                if is_site_root(key, self.site.base_url):
                    continue

                if key in seen:
                    idx = next((i for i, it in enumerate(items) if it.url == key), None)
                    if idx is not None:
                        cur = items[idx]
                        if not cur.title and card.title:
                            cur.title = card.title
                        if not cur.image_preview and card.image_preview:
                            cur.image_preview = card.image_preview
                    continue

                items.append(FeedCard(url=key, title=card.title, image_preview=card.image_preview))
                seen.add(key)

        return ParsedFeed(cards=items, html_soup=soup)