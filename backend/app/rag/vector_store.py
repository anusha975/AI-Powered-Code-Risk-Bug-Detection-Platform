"""
In-Memory Semantic Vector Store for Engineering Knowledge RAG.

Provides fast cosine-similarity search, category filtering, top-k ranking,
and minimum relevance threshold pruning across indexed document chunks.
"""

from typing import List, Tuple, Optional, Dict, Any
import numpy as np

from app.schemas.rag import DocumentChunk, SourceType
from app.rag.embeddings import EmbeddingEngine
from app.utils.logger import logger


class VectorStore:
    """In-memory vector database for indexing and searching technical knowledge chunks."""

    def __init__(self, embedding_engine: Optional[EmbeddingEngine] = None) -> None:
        self.embedding_engine = embedding_engine or EmbeddingEngine()
        self.chunks: List[DocumentChunk] = []
        self.vectors: np.ndarray = np.empty((0, self.embedding_engine.dimension), dtype=np.float32)

    def add_chunks(self, new_chunks: List[DocumentChunk]) -> int:
        """
        Embed and index a list of DocumentChunks into the vector database.
        """
        if not new_chunks:
            return 0

        texts = [f"{c.title} - {c.section}\n{c.content}" for c in new_chunks]
        new_vectors = self.embedding_engine.embed_batch(texts)

        if self.vectors.shape[0] == 0:
            self.vectors = new_vectors
        else:
            self.vectors = np.vstack([self.vectors, new_vectors])

        self.chunks.extend(new_chunks)
        logger.info(f"VectorStore: Indexed {len(new_chunks)} new chunks (Total chunks: {len(self.chunks)})")
        return len(new_chunks)

    def search(
        self,
        query: str,
        top_k: int = 3,
        threshold: float = 0.35,
        source_type_filter: Optional[SourceType] = None
    ) -> List[Tuple[DocumentChunk, float]]:
        """
        Perform vector cosine similarity search against indexed chunks.
        Returns sorted list of (DocumentChunk, similarity_score) exceeding the threshold.
        """
        if len(self.chunks) == 0 or not query.strip():
            return []

        query_vec = self.embedding_engine.embed_text(query)
        # Compute dot products (cosine similarity because all vectors are L2-normalized)
        scores = np.dot(self.vectors, query_vec)

        # Build candidate list with filtering
        candidates: List[Tuple[DocumentChunk, float]] = []
        for i, score in enumerate(scores):
            similarity = float(score)
            chunk = self.chunks[i]

            # Apply category filter
            if source_type_filter and chunk.source_type != source_type_filter:
                continue

            # Apply relevance threshold
            if similarity >= threshold:
                candidates.append((chunk, round(similarity, 4)))

        # Sort descending by similarity score
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[:top_k]

    def clear(self) -> None:
        """Reset the vector store index."""
        self.chunks = []
        self.vectors = np.empty((0, self.embedding_engine.dimension), dtype=np.float32)

    @property
    def count(self) -> int:
        """Return total number of indexed chunks."""
        return len(self.chunks)
