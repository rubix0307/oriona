from itertools import batched
from typing import Optional
from celery import shared_task
from ingest.choices import ArticleStatus
from ingest.models import Article
from ingest.parsers.factroom.duplicate_checker import are_cards_unique
from ingest.parsers.factroom.interfaces import DuplicateChecker
from ingest.parsers.factroom.parser import FactroomParser
from ingest.services.article_persist import ArticlePersistService
from ingest.services.feedcard_persist import FeedCardPersistService


def parse_factroom_cards(parse_depth: Optional[int] = None, checker: Optional[DuplicateChecker] = are_cards_unique):
    parser = FactroomParser()
    parsed_cards = parser.parse_feeds(parse_depth=parse_depth, checker=checker)
    FeedCardPersistService().save_many(site=parser.site, cards=parsed_cards)
    return parsed_cards


def parse_factroom_new_articles():
    parser = FactroomParser()
    cards = Article.objects.filter(
        site=parser.site,
        status=ArticleStatus.NEW,
        content__content_html__isnull=True,
        content__content_text__isnull=True,
    )
    for chunk in batched(cards, 10):
        articles = parser.parse_articles(cards=chunk)
        ArticlePersistService().save_many(site=parser.site, items=articles)


@shared_task(name='parse_factroom_task', ignore_result=True)
def parse_factroom_task():
    # polite scraping

    parse_factroom_cards(parse_depth=None, checker=are_cards_unique)
    parse_factroom_new_articles()
