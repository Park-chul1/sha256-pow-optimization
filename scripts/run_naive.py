from sha256pow.search.naive import run_naive_search


def main() -> None:
    result = run_naive_search(
        prefix=b"homework",
        k=16,
        double_hash=False,
    )
    print()
    print("[FOUND]")
    print(result)

if __name__ == "__main__":
    main()
