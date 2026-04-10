pub fn format_progress_line(
    backend: &str,
    k: u32,
    tries: u64,
    hashes_per_sec: f64,
    nonce: Option<u64>,
    workers: Option<usize>,
    best_lz: Option<u32>,
    elapsed_sec: Option<f64>,
) -> String {
    let mut parts = vec![format!("[progress:{}]", backend), format!("k={}", k)];
    if let Some(workers) = workers {
        parts.push(format!("workers={}", workers));
    }
    if let Some(nonce) = nonce {
        parts.push(format!("nonce={}", nonce));
    }
    if let Some(best_lz) = best_lz {
        parts.push(format!("best={} bits", best_lz));
    }
    parts.push(format!("tries={}", format_with_commas(tries)));
    parts.push(format!("throughput={:.2} MH/s", hashes_per_sec / 1e6));
    if let Some(elapsed_sec) = elapsed_sec {
        parts.push(format!("elapsed={:.1}s", elapsed_sec));
    }
    parts.join(" | ")
}

pub fn format_with_commas(value: u64) -> String {
    let s = value.to_string();
    let mut out = String::with_capacity(s.len() + s.len() / 3);
    for (i, ch) in s.chars().rev().enumerate() {
        if i != 0 && i % 3 == 0 {
            out.push(',');
        }
        out.push(ch);
    }
    out.chars().rev().collect()
}
