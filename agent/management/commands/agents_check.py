import json
from django.core.management.base import BaseCommand

from agent.service import AgentsService

class Command(BaseCommand):

    def handle(self, *args, **options):

        s = AgentsService(timeout=2200)
        data = {}

        title = 'Научное название поцелуя — оскуляция.'
        analyze = s.analyzer(query=title)
        if analyze.research:
            research = s.researcher(query=analyze.research)
            data.update(json.loads(research.json()))

        text = s.writer(query=title, data=data)

        print(text)
        pass