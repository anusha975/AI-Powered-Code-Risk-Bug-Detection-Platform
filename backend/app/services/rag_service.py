"""
RAG Service Layer for Engineering Knowledge Q&A and Document Indexing.
"""

from typing import List, Optional
import uuid

from app.schemas.rag import (
    KnowledgeDocument,
    DocumentIndexRequest,
    DocumentIndexResponse,
    RAGSearchRequest,
    RAGSearchResponse,
    RAGQueryRequest,
    RAGQueryResponse,
    RetrievedSource
)
from app.rag.engine import rag_engine
from app.utils.logger import logger


class RAGService:
    """Service providing high-level operations for Knowledge RAG."""

    @staticmethod
    def list_all_documents() -> List[KnowledgeDocument]:
        """List all indexed knowledge documents."""
        return rag_engine.list_documents()

    @staticmethod
    def index_document(req: DocumentIndexRequest) -> DocumentIndexResponse:
        """Index a new engineering knowledge document into the vector store."""
        doc_id = req.doc_id or f"DOC-USER-{uuid.uuid4().hex[:8].upper()}"

        doc = KnowledgeDocument(
            doc_id=doc_id,
            title=req.title,
            source_type=req.source_type,
            content=req.content,
            author=req.author or "Engineering Contributor",
            tags=req.tags or []
        )

        chunks_created = rag_engine.index_document(doc)

        logger.info(f"RAGService: Indexed document '{doc.title}' ({doc.doc_id}) into {chunks_created} chunks.")
        return DocumentIndexResponse(
            success=True,
            doc_id=doc.doc_id,
            title=doc.title,
            chunks_created=chunks_created,
            message=f"Document successfully indexed into {chunks_created} semantic vector chunk(s)."
        )

    @staticmethod
    def search_sources(req: RAGSearchRequest) -> RAGSearchResponse:
        """Perform semantic similarity search without LLM synthesis."""
        import time
        start_time = time.perf_counter()

        sources = rag_engine.search(
            query=req.query,
            top_k=req.top_k,
            threshold=req.similarity_threshold,
            source_type_filter=req.source_type_filter
        )

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        return RAGSearchResponse(
            query=req.query,
            results_count=len(sources),
            sources=sources,
            search_latency_ms=round(latency_ms, 2)
        )

    @staticmethod
    async def query_knowledge(req: RAGQueryRequest) -> RAGQueryResponse:
        """Execute full RAG retrieval + grounded AI explanation pipeline."""
        return await rag_engine.query_and_explain(
            query=req.query,
            top_k=req.top_k,
            threshold=req.similarity_threshold,
            source_type_filter=req.source_type_filter,
            provider_override=req.provider_override
        )
