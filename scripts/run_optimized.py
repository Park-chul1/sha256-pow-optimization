from sha256pow.search.optimized import run_optimized_search


def main() -> None:
    result = run_optimized_search(
        prefix=b"homework",
        k=28,
        double_hash=False,
        nonce_size=8,
    )
    print()
    print("[FOUND]")
    print(result)


if __name__ == "__main__":
    main()
