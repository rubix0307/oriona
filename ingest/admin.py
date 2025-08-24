from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .admin_actions import enable_categories, disable_categories
from .models import Site, Category, Article


class ReadOnlyTimestampsMixin:
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Site)
class SiteAdmin(ReadOnlyTimestampsMixin, admin.ModelAdmin):
    list_display = (
        'slug', 'base_url', 'is_active', 'categories_count_link', 'created_at', 'updated_at',
    )
    list_filter = ('is_active',)
    search_fields = ('slug', 'name', 'base_url')
    inlines: list = []

    readonly_fields = ReadOnlyTimestampsMixin.readonly_fields + ('categories_count_link',)

    fieldsets = (
        (None, {'fields': ('slug', 'name', 'base_url', 'is_active')}),
        ('Stats', {'fields': ('categories_count_link',)}),
        ('Timestamps', {'fields': ReadOnlyTimestampsMixin.readonly_fields}),
    )

    def categories_count_link(self, obj: Site):
        count = obj.categories.count()
        url = (
            reverse('admin:ingest_category_changelist')
            + f'?o=-3&site__id__exact=1'
        )
        return format_html('<a href="{}">{}</a>', url, f'{count} categories')
    categories_count_link.short_description = 'Categories'


@admin.register(Category)
class CategoryAdmin(ReadOnlyTimestampsMixin, admin.ModelAdmin):
    list_display = ('name', 'site', 'parent', 'is_enabled', 'url', 'created_at', 'updated_at')
    list_filter = ('site__name', 'is_enabled')
    search_fields = ('name', 'url')
    autocomplete_fields = ('site', 'parent')
    list_select_related = ('site', 'parent')  # fewer queries on changelist
    readonly_fields = ReadOnlyTimestampsMixin.readonly_fields
    actions = [enable_categories, disable_categories]


@admin.register(Article)
class ArticleAdmin(ReadOnlyTimestampsMixin, admin.ModelAdmin):
    list_display = (
        'title', 'site', 'category', 'status',
        'published_at', 'discovered_at', 'last_seen_at', 'last_crawled_at',
        'created_at', 'updated_at',
    )
    list_filter = ('site', 'status', 'published_at')
    search_fields = ('title', 'url')
    autocomplete_fields = ('site', 'category')
    date_hierarchy = 'published_at'
    readonly_fields = ('discovered_at', 'last_seen_at', 'last_crawled_at') + ReadOnlyTimestampsMixin.readonly_fields