from __future__ import annotations

from sha256pow.hash.single import sha256_once


def sha256_double(data: bytes) -> bytes:
    return sha256_once(sha256_once(data))