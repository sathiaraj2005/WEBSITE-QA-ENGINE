from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from app.retrieval.chunker import TextChunk
from app.retrieval.hybrid import HybridRetriever


@dataclass(slots=True)
class WebsiteSession:
    session_id: str
    url: str
    chunks: list[TextChunk]
    retriever: HybridRetriever


class SessionStore:

    def __init__(self) -> None:
        self._sessions: dict[
            str,
            WebsiteSession,
        ] = {}

    def create(
        self,
        url: str,
        chunks: list[TextChunk],
        retriever: HybridRetriever,
    ) -> WebsiteSession:

        session = WebsiteSession(
            session_id=str(uuid4()),
            url=url,
            chunks=chunks,
            retriever=retriever,
        )

        self._sessions[
            session.session_id
        ] = session

        return session

    def get(
        self,
        session_id: str,
    ) -> WebsiteSession | None:

        return self._sessions.get(
            session_id
        )

    def delete(
        self,
        session_id: str,
    ) -> None:

        self._sessions.pop(
            session_id,
            None,
        )


session_store = SessionStore()