from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .search import SearchService


@require_GET
def semantic_search(request):
    search_service = SearchService().search(
        query=request.GET.get('q', '')[:2000]
    )
    return JsonResponse({'results': search_service})