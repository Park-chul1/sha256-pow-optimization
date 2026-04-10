from __future__ import annotations

import hashlib
import multiprocessing as mp
import os
import queue
import time
from typing import Optional

from sha256pow.search.result import SearchResult
from sha256pow.utils.bits import has_leading_zero_bits


def _worker(
    worker_id: int,
    workers: int,
    prefix: bytes,
    k: int,
    double_hash: bool,
    nonce_size: int,
    found_event: mp.synchronize.Event,
    result_queue: mp.Queue,
) -> None:
    base = hashlib.sha256()
    base.update(prefix)

    max_nonce = 1 << (8 * nonce_size)
    nonce = worker_id
    local_tries = 0

    found_nonce: int | None = None
    found_digest_hex: str | None = None

    while nonce < max_nonce:
        if found_event.is_set():
            break

        nonce_bytes = nonce.to_bytes(nonce_size, "big")
        h = base.copy()
        h.update(nonce_bytes)
        digest = h.digest()

        if double_hash:
            digest = hashlib.sha256(digest).digest()

        local_tries += 1

        if has_leading_zero_bits(digest, k):
            found_nonce = nonce
            found_digest_hex = digest.hex()
            found_event.set()
            break

        nonce += workers

    result_queue.put(
        {
            "worker_id": worker_id,
            "tries": local_tries,
            "found": found_nonce is not None,
            "nonce": found_nonce,
            "digest_hex": found_digest_hex,
        }
    )


def run_multiprocessing_search(
    prefix: bytes,
    k: int,
    double_hash: bool = False,
    nonce_size: int = 8,
    workers: Optional[int] = None,
) -> SearchResult:
    if k < 0:
        raise ValueError("k must be >= 0")
    if nonce_size <= 0:
        raise ValueError("nonce_size must be > 0")

    if workers is None:
        workers = os.cpu_count() or 1
    if workers <= 0:
        raise ValueError("workers must be > 0")

    ctx = mp.get_context("fork")
    found_event = ctx.Event()
    result_queue = ctx.Queue()

    processes: list[mp.Process] = []
    start = time.perf_counter()

    for worker_id in range(workers):
        p = ctx.Process(
            target=_worker,
            args=(
                worker_id,
                workers,
                prefix,
                k,
                double_hash,
                nonce_size,
                found_event,
                result_queue,
            ),
        )
        p.start()
        processes.append(p)

    total_tries = 0
    found_payload: dict[str, object] | None = None

    try:
        received = 0
        while received < workers:
            try:
                payload = result_queue.get(timeout=1.0)
            except queue.Empty:
                if not any(p.is_alive() for p in processes):
                    break
                continue

            received += 1
            total_tries += int(payload["tries"])

            if payload["found"] and found_payload is None:
                found_payload = payload

    finally:
        found_event.set()
        for p in processes:
            p.join()

    if found_payload is None:
        raise RuntimeError("No solution found before workers exited")

    elapsed = time.perf_counter() - start
    hps = total_tries / elapsed if elapsed > 0 else 0.0

    return SearchResult(
        nonce=int(found_payload["nonce"]),
        digest_hex=str(found_payload["digest_hex"]),
        tries=total_tries,
        elapsed_sec=elapsed,
        hashes_per_sec=hps,
        double_hash=double_hash,
        k=k,
        nonce_size=nonce_size,
        backend="python_mp",
        workers=workers,
        prefix_hex=prefix.hex(),
    )