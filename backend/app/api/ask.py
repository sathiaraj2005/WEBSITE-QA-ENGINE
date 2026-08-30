from __future__ import annotations

from fastapi import (
    APIRouter,
    HTTPException,
    status,
)

from app.models.schemas import (
    AskRequest,
    AskResponse,
    SourceResponse,
)
from app.services.qa_pipeline import (
    qa_pipeline,
)
from app.services.session_store import (
    session_store,
)


router = APIRouter(
    prefix="/api",
    tags=["Questions"],
)


@router.post(
    "/ask",
    response_model=AskResponse,
    status_code=status.HTTP_200_OK,
)
async def ask_question(
    request: AskRequest,
) -> AskResponse:

    session = session_store.get(
        request.session_id
    )

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Analysis session not found."
            ),
        )

    try:
        result = qa_pipeline.answer_question(
            session=session,
            question=request.question,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    sources = [
        SourceResponse(
            url=citation.url,
            title=citation.title,
            evidence=citation.evidence,
            score=citation.score,
        )
        for citation in result.citations
    ]

    return AskResponse(
        answer=result.generated_answer.answer,
        sources=sources,
    )