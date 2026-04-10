use openssl::sha::Sha256;
use std::sync::{
    atomic::{AtomicBool, AtomicU32, AtomicU64, Ordering},
    Arc, Mutex,
};
use std::thread;
use std::time::{Duration, Instant};

use crate::bits::{count_leading_zero_bits, has_leading_zero_bits, to_hex};
use crate::progress::format_progress_line;
use crate::result::SearchResult;

fn sha256_once(prefix: &[u8], nonce: u64) -> [u8; 32] {
    let nonce_bytes = nonce.to_le_bytes();

    let mut hasher = Sha256::new();
    hasher.update(prefix);
    hasher.update(&nonce_bytes);
    hasher.finish()
}

fn sha256_double(prefix: &[u8], nonce: u64) -> [u8; 32] {
    let first = sha256_once(prefix, nonce);

    let mut hasher = Sha256::new();
    hasher.update(&first);
    hasher.finish()
}

pub fn run_openssl_search_mt(
    prefix: &[u8],
    k: u32,
    double_hash: bool,
    workers: usize,
) -> SearchResult {
    run_openssl_search_mt_with_progress(prefix, k, double_hash, workers, None, None)
}

pub fn run_openssl_search_mt_with_progress(
    prefix: &[u8],
    k: u32,
    double_hash: bool,
    workers: usize,
    progress_interval: Option<u64>,
    report_every_sec: Option<f64>,
) -> SearchResult {
    let found = Arc::new(AtomicBool::new(false));
    let result = Arc::new(Mutex::new(None::<(u64, [u8; 32])>));
    let prefix = Arc::new(prefix.to_vec());
    let total_tries = Arc::new(AtomicU64::new(0));
    let best_lz = Arc::new(AtomicU32::new(0));

    let start = Instant::now();
    let mut handles = Vec::with_capacity(workers);

    for tid in 0..workers {
        let found = Arc::clone(&found);
        let result = Arc::clone(&result);
        let prefix = Arc::clone(&prefix);
        let total_tries = Arc::clone(&total_tries);
        let best_lz = Arc::clone(&best_lz);

        let handle = thread::spawn(move || {
            let mut nonce = tid as u64;
            let step = workers as u64;
            let mut local_tries = 0u64;

            while !found.load(Ordering::Relaxed) {
                local_tries += 1;
                total_tries.fetch_add(1, Ordering::Relaxed);

                let digest = if double_hash {
                    sha256_double(&prefix, nonce)
                } else {
                    sha256_once(&prefix, nonce)
                };

                let lz = count_leading_zero_bits(&digest);
                let mut current_best = best_lz.load(Ordering::Relaxed);
                while lz > current_best {
                    match best_lz.compare_exchange(
                        current_best,
                        lz,
                        Ordering::Relaxed,
                        Ordering::Relaxed,
                    ) {
                        Ok(_) => break,
                        Err(updated) => current_best = updated,
                    }
                }

                if has_leading_zero_bits(&digest, k) {
                    if !found.swap(true, Ordering::SeqCst) {
                        let mut lock = result.lock().unwrap();
                        *lock = Some((nonce, digest));
                    }
                    break;
                }

                if let Some(interval) = progress_interval {
                    if interval > 0 && local_tries % interval == 0 && tid == 0 {
                        let tries = total_tries.load(Ordering::Relaxed);
                        let elapsed = start.elapsed().as_secs_f64();
                        let hps = if elapsed > 0.0 { tries as f64 / elapsed } else { 0.0 };
                        println!(
                            "{}",
                            format_progress_line(
                                "openssl_mt",
                                k,
                                tries,
                                hps,
                                None,
                                Some(workers),
                                Some(best_lz.load(Ordering::Relaxed)),
                                Some(elapsed),
                            )
                        );
                    }
                }

                nonce = nonce.wrapping_add(step);
            }

            local_tries
        });

        handles.push(handle);
    }

    if let Some(period_sec) = report_every_sec {
        if period_sec > 0.0 {
            while !found.load(Ordering::Relaxed) {
                thread::sleep(Duration::from_secs_f64(period_sec));
                let tries = total_tries.load(Ordering::Relaxed);
                let elapsed = start.elapsed().as_secs_f64();
                let hps = if elapsed > 0.0 { tries as f64 / elapsed } else { 0.0 };
                println!(
                    "{}",
                    format_progress_line(
                        "openssl_mt",
                        k,
                        tries,
                        hps,
                        None,
                        Some(workers),
                        Some(best_lz.load(Ordering::Relaxed)),
                        Some(elapsed),
                    )
                );
            }
        }
    }

    let mut joined_tries = 0u64;
    for h in handles {
        joined_tries += h.join().unwrap();
    }

    let elapsed = start.elapsed().as_secs_f64();
    let tries = total_tries.load(Ordering::Relaxed).max(joined_tries);
    let hps = if elapsed > 0.0 {
        tries as f64 / elapsed
    } else {
        0.0
    };

    let (nonce, digest) = result.lock().unwrap().clone().expect("no result found");

    SearchResult {
        nonce,
        digest_hex: to_hex(&digest),
        tries,
        elapsed_sec: elapsed,
        hashes_per_sec: hps,
        double_hash,
        k,
        nonce_size: 8,
        backend: "openssl_mt",
        workers,
        prefix_hex: Some(to_hex(prefix.as_ref())),
    }
}
