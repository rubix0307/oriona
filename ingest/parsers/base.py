from typing import Optional

from bs4 import BeautifulSoup
from requests import Request

from common.network import BaseHTTP


class BaseParser(BaseHTTP):

    def fetch(self, url: str, headers: Optional[dict] = None) -> str:
        return super(BaseParser, self).fetch(url, headers=headers).text

    def fetch_soup(self, url: str) -> BeautifulSoup:
        html = self.fetch(url=url)
        return BeautifulSoup(html, 'html.parser')
