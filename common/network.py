from __future__ import annotations
from typing import Optional, Callable, Literal
import requests
from requests import Request

from common.exceptions import HTTPError404


class BaseHTTP:
    def __init__(
        self,
        fetch_func: Optional[Callable[[str], str]] = None,
        timeout: int = 15,
        headers: Optional[dict] = None,
    ):
        self._fetch_func = fetch_func
        self._timeout = timeout
        self._headers = headers or {}

    def fetch(self, url: str, headers: Optional[dict] = None, method: Literal['get', 'post'] = 'get', **kwargs) -> Request:
        data = {
            'url': url,
            'timeout': self._timeout,
        }
        if headers is None:
             data.update({'headers': self._headers})

        resp = requests.request(method, **data, **kwargs)

        if resp.status_code == 404:
            raise HTTPError404(resp.url, resp.status_code, resp.text)
        resp.raise_for_status()
        return resp

