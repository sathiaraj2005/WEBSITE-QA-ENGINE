# from __future__ import annotations

# from pydantic import BaseModel, Field, HttpUrl


# class AnalyzeRequest(BaseModel):
#     url: HttpUrl = Field(
#         ...,
#         description="Website URL to analyze.",
#     )


# class PageResult(BaseModel):
#     url: str
#     title: str
#     text: str
#     characters: int
#     depth: int


# class AnalyzeResponse(BaseModel):
#     success: bool
#     url: str
#     pages_crawled: int
#     pages_failed: int
#     total_characters: int
#     pages: list[PageResult]


from __future__ import annotations

from pydantic import BaseModel, Field, HttpUrl


class AnalyzeRequest(BaseModel):
    url: HttpUrl = Field(
        ...,
        description="Website URL to analyze.",
    )


class PageResult(BaseModel):
    url: str
    title: str
    text: str
    characters: int
    depth: int


class AnalyzeResponse(BaseModel):
    success: bool
    session_id: str
    url: str
    pages_crawled: int
    pages_failed: int
    total_characters: int
    pages: list[PageResult]


class AskRequest(BaseModel):
    session_id: str = Field(
        ...,
        min_length=1,
        description="Analysis session identifier.",
    )

    question: str = Field(
        ...,
        min_length=1,
        description="Question about the analyzed website.",
    )


class SourceResponse(BaseModel):
    url: str
    title: str
    evidence: str
    score: float


class AskResponse(BaseModel):
    answer: str
    sources: list[SourceResponse]