from django.contrib import admin
from .models import ArticleIdea, ArticleAgentProcess, Article, ArticleTextAnalysis
from . import actions


@admin.register(ArticleIdea)
class ArticleIdeaAdmin(admin.ModelAdmin):
    list_display = ('title', 'status')
    readonly_fields = ('source_ingest', )
    list_filter = ('status',)
    actions = (actions.process_idea, )


@admin.register(ArticleAgentProcess)
class ArticleProcessAdmin(admin.ModelAdmin):
    list_display = ('idea', 'agent_name')


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', )

@admin.register(ArticleTextAnalysis)
class ArticleTextAnalysisAdmin(admin.ModelAdmin):
    list_display = ('article_id', 'unique' )