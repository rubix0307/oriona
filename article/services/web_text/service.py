from typing import Iterable
from article.models import Article, ArticleTextAnalysis
from article.services.web_text.core import WebTextServiceCore


class WebTextService(WebTextServiceCore):

    def analyze(self, article: Article) -> ArticleTextAnalysis:
        submited_article = self.submit(article=article)
        article_text = self.get_result(submited_article=submited_article)
        return article_text

    def analyze_many(self, articles: Iterable[Article]) -> list[ArticleTextAnalysis]:
        submited_articles = self.submit_many(articles=articles)
        article_texts = self.get_results(submited_articles=submited_articles)
        return article_texts


__all__ = [WebTextService]