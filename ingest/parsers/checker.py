from typing import Iterable

from ingest.models import Article
from ingest.parsers.interfaces import HasUrl


def are_cards_unique(cards: Iterable[HasUrl]) -> bool:
    urls = [card.url for card in cards]
    if not urls:
        return True

    return not Article.objects.filter(url__in=urls).exists()