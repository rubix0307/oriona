from django.contrib import admin
from .models import IngestArticleEmbedding


@admin.register(IngestArticleEmbedding)
class IngestArticleEmbeddingAdmin(admin.ModelAdmin):
    list_display = (
        'article', 'MODEL',
    )
    readonly_fields = ('article',)
