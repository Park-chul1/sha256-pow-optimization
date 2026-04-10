from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> None:
    p = argparse.ArgumentParser(description="Plot SHA-256 benchmark CSV")
    p.add_argument("--input", required=True)
    p.add_argument("--x", choices=["k", "workers"], required=True)
    p.add_argument("--metric", choices=["elapsed_sec", "hashes_per_sec", "mhashes_per_sec", "tries"], required=True)
    p.add_argument("--output", required=False)
    p.add_argument("--filter-k", type=int)
    p.add_argument("--filter-double", choices=["True", "False"])
    args = p.parse_args()

    rows = load_rows(Path(args.input))
    filtered: list[dict[str, str]] = []
    for r in rows:
        if args.filter_k is not None and int(r["k"]) != args.filter_k:
            continue
        if args.filter_double is not None and r["double_hash"] != args.filter_double:
            continue
        filtered.append(r)

    grouped: dict[str, dict[float, list[float]]] = defaultdict(lambda: defaultdict(list))
    for r in filtered:
        backend = r["backend"]
        x = float(r[args.x])
        y = float(r[args.metric])
        grouped[backend][x].append(y)

    plt.figure(figsize=(8, 5))
    for backend, series in sorted(grouped.items()):
        xs = sorted(series.keys())
        ys = [sum(series[x]) / len(series[x]) for x in xs]
        plt.plot(xs, ys, marker="o", label=backend)

    plt.xlabel(args.x)
    plt.ylabel(args.metric)
    plt.title(f"{args.metric} vs {args.x}")
    plt.legend()
    plt.tight_layout()

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(out, dpi=160)
        print(f"saved plot to {out}")
    else:
        default_out = Path("results/plots") / f"{args.metric}_vs_{args.x}.png"
        default_out.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(default_out, dpi=160)
        print(f"saved plot to {default_out}")


if __name__ == "__main__":
    main()
