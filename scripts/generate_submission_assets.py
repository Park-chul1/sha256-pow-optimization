from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import pandas as pd


RESULT_LINE_RE = re.compile(r"^([^:]+):\s*(.+)$")
THROUGHPUT_RE = re.compile(r"^([0-9,]+(?:\.[0-9]+)?)\s+H/s\s+\(([-0-9.]+)\s+MH/s\)$")


def run_cmd(cmd: list[str], cwd: Path, env: dict[str, str] | None = None) -> str:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        env=env,
    )
    if proc.returncode != 0:
        print("\n[command failed]")
        print("cwd:", cwd)
        print("cmd:", " ".join(cmd))
        print("\n[stdout]")
        print(proc.stdout)
        print("\n[stderr]")
        print(proc.stderr)
        raise RuntimeError(f"Command failed with exit code {proc.returncode}")
    return proc.stdout


def parse_search_result(stdout: str) -> dict[str, str]:
    in_block = False
    parsed: dict[str, str] = {}

    for raw in stdout.splitlines():
        line = raw.strip()
        if line == "[Search Result]":
            in_block = True
            continue
        if not in_block:
            continue
        if not line or line.startswith("-"):
            continue

        m = RESULT_LINE_RE.match(line)
        if m:
            key = m.group(1).strip().lower()
            value = m.group(2).strip()
            parsed[key] = value

    if not parsed:
        raise ValueError("Could not find [Search Result] block in output.")

    return parsed


def normalize_backend_name(name: str) -> str:
    table = {
        "naive": "python_naive",
        "optimized": "python_optimized",
        "mp": "python_mp",
        "python_naive": "python_naive",
        "python_optimized": "python_optimized",
        "python_mp": "python_mp",
        "rust": "pure_rust_sha2",
        "rust-mt": "pure_rust_sha2_mt",
        "rust_mt": "pure_rust_sha2_mt",
        "pure_rust_sha2": "pure_rust_sha2",
        "pure_rust_sha2_mt": "pure_rust_sha2_mt",
    }
    return table.get(name, name)


def parsed_to_row(parsed: dict[str, str], *, k: int, double_hash: bool, requested_backend: str) -> dict:
    throughput_str = parsed.get("throughput", "0 H/s (0.00 MH/s)")
    m = THROUGHPUT_RE.match(throughput_str)

    hashes_per_sec = 0.0
    mhashes_per_sec = 0.0
    if m:
        hashes_per_sec = float(m.group(1).replace(",", ""))
        mhashes_per_sec = float(m.group(2))

    backend = normalize_backend_name(parsed.get("backend", requested_backend).strip())

    def to_int(x: str, default: int = 0) -> int:
        try:
            return int(str(x).replace(",", "").split()[0])
        except Exception:
            return default

    def to_float(x: str, default: float = 0.0) -> float:
        try:
            return float(str(x).replace(",", ""))
        except Exception:
            return default

    return {
        "backend": backend,
        "k": k,
        "double_hash": bool(double_hash),
        "workers": to_int(parsed.get("workers", "1"), 1),
        "nonce": str(parsed.get("nonce", "")),
        "tries": to_int(parsed.get("tries", "0"), 0),
        "elapsed_sec": to_float(parsed.get("elapsed (sec)", "0"), 0.0),
        "hashes_per_sec": hashes_per_sec,
        "mhashes_per_sec": mhashes_per_sec,
        "target_bits": to_int(parsed.get("target bits (k)", str(k)), k),
        "nonce_size_bytes": to_int(parsed.get("nonce size", "8 bytes"), 8),
        "prefix_hex": parsed.get("prefix (hex)", ""),
    }


def run_python_search(
    project_root: Path,
    backend: str,
    k: int,
    double_hash: bool,
    workers: int,
) -> dict:
    cmd = [
        sys.executable,
        "scripts/run_search.py",
        "--backend", backend,
        "--prefix", "homework",
        "--k", str(k),
        "--nonce-size", "8",
    ]

    if backend == "mp":
        cmd.extend(["--workers", str(workers)])

    if double_hash:
        cmd.append("--double")

    env = os.environ.copy()
    env["PYTHONPATH"] = "src"

    stdout = run_cmd(cmd, cwd=project_root, env=env)
    parsed = parse_search_result(stdout)
    return parsed_to_row(parsed, k=k, double_hash=double_hash, requested_backend=backend)


def run_rust_search(
    rust_root: Path,
    backend: str,
    k: int,
    double_hash: bool,
    workers: int,
) -> dict:
    cmd = [
        "cargo", "run", "--release", "--",
        "--backend", backend,
        "--prefix", "homework",
        "--k", str(k),
    ]

    if backend == "rust-mt":
        cmd.extend(["--workers", str(workers)])

    if double_hash:
        cmd.append("--double")

    stdout = run_cmd(cmd, cwd=rust_root)
    parsed = parse_search_result(stdout)
    return parsed_to_row(parsed, k=k, double_hash=double_hash, requested_backend=backend)


def save_plot(df: pd.DataFrame, metric: str, title: str, output_path: Path) -> None:
    plt.figure(figsize=(8, 5))

    for backend, sub in df.groupby("backend"):
        sub = sub.sort_values("k")
        plt.plot(sub["k"], sub[metric], marker="o", label=backend)

    plt.xlabel("k")
    plt.ylabel(metric)
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=160)
    plt.close()


def benchmark_python(project_root: Path, out_dir: Path, mp_workers: int) -> None:
    rows: list[dict] = []

    for double_hash in [False, True]:
        for k in range(1, 21):
            print(f"[python] k={k} double={double_hash} backend=naive")
            rows.append(run_python_search(project_root, "naive", k, double_hash, workers=1))

            print(f"[python] k={k} double={double_hash} backend=optimized")
            rows.append(run_python_search(project_root, "optimized", k, double_hash, workers=1))

            print(f"[python] k={k} double={double_hash} backend=mp workers={mp_workers}")
            rows.append(run_python_search(project_root, "mp", k, double_hash, workers=mp_workers))

    df = pd.DataFrame(rows).sort_values(["double_hash", "backend", "k"]).reset_index(drop=True)

    single_df = df[df["double_hash"] == False].copy()
    double_df = df[df["double_hash"] == True].copy()

    single_df.to_csv(out_dir / "python_single_k1_20.csv", index=False)
    double_df.to_csv(out_dir / "python_double_k1_20.csv", index=False)
    df.to_csv(out_dir / "python_all_k1_20.csv", index=False)

    save_plot(
        single_df,
        metric="elapsed_sec",
        title="Python single SHA: elapsed_sec vs k",
        output_path=out_dir / "python_single_elapsed_k1_20.png",
    )
    save_plot(
        double_df,
        metric="elapsed_sec",
        title="Python double SHA: elapsed_sec vs k",
        output_path=out_dir / "python_double_elapsed_k1_20.png",
    )
    save_plot(
        single_df,
        metric="mhashes_per_sec",
        title="Python single SHA: mhashes_per_sec vs k",
        output_path=out_dir / "python_single_throughput_k1_20.png",
    )
    save_plot(
        double_df,
        metric="mhashes_per_sec",
        title="Python double SHA: mhashes_per_sec vs k",
        output_path=out_dir / "python_double_throughput_k1_20.png",
    )


def benchmark_rust(project_root: Path, out_dir: Path, mt_workers: int, k_values: Iterable[int]) -> None:
    rust_root = project_root / "native" / "rust"
    rows: list[dict] = []

    for double_hash in [False, True]:
        for k in k_values:
            print(f"[rust] k={k} double={double_hash} backend=rust")
            rows.append(run_rust_search(rust_root, "rust", k, double_hash, workers=1))

            print(f"[rust] k={k} double={double_hash} backend=rust-mt workers={mt_workers}")
            rows.append(run_rust_search(rust_root, "rust-mt", k, double_hash, workers=mt_workers))

    df = pd.DataFrame(rows).sort_values(["double_hash", "backend", "k"]).reset_index(drop=True)

    single_df = df[df["double_hash"] == False].copy()
    double_df = df[df["double_hash"] == True].copy()

    single_df.to_csv(out_dir / "rust_single_k20_30.csv", index=False)
    double_df.to_csv(out_dir / "rust_double_k20_30.csv", index=False)
    df.to_csv(out_dir / "rust_all_k20_30.csv", index=False)

    save_plot(
        single_df,
        metric="elapsed_sec",
        title="Rust single SHA: elapsed_sec vs k",
        output_path=out_dir / "rust_single_elapsed_k20_30.png",
    )
    save_plot(
        double_df,
        metric="elapsed_sec",
        title="Rust double SHA: elapsed_sec vs k",
        output_path=out_dir / "rust_double_elapsed_k20_30.png",
    )
    save_plot(
        single_df,
        metric="mhashes_per_sec",
        title="Rust single SHA: mhashes_per_sec vs k",
        output_path=out_dir / "rust_single_throughput_k20_30.png",
    )
    save_plot(
        double_df,
        metric="mhashes_per_sec",
        title="Rust double SHA: mhashes_per_sec vs k",
        output_path=out_dir / "rust_double_throughput_k20_30.png",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate CSVs and plots for the submission.")
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--out-dir", type=Path, default=Path("results/submission"))
    parser.add_argument("--python-only", action="store_true")
    parser.add_argument("--rust-only", action="store_true")
    parser.add_argument("--mp-workers", type=int, default=12)
    parser.add_argument("--rust-mt-workers", type=int, default=12)
    parser.add_argument(
        "--rust-k-values",
        type=int,
        nargs="+",
        default=[20, 24, 28, 30],
    )
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)

    if not args.rust_only:
        benchmark_python(args.project_root, args.out_dir, mp_workers=args.mp_workers)

    if not args.python_only:
        benchmark_rust(
            args.project_root,
            args.out_dir,
            mt_workers=args.rust_mt_workers,
            k_values=args.rust_k_values,
        )

    print(f"[done] outputs saved to {args.out_dir}")


if __name__ == "__main__":
    main()