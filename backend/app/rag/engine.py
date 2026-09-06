"""
Core RAG Orchestration Engine for Privacy-Aware Engineering Knowledge.

Coordinates document chunking, vector indexing, similarity retrieval with threshold gating,
source attribution, and strictly grounded AI explanations.
"""

from typing import List, Dict, Optional, Tuple, Any
import time

from app.schemas.rag import (
    KnowledgeDocument,
    DocumentChunk,
    RetrievedSource,
    SourceType,
    RAGQueryResponse,
    RAGSearchResponse
)
from app.rag.chunker import DocumentChunker
from app.rag.embeddings import EmbeddingEngine
from app.rag.vector_store import VectorStore
from app.rag.knowledge_base import SEED_KNOWLEDGE_DOCUMENTS
from app.ai.providers import get_llm_provider
from app.utils.logger import logger


class RAGEngine:
    """Orchestrates privacy-aware knowledge indexing, semantic retrieval, and grounded Q&A."""

    def __init__(
        self,
        chunker: Optional[DocumentChunker] = None,
        embedding_engine: Optional[EmbeddingEngine] = None
    ) -> None:
        self.chunker = chunker or DocumentChunker(target_chunk_size=500, chunk_overlap=50)
        self.embedding_engine = embedding_engine or EmbeddingEngine()
        self.vector_store = VectorStore(self.embedding_engine)
        self.documents_catalog: Dict[str, KnowledgeDocument] = {}

        # Auto-seed the vector store with curated engineering knowledge
        self._seed_knowledge_library()

    def _seed_knowledge_library(self) -> None:
        """Populate the vector store with curated security guidelines and post-mortems."""
        for doc in SEED_KNOWLEDGE_DOCUMENTS:
            self.index_document(doc)
        logger.info(f"RAGEngine initialized: {len(self.documents_catalog)} documents, {self.vector_store.count} chunks indexed.")

    def index_document(self, doc: KnowledgeDocument) -> int:
        """
        Chunk and index a KnowledgeDocument into the vector store.
        Returns the number of chunks created.
        """
        self.documents_catalog[doc.doc_id] = doc
        chunks = self.chunker.chunk_document(doc)
        added_count = self.vector_store.add_chunks(chunks)
        return added_count

    def search(
        self,
        query: str,
        top_k: int = 3,
        threshold: float = 0.35,
        source_type_filter: Optional[SourceType] = None
    ) -> List[RetrievedSource]:
        """
        Perform vector similarity search and return ranked, attributed sources.
        """
        raw_results = self.vector_store.search(
            query=query,
            top_k=top_k,
            threshold=threshold,
            source_type_filter=source_type_filter
        )

        sources: List[RetrievedSource] = []
        for chunk, score in raw_results:
            sources.append(
                RetrievedSource(
                    doc_id=chunk.doc_id,
                    title=chunk.title,
                    source_type=chunk.source_type,
                    section=chunk.section,
                    snippet=chunk.content,
                    relevance_score=score,
                    chunk_id=chunk.chunk_id
                )
            )

        return sources

    async def query_and_explain(
        self,
        query: str,
        top_k: int = 3,
        threshold: float = 0.35,
        source_type_filter: Optional[SourceType] = None,
        provider_override: Optional[str] = None
    ) -> RAGQueryResponse:
        """
        Execute full RAG pipeline:
        1. Retrieve top-k relevant knowledge chunks.
        2. Verify evidence threshold.
        3. If evidence is below threshold -> Return 'No relevant evidence found.'
        4. If evidence is present -> Ground LLM with strict evidence and return attributed answer.
        """
        start_time = time.perf_counter()

        sources = self.search(
            query=query,
            top_k=top_k,
            threshold=threshold,
            source_type_filter=source_type_filter
        )

        # Anti-hallucination guard: Missing evidence handling
        if not sources:
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            return RAGQueryResponse(
                query=query,
                answer="No relevant evidence found.",
                is_evidence_found=False,
                confidence_score=0.0,
                sources=[],
                retrieval_latency_ms=round(latency_ms, 2)
            )

        top_confidence = sources[0].relevance_score

        # Grounded Answer Synthesis
        provider = get_llm_provider(provider_override)
        answer = await self._synthesize_grounded_answer(
            query=query,
            sources=sources,
            provider=provider
        )

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        return RAGQueryResponse(
            query=query,
            answer=answer,
            is_evidence_found=True,
            confidence_score=top_confidence,
            sources=sources,
            retrieval_latency_ms=round(latency_ms, 2)
        )

    async def _synthesize_grounded_answer(
        self,
        query: str,
        sources: List[RetrievedSource],
        provider: Any
    ) -> str:
        """
        Generate grounded answer based strictly on retrieved sources.
        """
        # Assemble context blocks with strict attribution headers
        context_blocks = []
        for i, src in enumerate(sources, 1):
            context_blocks.append(
                f"[Source {i} - {src.doc_id}: {src.title} (Section: {src.section})]\n{src.snippet}"
            )
        combined_context = "\n\n---\n\n".join(context_blocks)

        system_prompt = (
            "You are a specialized security engineering documentation assistant. "
            "Answer the developer's question STRICTLY based on the provided retrieved documentation sources. "
            "Do NOT invent guidelines, APIs, or historical incidents. "
            "If the provided sources do not contain the answer, state 'No relevant evidence found.' "
            "Always cite the source document IDs (e.g. [DOC-SEC-SQLI-001] or [INC-2024-001]) when explaining."
        )

        user_prompt = (
            f"Developer Question: {query}\n\n"
            f"Retrieved Evidence:\n{combined_context}\n\n"
            "Provide a clear, grounded answer citing the source document IDs above:"
        )

        try:
            # Check provider type
            if hasattr(provider, "_query_local_model"):
                raw_ans = await provider._query_local_model(system_prompt, user_prompt)
                if raw_ans and len(raw_ans.strip()) > 10:
                    return raw_ans.strip()
        except Exception as exc:
            logger.warning(f"RAG LLM synthesis error ({exc}). Using deterministic summary.")

        # Deterministic grounded synthesis fallback (Mock / Fast path)
        primary_source = sources[0]
        answer_lines = [
            f"Based on **{primary_source.title}** (`{primary_source.doc_id}`):",
            "",
            primary_source.snippet.strip().split("\n\n")[0] if "\n\n" in primary_source.snippet else primary_source.snippet.strip(),
            "",
            "### Recommended Key Takeaways:"
        ]

        for s in sources:
            answer_lines.append(f"- **{s.title}** (`{s.doc_id}` - *{s.section}*): Verified relevance score of {int(s.relevance_score * 100)}%.")

        return "\n".join(answer_lines)

    def list_documents(self) -> List[KnowledgeDocument]:
        """Return all cataloged knowledge documents."""
        return list(self.documents_catalog.values())

    def get_document(self, doc_id: str) -> Optional[KnowledgeDocument]:
        """Retrieve a specific knowledge document by ID."""
        return self.documents_catalog.get(doc_id)


# Global singleton engine instance
rag_engine = RAGEngine()
