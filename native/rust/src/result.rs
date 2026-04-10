use crate::progress::format_with_commas;

#[derive(Debug, Clone)]
pub struct SearchResult {
    pub nonce: u64,
    pub digest_hex: String,
    pub tries: u64,
    pub elapsed_sec: f64,
    pub hashes_per_sec: f64,
    pub double_hash: bool,
    pub k: u32,
    pub nonce_size: usize,
    pub backend: &'static str,
    pub workers: usize,
    pub prefix_hex: Option<String>,
}

impl std::fmt::Display for SearchResult {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        writeln!(f)?;
        writeln!(f, "[Search Result]")?;
        writeln!(f, "-----------------------------")?;
        writeln!(f, "backend         : {}", self.backend)?;
        writeln!(f, "workers         : {}", self.workers)?;
        writeln!(f, "nonce           : {}", self.nonce)?;
        writeln!(f, "digest (hex)    : {}", self.digest_hex)?;
        writeln!(f, "tries           : {}", format_with_commas(self.tries))?;
        writeln!(f, "elapsed (sec)   : {:.4}", self.elapsed_sec)?;
        writeln!(
            f,
            "throughput      : {:.2} H/s ({:.2} MH/s)",
            self.hashes_per_sec,
            self.hashes_per_sec / 1e6
        )?;
        writeln!(f, "double hash     : {}", self.double_hash)?;
        writeln!(f, "target bits (k) : {}", self.k)?;
        writeln!(f, "nonce size      : {} bytes", self.nonce_size)?;
        if let Some(prefix_hex) = &self.prefix_hex {
            writeln!(f, "prefix (hex)    : {}", prefix_hex)?;
        }
        Ok(())
    }
}
