import threading
from concurrent.futures import ThreadPoolExecutor
from django.contrib import admin
from django.db.models import QuerySet
from .models import ArticleIdea
from .services.idea import IdeaService


@admin.action(description='Process article ideas (max 10 concurrent)')
def process_idea(modeladmin, request, queryset: QuerySet[ArticleIdea]):
    # TODO celery
    def worker(idea):
        service = IdeaService(idea=idea)
        service.process_idea()

    def run_in_background(ideas):
        with ThreadPoolExecutor(max_workers=10) as executor:
            for idea in ideas:
                executor.submit(worker, idea)

    thread = threading.Thread(target=run_in_background, args=(list(queryset),), daemon=True)
    thread.start()

    modeladmin.message_user(
        request,
        f'Started processing {queryset.count()} ideas (max 10 concurrent) in background.'
    )