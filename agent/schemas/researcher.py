from pydantic import BaseModel


class ResearchResultItemSourseSchema(BaseModel):
    name: str
    url: str

class ResearchResultItemSchema(BaseModel):
    quote: str
    source: ResearchResultItemSourseSchema

class ResearchResultSchema(BaseModel):
    sources: list[ResearchResultItemSchema]
    summary: str
