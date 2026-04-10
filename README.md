# SHA256 Proof-of-Work Optimization Project

## Problem

Find a nonce `x` such that:

- SHA256("homework" || x) has k leading zero bits
- Also evaluate double SHA256(SHA256(...))

This is a brute-force Proof-of-Work search problem.

---

## Core Insight

Expected trials ≈ 2^k

Total runtime:

Total time ≈ (cost per iteration) × (2^k)

→ Algorithmic complexity is fixed  
→ Only optimization target = **reduce iteration cost**

---

## Key Results

Measured throughput (average):

- OpenSSL (multi-thread): **~19.8 MH/s**
- Rust (multi-thread): **~13.8 MH/s**
- OpenSSL (single-thread): ~5.8 MH/s
- Rust (single-thread): ~3.6 MH/s
- Python (optimized): ~0.94 MH/s
- Python (naive): ~0.80 MH/s
- Python (multiprocessing): **~0.16 MH/s**

---

## Speedup Summary

- Python → Rust (single-thread): ~4×
- Python → OpenSSL (single-thread): ~6×
- Rust → OpenSSL: ~1.6×
- Single → Multi-thread (Rust): ~3.8×
- Single → Multi-thread (OpenSSL): ~3.4×

---

## What Actually Mattered

The dominant performance factors were:

- Eliminating allocations inside the inner loop
- Avoiding string / hex conversions
- Precomputing hash prefix state
- Using native code (Rust) instead of Python interpreter
- Leveraging optimized crypto backends (OpenSSL)
- Multi-threading across CPU cores

---

## Bottlenecks Observed

- Python multiprocessing performed worse than single-threaded execution
  - Process overhead dominates for tight loops
- Hash computation fully dominates runtime
- Python interpreter overhead limits throughput (~1 MH/s ceiling)
- Native implementations shift bottleneck to CPU execution and memory

---

## System Design Layers

### Layer 1: Algorithm (fixed)
- Brute-force search
- No asymptotic improvement possible

### Layer 2: System Structure
- Thread-based parallelism
- Work partitioning (nonce ranges)

### Layer 3: Loop Optimization (critical)
- Zero-allocation inner loop
- Byte-level operations
- Prefix reuse

### Layer 4: Native Execution
- Rust implementation
- Removal of interpreter overhead

### Layer 5: ISA / Backend Optimization
- OpenSSL backend
- CPU-level optimizations (vectorization, SHA extensions)

---

## Experimental Scope

- k = 1 ~ 20 baseline benchmarking
- Single vs double SHA256
- Backend comparison (Python, Rust, OpenSSL)
- Scaling across threads

---

## Key Takeaway

This is not a cryptography problem.

This is a **systems and performance engineering problem**, where:

- computation is fixed
- performance depends entirely on execution efficiency

---

## Future Work

- GPU implementation (CUDA / OpenCL)
- Extended difficulty (k > 24)
- Hardware-level optimization exploration (FPGA concepts)
