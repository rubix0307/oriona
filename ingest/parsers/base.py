from __future__ import annotations
from typing import Optional, Callable
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from ingest.parsers.exceptions import HTTPError404


class BaseHTTPParser:
    def __init__(
        self,
        fetch_func: Optional[Callable[[str], str]] = None,
        timeout: int = 15,
        user_agent: Optional[str] = None,
    ):
        self._fetch_func = fetch_func
        self._timeout = timeout

        self._ua = user_agent or UserAgent().random

    def fetch(self, url: str) -> str:
        if self._fetch_func:
            return self._fetch_func(url)

        headers = {'User-Agent': self._ua}
        resp = requests.get(url, headers=headers, timeout=self._timeout)
        if resp.status_code == 404:
            raise HTTPError404(resp.url, resp.status_code, resp.text)
        resp.raise_for_status()
        return resp.text

    def fetch_soup(self, url: str) -> BeautifulSoup:
        html = self.fetch(url=url)
        return BeautifulSoup(html, 'html.parser')


class BaseParser(BaseHTTPParser):
    ...
