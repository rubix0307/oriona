from django.contrib import admin
from .models import ArticleIdea, ArticleProcess, Article
from . import actions


@admin.register(ArticleIdea)
class ArticleIdeaAdmin(admin.ModelAdmin):
    list_display = ('title', 'status')
    readonly_fields = ('source_ingest', )
    list_filter = ('status',)
    actions = (actions.process_idea, )


@admin.register(ArticleProcess)
class ArticleProcessAdmin(admin.ModelAdmin):
    list_display = ('idea', 'agent_name')


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', )