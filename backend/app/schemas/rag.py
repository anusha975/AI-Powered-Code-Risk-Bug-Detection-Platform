"""
Pydantic Schemas for Privacy-Aware Engineering Knowledge RAG.
"""

from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class SourceType(str, Enum):
    """Categorization of engineering knowledge sources."""
    SECURITY_GUIDELINE = "SECURITY_GUIDELINE"
    HISTORICAL_INCIDENT = "HISTORICAL_INCIDENT"
    CODING_STANDARD = "CODING_STANDARD"
    ARCHITECTURE_DOC = "ARCHITECTURE_DOC"


class DocumentChunk(BaseModel):
    """A semantic chunk of an engineering document stored in the vector index."""
    chunk_id: str = Field(..., description="Unique ID for this chunk")
    doc_id: str = Field(..., description="Parent document ID")
    title: str = Field(..., description="Document title")
    source_type: SourceType = Field(..., description="Category of knowledge source")
    section: str = Field(default="General", description="Section or heading title")
    content: str = Field(..., description="Text content of the chunk")
    char_count: int = Field(..., description="Length of chunk in characters")
    chunk_index: int = Field(..., description="Zero-indexed chunk offset in document")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional arbitrary metadata")


class KnowledgeDocument(BaseModel):
    """A full engineering knowledge document."""
    doc_id: str = Field(..., description="Unique document ID (e.g. DOC-OWASP-SQLI, INC-2024-001)")
    title: str = Field(..., description="Human-readable title")
    source_type: SourceType = Field(..., description="Category of knowledge source")
    content: str = Field(..., description="Complete document text (Markdown or plain text)")
    author: Optional[str] = Field("Security Architecture Team", description="Author or team owner")
    tags: List[str] = Field(default_factory=list, description="Categorical tags (e.g. ['sqli', 'owasp', 'python'])")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="Creation timestamp")


class DocumentIndexRequest(BaseModel):
    """Request payload to index a new engineering knowledge document."""
    doc_id: Optional[str] = Field(None, description="Optional custom document ID")
    title: str = Field(..., min_length=3, description="Title of the document")
    source_type: SourceType = Field(..., description="Category of knowledge source")
    content: str = Field(..., min_length=20, description="Full text or markdown content")
    author: Optional[str] = Field("Security Team", description="Author or owning team")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags for categorization")


class DocumentIndexResponse(BaseModel):
    """Response returned after indexing a document."""
    success: bool = Field(..., description="Whether indexing succeeded")
    doc_id: str = Field(..., description="Document ID")
    title: str = Field(..., description="Document title")
    chunks_created: int = Field(..., description="Number of vector chunks generated")
    message: str = Field(..., description="Status summary message")


class RetrievedSource(BaseModel):
    """Attributed source document snippet returned from vector search."""
    doc_id: str = Field(..., description="Source document identifier")
    title: str = Field(..., description="Document title")
    source_type: SourceType = Field(..., description="Knowledge source category")
    section: str = Field(..., description="Section heading")
    snippet: str = Field(..., description="Retrieved excerpt from document")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Cosine similarity score (0.0 to 1.0)")
    chunk_id: str = Field(..., description="Specific chunk ID")


class RAGSearchRequest(BaseModel):
    """Request payload for raw vector semantic similarity search."""
    query: str = Field(..., min_length=2, description="Developer natural language query or finding summary")
    source_type_filter: Optional[SourceType] = Field(None, description="Optional category filter")
    top_k: int = Field(default=3, ge=1, le=10, description="Maximum number of relevant chunks to retrieve")
    similarity_threshold: float = Field(default=0.35, ge=0.0, le=1.0, description="Minimum cosine similarity cutoff")


class RAGSearchResponse(BaseModel):
    """Response containing ranked vector search results."""
    query: str = Field(..., description="Original search query")
    results_count: int = Field(..., description="Number of results exceeding threshold")
    sources: List[RetrievedSource] = Field(default_factory=list, description="Ranked retrieved sources")
    search_latency_ms: float = Field(..., description="Vector search execution time in ms")


class RAGQueryRequest(BaseModel):
    """Request payload for grounded RAG query + AI explanation."""
    query: str = Field(..., min_length=2, description="Natural language question or security inquiry")
    source_type_filter: Optional[SourceType] = Field(None, description="Optional filter by knowledge category")
    top_k: int = Field(default=3, ge=1, le=8, description="Maximum context chunks to ground against")
    similarity_threshold: float = Field(default=0.35, ge=0.0, le=1.0, description="Minimum relevance threshold")
    provider_override: Optional[str] = Field(None, description="Optional LLM provider override ('local', 'external', 'mock')")


class RAGQueryResponse(BaseModel):
    """Comprehensive RAG answer with strict source attribution and missing-evidence handling."""
    query: str = Field(..., description="Original query")
    answer: str = Field(..., description="Grounded AI response or 'No relevant evidence found.'")
    is_evidence_found: bool = Field(..., description="True if relevant knowledge chunks met the threshold")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Highest relevance similarity score")
    sources: List[RetrievedSource] = Field(default_factory=list, description="Explicit source attributions")
    retrieval_latency_ms: float = Field(..., description="Total RAG pipeline execution latency in ms")
    privacy_guarantee: str = Field(
        default="Knowledge Boundary Invariant: The vector store indexes only approved guidelines and post-mortems. Proprietary source code is never automatically ingested.",
        description="Privacy enforcement statement"
    )
