from typing import Literal
import requests
from pydantic import ValidationError

from common.network import BaseHTTP
from django.conf import settings
from interest.exceptions import InterestAPIError
from interest.types import TopRequestsResult


class InterestService(BaseHTTP):

    def __init__(self, *, timeout: int = 15, **kwargs) -> None:
        super().__init__(
            timeout=timeout,
            fetch_func=kwargs.get('fetch_func'),
            user_agent=kwargs.get('user_agent'),
        )
        self.timeout = timeout

    def get_requests(self, phrase: str, *,
        num_phrases: int = 100,
        regions: list[int] | None = None,
        devices: list[Literal['all', 'desktop', 'phone', 'tablet']] | None = None,
    ) -> TopRequestsResult:
        
        payload: dict[str, object] = {
            'phrase': phrase,
            'num_phrases': num_phrases,
            'devices': ['all'],
        }
        if regions:
            payload['regions'] = regions
        if devices:
            payload['devices'] = devices

        headers = {'Content-Type': 'application/json'}
        url = f'{settings.INTEREST_API_URL}/v1/requests'

        r = self.fetch(url, headers=headers, json=payload, method='post')

        try:
            return TopRequestsResult.model_validate(r.json())
        except ValidationError as e:
            raise InterestAPIError(f'Unexpected schema: {e}') from e