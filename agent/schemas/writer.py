from pydantic import BaseModel


class ArticleResultSchema(BaseModel):
    title: str
    content: str