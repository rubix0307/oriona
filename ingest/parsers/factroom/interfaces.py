from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass

from ingest.services.common import normalize_url


@dataclass
class ParsedCategory:
    name: str
    url: str
    parent_url: Optional[str] = None

    def __post_init__(self):
        self.name = self.name.strip()
        self.url = normalize_url(self.url)
        if self.parent_url:
            self.parent_url = normalize_url(self.parent_url)

class CategoryParser(ABC):
    @abstractmethod
    def parse(self, html: str) -> List[ParsedCategory]:
        ...
