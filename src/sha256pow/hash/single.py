from __future__ import annotations

import hashlib


def sha256_once(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()