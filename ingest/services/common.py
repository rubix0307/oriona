from urllib.parse import urlparse, urlunparse

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