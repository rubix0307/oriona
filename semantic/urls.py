from django.urls import path
from .views import semantic_search


urlpatterns = [
    path('search/', semantic_search, name='semantic-search'),
]