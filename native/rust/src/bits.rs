pub fn has_leading_zero_bits(digest: &[u8], k: u32) -> bool {
    let full_bytes = (k / 8) as usize;
    let rem_bits = (k % 8) as usize;

    if digest.len() < full_bytes {
        return false;
    }

    for &b in &digest[..full_bytes] {
        if b != 0 {
            return false;
        }
    }

    if rem_bits == 0 {
        return true;
    }

    if full_bytes >= digest.len() {
        return false;
    }

    let mask = 0xFFu8 << (8 - rem_bits);
    (digest[full_bytes] & mask) == 0
}

pub fn to_hex(bytes: &[u8]) -> String {
    let mut s = String::with_capacity(bytes.len() * 2);
    for b in bytes {
        use std::fmt::Write;
        let _ = write!(s, "{:02x}", b);
    }
    s
}

pub fn count_leading_zero_bits(digest: &[u8]) -> u32 {
    let mut count = 0u32;
    for &b in digest {
        if b == 0 {
            count += 8;
        } else {
            count += b.leading_zeros() - 24;
            break;
        }
    }
    count
}
