from typing import Any
import requests
from requests import HTTPError

from .config import Settings
from .exceptions import ApiError, ERROR_HINTS, WebTextHttpError
from .utils import parse_kv_response


class ApiClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.session = requests.Session()

    def post_form(self, path: str, form: dict[str, Any]) -> dict[str, Any]:
        url = str(self.settings.base_url).rstrip('/') + path
        try:
            resp = self.session.post(url, data=form, timeout=30)
            resp.raise_for_status()
            data = parse_kv_response(resp.text)

            if 'error_code' in data:
                try:
                    code = int(data.get('error_code'))
                except Exception:
                    code = -1
                desc = data.get('error_desc') or ERROR_HINTS.get(code)
                raise WebTextHttpError(f'{code=}, {desc=}')

            return data
        except HTTPError as e:
            raise WebTextHttpError(str(e))