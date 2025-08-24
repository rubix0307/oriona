from __future__ import annotations
from typing import Optional, TypedDict
from bs4 import BeautifulSoup
import re


class PaginationInfo(TypedDict):
    current: int
    total: int
    next: Optional[int]


_HREF_PAGE_NUM_RE = re.compile(r"/page/(\d+)(?:/)?$")

def _extract_page_num_from_href(href: str) -> Optional[int]:
    if not href:
        return None
    m = _HREF_PAGE_NUM_RE.search(href)
    return int(m.group(1)) if m else None


def parse_pagination(html_page: BeautifulSoup | str) -> PaginationInfo:
    if isinstance(html_page, str):
        html_page = BeautifulSoup(html_page, 'html.parser')

    nav = html_page.select_one("div.navigation")
    if not nav:
        return PaginationInfo(current=1, total=1, next=None)

    current_el = nav.select_one(".page-numbers.current")
    if current_el and current_el.get_text(strip=True).isdigit():
        current = int(current_el.get_text(strip=True))
    else:
        current = 1

    total_candidates: list[int] = []
    for a in nav.select("a.page-numbers"):
        txt = a.get_text(strip=True)
        if txt.isdigit():
            total_candidates.append(int(txt))
        num_from_href = _extract_page_num_from_href(a.get("href", ""))
        if num_from_href is not None:
            total_candidates.append(num_from_href)

    if current:
        total_candidates.append(current)

    total = max(total_candidates) if total_candidates else (current or 1)
    next_el = nav.select_one("a.next.page-numbers")
    if next_el:
        next_num = _extract_page_num_from_href(next_el.get("href", ""))
    else:
        next_num = current + 1 if current and total and current < total else None

    return PaginationInfo(current=current, total=total, next=next_num)