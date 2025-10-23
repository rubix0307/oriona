from typing import NewType

from django.db import transaction
from agent.service import AgentsService
from article.choices import IdeaStatus
from article.models import ArticleIdea, Article


AgentName = NewType('AgentName', str)

class IdeaService:

    def __init__(self, idea: ArticleIdea):
        self.idea = idea
        self.agents = AgentsService(timeout=3000)
        self.language = self.idea.language
        self.steps = self.get_processed_steps()
    
    def update_idea_status(self, status: IdeaStatus):
        self.idea.status = status
        self.idea.save(update_fields=['status'])
    
    def save_step(self, agent_name: AgentName, result: dict):
        new_process = self.idea.processes.create(
            idea=self.idea,
            agent_name=agent_name,
            result=result,
        )
        self.steps[agent_name] = new_process.result

    def get_processed_steps(self) -> dict[AgentName, dict]:
        processes = self.idea.processes.filter(idea__language=self.language).distinct('idea', 'agent_name')
        return {p.agent_name: p.result for p in processes}

    def process_idea(self) -> Article:
        # TODO separate calls to agents
        try:
            self.update_idea_status(IdeaStatus.ACCEPTED)

            article_body = self.idea.title + '\n' + self.idea.content

            if not (agent_name := 'analyzer') in self.steps:
                analyze = self.agents.analyzer(query=article_body, output_language=self.language)
                self.save_step(agent_name=agent_name, result=analyze.dict())

            if not (agent_name := 'researcher') in self.steps and self.steps['analyzer'].get('research'):
                research = self.agents.researcher(query=self.steps['analyzer']['research'], output_language=self.language)
                self.save_step(agent_name=agent_name, result=research.dict())

            agent_name = 'writer'
            article_result = self.agents.writer(query=article_body, data=self.steps, output_language=self.language)
            self.save_step(agent_name=agent_name, result=article_result.dict())

            with transaction.atomic():
                self.update_idea_status(IdeaStatus.PROCESSED)
                new_article, created = Article.objects.update_or_create(
                    idea=self.idea,
                    defaults=dict(
                        title=article_result.title,
                        content=article_result.content,
                    ),
                )
                return new_article
        except Exception as ex:
            self.update_idea_status(IdeaStatus.ERROR)
            raise ex
