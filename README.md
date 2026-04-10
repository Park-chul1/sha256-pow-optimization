# SHA-256 Proof-of-Work Optimization Project

## Overview

This project studies a SHA-256 brute-force proof-of-work search problem.

Goal:

- find a nonce `x` such that `SHA256(prefix || x)` has `k` leading zero bits
- also compare double SHA-256: `SHA256(SHA256(prefix || x))`

This is mainly a systems and performance engineering project, not an algorithmic-complexity project.
The asymptotic structure is fixed, so the main target is reducing constant-factor cost per hash.

---

## Implementations

### Python

- `naive`: simple baseline
- `optimized`: prefix reuse, byte-level check, fewer allocations
- `mp`: multiprocessing version

### Rust

- `rust`: pure Rust single-thread
- `rust-mt`: pure Rust multithread
- `openssl`: OpenSSL-backed single-thread
- `openssl-mt`: OpenSSL-backed multithread

---

## Output style

The outputs are not forced to be perfectly identical, but they are intentionally similar enough to compare easily.

Typical result block:

```text
[Search Result]
-----------------------------
backend         : python_optimized
workers         : 1
nonce           : 123456
digest (hex)    : 0000ab...
tries           : 1,234,567
elapsed (sec)   : 3.2140
throughput      : 384,000.00 H/s (0.38 MH/s)
double hash     : True
target bits (k) : 24
nonce size      : 8 bytes
prefix (hex)    : 686f6d65776f726b
```

Typical progress line:

```text
[progress:python_optimized] | k=24 | workers=1 | nonce=1999999 | tries=2,000,000 | throughput=0.39 MH/s | elapsed=5.1s
[progress:python_mp] | k=24 | workers=12 | best=21 bits | tries=8,000,000 | throughput=5.40 MH/s | elapsed=1.5s
```

---

## Python commands

Run from the project root.

### Basic runs

```bash
PYTHONPATH=src python scripts/run_search.py --backend naive --k 16
PYTHONPATH=src python scripts/run_search.py --backend optimized --k 24
PYTHONPATH=src python scripts/run_search.py --backend mp --k 24 --workers 12
```

### Double SHA

```bash
PYTHONPATH=src python scripts/run_search.py --backend naive --k 16 --double
PYTHONPATH=src python scripts/run_search.py --backend optimized --k 24 --double
PYTHONPATH=src python scripts/run_search.py --backend mp --k 24 --workers 12 --double
```

### Useful options

```bash
PYTHONPATH=src python scripts/run_search.py   --backend optimized   --k 28   --double   --nonce-size 8   --start-nonce 0   --step 1   --progress-interval 1000000
```

```bash
PYTHONPATH=src python scripts/run_search.py   --backend mp   --k 28   --double   --workers 12   --nonce-size 8   --progress-interval 1000000   --report-every-sec 2
```

### What Python can do

- switch backend with `--backend`
- change difficulty with `--k`
- enable double SHA with `--double`
- change multiprocessing worker count with `--workers`
- change progress print cadence with `--progress-interval`
- change periodic mp report cadence with `--report-every-sec`
- change nonce byte width with `--nonce-size`
- change prefix text with `--prefix`

---

## Rust commands

Run from `native/rust`.

### Build

```bash
cd native/rust
cargo build --release
```

### Basic runs

```bash
cargo run --release -- --backend rust --k 24
cargo run --release -- --backend openssl --k 24
cargo run --release -- --backend rust-mt --k 24 --workers 12
cargo run --release -- --backend openssl-mt --k 24 --workers 12
```

### Double SHA

```bash
cargo run --release -- --backend rust --k 24 --double
cargo run --release -- --backend openssl --k 24 --double
cargo run --release -- --backend rust-mt --k 24 --workers 12 --double
cargo run --release -- --backend openssl-mt --k 24 --workers 12 --double
```

### Progress options

```bash
cargo run --release -- --backend rust --k 24 --progress-interval 1000000
cargo run --release -- --backend openssl --k 24 --double --progress-interval 1000000
cargo run --release -- --backend rust-mt --k 28 --workers 12 --report-every-sec 2
cargo run --release -- --backend openssl-mt --k 28 --workers 12 --double --report-every-sec 2
```

### What Rust can do

- select backend with `--backend`
- run single or double SHA with `--double`
- run multithreaded versions with `--workers`
- print progress by interval with `--progress-interval`
- print periodic multithread summaries with `--report-every-sec`
- change `k` and `prefix`

---

## Benchmark workflow

### 1. Run a small comparison

```bash
python scripts/run_benchmarks.py   --python-backends naive optimized mp   --rust-backends rust openssl rust-mt openssl-mt   --k-values 16 20 24   --repeats 3   --workers 12   --output results/raw/compare_main.csv
```

### 2. Plot elapsed time

```bash
python scripts/plot_results.py   --input results/raw/compare_main.csv   --x k   --metric elapsed_sec   --output results/plots/elapsed_vs_k.png
```

### 3. Plot throughput

```bash
python scripts/plot_results.py   --input results/raw/compare_main.csv   --x k   --metric mhashes_per_sec   --output results/plots/mhps_vs_k.png
```

### 4. Plot scaling at fixed difficulty

```bash
python scripts/run_benchmarks.py   --python-backends mp   --rust-backends rust-mt openssl-mt   --k-values 24   --worker-values 1 2 4 8 12   --repeats 3   --output results/raw/scaling_k24.csv
```

```bash
python scripts/plot_results.py   --input results/raw/scaling_k24.csv   --x workers   --metric mhashes_per_sec   --filter-k 24   --output results/plots/scaling_k24.png
```

---

## Recommended graphs

The most useful graphs for the report are:

1. `k` vs `elapsed_sec`
2. `k` vs `mhashes_per_sec`
3. `workers` vs `mhashes_per_sec` at fixed `k`
4. single SHA vs double SHA throughput comparison

---

## Notes

- expected trials are about `2^k`
- runtime growth should look exponential as `k` increases
- backend differences mainly reflect constant-factor optimization
- multiprocessing and multithreading can scale, but not perfectly, because of overhead and hardware limits
