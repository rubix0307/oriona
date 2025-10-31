from typing import Iterable
from article.models import Article, ArticleTextAnalysis
from text.services.web_text.service import WebTextService as AnalyzeService


class WebTextServiceCore:

    def __init__(self, service: AnalyzeService | None = None):
        self.service = service or AnalyzeService()

    def submit(self, article: Article) -> ArticleTextAnalysis:
        uid = self.service.submit_text(
            text=article.content,
        )
        article_text = ArticleTextAnalysis.objects.update_or_create(article_id=article.id, uid=uid)
        return article_text

    def submit_many(self, articles: Iterable[Article]) -> list[ArticleTextAnalysis]:
        submited_articles = []
        for article in articles:
            article_text = self.submit(article=article)
            submited_articles.append(article_text)
        return submited_articles

    def get_result(self, submited_article: ArticleTextAnalysis) -> ArticleTextAnalysis:
        result = self.service.wait_result(
            uid=submited_article.uid,
            jsonvisible='detail',
        )
        article_text = ArticleTextAnalysis.from_service(article_id=submited_article.article.id, result=result)
        return article_text

    def get_results(self, submited_articles: Iterable[ArticleTextAnalysis]) -> list[ArticleTextAnalysis]:
        results = []
        for submited_article in submited_articles:
            article_text = self.get_result(submited_article=submited_article)
            results.append(article_text)
        return results