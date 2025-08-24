from typing import Optional
from urllib.parse import urlparse, urlunparse, urljoin

from bs4 import Tag, NavigableString


def normalize_url(url: str) -> str:
    '''
    Normalize category URL:
    - force trailing slash
    - drop params, query, fragment
    '''
    p = urlparse(url)
    path = p.path or '/'
    if not path.endswith('/'):
        path += '/'
    return urlunparse((p.scheme, p.netloc, path, '', '', ''))

def is_site_root(u: str, base_url: str) -> bool:
    return normalize_url(u) == normalize_url(base_url)

def clean_text(s: str) -> str:
    return " ".join(s.split()).strip()

def clean_anchor_text(a: Tag) -> str:
    '''
    Return anchor text without <small> counters and <i> icons.
    '''
    parts: list[str] = []
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

def abs_url(base_url: str, href: Optional[str]) -> Optional[str]:
    if not href:
        return None
    try:
        return urljoin(base_url, href)
    except Exception:
        return None
