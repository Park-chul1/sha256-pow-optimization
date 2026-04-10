from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
from pathlib import Path

RESULT_RE = re.compile(r"^([^:]+):\s*(.+)$")


def parse_result_block(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    in_block = False
    for line in text.splitlines():
        s = line.strip()
        if s == "[Search Result]":
            in_block = True
            continue
        if not in_block or not s or s.startswith("---"):
            continue
        m = RESULT_RE.match(s)
        if m:
            key = m.group(1).strip().lower()
            val = m.group(2).strip()
            out[key] = val
    return out


def to_row(
    parsed: dict[str, str],
    run_type: str,
    k: int,
    double_hash: bool,
    workers: int | None,
    repeat: int,
) -> dict[str, object]:
    throughput = parsed.get("throughput", "0 H/s (0 MH/s)")
    mh_match = re.search(r"\(([-0-9.]+)\s+MH/s\)", throughput)
    h_match = re.search(r"^([0-9,]+(?:\.[0-9]+)?)\s+H/s", throughput)

    return {
        "run_type": run_type,
        "backend": parsed.get("backend", "unknown"),
        "workers": int(str(parsed.get("workers", workers or 1)).replace(",", "")),
        "k": k,
        "double_hash": str(double_hash),
        "nonce": str(parsed.get("nonce", "0")).replace(",", ""),
        "tries": int(str(parsed.get("tries", "0")).replace(",", "")),
        "elapsed_sec": float(parsed.get("elapsed (sec)", "0")),
        "hashes_per_sec": float(h_match.group(1).replace(",", "")) if h_match else 0.0,
        "mhashes_per_sec": float(mh_match.group(1)) if mh_match else 0.0,
        "target_bits": int(str(parsed.get("target bits (k)", k)).replace(",", "")),
        "nonce_size": int(str(parsed.get("nonce size", "8 bytes")).split()[0]),
        "repeat": repeat,
    }


def run_cmd(cmd: list[str], cwd: Path | None = None) -> str:
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            f"command failed\n"
            f"CMD: {' '.join(cmd)}\n"
            f"STDOUT:\n{proc.stdout}\n"
            f"STDERR:\n{proc.stderr}"
        )
    return proc.stdout


def main() -> None:
    p = argparse.ArgumentParser(description="Run SHA-256 PoW benchmarks and save CSV")
    p.add_argument("--python-backends", nargs="*", default=[])
    p.add_argument("--rust-backends", nargs="*", default=[])
    p.add_argument("--k-values", nargs="+", type=int, required=True)
    p.add_argument("--worker-values", nargs="*", type=int, default=[])
    p.add_argument("--repeats", type=int, default=1)
    p.add_argument("--workers", type=int, default=1)
    p.add_argument("--double", action="store_true")
    p.add_argument("--prefix", default="homework")
    p.add_argument("--output", required=True)
    args = p.parse_args()

    rows: list[dict[str, object]] = []
    root = Path(__file__).resolve().parents[1]
    rust_dir = root / "native" / "rust"
    worker_values = args.worker_values or [args.workers]

    for repeat in range(1, args.repeats + 1):
        for k in args.k_values:
            for backend in args.python_backends:
                python_worker_values = worker_values if backend == "mp" else [1]

                for w in python_worker_values:
                    cmd = [
                        sys.executable,
                        "scripts/run_search.py",
                        "--backend",
                        backend,
                        "--prefix",
                        args.prefix,
                        "--k",
                        str(k),
                        "--workers",
                        str(w),
                    ]
                    if args.double:
                        cmd.append("--double")

                    text = run_cmd(cmd, cwd=root)
                    rows.append(to_row(parse_result_block(text), "python", k, args.double, w, repeat))

            for backend in args.rust_backends:
                backend_worker_values = worker_values if backend.endswith("-mt") else [1]

                for w in backend_worker_values:
                    cmd = [
                        "cargo",
                        "run",
                        "--release",
                        "--",
                        "--backend",
                        backend,
                        "--prefix",
                        args.prefix,
                        "--k",
                        str(k),
                        "--workers",
                        str(w),
                    ]
                    if args.double:
                        cmd.append("--double")

                    text = run_cmd(cmd, cwd=rust_dir)
                    rows.append(to_row(parse_result_block(text), "rust", k, args.double, w, repeat))

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    if not rows:
        raise RuntimeError("no benchmark rows produced")

    fieldnames = list(rows[0].keys())
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"saved benchmark CSV to {output}")


if __name__ == "__main__":
    main()