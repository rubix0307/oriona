from typing import Optional, Iterable

from ingest.models import Category, Site
from ingest.parsers.base import BaseParser
from ingest.parsers.factroom.interfaces import DuplicateChecker
from ingest.parsers.factroom.parser_article import FactroomArticleParser
from ingest.parsers.factroom.parser_feed import FactroomFeedParser
from ingest.parsers.factroom.parser_paginator import parse_pagination
from ingest.parsers.factroom.types import URL, ParsedArticle, FeedCard
from ingest.parsers.interfaces import HasUrl


class FactroomParser(BaseParser):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.site = Site.objects.get(slug='factroom')

    def parse_by_categories(self, categories: Iterable[Category], parse_depth: Optional[int] = None) -> list[ParsedArticle]:
        cards: list[FeedCard] = []

        for category in categories:
            if category.site == self.site:
                cards += self.parse_feeds(start_url=category.url, parse_depth=parse_depth)

        return self.parse_articles(cards=cards)

    def parse_feeds(
        self,
        start_url: Optional[URL] = None,
        parse_depth: Optional[int] = None,
        checker: Optional[DuplicateChecker] = None
    ) -> list[FeedCard]:
        if not start_url:
            start_url = self.site.base_url

        cards: list[FeedCard] = []
        feed_parser = FactroomFeedParser()

        feed_url = start_url
        pages = 0
        while feed_url:
            pages += 1

            feed = feed_parser.parse(url=feed_url)
            cards += feed.cards

            if parse_depth and pages >= parse_depth:
                break
            if checker and not checker(cards=feed.cards):
                break

            paginator = parse_pagination(soup=feed.html_soup)
            feed_url = paginator.next_url

        return cards

    @staticmethod
    def parse_articles(cards: Iterable[HasUrl]) -> list[ParsedArticle]:
        parsed_articles: list[ParsedArticle] = []
        if not cards:
            return parsed_articles

        parser = FactroomArticleParser()
        for card in cards:
            parsed_articles.append(
                parser.parse(url=card.url)
            )

        return parsed_articles


