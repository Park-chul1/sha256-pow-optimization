use std::env;

use sha256pow_rust::pow::run_search_with_progress;
use sha256pow_rust::pow_mt::run_search_mt_with_progress;
use sha256pow_rust::pow_openssl::run_openssl_search_with_progress;
use sha256pow_rust::pow_openssl_mt::run_openssl_search_mt_with_progress;

#[derive(Debug, Clone)]
struct Args {
    backend: String,
    prefix: String,
    k: u32,
    double_hash: bool,
    workers: usize,
    progress_interval: Option<u64>,
    report_every_sec: Option<f64>,
}

impl Default for Args {
    fn default() -> Self {
        Self {
            backend: "openssl".to_string(),
            prefix: "homework".to_string(),
            k: 24,
            double_hash: false,
            workers: std::thread::available_parallelism()
                .map(|n| n.get())
                .unwrap_or(1),
            progress_interval: None,
            report_every_sec: None,
        }
    }
}

fn parse_args() -> Args {
    let mut args = Args::default();
    let mut it = env::args().skip(1);

    while let Some(arg) = it.next() {
        match arg.as_str() {
            "--backend" => args.backend = it.next().expect("missing value for --backend"),
            "--prefix" => args.prefix = it.next().expect("missing value for --prefix"),
            "--k" => args.k = it.next().expect("missing value for --k").parse().expect("invalid --k"),
            "--workers" => {
                args.workers = it
                    .next()
                    .expect("missing value for --workers")
                    .parse()
                    .expect("invalid --workers")
            }
            "--progress-interval" => {
                args.progress_interval = Some(
                    it.next()
                        .expect("missing value for --progress-interval")
                        .parse()
                        .expect("invalid --progress-interval"),
                )
            }
            "--report-every-sec" => {
                args.report_every_sec = Some(
                    it.next()
                        .expect("missing value for --report-every-sec")
                        .parse()
                        .expect("invalid --report-every-sec"),
                )
            }
            "--double" => args.double_hash = true,
            "-h" | "--help" => {
                print_help();
                std::process::exit(0);
            }
            other => {
                eprintln!("unknown argument: {}", other);
                print_help();
                std::process::exit(2);
            }
        }
    }

    args
}

fn print_help() {
    println!("Unified Rust SHA-256 PoW runner");
    println!("Usage:");
    println!("  cargo run --release -- --backend <rust|rust-mt|openssl|openssl-mt> [options]");
    println!();
    println!("Options:");
    println!("  --prefix <text>                Prefix string (default: homework)");
    println!("  --k <bits>                    Target leading zero bits (default: 24)");
    println!("  --double                      Use double SHA-256");
    println!("  --workers <n>                 Worker count for *-mt backends");
    println!("  --progress-interval <n>       Print progress every n tries on single-thread or thread-0 local interval on mt");
    println!("  --report-every-sec <sec>      Print periodic progress for mt backends");
}

fn main() {
    let args = parse_args();
    let prefix = args.prefix.as_bytes();

    let result = match args.backend.as_str() {
        "rust" => run_search_with_progress(prefix, args.k, args.double_hash, args.progress_interval),
        "rust-mt" => run_search_mt_with_progress(
            prefix,
            args.k,
            args.double_hash,
            args.workers,
            args.progress_interval,
            args.report_every_sec,
        ),
        "openssl" => run_openssl_search_with_progress(
            prefix,
            args.k,
            args.double_hash,
            args.progress_interval,
        ),
        "openssl-mt" => run_openssl_search_mt_with_progress(
            prefix,
            args.k,
            args.double_hash,
            args.workers,
            args.progress_interval,
            args.report_every_sec,
        ),
        other => {
            eprintln!("unsupported backend: {}", other);
            print_help();
            std::process::exit(2);
        }
    };

    println!("{}", result);
}
