from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.crawler.crawler import (
    CrawlError,
    crawl_website,
)
from app.crawler.url_utils import (
    URLValidationError,
)
from app.models.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    PageResult,
)
from app.retrieval.chunker import build_chunks
from app.retrieval.hybrid import HybridRetriever
from app.services.session_store import session_store


router = APIRouter(
    prefix="/api",
    tags=["Analysis"],
)


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    status_code=status.HTTP_200_OK,
)
async def analyze_website(
    request: AnalyzeRequest,
) -> AnalyzeResponse:

    try:
        result = await crawl_website(
            str(request.url)
        )

    except URLValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except CrawlError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    # --------------------------------------------------
    # Build searchable chunks
    # --------------------------------------------------

    chunks = build_chunks(
        result.pages
    )

    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "No searchable content was found "
                "on the website."
            ),
        )

    # --------------------------------------------------
    # Build hybrid retrieval index
    # --------------------------------------------------

    retriever = HybridRetriever()

    retriever.build(chunks)

    # --------------------------------------------------
    # Create persistent in-memory session
    # --------------------------------------------------

    session = session_store.create(
        url=result.start_url,
        chunks=chunks,
        retriever=retriever,
    )

    # --------------------------------------------------
    # Preserve existing API response contract
    # --------------------------------------------------

    pages = [
        PageResult(
            url=crawled.url,
            title=crawled.page.title,
            text=crawled.page.text,
            characters=len(crawled.page.text),
            depth=crawled.depth,
        )
        for crawled in result.pages
    ]

    return AnalyzeResponse(
        success=True,
        session_id=session.session_id,
        url=result.start_url,
        pages_crawled=len(pages),
        pages_failed=len(result.failed_urls),
        total_characters=sum(
            page.characters
            for page in pages
        ),
        pages=pages,
    )