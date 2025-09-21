from __future__ import annotations
from typing import Optional, Callable, Literal
import requests
from fake_useragent import UserAgent
from requests import Request

from common.exceptions import HTTPError404


class BaseHTTP:
    def __init__(
        self,
        fetch_func: Optional[Callable[[str], str]] = None,
        timeout: int = 15,
        user_agent: Optional[str] = None,
    ):
        self._fetch_func = fetch_func
        self._timeout = timeout

        self._ua = user_agent or UserAgent().random

    def fetch(self, url: str, headers: Optional[dict] = None, method: Literal['get', 'post'] = 'get', **kwargs) -> Request:
        if self._fetch_func:
            return self._fetch_func(url)

        if headers is None:
            headers = {'User-Agent': self._ua}

        data = {
            'url': url,
            'headers': headers,
            'timeout': self._timeout,
        }

        resp = requests.request(method, **data, **kwargs)

        if resp.status_code == 404:
            raise HTTPError404(resp.url, resp.status_code, resp.text)
        resp.raise_for_status()
        return resp

