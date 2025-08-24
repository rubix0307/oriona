# ingest/management/commands/collect_feed.py
from __future__ import annotations

from urllib.parse import urljoin
from django.core.management.base import BaseCommand, CommandError

from ingest.models import Site
from ingest.parsers.factroom.parser_feed import FactroomFeedParser
from ingest.services.feedcard_persist import FeedCardPersistService
from ingest.choices import ArticleStatus


class Command(BaseCommand):
    help = "Fetch, parse and persist a Factroom feed page into Article records."

    def add_arguments(self, parser):
        parser.add_argument("slug", type=str, help="Site slug (e.g. factroom)")
        parser.add_argument(
            "--page",
            type=str,
            required=True,
            help="Absolute or relative feed page URL (e.g. /zhivotnye/zemnovodnye/).",
        )
        parser.add_argument(
            "--print",
            dest="print_limit",
            type=int,
            default=20,
            help="Print first N parsed cards to stdout (default: 20).",
        )
        parser.add_argument(
            "--status",
            type=str,
            default=ArticleStatus.NEW,
            choices=[c for c, _ in ArticleStatus.choices],
            help="Default status for newly created articles (default: NEW).",
        )

    def handle(self, *args, **options):
        slug = options["slug"]
        page = options["page"]
        print_limit = options["print_limit"]
        default_status = options["status"]

        try:
            site = Site.objects.get(slug=slug, is_active=True)
        except Site.DoesNotExist:
            raise CommandError(f'Active site with slug="{slug}" not found')

        parser = FactroomFeedParser(base_url=site.base_url)

        # build absolute page url
        if page.startswith(("http://", "https://")):
            page_url = page
        else:
            page_url = urljoin(site.base_url, page)

        self.stdout.write(self.style.NOTICE(f"[{slug}] Fetching feed page: {page_url}"))
        html = parser.fetch(page_url)

        self.stdout.write(self.style.NOTICE(f"[{slug}] Parsing cards..."))
        cards = parser.parse(html)
        self.stdout.write(self.style.SUCCESS(f"[{slug}] Parsed {len(cards)} cards."))

        if print_limit and print_limit > 0:
            for i, c in enumerate(cards[:print_limit], start=1):
                self.stdout.write(
                    f"{i:02d}. url={c.url} | title={repr(c.title)} | image={c.image_preview}"
                )

        # persist
        self.stdout.write(self.style.NOTICE(f"[{slug}] Persisting cards..."))
        persist = FeedCardPersistService(default_status=default_status)
        stats = persist.save_many(site, cards)

        self.stdout.write(
            self.style.SUCCESS(
                f"[{slug}] Persisted: created={stats['created']} updated={stats['updated']} "
                f"(unique={stats['total_unique']}, input={stats['total_input']})"
            )
        )