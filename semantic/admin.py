from django.contrib import admin
from .models import IngestArticleEmbedding


@admin.register(IngestArticleEmbedding)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        'article', 'MODEL',
    )
