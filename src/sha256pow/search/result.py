from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class SearchResult:
    nonce: int
    digest_hex: str
    tries: int
    elapsed_sec: float
    hashes_per_sec: float
    double_hash: bool
    k: int
    nonce_size: Optional[int] = None
    backend: str = "unknown"
    workers: int = 1
    prefix_hex: Optional[str] = None

    @property
    def mhashes_per_sec(self) -> float:
        return self.hashes_per_sec / 1e6

    def format_block(self) -> str:
        lines = [
            "[Search Result]",
            "-----------------------------",
            f"backend         : {self.backend}",
            f"workers         : {self.workers}",
            f"nonce           : {self.nonce}",
            f"digest (hex)    : {self.digest_hex}",
            f"tries           : {self.tries:,}",
            f"elapsed (sec)   : {self.elapsed_sec:.4f}",
            f"throughput      : {self.hashes_per_sec:,.2f} H/s ({self.mhashes_per_sec:.2f} MH/s)",
            f"double hash     : {self.double_hash}",
            f"target bits (k) : {self.k}",
        ]
        if self.nonce_size is not None:
            lines.append(f"nonce size      : {self.nonce_size} bytes")
        if self.prefix_hex is not None:
            lines.append(f"prefix (hex)    : {self.prefix_hex}")
        return "\n".join(lines)

    def __str__(self) -> str:
        return "\n" + self.format_block() + "\n"
