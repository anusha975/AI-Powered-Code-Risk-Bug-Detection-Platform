"""
Pydantic Schemas for Code Submission, Ingestion, and Metadata Telemetry.
"""

from typing import Optional
from pydantic import BaseModel, Field


class CodeSubmissionRequest(BaseModel):
    """Payload schema for direct source-code paste ingestion."""
    language: Optional[str] = Field(
        None,
        description="Target programming language (python, java, javascript, typescript). Auto-detected if omitted.",
        examples=["python"]
    )
    filename: Optional[str] = Field(
        "snippet.py",
        description="Logical filename of the code artifact.",
        examples=["payment_service.py"]
    )
    content: str = Field(
        ...,
        min_length=1,
        description="Raw source code content to ingest safely.",
        examples=["def process_payment(amount: float):\n    return {'status': 'processed', 'amount': amount}"]
    )


class CodeIngestionMetadata(BaseModel):
    """Metadata returned after safe ingestion and validation."""
    submission_id: str = Field(..., description="Unique UUID tracking this ingestion session")
    filename: str = Field(..., description="Original filename provided in the request")
    sanitized_filename: str = Field(..., description="Sanitized, path-traversal-safe filename")
    language: str = Field(..., description="Validated normalized programming language")
    line_count: int = Field(..., description="Total line count of the ingested source code")
    character_count: int = Field(..., description="Total character count")
    size_bytes: int = Field(..., description="Payload size in bytes (UTF-8)")
    sha256_hash: str = Field(..., description="Cryptographic SHA-256 integrity fingerprint")
    status: str = Field(..., description="Ingestion validation status (e.g. ACCEPTED)")
    message: str = Field(..., description="Human-readable safety confirmation")
    created_at: str = Field(..., description="UTC ISO-8601 timestamp of ingestion")
