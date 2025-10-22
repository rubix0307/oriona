from __future__ import annotations
from enum import Enum
from pydantic import BaseModel, Field


class Language(str, Enum):
    EN = 'en'
    RU = 'ru'

class ErrorLoc(BaseModel):
    loc: list[str | int]
    msg: str
    type: str

class Error422(BaseModel):
    detail: list[ErrorLoc] = Field(default_factory=list)