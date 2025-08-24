from urllib.parse import urlparse

from django.db import transaction
from ingest.parsers.factroom.interfaces import ParsedCategory
from ingest.models import Site, Category
from ingest.services.common import normalize_url, is_site_root


class CategoryPersistService:
    def __init__(self, enable_new: bool = False):
        self.enable_new = enable_new

    @transaction.atomic
    def save(self, site: Site, items: list[ParsedCategory]) -> dict[str, int]:
        stats = {
            'total_input': len(items),
            'total_unique': 0,
            'created': 0,
            'updated': 0,
            'linked': 0,
        }

        uniq = self._dedupe(items)
        stats['total_unique'] = len(uniq)

        created, updated = self._upsert_nodes(site, uniq)
        stats['created'] += created
        stats['updated'] += updated

        existing = self._load_existing(uniq)

        created2, linked = self._link_parents(site, uniq, existing)
        stats['created'] += created2
        stats['linked'] += linked

        return stats

    @staticmethod
    def _dedupe(items: list[ParsedCategory]) -> dict[str, ParsedCategory]:
        # last occurrence wins
        return {c.url: c for c in items}

    def _upsert_nodes(self, site: Site, by_url: dict[str, ParsedCategory]) -> tuple[int, int]:
        created = 0
        updated = 0

        for url, pc in by_url.items():
            try:
                obj = Category.objects.get(url=url)

                fields_to_update: list[str] = []

                if obj.site_id != site.id:
                    obj.site = site
                    fields_to_update.append('site')

                if pc.name and obj.name != pc.name:
                    obj.name = pc.name
                    fields_to_update.append('name')

                if fields_to_update:
                    obj.save(update_fields=fields_to_update + ['updated_at'])
                    updated += 1

            except Category.DoesNotExist:
                Category.objects.create(
                    site=site,
                    url=url,
                    name=pc.name or self._guess_name(url),
                    is_enabled=self.enable_new,
                    parent=None,
                )
                created += 1

        return created, updated

    @staticmethod
    def _load_existing(by_url: dict[str, ParsedCategory]) -> dict[str, Category]:
        urls = list(by_url.keys())
        return {c.url: c for c in Category.objects.filter(url__in=urls)}

    def _link_parents(
        self, site: Site, by_url: dict[str, ParsedCategory], existing: dict[str, Category]
    ) -> tuple[int, int]:
        created = 0
        linked = 0

        for pc in by_url.values():
            child = existing.get(pc.url)

            # Top level or site-root parent: ensure parent=None
            if not pc.parent_url or is_site_root(pc.parent_url, site.base_url):
                if child and child.parent_id is not None:
                    child.parent = None
                    child.save(update_fields=['parent', 'updated_at'])
                    linked += 1
                continue

            parent = existing.get(pc.parent_url)
            if parent is None:
                parent = self._create_missing_parent(site, pc.parent_url)
                existing[parent.url] = parent
                created += 1

            if child is None:
                child = Category.objects.create(
                    site=site,
                    url=pc.url,
                    name=pc.name or self._guess_name(pc.url),
                    is_enabled=self.enable_new,
                    parent=parent,
                )
                existing[pc.url] = child
                created += 1
                linked += 1
                continue

            if child.parent_id != parent.id:
                child.parent = parent
                child.save(update_fields=['parent', 'updated_at'])
                linked += 1

        return created, linked

    def _create_missing_parent(self, site: Site, parent_url: str) -> Category:
        return Category.objects.create(
            site=site,
            url=normalize_url(parent_url),
            name=self._guess_name(parent_url),
            is_enabled=self.enable_new,
        )

    @staticmethod
    def _guess_name(url: str) -> str:
        path = urlparse(url).path.rstrip('/')
        slug = path.split('/')[-1] if path else ''
        return slug.replace('-', ' ').capitalize() or url