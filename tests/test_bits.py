from sha256pow.utils.bits import has_leading_zero_bits, leading_zero_bits


def test_has_leading_zero_bits_basic() -> None:
    digest = bytes.fromhex("00f000")
    assert has_leading_zero_bits(digest, 8) is True
    assert has_leading_zero_bits(digest, 9) is False
    assert has_leading_zero_bits(digest, 12) is False
    assert has_leading_zero_bits(digest, 13) is False


def test_has_leading_zero_bits_zero() -> None:
    digest = bytes.fromhex("abcdef")
    assert has_leading_zero_bits(digest, 0) is True


def test_leading_zero_bits_count() -> None:
    digest = bytes.fromhex("0010")
    assert leading_zero_bits(digest) == 11

from sha256pow.utils.bits import has_leading_zero_bits


def test_basic() -> None:
    digest = bytes.fromhex("00f000")
    assert has_leading_zero_bits(digest, 8) is True
