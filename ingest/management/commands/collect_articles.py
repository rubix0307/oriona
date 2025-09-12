from itertools import batched
from django.core.management.base import BaseCommand

from ingest.models import Article
from ingest.parsers.factroom.parser import FactroomParser
from ingest.services.article_persist import ArticlePersistService
from ingest.services.feedcard_persist import FeedCardPersistService


class Command(BaseCommand):

    def handle(self, *args, **options):

        parser = FactroomParser()

        parse_cards = False
        if parse_cards:
            cards = parser.parse_feeds(parse_depth=1)
            cards_stats = FeedCardPersistService().save_many(site=parser.site, cards=cards)
        else:
            cards = Article.objects.filter(site=parser.site, content__content_text__isnull=True)


        for chunk in batched(cards, 10):
            articles = parser.parse_articles(cards=chunk)
            articles_stats = ArticlePersistService().save_many(site=parser.site, items=articles)

        pass