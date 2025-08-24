from typing import List, Optional, Callable, Dict, Set, Tuple
from urllib.parse import urljoin, urlparse, urlunparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup, NavigableString, Tag

from ingest.parsers.base import BaseHTTPParser
from ingest.parsers.factroom.interfaces import CategoryParser, ParsedCategory
from ingest.services.common import normalize_url, is_site_root


def _clean_anchor_text(a: Tag) -> str:
    '''
    Return anchor text without <small> counters and <i> icons.
    '''
    parts: List[str] = []
    for node in a.contents:
        if isinstance(node, NavigableString):
            txt = str(node).strip()
            if txt:
                parts.append(txt)
        elif isinstance(node, Tag):
            if node.name in ('small', 'i'):
                continue
            txt = node.get_text(strip=True)
            if txt:
                parts.append(txt)
    return ' '.join(parts).strip()


def _parent_from_url(child_url: str) -> Optional[str]:
    '''
    Return parent URL by removing the last path segment.
    If there is no parent (root), return None.
    '''
    p = urlparse(child_url)
    path = p.path or '/'
    if not path.endswith('/'):
        path += '/'
    parts = path.rstrip('/').split('/')
    if len(parts) <= 1:
        return None
    parent_path = '/'.join(parts[:-1]) + '/'
    return urlunparse(p._replace(path=parent_path, params='', query='', fragment=''))


class FactroomCategoryParser(BaseHTTPParser, CategoryParser):
    '''
    1) Parse left menu (parents + children).
    2) Recursively discover subcategories from category pages (nav.subcategory-list),
       loading pages in parallel (max_workers threads).
    All emitted URLs are normalized; site root is never used as a parent.
    '''

    def __init__(
        self,
        base_url: str,
        fetch_func: Optional[Callable[[str], str]] = None,
        max_workers: int = 10,
    ):
        super().__init__(base_url, fetch_func=fetch_func)
        self.max_workers = max_workers

    def parse(self, html: str) -> List[ParsedCategory]:
        initial = self._parse_menu_categories(html)
        return self._walk_subcategories_parallel(initial)

    def _parse_menu_categories(self, html: str) -> List[ParsedCategory]:
        soup = BeautifulSoup(html, 'html.parser')
        aside = soup.select_one('aside.left-sidebar')
        if not aside:
            return []

        out: List[ParsedCategory] = []

        for li in aside.select('ul.facts-navigation > li.bigcat-nav'):
            parent_a = li.select_one('a.bigcat-nav-link')
            if not parent_a:
                continue

            parent_name = _clean_anchor_text(parent_a)
            parent_url = urljoin(self.base_url, parent_a.get('href') or '/')
            out.append(ParsedCategory(name=parent_name, url=parent_url, parent_url=None))

            for a in li.select('div.bigcat-nav-childs a.bigcat-nav-child'):
                child_name = _clean_anchor_text(a)
                out.append(
                    ParsedCategory(
                        name=child_name,
                        url=urljoin(self.base_url, a.get('href') or '/'),
                        parent_url=parent_url,
                    )
                )

        # Tail block: child-only categories without an explicit parent link
        for a in aside.select('li > div.bigcat-nav-childs a.bigcat-nav-child'):
            child_name = _clean_anchor_text(a)
            child_url = urljoin(self.base_url, a.get('href') or '/')
            parent_url = _parent_from_url(child_url)
            parent_url = normalize_url(parent_url) if parent_url else None
            if parent_url and is_site_root(parent_url, self.base_url):
                parent_url = None
            out.append(
                ParsedCategory(
                    name=child_name,
                    url=child_url,
                    parent_url=parent_url,
                )
            )

        uniq: Dict[str, ParsedCategory] = {}
        for c in out:
            uniq[c.url] = ParsedCategory(name=c.name, url=c.url, parent_url=c.parent_url)

        return list(uniq.values())

    def _extract_subcategories_from_category_page(self, html: str, current_parent_url: str) -> List[ParsedCategory]:
        soup = BeautifulSoup(html, 'html.parser')
        nav = soup.select_one('nav.subcategory-list')
        if not nav:
            return []

        result: List[ParsedCategory] = []
        for a in nav.select('a.subcategory-link'):
            href = a.get('href')
            if not href:
                continue

            name = _clean_anchor_text(a) or a.get_text(strip=True)
            parent_url = current_parent_url
            if is_site_root(current_parent_url, self.base_url):
                parent_url = None
            result.append(ParsedCategory(name=name, url=urljoin(self.base_url, href), parent_url=parent_url))
        return result

    def _walk_subcategories_parallel(self, initial: List[ParsedCategory]) -> List[ParsedCategory]:
        by_url: Dict[str, ParsedCategory] = {}
        for c in initial:
            key = normalize_url(c.url)
            by_url[key] = ParsedCategory(name=c.name, url=key, parent_url=c.parent_url)

        visited: Set[str] = set()
        frontier: List[ParsedCategory] = list(by_url.values())

        def _load_and_extract(cat: ParsedCategory) -> Tuple[str, List[ParsedCategory]]:
            '''
            Fetch a category page and return (cat.url, discovered subcategories).
            Swallow exceptions to keep the pool running.
            '''
            try:
                html = self.fetch(cat.url)
                subs = self._extract_subcategories_from_category_page(html, current_parent_url=cat.url)
                return cat.url, subs
            except Exception:
                return cat.url, []

        while frontier:
            batch = [c for c in frontier if c.url not in visited]
            frontier = []
            if not batch:
                break

            for c in batch:
                visited.add(c.url)

            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = [executor.submit(_load_and_extract, c) for c in batch]
                for fut in as_completed(futures):
                    _, subs = fut.result()
                    for sc in subs:
                        key = normalize_url(sc.url)
                        existing = by_url.get(key)
                        if existing:
                            if existing.parent_url is None and sc.parent_url is not None:
                                by_url[key] = ParsedCategory(name=sc.name, url=key, parent_url=sc.parent_url)
                        else:
                            by_url[key] = ParsedCategory(name=sc.name, url=key, parent_url=sc.parent_url)
                            if key not in visited:
                                frontier.append(by_url[key])

        return list(by_url.values())