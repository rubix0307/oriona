from __future__ import annotations

from typing import Iterable
from django.db import transaction
from django.utils import timezone

from ingest.models import Site, Article, ArticleContent
from ingest.choices import ArticleStatus
from ingest.parsers.factroom.types import ParsedArticle
from ingest.services.interfaces import ArticlePersistInterface
from ingest.services.types import ArticlePersistStats


class ArticlePersistService(ArticlePersistInterface):
    '''
    Upsert ParsedArticle(s) into Article/ArticleContent:

    - Match Article by (site, url)
    - Create Article with default status if missing
    - Update fields only when new values are provided AND differ
    - Touch `last_seen_at` on each upsert
    - Upsert ArticleContent (create if missing; update only changed fields)
    '''

    def __init__(self, default_status: ArticleStatus = ArticleStatus.NEW) -> None:
        self.default_status: ArticleStatus = default_status

    @transaction.atomic
    def save_one(self, site: Site, parsed: ParsedArticle) -> tuple[Article, bool]:
        now = timezone.now()

        article, created = Article.objects.get_or_create(
            site=site,
            url=parsed.url,
            defaults={
                'status': self.default_status,
                'title': (parsed.title or ''),
                'image_preview': parsed.lead_image,
                'published_at': parsed.published_at,
                'discovered_at': now,
                'last_seen_at': now,
            },
        )

        fields_to_update: list[str] = []
        if not created:
            # title
            if parsed.title and parsed.title != article.title:
                article.title = parsed.title
                fields_to_update.append('title')

            # image preview
            if parsed.lead_image and parsed.lead_image != article.image_preview:
                article.image_preview = parsed.lead_image
                fields_to_update.append('image_preview')

            # published_at
            if parsed.published_at and parsed.published_at != article.published_at:
                article.published_at = parsed.published_at
                fields_to_update.append('published_at')

            # last_seen_at
            article.last_seen_at = now
            fields_to_update.append('last_seen_at')

            if fields_to_update:
                article.save(update_fields=fields_to_update)

        content_created = False
        content_updated = False

        has_html = bool(parsed.content_html)
        has_text = bool(parsed.content_text)

        if has_html or has_text:
            content, c_created = ArticleContent.objects.get_or_create(
                article=article,
                defaults={
                    'content_html': parsed.content_html,
                    'content_text': parsed.content_text,
                },
            )
            content_created = c_created
            if not c_created:
                c_fields: list[str] = []
                if has_html and parsed.content_html != content.content_html:
                    content.content_html = parsed.content_html
                    c_fields.append('content_html')
                if has_text and parsed.content_text != content.content_text:
                    content.content_text = parsed.content_text
                    c_fields.append('content_text')
                if c_fields:
                    content.save(update_fields=c_fields)
                    content_updated = True

        article._content_created = content_created
        article._content_updated = content_updated

        return article, created

    @transaction.atomic
    def save_many(self, site: Site, items: Iterable[ParsedArticle]) -> ArticlePersistStats:
        stats: ArticlePersistStats = {
            'total_input': 0,
            'total_unique': 0,
            'created': 0,
            'updated': 0,
            'content_created': 0,
            'content_updated': 0,
        }

        # Deduplicate by URL
        by_url: dict[str, ParsedArticle] = {}
        for it in items:
            stats['total_input'] += 1
            if it.url:
                by_url[it.url] = it
        stats['total_unique'] = len(by_url)

        for parsed in by_url.values():
            article, created = self.save_one(site, parsed)
            if created:
                stats['created'] += 1
            else:
                stats['updated'] += 1

            # Inspect flags set in save_one()
            if getattr(article, '_content_created', False):  # type: ignore[attr-defined]
                stats['content_created'] += 1
            if getattr(article, '_content_updated', False):  # type: ignore[attr-defined]
                stats['content_updated'] += 1

        return stats