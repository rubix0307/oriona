from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from article.models import Article


class ArticleListView(ListView):
    model = Article
    template_name = "article/article_list.html"
    context_object_name = "articles"
    paginate_by = 15

def get_article(requests: WSGIRequest, pk: int):
    context = {
        'article': get_object_or_404(Article, pk=pk),
    }
    return render(requests, 'article/article.html', context=context)
