from __future__ import annotations

import argparse
import os

from sha256pow.search.multiprocessing_search import run_multiprocessing_search
from sha256pow.search.naive import run_naive_search
from sha256pow.search.optimized import run_optimized_search


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Unified SHA-256 PoW search runner")
    parser.add_argument("--backend", choices=["naive", "optimized", "mp"], default="optimized")
    parser.add_argument("--prefix", default="homework")
    parser.add_argument("--k", type=int, default=24)
    parser.add_argument("--double", action="store_true", help="Use double SHA-256")
    parser.add_argument("--nonce-size", type=int, default=8)
    parser.add_argument("--start-nonce", type=int, default=0)
    parser.add_argument("--step", type=int, default=1)
    parser.add_argument("--workers", type=int, default=os.cpu_count() or 1)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    prefix = args.prefix.encode("ascii")

    if args.backend == "naive":
        result = run_naive_search(
            prefix=prefix,
            k=args.k,
            double_hash=args.double,
        )

    elif args.backend == "optimized":
        result = run_optimized_search(
            prefix=prefix,
            k=args.k,
            double_hash=args.double,
            nonce_size=args.nonce_size,
            start_nonce=args.start_nonce,
            step=args.step,
        )

    else:
        result = run_multiprocessing_search(
            prefix=prefix,
            k=args.k,
            double_hash=args.double,
            nonce_size=args.nonce_size,
            workers=args.workers,
            
        )

    print()
    print(result)


if __name__ == "__main__":
    main()