use sha256pow_rust::pow::run_search;
use sha256pow_rust::pow_mt::run_search_mt;
use sha256pow_rust::pow_openssl::run_openssl_search;
use sha256pow_rust::pow_openssl_mt::run_openssl_search_mt;

fn main() {
    let prefix = b"homework";
    let k = 28;
    let workers = 12;

    println!("=== pure Rust single ===");
    let r1 = run_search(prefix, k, false);
    println!("{}", r1);

    println!("=== OpenSSL single ===");
    let r2 = run_openssl_search(prefix, k, false);
    println!("{}", r2);

    println!("=== pure Rust multi-thread ===");
    let r3 = run_search_mt(prefix, k, false, workers);
    println!("{}", r3);

    println!("=== OpenSSL multi-thread ===");
    let r4 = run_openssl_search_mt(prefix, k, false, workers);
    println!("{}", r4);

    println!("=== OpenSSL single (double SHA) ===");
    let r5 = run_openssl_search(prefix, k, true);
    println!("{}", r5);
}