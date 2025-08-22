from django.contrib import admin


@admin.action(description="Enable selected categories")
def enable_categories(modeladmin, request, queryset):
    queryset.update(is_enabled=True)

@admin.action(description="Disable selected categories")
def disable_categories(modeladmin, request, queryset):
    queryset.update(is_enabled=False)