from __future__ import annotations
from typing import Optional
from bs4 import BeautifulSoup, Tag
from ingest.parsers.factroom.interfaces import FeedCardParser, FeedCard
from ingest.services.common import (
    normalize_url,
    clean_text,
    clean_anchor_text,
    abs_url,
)


class NewTextPostCardParser(FeedCardParser):
    '''
    Handles cards like:
    <div class='new-text-post-outer'>
      <a class='new-text-post' href='...'>
        <span class='new-text-post-image'><img src='...'></span>
        <span class='new-text-post-title'>Title</span>
      </a>
    </div>
    '''

    def parse_many(self, soup: BeautifulSoup, base_url: str) -> list[FeedCard]:
        out: list[FeedCard] = []
        for a in soup.select('div.new-text-post-outer a.new-text-post[href]'):
            href = a.get('href')
            absu = abs_url(base_url, href)
            if not absu:
                continue
            url = normalize_url(absu)

            # title
            title_el: Optional[Tag] = a.select_one('.new-text-post-title')
            title = clean_text(title_el.get_text(' ', strip=True)) if title_el else clean_anchor_text(a)
            title = title or None

            # image
            img = a.select_one('.new-text-post-image img')
            image = (img.get('src') or img.get('data-src')) if img else None

            out.append(FeedCard(url=url, title=title, image_preview=image or None))
        return out


class PictureFactCardParser(FeedCardParser):
    '''
    Handles picture-fact cards like:
    <div class='feed-picture-fact-outer'>
      <div class='feed-picture-fact'>
        <a href='...'><img src='...' alt='...'></a>
      </div>
    </div>
    '''

    def parse_many(self, soup: BeautifulSoup, base_url: str) -> list[FeedCard]:
        out: list[FeedCard] = []

        for box in soup.select('div.feed-picture-fact-outer'):
            # main <a> with img
            a = box.select_one('div.feed-picture-fact a[href]')
            if not a:
                continue
            absu = abs_url(base_url, a.get('href'))
            if not absu:
                continue
            url = normalize_url(absu)

            img = a.select_one('img')
            image = (img.get('src') or img.get('data-src')) if img else None

            title = None
            share = box.select_one('div.ya-share2')
            if share:
                if share.has_attr('data-title'):
                    title = clean_text(share['data-title'])
                if not title:
                    # fallback: look at <a title='...'> inside
                    link_with_title = share.select_one('a[title]')
                    if link_with_title:
                        title = clean_text(link_with_title['title'])


            out.append(
                FeedCard(url=url, title=title, image_preview=image or None)
            )
        return out