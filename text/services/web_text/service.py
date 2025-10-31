import time
from typing import Optional, Literal, Any, Union

from kombu.exceptions import HttpError

from .config import Settings
from .client import ApiClient
from .exceptions import WebTextError, WebTextResponceError, WebTextHttpError, WebTextTimeoutError
from .schemas import (
    AddTextOptions,
    CheckResult,
    ResultJson,
    SeoCheck,
    SpellIssue,
)


class WebTextService:
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or Settings.from_env()
        self.client = ApiClient(self.settings)

    def submit_text(
        self,
        text: str,
        options: Optional[AddTextOptions] = None,
    ) -> str:
        """
        :exceptions WebTextError, WebTextResponceError, WebTextHttpError
        """
        if not text:
            raise WebTextError('text must be non-empty')

        form: dict[str, Any] = {
            'userkey': self.settings.userkey,
            'text': text,
        }
        if options:
            form.update(options.to_form())

        try:
            data = self.client.post_form('/post', form)
            uid = data.get('text_uid') or data.get('uid')
            if not uid:
                raise WebTextResponceError('unexpected submit response, no uid')
            return uid
        except HttpError as e:
            raise WebTextHttpError(str(e))


    def get_result(
        self,
        uid: str,
        jsonvisible: Optional[Literal['detail', 'detail_view']] = None,
        ) -> CheckResult:
        form: dict[str, Any] = {
            'userkey': self.settings.userkey,
            'uid': uid,
        }
        if jsonvisible:
            form['jsonvisible'] = jsonvisible

        try:
            data = self.client.post_form('/post', form)
            text_unique = None
            if 'text_unique' in data:
                try:
                    text_unique = float(str(data['text_unique']).replace(',', '.'))
                except Exception:
                    text_unique = None

            parsed_result_json = None
            if 'result_json' in data and data['result_json']:
                try:
                    parsed_result_json = ResultJson.model_validate_json(data['result_json'])
                except Exception:
                    if isinstance(data['result_json'], dict):
                        parsed_result_json = ResultJson.model_validate(data['result_json'])

            spell_check: Optional[Union[list[SpellIssue], str]] = None
            if 'spell_check' in data:
                sc = data['spell_check']
                if isinstance(sc, str):
                    if sc.strip() == '':
                        spell_check = ''
                    else:
                        try:
                            spell_check = [SpellIssue.model_validate(x) for x in __import__('json').loads(sc)]
                        except Exception:
                            spell_check = None
                elif isinstance(sc, list):
                    spell_check = [SpellIssue.model_validate(x) for x in sc]

            seo_check: Optional[Union[SeoCheck, str]] = None
            if 'seo_check' in data:
                s = data['seo_check']
                if isinstance(s, str):
                    if s.strip() == '':
                        seo_check = ''
                    else:
                        try:
                            seo_check = SeoCheck.model_validate(__import__('json').loads(s))
                        except Exception:
                            seo_check = None
                elif isinstance(s, dict):
                    seo_check = SeoCheck.model_validate(s)

            return CheckResult(
                uid=uid,
                text_unique=text_unique,
                result_json=parsed_result_json,
                spell_check=spell_check,
                seo_check=seo_check,
                raw=data,
            )
        except WebTextHttpError as e:
            raise e

    def wait_result(
        self,
        uid: str,
        jsonvisible: Optional[Literal['detail', 'detail_view']] = None,
        timeout_sec: int = 120,
        poll_interval_sec: int = 3,
    ) -> CheckResult:
        deadline = time.time() + timeout_sec
        last_err: Optional[Exception] = None
        while time.time() < deadline:
            try:
                result = self.get_result(uid, jsonvisible=jsonvisible)
                if result.text_unique is not None and result.result_json is not None:
                    return result
            except Exception as e:
                last_err = e
            time.sleep(poll_interval_sec)
        if last_err:
            raise last_err
        raise WebTextTimeoutError('result not ready in given timeout')

    def get_balance(self) -> int:
        form = {
            'userkey': self.settings.userkey,
            'method': 'get_packages_info',
        }
        data = self.client.post_form('/account', form)
        size = data.get('size')
        if size is None:
            try:
                size = int(data.get('data', {}).get('size'))
            except Exception:
                pass
        if size is None:
            raise WebTextResponceError('unexpected account response')
        return int(size)