from pydantic import BaseModel


class QueryCountItem(BaseModel):
    query: str
    count: int


class TopRequestsResult(BaseModel):
    input_query: str
    total_count: int
    requests: list[QueryCountItem]
    associations: list[QueryCountItem]