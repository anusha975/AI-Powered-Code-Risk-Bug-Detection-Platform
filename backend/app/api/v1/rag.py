"""
Privacy-Aware Engineering Knowledge RAG API Endpoints.
"""

from typing import List
from fastapi import APIRouter, HTTPException, status

from app.schemas.rag import (
    KnowledgeDocument,
    DocumentIndexRequest,
    DocumentIndexResponse,
    RAGSearchRequest,
    RAGSearchResponse,
    RAGQueryRequest,
    RAGQueryResponse
)
from app.services.rag_service import RAGService

router = APIRouter(tags=["Engineering Knowledge RAG"])


@router.get(
    "/documents",
    response_model=List[KnowledgeDocument],
    status_code=status.HTTP_200_OK,
    summary="List Indexed Knowledge Documents",
    description="Returns all curated security guidelines, coding standards, and incident post-mortems in the vector library."
)
def list_knowledge_documents() -> List[KnowledgeDocument]:
    """Retrieve catalog of all indexed engineering documents."""
    return RAGService.list_all_documents()


@router.post(
    "/documents",
    response_model=DocumentIndexResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Index an Engineering Knowledge Document",
    description="Splits, embeds, and indexes a new security guideline or architecture document into the semantic vector store."
)
def index_knowledge_document(payload: DocumentIndexRequest) -> DocumentIndexResponse:
    """Ingest and index a new engineering knowledge document."""
    try:
        return RAGService.index_document(payload)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to index document: {str(exc)}"
        )


@router.post(
    "/search",
    response_model=RAGSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Semantic Vector Search for Knowledge Chunks",
    description="Performs cosine similarity search against indexed technical documentation with strict threshold pruning."
)
def search_knowledge_chunks(payload: RAGSearchRequest) -> RAGSearchResponse:
    """Execute raw semantic similarity vector search across knowledge base."""
    try:
        return RAGService.search_sources(payload)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Vector search failed: {str(exc)}"
        )


@router.post(
    "/query",
    response_model=RAGQueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Grounded Knowledge RAG Query & AI Explanation",
    description=(
        "Retrieves relevant security guidelines/post-mortems, verifies relevance threshold, "
        "and synthesizes a grounded answer with strict source attribution. "
        "Returns 'No relevant evidence found.' if no sources meet the threshold."
    )
)
async def query_knowledge_rag(payload: RAGQueryRequest) -> RAGQueryResponse:
    """Execute grounded RAG query with strict source attribution and anti-hallucination guard."""
    try:
        return await RAGService.query_knowledge(payload)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAG query execution failed: {str(exc)}"
        )
