from __future__ import annotations
from django.db import transaction
from django.utils import timezone

from ingest.models import Site, Article
from ingest.choices import ArticleStatus
from ingest.parsers.factroom.interfaces import FeedCard
from ingest.services.types import FeedPersistStats


class FeedCardPersistService:
    '''
    Upsert FeedCard(s) into Article records:
      - Match by (site, url)
      - Create missing Article with minimal fields
      - Update existing fields only if new values are provided and different
      - Touch last_seen_at on every upsert
    '''

    def __init__(self, default_status: ArticleStatus = ArticleStatus.NEW):
        self.default_status: ArticleStatus = default_status

    @transaction.atomic
    def save_one(self, site: Site, card: FeedCard) -> tuple[Article, bool]:
        if not card.url:
            raise ValueError('FeedCard.url is required')

        now = timezone.now()

        article, created = Article.objects.get_or_create(
            site=site,
            url=card.url,
            defaults={
                'image_preview': card.image_preview,
                'title': card.title or '',
                'status': self.default_status,
                'discovered_at': now,
                'last_seen_at': now,
            },
        )

        if not created:
            fields_to_update: list[str] = []

            if card.title and article.title != card.title:
                article.title = card.title
                fields_to_update.append('title')

            if card.image_preview and article.image_preview != card.image_preview:
                article.image_preview = card.image_preview
                fields_to_update.append('image_preview')

            article.last_seen_at = now
            fields_to_update.append('last_seen_at')

            if fields_to_update:
                article.save(update_fields=fields_to_update)

        return article, created

    @transaction.atomic
    def save_many(self, site: Site, cards: list[FeedCard]) -> FeedPersistStats:
        stats = FeedPersistStats(
            total_input=len(cards),
            total_unique=0,
            created=0,
            updated=0,
        )

        by_url: dict[str, FeedCard] = {c.url: c for c in cards if c.url}
        stats['total_unique'] = len(by_url)

        for card in by_url.values():
            _, created = self.save_one(site, card)
            if created:
                stats['created'] += 1
            else:
                stats['updated'] += 1

        return stats