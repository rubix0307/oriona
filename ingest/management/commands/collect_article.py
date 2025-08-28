from urllib.parse import urljoin
from django.core.management.base import BaseCommand, CommandError

from ingest.models import Site
from ingest.parsers.factroom.parser_article import FactroomArticleParser


class Command(BaseCommand):
    help = "Fetch and parse a Factroom article by URL."

    def add_arguments(self, parser):
        parser.add_argument(
            "slug",
            type=str,
            help="Site slug (e.g. factroom)",
        )
        parser.add_argument(
            "url",
            type=str,
            help="Absolute or relative article URL (e.g. /zhivotnye/zemnovodnye/lyagushki/uzhasnyj-yadovityj-listolaz/)",
        )

    def handle(self, *args, **options):
        slug = options["slug"]
        url_arg = options["url"]

        try:
            site = Site.objects.get(slug=slug, is_active=True)
        except Site.DoesNotExist:
            raise CommandError(f'Active site with slug="{slug}" not found')

        # build absolute url if relative
        if url_arg.startswith("http://") or url_arg.startswith("https://"):
            article_url = url_arg
        else:
            article_url = urljoin(site.base_url, url_arg)

        self.stdout.write(self.style.NOTICE(f"[{slug}] Fetching article: {article_url}"))

        parser = FactroomArticleParser(base_url=site.base_url)
        parsed = parser.parse(url=article_url)

        self.stdout.write(self.style.SUCCESS(f"[{slug}] Parsed article"))
        self.stdout.write(f"URL: {parsed.url}")
        self.stdout.write(f"Title: {parsed.title!r}")
        self.stdout.write(f"Published: {parsed.published_at}")
        self.stdout.write("--- BODY START ---")
        self.stdout.write(parsed.content_text[:1000] if parsed.content_text else '')  # print only first 1000 chars
        self.stdout.write("--- BODY END ---")