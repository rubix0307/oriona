import asyncio
from typing import List, Optional
from pydantic import BaseModel, Field
from agents import Agent, Runner, WebSearchTool

URL_PATTERN = r'^https?://.+'

class Source(BaseModel):
    url: str = Field(..., description='Absolute URL', pattern=URL_PATTERN)
    title: Optional[str] = None
    outlet: Optional[str] = None
    published: Optional[str] = None

class ResearchMemo(BaseModel):
    topic: str
    summary: str
    details: List[str] = Field(default_factory=list)
    controversies: List[str] = Field(default_factory=list)
    sources: List[Source] = Field(default_factory=list)

class FinalReport(BaseModel):
    topic: str
    summary: str
    details: List[str] = Field(default_factory=list)
    controversies: List[str] = Field(default_factory=list)
    sources: List[Source] = Field(default_factory=list)
    article_markdown: str

researcher = Agent(
    name='Researcher',
    model='gpt-5',
    tools=[WebSearchTool()],
    output_type=ResearchMemo,
    instructions='Собери проверяемые факты и источники по теме. Верни краткий консолидированный конспект (ResearchMemo).',
)

writer = Agent(
    name='Writer',
    model='gpt-5',
    output_type=FinalReport,
    instructions=('На основе ResearchMemo подготовь итоговый отчёт FinalReport: '
                  'сохрани поля memo и сгенерируй article_markdown (Markdown). Без выдумок.'),
)

hub = Agent(
    name='Hub',
    model='gpt-5',
    handoffs=[researcher, writer],
    instructions=('Сначала делегируй задачу Researcher для сбора фактов. '
                  'Затем передай результат Writer для подготовки итогового отчёта.'),
)

researcher.handoffs = [writer]


QUERY = 'В левом верхнем углу картины «Крик» 1893 года есть небольшая надпись'
STYLE = 'Стиль: деловой, короткие абзацы, подзаголовки, факты и цифры.'

async def main():
    user_input = f'{QUERY}\n\n{STYLE}'
    result = await Runner.run(hub, user_input, max_turns=8)
    report = result.final_output_as(FinalReport)

    print('\nSUMMARY')
    print(report.summary)
    print('\nDETAILS')
    for d in report.details:
        print('•', d)
    if report.controversies:
        print('\nCONTROVERSIES')
        for c in report.controversies:
            print('•', c)
    print('\nSOURCES')
    for s in report.sources:
        print('-', s.outlet or s.title or s.url, '->', s.url)
    print('\nARTICLE (Markdown)\n')
    print(report.article_markdown)

if __name__ == '__main__':
    asyncio.run(main())