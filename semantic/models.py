from django.db import models
from django.utils import timezone
from pgvector.django import VectorField


class IngestArticleEmbedding(models.Model):
    MODEL = 'intfloat/multilingual-e5-large'

    article = models.OneToOneField(
        'ingest.Article',
        on_delete=models.CASCADE,
        related_name='embedding_e5_large',
    )

    vector = VectorField(dimensions=1024)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Article Embedding'
        verbose_name_plural = 'Article Embeddings'

    def __str__(self):
        return str(self.article_id)
