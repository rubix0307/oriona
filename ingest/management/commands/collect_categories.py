from django.core.management.base import BaseCommand, CommandError
from ingest.models import Site
from ingest.services.category_persist import CategoryPersistService
from ingest.parsers.factroom.parser_category import FactroomCategoryParser

PARSER_REGISTRY = {
    'factroom': FactroomCategoryParser,
}

class Command(BaseCommand):
    help = 'Collect and save categories for a given site (1 site = 1 parser).'

    def add_arguments(self, parser):
        parser.add_argument('slug', type=str, help='Site slug (e.g. factroom)')
        parser.add_argument(
            '--workers',
            type=int,
            default=10,
            help='Number of threads for parsing (default: 10)',
        )

    def handle(self, *args, **options):
        slug = options['slug']
        workers = options['workers']

        try:
            site = Site.objects.get(slug=slug, is_active=True)
        except Site.DoesNotExist:
            raise CommandError(f'Active site with slug="{slug}" not found')

        ParserCls = PARSER_REGISTRY.get(slug)
        if not ParserCls:
            raise CommandError(f'No parser registered for site "{slug}"')

        parser = ParserCls(base_url=site.base_url, max_workers=workers)

        self.stdout.write(self.style.NOTICE(f'[{slug}] Fetching main page: {site.base_url}'))
        main_html = parser.fetch(site.base_url)

        self.stdout.write(self.style.NOTICE(f'[{slug}] Parsing categories (workers={workers})...'))
        categories = parser.parse(main_html)
        self.stdout.write(self.style.NOTICE(f'[{slug}] Found {len(categories)} categories. Saving...'))

        stats = CategoryPersistService(enable_new=False).save(site, categories)

        self.stdout.write(self.style.SUCCESS(
            f'[{slug}] Done. '
            f'input={stats['total_input']} '
            f'unique={stats['total_unique']} '
            f'created={stats['created']} '
            f'updated={stats['updated']} '
            f'linked={stats['linked']}'
        ))