
from django.core.management.base import BaseCommand
from ingest.parsers.factroom.parser import FactroomParser
from ingest.services.article_persist import ArticlePersistService
from ingest.services.feedcard_persist import FeedCardPersistService


class Command(BaseCommand):

    def handle(self, *args, **options):
        parser = FactroomParser()
        cards = parser.parse_feeds(parse_depth=1)
        articles = parser.parse_articles(cards=cards)

        cards_stats = FeedCardPersistService().save_many(site=parser.site, cards=cards)
        articles_stats = ArticlePersistService().save_many(site=parser.site, items=articles)
        pass