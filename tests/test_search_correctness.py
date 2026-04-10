from sha256pow.search.naive import run_naive_search
from sha256pow.search.optimized import run_optimized_search
from sha256pow.utils.bits import has_leading_zero_bits
'''
이 테스트는 naive와 optimized가 “같은 조건을 만족하는 해를 찾는지” 보는 용도다.
같은 nonce를 찾는다는 보장은 없지만, 적어도 조건은 만족해야 한다.
'''

def test_naive_search_finds_valid_solution() -> None:
    result = run_naive_search(prefix=b"homework", k=8, double_hash=False)
    assert result.tries >= 1
    assert has_leading_zero_bits(bytes.fromhex(result.digest_hex), 8)


def test_optimized_search_finds_valid_solution() -> None:
    result = run_optimized_search(prefix=b"homework", k=8, double_hash=False, nonce_size=8)
    assert result.tries >= 1
    assert has_leading_zero_bits(bytes.fromhex(result.digest_hex), 8)


def test_naive_search_double_finds_valid_solution() -> None:
    result = run_naive_search(prefix=b"homework", k=8, double_hash=True)
    assert result.tries >= 1
    assert has_leading_zero_bits(bytes.fromhex(result.digest_hex), 8)


def test_optimized_search_double_finds_valid_solution() -> None:
    result = run_optimized_search(prefix=b"homework", k=8, double_hash=True, nonce_size=8)
    assert result.tries >= 1
    assert has_leading_zero_bits(bytes.fromhex(result.digest_hex), 8)