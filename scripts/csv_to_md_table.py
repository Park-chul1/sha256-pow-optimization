import pandas as pd
import argparse
from pathlib import Path


def fmt(x):
    if pd.isna(x):
        return ""
    return f"{float(x):.4f}"


def make_python_table(df, double_hash: bool) -> str:
    df = df[df["double_hash"] == double_hash].copy()

    naive = df[df["backend"] == "python_naive"]
    opt = df[df["backend"] == "python_optimized"]
    mp = df[df["backend"] == "python_mp"]

    ks = sorted(df["k"].unique())

    lines = []
    lines.append("| k | naive (s) | optimized (s) | mp (s) |")
    lines.append("|---|-----------|---------------|--------|")

    for k in ks:
        n = naive.loc[naive["k"] == k, "elapsed_sec"]
        o = opt.loc[opt["k"] == k, "elapsed_sec"]
        m = mp.loc[mp["k"] == k, "elapsed_sec"]

        n_val = fmt(n.iloc[0]) if len(n) else ""
        o_val = fmt(o.iloc[0]) if len(o) else ""
        m_val = fmt(m.iloc[0]) if len(m) else ""

        lines.append(f"| {k} | {n_val} | {o_val} | {m_val} |")

    return "\n".join(lines)


def make_rust_table(df, double_hash: bool) -> str:
    df = df[df["double_hash"] == double_hash].copy()

    rust = df[df["backend"] == "pure_rust_sha2"]
    rust_mt = df[df["backend"] == "pure_rust_sha2_mt"]

    ks = sorted(df["k"].unique())

    lines = []
    lines.append("| k | rust (s) | rust mt (s) |")
    lines.append("|---|----------|-------------|")

    for k in ks:
        r = rust.loc[rust["k"] == k, "elapsed_sec"]
        rm = rust_mt.loc[rust_mt["k"] == k, "elapsed_sec"]

        r_val = fmt(r.iloc[0]) if len(r) else ""
        rm_val = fmt(rm.iloc[0]) if len(rm) else ""

        lines.append(f"| {k} | {r_val} | {rm_val} |")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--python-input", type=str, default="results/submission/python_all_k1_20.csv")
    parser.add_argument("--rust-input", type=str, default="results/submission/rust_all_k20_30.csv")
    parser.add_argument("--output", type=str, default="submission_tables.md")
    args = parser.parse_args()

    md_parts = []

    python_path = Path(args.python_input)
    if python_path.exists():
        py_df = pd.read_csv(python_path)

        md_parts.append("## Python (k = 1 ~ 20)\n")
        md_parts.append("### Single SHA\n")
        md_parts.append(make_python_table(py_df, double_hash=False))
        md_parts.append("\n")
        md_parts.append("### Double SHA\n")
        md_parts.append(make_python_table(py_df, double_hash=True))
        md_parts.append("\n")
    else:
        md_parts.append(f"<!-- Missing Python CSV: {python_path} -->\n")

    rust_path = Path(args.rust_input)
    if rust_path.exists():
        rust_df = pd.read_csv(rust_path)

        md_parts.append("## Rust (k = 20 ~ 30)\n")
        md_parts.append("### Single SHA\n")
        md_parts.append(make_rust_table(rust_df, double_hash=False))
        md_parts.append("\n")
        md_parts.append("### Double SHA\n")
        md_parts.append(make_rust_table(rust_df, double_hash=True))
        md_parts.append("\n")
    else:
        md_parts.append(f"<!-- Missing Rust CSV: {rust_path} -->\n")

    output_text = "\n".join(md_parts)
    Path(args.output).write_text(output_text, encoding="utf-8")
    print(f"saved to {args.output}")


if __name__ == "__main__":
    main()