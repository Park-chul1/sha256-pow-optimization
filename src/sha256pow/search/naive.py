from __future__ import annotations

import time

from sha256pow.hash.double import sha256_double
from sha256pow.hash.single import sha256_once

from sha256pow.search.result import SearchResult
from sha256pow.utils.bits import has_leading_zero_bits


def run_naive_search(
    prefix: bytes,
    k: int,
    double_hash: bool = False,
) -> SearchResult:
    """
    Naive baseline:
    - for each nonce:
      - convert nonce to decimal string
      - concatenate prefix + ascii(nonce)
      - hash
      - check leading zero bits
    """
    if k < 0:
        raise ValueError("k must be >= 0")

    hash_fn = sha256_double if double_hash else sha256_once

    nonce = 0
    tries = 0
    start = time.perf_counter()

    while True:
        nonce_bytes = str(nonce).encode("ascii")
        msg = prefix + nonce_bytes
        digest = hash_fn(msg)
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
                nonce_size=None,
                backend="python_naive",
                workers=1,
                prefix_hex=prefix.hex(),
            )

        nonce += 1
