from typing import List, Optional, Literal, Dict, Any, Union, Annotated
from pydantic import BaseModel, Field, AnyHttpUrl, confloat


class AddTextOptions(BaseModel):
    exceptdomain: Optional[List[str]] = None
    excepturl: Optional[List[str]] = None
    visible: Optional[Literal['vis_on']] = None
    copying: Optional[Literal['noadd']] = None
    callback: Optional[AnyHttpUrl] = None

    def to_form(self) -> Dict[str, Any]:
        form: Dict[str, Any] = {}
        if self.exceptdomain:
            form['exceptdomain'] = ','.join(self.exceptdomain)
        if self.excepturl:
            form['excepturl'] = ','.join(self.excepturl)
        if self.visible:
            form['visible'] = self.visible
        if self.copying:
            form['copying'] = self.copying
        if self.callback:
            form['callback'] = str(self.callback)
        return form


class UrlMatch(BaseModel):
    url: str
    plagiat: Annotated[float, Field(strict=True, ge=0, le=100)]
    words: Optional[str] = None

class ResultJson(BaseModel):
    date_check: str
    unique: confloat(ge=0, le=100) | float
    urls: List[UrlMatch] = Field(default_factory=list)
    clear_text: Optional[str] = None

class SpellIssue(BaseModel):
    error_type: str
    reason: str
    error_text: str
    replacements: List[str] = Field(default_factory=list)
    start: Annotated[float, Field(strict=True, ge=0,)]
    end: Annotated[float, Field(strict=True, ge=0,)]

class KeyItem(BaseModel):
    key_title: str
    count: Annotated[float, Field(strict=True, ge=0,)]

class GroupedKeyItem(BaseModel):
    key_title: str
    count: Annotated[float, Field(strict=True, ge=0,)]
    sub_keys: List[KeyItem] = Field(default_factory=list)

class SeoCheck(BaseModel):
    count_chars_with_space: Annotated[float, Field(strict=True, ge=0,)]
    count_chars_without_space: Annotated[float, Field(strict=True, ge=0,)]
    count_words: Annotated[float, Field(strict=True, ge=0,)]
    water_percent: Annotated[float, Field(strict=True, ge=0,)]
    spam_percent: Annotated[float, Field(strict=True, ge=0,)]
    mixed_words: List[int] = Field(default_factory=list)
    list_keys: List[KeyItem] = Field(default_factory=list)
    list_keys_group: List[GroupedKeyItem] = Field(default_factory=list)

class CheckResult(BaseModel):
    uid: str
    text_unique: Optional[confloat(ge=0, le=100)] = None
    result_json: Optional[ResultJson] = None
    spell_check: Optional[Union[List[SpellIssue], str]] = None
    seo_check: Optional[Union[SeoCheck, str]] = None
    raw: Dict[str, Any] = Field(default_factory=dict)