"""
Safe Temporary File Management for Transient Code Storage.
Ensures source code is buffered securely in isolated temporary files and guaranteed deleted.
"""

import os
import time
import uuid
from pathlib import Path
from typing import Generator
from contextlib import contextmanager
from app.core.config import settings
from app.utils.logger import logger


def get_temp_storage_dir() -> Path:
    """Return and create the isolated transient storage directory."""
    temp_dir = Path(settings.TEMP_STORAGE_DIR)
    if not temp_dir.is_absolute():
        # Place relative to current working dir
        temp_dir = Path.cwd() / temp_dir
    
    temp_dir.mkdir(parents=True, exist_ok=True)
    return temp_dir


@contextmanager
def safe_transient_code_file(content: str, suffix: str = ".tmp") -> Generator[Path, None, None]:
    """
    Context manager that safely writes source code to an isolated temporary file,
    yields the Path for transient processing, and guarantees absolute file removal upon exit.
    
    Usage:
        with safe_transient_code_file(content, suffix=".py") as temp_path:
            # perform read-only static analysis on temp_path
            ...
        # temp_path is automatically deleted here
    """
    temp_dir = get_temp_storage_dir()
    file_id = uuid.uuid4().hex
    temp_file_path = temp_dir / f"ingest_{file_id}{suffix}"

    try:
        # Write content with UTF-8 encoding
        with open(temp_file_path, "w", encoding="utf-8", errors="strict") as f:
            f.write(content)
        
        yield temp_file_path

    finally:
        # Guaranteed cleanup
        try:
            if temp_file_path.exists():
                temp_file_path.unlink(missing_ok=True)
        except Exception as exc:
            logger.warning(f"Failed to remove transient temp file {temp_file_path.name}: {exc}")


def cleanup_stale_temp_files(max_age_seconds: int = 600) -> int:
    """
    Sweep any orphaned transient files older than max_age_seconds.
    Returns count of cleaned files.
    """
    cleaned_count = 0
    now = time.time()
    temp_dir = get_temp_storage_dir()
    
    try:
        for item in temp_dir.glob("ingest_*"):
            if item.is_file():
                age = now - item.stat().st_mtime
                if age > max_age_seconds:
                    item.unlink(missing_ok=True)
                    cleaned_count += 1
    except Exception as exc:
        logger.warning(f"Error during transient storage sweep: {exc}")
        
    return cleaned_count
