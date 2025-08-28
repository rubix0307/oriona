from __future__ import annotations

import re
from datetime import datetime
from typing import List, Optional

from bs4 import BeautifulSoup, Tag

from ingest.parsers.base import BaseHTTPParser
from ingest.parsers.factroom.types import ParsedArticle, Breadcrumb, ContentInfo
from ingest.services.common import (
    normalize_url,
    clean_text,
    clean_anchor_text,
    abs_url,
)


class FactroomArticleParser(BaseHTTPParser):
    '''
    Parses a Factroom article page into a ParsedArticle:
      - title
      - published_at (if available)
      - content_html (cleaned HTML)
      - content_text (plain text)
    Notes:
      - Supports regular article pages and 'picture-fact' single layout.
    '''
    available_tags = ['p', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'blockquote']

    def parse(self, url: str) -> ParsedArticle:
        html = self.fetch(url=url)
        soup = BeautifulSoup(html, 'html.parser')
        content = self._extract_content(soup)
        return ParsedArticle(
            url=normalize_url(url),
            title=self._extract_title(soup),
            content_html=content.content_html,
            content_text=content.content_text,
            published_at=self._extract_date(soup),
            breadcrumbs=self._extract_breadcrumbs(soup),
        )


    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        h1 = soup.find('h1')
        if not h1:
            return None
        txt = clean_text(h1.get_text(' ', strip=True))
        return txt or None

    def _extract_date(self, soup: BeautifulSoup) -> Optional[datetime]:
        '''
        Date is usually in: <small class='date'> 23.08.2025</small>
        Parse as naive datetime at 00:00 (timezone handling can be added later).
        '''
        date_el = soup.select_one('article.post-box small.date')
        if not date_el:
            return None

        raw = clean_text(date_el.get_text(' ', strip=True))
        if not raw:
            return None

        try:
            return datetime.strptime(raw, '%d.%m.%Y')
        except ValueError:
            return None

    def _extract_breadcrumbs(self, soup: BeautifulSoup) -> List[Breadcrumb]:
        '''
        Breadcrumbs in: <small id='breadcrumbs'> ... <a href='...'>Name</a> • ... </small>
        '''
        out: List[Breadcrumb] = []

        root = soup.select_one('article.post-box small#breadcrumbs')
        if not root:
            return out

        for a in root.select('a[href]'):
            name = clean_anchor_text(a)
            url = abs_url(self.base_url, a.get('href'))
            if not url:
                continue
            out.append(Breadcrumb(name=name, url=normalize_url(url)))

        return out

    def _extract_lead_image(self, soup: BeautifulSoup) -> Optional[str]:
        '''
        Lead image is the first content image within .post-box-text.
        For picture-fact single, there is a .feed-picture-fact-single img as well.
        '''
        img = soup.select_one('article.post-box section.post-box-text img[src]')
        if img and img.get('src'):
            return normalize_url(img.get('src'))

        img2 = soup.select_one('.feed-picture-fact-single img[src]')
        if img2 and img2.get('src'):
            return normalize_url(img2.get('src'))

        return None


    def _is_read_also_node(self, node: Tag) -> bool:
        '''
        Heuristics to detect inline 'Читайте также…' blocks inside the main flow.
        We use multiple signals:
          - Text begins with 'Читайте также' or 'Читать также' (case-insensitive)
          - Presence of a <big> tag wrapping the text (common pattern)
          - Has an <a> link (usually internal)
        '''
        text = clean_text(node.get_text(' ', strip=True)).lower()
        # normalize spaces and NBSP
        text_norm = re.sub(r'\s+', ' ', text.replace('\u00a0', ' ')).strip()

        starts_with_phrase = bool(re.match(r'^(читайте|читать)\s+также\b', text_norm))
        has_big = node.find('big') is not None
        has_link = node.find('a', href=True) is not None

        # require phrase + (big or link) to reduce false positives
        if starts_with_phrase and (has_big or has_link):
            return True

        return False

    def _decompose_content(self, soup: BeautifulSoup) -> BeautifulSoup:
        for sel in [
            '.podpost-rtb',                     # ad blocks
            '.post-box-share',                  # share block
            '.underpost-title',                 # 'More' title
            '.underpost-feed-list',             # 'More' list
            '.underpost-feed-list-cat-link',    # link to category
            'script',
            'style',
            'figcaption',                       # wiki block
        ]:
            for node in soup.select(sel):
                node.decompose()

        # Inline 'Читайте также…' inside main content flow
        for node in soup.select('p, div, section'):
            if isinstance(node, Tag) and self._is_read_also_node(node):
                node.decompose()

        return soup

    def _extract_content(self, soup: BeautifulSoup) -> ContentInfo:
        '''
        Extract the main body from section.post-box-text, remove junk blocks,
        absolutize links and images, and produce both HTML and plain text.
        '''
        container = soup.select_one('article.post-box section.post-box-text')
        if not container:
            container = soup.select_one('article.post-box')
            if not container:
                return ContentInfo(content_html=None, content_text=None)

        content = self._decompose_content(
            soup=BeautifulSoup(str(container), 'html.parser')
        )

        # Absolutize <a href>, <img src>, and srcset attributes
        for a in content.select('a[href]'):
            href = a.get('href')
            if href:
                a['href'] = abs_url(self.base_url, href) or href

        for img in content.select('img[src]'):
            src = img.get('src')
            if src:
                img['src'] = abs_url(self.base_url, src) or src
            if img.has_attr('srcset'):
                img['srcset'] = self._normalize_srcset(img['srcset'])

        for source in content.select('source[srcset]'):
            source['srcset'] = self._normalize_srcset(source['srcset'])

        # Remove decorative clears, etc.
        for el in content.select('span.clear'):
            el.decompose()

        html_str = content.decode().strip()

        # Plain text from common block elements
        text_parts: List[str] = []
        for blk in content.select(', '.join(self.available_tags)):
            t = clean_text(blk.get_text(' ', strip=True))
            if t:
                text_parts.append(t)
        text_str = '\n\n'.join(text_parts) if text_parts else None

        return ContentInfo(content_html=html_str or None, content_text=text_str or None)

    def _normalize_srcset(self, srcset_value: str) -> str:
        '''Convert relative URLs inside srcset to absolute.'''
        if not srcset_value:
            return srcset_value
        parts = []
        for chunk in srcset_value.split(','):
            chunk = chunk.strip()
            if not chunk:
                continue
            segs = chunk.split()
            if not segs:
                continue
            url = segs[0]
            rest = ' '.join(segs[1:]) if len(segs) > 1 else ''
            absu = abs_url(self.base_url, url) or url
            parts.append((absu + (' ' + rest if rest else '')).strip())
        return ', '.join(parts)