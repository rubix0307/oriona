from typing import TypedDict, Literal, Optional
from django.db.models import F, FloatField, QuerySet
from django.db.models.expressions import RawSQL, ExpressionWrapper, Value
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models.functions import Coalesce

from .models import IngestArticleEmbedding
from .providers import E5Provider


class SearchHit(TypedDict):
    article_id: int
    url: str
    title: str
    score: float


class SearchService:

    def __init__(
        self,
        embedding_provider: Optional[E5Provider] = None,
        language_config: Literal['russian'] = 'russian',
        max_limit: int = 50,
    ):
        self.embedding_provider = embedding_provider
        if embedding_provider is None:
            self.embedding_provider = E5Provider()

        self.language_config = language_config
        self.max_limit = max_limit

    def embed_query(self, query: str) -> list[float]:
        return self.embedding_provider.embed_query(text=query)

    def add_cosine_similarity(self, embeddings_queryset: QuerySet[IngestArticleEmbedding], query: str) -> QuerySet[IngestArticleEmbedding]:
        sim_sql = '1 - (vector <=> %s::vector)'
        return embeddings_queryset.annotate(
            cos_sim=RawSQL(sim_sql, (self.embed_query(query),), output_field=FloatField())
        )

    def add_bm25(self, query: str, embeddings_queryset: QuerySet[IngestArticleEmbedding],) -> QuerySet[IngestArticleEmbedding]:
        # TODO extra SearchVectorField for ingest.ArticleContent
        text_search = SearchQuery(query, config=self.language_config)
        return embeddings_queryset.annotate(
            bm25=Coalesce(
                SearchRank(
                    SearchVector('article__title', weight='A', config=self.language_config) +
                    SearchVector('article__content__content_text', weight='B', config=self.language_config),
                    text_search,
                ),
                Value(0.0, output_field=FloatField()),
            )
        )

    @staticmethod
    def add_score(embeddings_queryset: QuerySet[IngestArticleEmbedding],) -> QuerySet[IngestArticleEmbedding]:
        return embeddings_queryset.annotate(
            score=ExpressionWrapper(
                Value(0.8, output_field=FloatField()) * F('cos_sim')
                + Value(0.2, output_field=FloatField()) * F('bm25'),
                output_field=FloatField(),
            )
        )

    def search(self, query: str, limit: int = 10) -> list[SearchHit]:
        if not query.strip():
            return []

        em_q: QuerySet[IngestArticleEmbedding] = IngestArticleEmbedding.objects.select_related(
            'article', 'article__content'
        )
        em_q = self.add_cosine_similarity(
            embeddings_queryset=em_q,
            query=query,
        )
        em_q = self.add_bm25(
            embeddings_queryset=em_q,
            query=query,
        )
        em_q = self.add_score(
            embeddings_queryset=em_q,
        )
        em_q = em_q.order_by('-score')[:max(1, min(limit, self.max_limit))]

        return [
            {
                'article_id': e.article.id,
                'url': e.article.url,
                'title': e.article.title or e.article.url,
                'score': float(e.score),
            }
            for e in em_q
        ]

