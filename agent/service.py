from __future__ import annotations
from typing import Any, Literal, TypeVar, Optional
from urllib.parse import urljoin

from django.conf import settings
from pydantic import ValidationError as PydValidationError
from fake_useragent import UserAgent

from common.network import BaseHTTP
from agent.schemas.common import Language
from .schemas.analyzer import AnalysisResultSchema
from .schemas.researcher import ResearchResultSchema
from .schemas.writer import ArticleResultSchema
from .exceptions import ValidationError


T = TypeVar('T')
class AgentsService:
    BASE_URL = settings.AGENTS_BASE_URL

    def __init__(self, *, timeout: float | int = 300) -> None:

        headers = {
            'Authorization': f'Bearer {settings.AGENTS_TOKEN}',
            'Accept': 'application/json',
            'User-Agent': UserAgent().random,
        }
        self._http = BaseHTTP(
            headers=headers,
            timeout=timeout,
        )

    def _fetch_agent(self, response: type[T], url: str, params: dict[str, Any], method: Literal['get', 'post'] = 'post', **kwargs) -> T:
        resp = self._http.fetch(url=urljoin(self.BASE_URL, url), method=method, params=params, **kwargs)
        try:
            return response.model_validate(resp.json())
        except PydValidationError as e:
            raise ValidationError(f'Invalid analyzer response: {e!s}') from e

    def analyzer(self, *, query: str, output_language: Language = Language.RU):
        params: dict[str, Any] = {'query': query, 'output_language': output_language}
        return self._fetch_agent(AnalysisResultSchema, url='/agents/analyzer', params=params)

    def researcher(self, *, query: str, output_language: Language = Language.RU):
        params: dict[str, Any] = {'query': query, 'output_language': output_language}
        return self._fetch_agent(ResearchResultSchema, url='/agents/researcher', params=params)

    def writer(self, *, query: str, output_language: Language = Language.RU, data: Optional[dict] = None,):
        params: dict[str, Any] = {'query': query, 'output_language': output_language}
        return self._fetch_agent(ArticleResultSchema, url='/agents/writer', params=params, json=data)
