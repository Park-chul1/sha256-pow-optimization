from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from sha256pow.search.result import SearchResult


def append_result_csv(
    result: SearchResult,
    *,
    csv_path: str | Path,
    method: str,
) -> None:
    csv_path = Path(csv_path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    row = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "method": method,
        "backend": result.backend,
        "k": result.k,
        "double_hash": result.double_hash,
        "workers": result.workers,
        "nonce": result.nonce,
        "tries": result.tries,
        "elapsed_sec": result.elapsed_sec,
        "hashes_per_sec": result.hashes_per_sec,
        "mhps": result.hashes_per_sec / 1e6,
        "prefix_hex": result.prefix_hex,
    }

    fieldnames = list(row.keys())
    file_exists = csv_path.exists()

    with csv_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)