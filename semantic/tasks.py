from celery import shared_task
from ingest.models import Article
from semantic.services import EmbeddingIngestService


def cold_start_articles_embedding(limit: int = 1000) -> None:
    service = EmbeddingIngestService()

    articles = Article.objects.filter(
        content__content_html__isnull=False,
        content__content_text__isnull=False,
        embedding_e5_large__isnull=True,
    ).select_related('content')[:limit]
    for article in articles:
        service.save_article_embedding(article=article)


@shared_task(name='embedding_new_articles_task', ignore_result=True)
def embedding_articles_task(limit: int = 1000):
    cold_start_articles_embedding(limit=limit)
