"""
Secure Code Ingestion API Endpoints.
Provides endpoints for direct code paste and file upload ingestion.
"""

from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from app.schemas.submission import CodeSubmissionRequest, CodeIngestionMetadata
from app.services.ingestion_service import ingestion_service
from app.core.security_validator import SecurityValidationError
from app.services.language_detector import UnsupportedLanguageError
from app.core.config import settings

router = APIRouter(tags=["Code Ingestion"])


@router.post(
    "/analyze",
    response_model=CodeIngestionMetadata,
    status_code=status.HTTP_200_OK,
    summary="Ingest Source Code (JSON Paste)",
    description="Safely ingests source code pasted in JSON format, validates language and constraints, and returns ingestion metadata."
)
def ingest_code_paste(payload: CodeSubmissionRequest) -> CodeIngestionMetadata:
    """Ingest pasted source code without execution."""
    try:
        return ingestion_service.process_code_ingestion(
            content=payload.content,
            filename=payload.filename,
            explicit_language=payload.language
        )
    except (SecurityValidationError, UnsupportedLanguageError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while ingesting the code snippet."
        )


@router.post(
    "/upload",
    response_model=CodeIngestionMetadata,
    status_code=status.HTTP_200_OK,
    summary="Ingest Source Code (File Upload)",
    description="Safely ingests an uploaded source code file (.py, .java, .js, .ts, etc.), validating size and MIME type."
)
async def ingest_code_file(
    file: UploadFile = File(..., description="Source code file to upload"),
    language: Optional[str] = Form(None, description="Optional explicit language override")
) -> CodeIngestionMetadata:
    """Ingest uploaded source code file safely."""
    try:
        # Read file content safely with size threshold inspection
        raw_bytes = await file.read(settings.MAX_FILE_SIZE_BYTES + 1024)
        
        if len(raw_bytes) > settings.MAX_FILE_SIZE_BYTES:
            raise SecurityValidationError(
                f"File size exceeds maximum limit of {settings.MAX_FILE_SIZE_BYTES:,} bytes (2 MB)."
            )

        if not raw_bytes or len(raw_bytes.strip()) == 0:
            raise SecurityValidationError("Uploaded file is empty.")

        # Decode as UTF-8 text
        try:
            content = raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            raise SecurityValidationError(
                "Uploaded file is not a valid UTF-8 text file. Binary or non-text files are prohibited."
            )

        return ingestion_service.process_code_ingestion(
            content=content,
            filename=file.filename,
            explicit_language=language
        )

    except (SecurityValidationError, UnsupportedLanguageError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while processing the uploaded file."
        )
