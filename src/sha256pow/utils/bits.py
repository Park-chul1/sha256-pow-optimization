from __future__ import annotations


def has_leading_zero_bits(digest: bytes, k: int) -> bool:
    """
    Return True if `digest` has at least k leading zero bits.

    Examples:
        k = 0  -> always True
        k = 8  -> first byte must be 0x00
        k = 12 -> first byte 0x00 and high 4 bits of second byte are 0
    """
    if k < 0:
        raise ValueError("k must be >= 0")

    total_bits = len(digest) * 8
    if k > total_bits:
        return False

    full_zero_bytes = k // 8
    remaining_bits = k % 8

    for i in range(full_zero_bytes):
        if digest[i] != 0:
            return False

    if remaining_bits == 0:
        return True

    next_byte = digest[full_zero_bytes]
    mask = 0xFF << (8 - remaining_bits)
    mask &= 0xFF
    return (next_byte & mask) == 0


def leading_zero_bits(digest: bytes) -> int:
    """
    Count the exact number of leading zero bits in the digest.
    """
    count = 0
    for b in digest:
        if b == 0:
            count += 8
            continue

        for shift in range(7, -1, -1):
            if (b >> shift) & 1 == 0:
                count += 1
            else:
                return count
    return count