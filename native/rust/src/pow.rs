use sha2::{Digest, Sha256};
use std::time::Instant;

use crate::bits::{has_leading_zero_bits, to_hex};
use crate::progress::format_progress_line;
use crate::result::SearchResult;

fn sha256_once(prefix: &[u8], nonce: u64) -> [u8; 32] {
    let nonce_bytes = nonce.to_le_bytes();

    let mut hasher = Sha256::new();
    hasher.update(prefix);
    hasher.update(nonce_bytes);
    hasher.finalize().into()
}

fn sha256_double(prefix: &[u8], nonce: u64) -> [u8; 32] {
    let first = sha256_once(prefix, nonce);

    let mut hasher = Sha256::new();
    hasher.update(first);
    hasher.finalize().into()
}

pub fn run_search(prefix: &[u8], k: u32, double_hash: bool) -> SearchResult {
    run_search_with_progress(prefix, k, double_hash, None)
}

pub fn run_search_with_progress(
    prefix: &[u8],
    k: u32,
    double_hash: bool,
    progress_interval: Option<u64>,
) -> SearchResult {
    let start = Instant::now();
    let mut tries: u64 = 0;
    let mut nonce: u64 = 0;

    loop {
        tries += 1;

        let digest = if double_hash {
            sha256_double(prefix, nonce)
        } else {
            sha256_once(prefix, nonce)
        };

        if let Some(interval) = progress_interval {
            if interval > 0 && tries % interval == 0 {
                let elapsed = start.elapsed().as_secs_f64();
                let hps = if elapsed > 0.0 { tries as f64 / elapsed } else { 0.0 };
                println!(
                    "{}",
                    format_progress_line(
                        "pure_rust_sha2",
                        k,
                        tries,
                        hps,
                        Some(nonce),
                        Some(1),
                        None,
                        Some(elapsed),
                    )
                );
            }
        }

        if has_leading_zero_bits(&digest, k) {
            let elapsed = start.elapsed().as_secs_f64();
            let hps = if elapsed > 0.0 {
                tries as f64 / elapsed
            } else {
                0.0
            };

            return SearchResult {
                nonce,
                digest_hex: to_hex(&digest),
                tries,
                elapsed_sec: elapsed,
                hashes_per_sec: hps,
                double_hash,
                k,
                nonce_size: 8,
                backend: "pure_rust_sha2",
                workers: 1,
                prefix_hex: Some(to_hex(prefix)),
            };
        }

        nonce = nonce.wrapping_add(1);
    }
}
