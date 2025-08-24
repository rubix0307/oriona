from __future__ import annotations
from typing import Optional, Callable
import requests
from fake_useragent import UserAgent


class BaseHTTPParser:
    def __init__(
        self,
        base_url: str,
        fetch_func: Optional[Callable[[str], str]] = None,
        timeout: int = 15,
        user_agent: Optional[str] = None,
    ):
        self.base_url = base_url.rstrip('/') + '/'
        self._fetch_func = fetch_func
        self._timeout = timeout

        self._ua = user_agent or UserAgent().random

    def fetch(self, url: str) -> str:
        if self._fetch_func:
            return self._fetch_func(url)

        headers = {'User-Agent': self._ua}
        resp = requests.get(url, headers=headers, timeout=self._timeout)
        resp.raise_for_status()
        return resp.text