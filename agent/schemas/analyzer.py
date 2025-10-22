from typing import Optional
from pydantic import BaseModel, Field


class AnalysisResultSchema(BaseModel):
    image_prompt: Optional[str] = Field(
        default=None,
        description='A detailed prompt for AI image generation if appropriate; null if not applicable.'
    )
    research: Optional[str] = Field(
        default=None,
        description='A full research/search prompt if the article needs verification or expansion; null if not needed.'
    )