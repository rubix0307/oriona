from django.db import transaction

from ingest.models import Article
from .models import IngestArticleEmbedding
from .providers import E5Provider


class EmbeddingService:
    ...


class EmbeddingIngestService(EmbeddingService):

    @staticmethod
    def build_article_text(article: Article) -> str:
        return article.title + '\n' + article.content.content_text

    @transaction.atomic
    def save_article_embedding(self, article: Article) -> IngestArticleEmbedding:
        text = self.build_article_text(article)
        provider = E5Provider()
        vector = provider.embed_docs([text])[0]

        embedding, _ = IngestArticleEmbedding.objects.update_or_create(
            article=article,
            defaults={'vector': vector},
        )
        return embedding