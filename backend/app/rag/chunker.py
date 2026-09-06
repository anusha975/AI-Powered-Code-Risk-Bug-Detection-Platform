"""
Document Chunking Engine for Engineering Knowledge RAG.

Splits technical markdown and text documents into coherent semantic chunks
while preserving section headers, code examples, and document metadata.
"""

from typing import List, Dict, Any, Optional
import re
import uuid

from app.schemas.rag import DocumentChunk, KnowledgeDocument, SourceType


class DocumentChunker:
    """Splits knowledge documents into structured, overlap-aware chunks."""

    def __init__(self, target_chunk_size: int = 500, chunk_overlap: int = 50) -> None:
        self.target_chunk_size = target_chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(self, doc: KnowledgeDocument) -> List[DocumentChunk]:
        """
        Chunk a single KnowledgeDocument by markdown section headings and paragraphs.
        """
        content = doc.content.strip()
        if not content:
            return []

        # Split into sections based on Markdown headers (# Header)
        sections = self._split_by_markdown_headers(content)
        chunks: List[DocumentChunk] = []
        chunk_offset = 0

        for section_title, section_text in sections:
            section_chunks = self._chunk_section_text(
                text=section_text,
                doc_id=doc.doc_id,
                doc_title=doc.title,
                source_type=doc.source_type,
                section_title=section_title,
                start_offset=chunk_offset
            )
            chunks.extend(section_chunks)
            chunk_offset += len(section_chunks)

        return chunks

    def _split_by_markdown_headers(self, text: str) -> List[tuple[str, str]]:
        """Split text into (section_title, section_body) pairs."""
        lines = text.split("\n")
        sections: List[tuple[str, str]] = []
        current_title = "Overview"
        current_lines: List[str] = []

        for line in lines:
            if re.match(r"^#{1,4}\s+", line):
                if current_lines:
                    sections.append((current_title, "\n".join(current_lines).strip()))
                    current_lines = []
                current_title = re.sub(r"^#{1,4}\s+", "", line).strip()
            else:
                current_lines.append(line)

        if current_lines:
            sections.append((current_title, "\n".join(current_lines).strip()))

        return sections

    def _chunk_section_text(
        self,
        text: str,
        doc_id: str,
        doc_title: str,
        source_type: SourceType,
        section_title: str,
        start_offset: int
    ) -> List[DocumentChunk]:
        """Split a section's text into size-bounded overlapping chunks."""
        if not text:
            return []

        # If text is small enough, return as single chunk
        if len(text) <= self.target_chunk_size + 100:
            chunk_id = f"{doc_id}-CHK-{start_offset:03d}"
            return [
                DocumentChunk(
                    chunk_id=chunk_id,
                    doc_id=doc_id,
                    title=doc_title,
                    source_type=source_type,
                    section=section_title,
                    content=text,
                    char_count=len(text),
                    chunk_index=start_offset
                )
            ]

        # Paragraph-aware chunking
        paragraphs = text.split("\n\n")
        chunks: List[DocumentChunk] = []
        current_chunk_paragraphs: List[str] = []
        current_length = 0
        idx = start_offset

        for p in paragraphs:
            p_clean = p.strip()
            if not p_clean:
                continue

            if current_length + len(p_clean) > self.target_chunk_size and current_chunk_paragraphs:
                chunk_text = "\n\n".join(current_chunk_paragraphs)
                chunks.append(
                    DocumentChunk(
                        chunk_id=f"{doc_id}-CHK-{idx:03d}",
                        doc_id=doc_id,
                        title=doc_title,
                        source_type=source_type,
                        section=section_title,
                        content=chunk_text,
                        char_count=len(chunk_text),
                        chunk_index=idx
                    )
                )
                idx += 1
                # Sliding window overlap: retain last paragraph if small
                if len(current_chunk_paragraphs[-1]) < self.chunk_overlap * 2:
                    current_chunk_paragraphs = [current_chunk_paragraphs[-1], p_clean]
                    current_length = sum(len(x) for x in current_chunk_paragraphs)
                else:
                    current_chunk_paragraphs = [p_clean]
                    current_length = len(p_clean)
            else:
                current_chunk_paragraphs.append(p_clean)
                current_length += len(p_clean)

        if current_chunk_paragraphs:
            chunk_text = "\n\n".join(current_chunk_paragraphs)
            chunks.append(
                DocumentChunk(
                    chunk_id=f"{doc_id}-CHK-{idx:03d}",
                    doc_id=doc_id,
                    title=doc_title,
                    source_type=source_type,
                    section=section_title,
                    content=chunk_text,
                    char_count=len(chunk_text),
                    chunk_index=idx
                )
            )

        return chunks
