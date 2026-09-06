"""
Unit and Integration Tests for Module 9: Privacy-Aware Engineering Knowledge RAG.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.rag import (
    KnowledgeDocument,
    SourceType,
    DocumentIndexRequest,
    RAGSearchRequest,
    RAGQueryRequest
)
from app.rag.chunker import DocumentChunker
from app.rag.embeddings import EmbeddingEngine
from app.rag.vector_store import VectorStore
from app.rag.engine import RAGEngine
from app.services.rag_service import RAGService

client = TestClient(app)


def test_chunker_basic_and_overlap():
    """Verify DocumentChunker splits text into bounded chunks with metadata."""
    chunker = DocumentChunker(target_chunk_size=150, chunk_overlap=30)

    doc = KnowledgeDocument(
        doc_id="TEST-DOC-001",
        title="Test Document",
        source_type=SourceType.SECURITY_GUIDELINE,
        content=(
            "# Header 1\n\n"
            "This is paragraph one containing detailed information on security rules.\n\n"
            "# Header 2\n\n"
            "This is paragraph two detailing remediation steps and safe coding patterns.\n\n"
            "This is paragraph three adding more contextual information."
        )
    )

    chunks = chunker.chunk_document(doc)
    assert len(chunks) >= 2
    assert all(c.doc_id == "TEST-DOC-001" for c in chunks)
    assert all(c.title == "Test Document" for c in chunks)
    assert any(c.section == "Header 1" for c in chunks)
    assert any(c.section == "Header 2" for c in chunks)


def test_embedding_engine_cosine_similarity():
    """Verify EmbeddingEngine generates normalized vectors and calculates cosine similarity."""
    engine = EmbeddingEngine(dimension=256)

    v1 = engine.embed_text("sql injection parameterization")
    v2 = engine.embed_text("preventing sql injection with parameterized queries")
    v3 = engine.embed_text("baking chocolate chip cookies in the oven")

    sim_related = engine.cosine_similarity(v1, v2)
    sim_unrelated = engine.cosine_similarity(v1, v3)

    assert sim_related > 0.40
    assert sim_related > sim_unrelated
    assert sim_unrelated < 0.25


def test_vector_store_indexing_and_top_k():
    """Verify VectorStore indexes chunks and returns ranked top-k results."""
    chunker = DocumentChunker(target_chunk_size=300)
    store = VectorStore()

    doc1 = KnowledgeDocument(
        doc_id="DOC-SQL",
        title="SQL Security",
        source_type=SourceType.SECURITY_GUIDELINE,
        content="Always use parameterized queries to stop SQL injection attacks."
    )
    doc2 = KnowledgeDocument(
        doc_id="DOC-RCE",
        title="RCE Prevention",
        source_type=SourceType.CODING_STANDARD,
        content="Avoid eval and exec to prevent remote code execution vulnerabilities."
    )

    store.add_chunks(chunker.chunk_document(doc1))
    store.add_chunks(chunker.chunk_document(doc2))

    assert store.count >= 2

    # Query for SQL
    results_sql = store.search("sql injection parameterization", top_k=1, threshold=0.2)
    assert len(results_sql) == 1
    assert results_sql[0][0].doc_id == "DOC-SQL"

    # Query for eval
    results_rce = store.search("dynamic eval exec rce", top_k=1, threshold=0.2)
    assert len(results_rce) == 1
    assert results_rce[0][0].doc_id == "DOC-RCE"


def test_vector_store_category_filtering():
    """Verify VectorStore filters search results by SourceType."""
    chunker = DocumentChunker()
    store = VectorStore()

    doc_guideline = KnowledgeDocument(
        doc_id="DOC-G",
        title="SQL Guideline",
        source_type=SourceType.SECURITY_GUIDELINE,
        content="Guideline for parameterized SQL injection defense."
    )
    doc_incident = KnowledgeDocument(
        doc_id="INC-1",
        title="SQL Incident",
        source_type=SourceType.HISTORICAL_INCIDENT,
        content="Historical incident post-mortem on billing SQL injection exploit."
    )

    store.add_chunks(chunker.chunk_document(doc_guideline))
    store.add_chunks(chunker.chunk_document(doc_incident))

    # Search with category filter: HISTORICAL_INCIDENT only
    results = store.search(
        query="sql injection",
        top_k=5,
        threshold=0.1,
        source_type_filter=SourceType.HISTORICAL_INCIDENT
    )

    assert len(results) == 1
    assert results[0][0].doc_id == "INC-1"
    assert results[0][0].source_type == SourceType.HISTORICAL_INCIDENT


def test_rag_engine_seed_knowledge_preloaded():
    """Verify RAGEngine initializes with 10 seed knowledge documents."""
    engine = RAGEngine()
    docs = engine.list_documents()

    assert len(docs) >= 10
    doc_ids = [d.doc_id for d in docs]
    assert "DOC-SEC-SQLI-001" in doc_ids
    assert "DOC-SEC-RCE-001" in doc_ids
    assert "DOC-SEC-CMD-001" in doc_ids
    assert "INC-2024-001" in doc_ids
    assert "INC-2024-002" in doc_ids


@pytest.mark.asyncio
async def test_rag_query_sql_injection_grounding():
    """Verify RAG query for SQL injection returns attributed sources and high confidence."""
    engine = RAGEngine()

    res = await engine.query_and_explain(
        query="How do I prevent SQL injection in database queries?",
        top_k=3,
        threshold=0.30
    )

    assert res.is_evidence_found is True
    assert res.confidence_score >= 0.30
    assert len(res.sources) >= 1
    # Check that SQL injection document or incident is cited
    source_ids = [s.doc_id for s in res.sources]
    assert any("SQL" in sid for sid in source_ids)
    assert len(res.answer) > 20


@pytest.mark.asyncio
async def test_rag_query_command_injection_incident():
    """Verify RAG query for network incident retrieves INC-2024-002."""
    engine = RAGEngine()

    res = await engine.query_and_explain(
        query="What was the root cause of the network diagnostic traceroute incident?",
        top_k=2,
        threshold=0.30
    )

    assert res.is_evidence_found is True
    source_ids = [s.doc_id for s in res.sources]
    assert "INC-2024-002" in source_ids


@pytest.mark.asyncio
async def test_rag_query_missing_evidence_fallback():
    """Verify RAG returns 'No relevant evidence found.' when query has no relevant evidence."""
    engine = RAGEngine()

    res = await engine.query_and_explain(
        query="How to bake sourdough chocolate bread with yeast?",
        top_k=3,
        threshold=0.35
    )

    # Invariant: Must NOT hallucinate non-existent evidence
    assert res.is_evidence_found is False
    assert res.confidence_score == 0.0
    assert res.answer == "No relevant evidence found."
    assert len(res.sources) == 0


def test_api_rag_documents_list_endpoint():
    """Verify GET /api/rag/documents returns the document catalog."""
    res = client.get("/api/rag/documents")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 10


def test_api_rag_search_endpoint():
    """Verify POST /api/rag/search returns ranked chunks."""
    payload = {
        "query": "safe alternatives to eval function in Python",
        "top_k": 2,
        "similarity_threshold": 0.25
    }
    res = client.post("/api/rag/search", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert data["results_count"] >= 1
    assert len(data["sources"]) >= 1
    assert data["sources"][0]["doc_id"] == "DOC-SEC-RCE-001"


def test_api_rag_query_endpoint():
    """Verify POST /api/rag/query executes full grounded pipeline."""
    payload = {
        "query": "How to prevent unsafe pickle deserialization vulnerabilities?",
        "top_k": 2,
        "similarity_threshold": 0.25
    }
    res = client.post("/api/rag/query", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert data["is_evidence_found"] is True
    assert len(data["sources"]) >= 1
    assert "pickle" in data["answer"].lower() or "deserialization" in data["answer"].lower()


def test_api_rag_index_custom_document_and_query():
    """Verify custom document indexing and subsequent retrieval."""
    index_payload = {
        "doc_id": "DOC-CUSTOM-K8S-001",
        "title": "Kubernetes Pod Security Standard",
        "source_type": "SECURITY_GUIDELINE",
        "content": "# Kubernetes Pod Security\n\nAlways enforce readOnlyRootFilesystem and drop ALL Linux capabilities in securityContext.",
        "author": "CloudSec Team",
        "tags": ["kubernetes", "containers", "securityContext"]
    }

    # 1. Index document
    res_index = client.post("/api/rag/documents", json=index_payload)
    assert res_index.status_code == 201
    data_index = res_index.json()
    assert data_index["success"] is True
    assert data_index["chunks_created"] >= 1

    # 2. Search for the indexed document
    search_payload = {
        "query": "readOnlyRootFilesystem drop ALL Linux capabilities in securityContext",
        "top_k": 1,
        "similarity_threshold": 0.20
    }
    res_search = client.post("/api/rag/search", json=search_payload)
    assert res_search.status_code == 200
    data_search = res_search.json()
    assert data_search["results_count"] >= 1
    assert data_search["sources"][0]["doc_id"] == "DOC-CUSTOM-K8S-001"
