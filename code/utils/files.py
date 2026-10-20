"""File hashes and guarded atomic updates shared by detector data tools."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import tempfile


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write(path: Path, payload: bytes, expected_hash: str) -> None:
    """Refuse to overwrite a file changed since the caller last read it."""
    path = Path(path)
    if sha256(path) != expected_hash:
        raise ValueError('Review file changed outside the reviewer. Reload before saving.')
    fd, name = tempfile.mkstemp(prefix='.decisions-', suffix='.tmp', dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        if sha256(path) != expected_hash:
            raise ValueError('Review file changed outside the reviewer. Reload before saving.')
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)
