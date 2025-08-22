from django.contrib import admin
from .admin_actions import enable_categories, disable_categories
from .models import Site, Category, Article


class ReadOnlyTimestampsMixin:
    readonly_fields = ('created_at', 'updated_at')


class CategoryInline(admin.TabularInline):
    model = Category
    fields = ('name', 'url', 'parent', 'is_enabled', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    extra = 0
    show_change_link = True


@admin.register(Site)
class SiteAdmin(ReadOnlyTimestampsMixin, admin.ModelAdmin):
    list_display = ('slug', 'base_url', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('slug', 'name', 'base_url')
    inlines = [CategoryInline]


@admin.register(Category)
class CategoryAdmin(ReadOnlyTimestampsMixin, admin.ModelAdmin):
    list_display = ('name', 'site', 'parent', 'is_enabled', 'url', 'created_at', 'updated_at')
    list_filter = ('site', 'is_enabled')
    search_fields = ('name', 'url')
    autocomplete_fields = ('site', 'parent')
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