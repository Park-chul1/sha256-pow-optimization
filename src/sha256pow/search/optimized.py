from __future__ import annotations

import hashlib
import time


from sha256pow.search.result import SearchResult
from sha256pow.utils.bits import has_leading_zero_bits


def run_optimized_search(
    prefix: bytes,
    k: int,
    double_hash: bool = False,
    nonce_size: int = 8,
    start_nonce: int = 0,
    step: int = 1,
) -> SearchResult:
    if k < 0:
        raise ValueError("k must be >= 0")
    if nonce_size <= 0:
        raise ValueError("nonce_size must be > 0")
    if step <= 0:
        raise ValueError("step must be > 0")

    base = hashlib.sha256()
    base.update(prefix)

    max_nonce = 1 << (8 * nonce_size)

    nonce = start_nonce
    tries = 0
    start = time.perf_counter()

    while nonce < max_nonce:
        nonce_bytes = nonce.to_bytes(nonce_size, "big")

        h = base.copy()
        h.update(nonce_bytes)
        digest = h.digest()

        if double_hash:
            digest = hashlib.sha256(digest).digest()

        tries += 1

        if has_leading_zero_bits(digest, k):
            elapsed = time.perf_counter() - start
            hps = tries / elapsed if elapsed > 0 else float("inf")
            
         
            return SearchResult(
                nonce=nonce,
                digest_hex=digest.hex(),
                tries=tries,
                elapsed_sec=elapsed,
                hashes_per_sec=hps,
                double_hash=double_hash,
                k=k,
                nonce_size=nonce_size,
                backend="python_optimized",
                workers=1,
                prefix_hex=prefix.hex(),
            )


        nonce += step

    raise RuntimeError("nonce space exhausted")
