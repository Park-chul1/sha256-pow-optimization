import os

from sha256pow.search.multiprocessing_search import run_multiprocessing_search


def main() -> None:
    detected = os.cpu_count() or 1
    print(f"[info] detected logical CPUs: {detected}")

    result = run_multiprocessing_search(
        prefix=b"homework",
        nonce_size=8,
        k=24,
        workers=min(4, detected),
    )
    print()
    print("[FOUND]")
    print(result)

if __name__ == "__main__":
    main()
