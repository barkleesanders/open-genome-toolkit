#!/usr/bin/env python3
"""Distance-based LD clumping for GWAS summary statistics.

WHY THIS EXISTS -- the mistake that silently inflates polygenic scores
    Nearby variants are inherited together (linkage disequilibrium), so a single
    real association shows up as hundreds or thousands of correlated variants,
    each carrying its own weight in the summary statistics. Summing all of them
    counts the same signal over and over. The worst offender is the MHC/HLA
    region on chromosome 6, where long-range LD can make one locus contribute
    thousands of terms and dominate the entire score.

    A score computed without clumping is not a slightly-off score. It can be off
    by orders of magnitude, and it will still look like a plausible number.

WHAT THIS DOES
    Greedy distance-based clumping: sort variants by p-value, keep the most
    significant one in each window as the lead variant, discard every other
    variant within the window on the same chromosome, repeat.

    Distance is a proxy for correlation. Real LD clumping (PLINK's --clump) uses
    an actual r-squared matrix from a reference panel, which is more precise but
    needs a multi-gigabyte reference download. Distance-based clumping needs
    nothing, runs in seconds, and removes the great majority of the redundancy.
    Use PLINK if you need publication-grade rigor; use this to stop your score
    from being dominated by one locus.

Window guidance: 250kb aggressive, 500kb default, 1000kb conservative.

Usage:
    python3 scripts/clump.py --input gwas.tsv --output clumped.tsv
    python3 scripts/clump.py --input gwas.tsv --output clumped.tsv --window-kb 250
    python3 scripts/clump.py --self-test
"""

from __future__ import annotations

import argparse
import csv
import gzip
import io
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO

# Column-name aliases. GWAS summary statistics have no standard header, so
# every field is resolved by trying known spellings rather than by position.
ALIASES: dict[str, tuple[str, ...]] = {
    "snp": ("snp", "rsid", "rsids", "variant_id", "markername", "id", "snpid"),
    "chr": ("chr", "chrom", "chromosome", "chr_name", "#chrom", "hg19chr"),
    "pos": ("pos", "position", "bp", "base_pair_location", "chr_position", "bp_hg19"),
    "pval": ("p", "pval", "p_value", "pvalue", "p-value", "p_bolt_lmm", "frequentist_add_pvalue"),
}


@dataclass
class ClumpStats:
    total_in: int = 0
    unparseable: int = 0
    kept: int = 0

    @property
    def removed(self) -> int:
        return self.total_in - self.unparseable - self.kept

    @property
    def ratio(self) -> float:
        return (self.total_in / self.kept) if self.kept else 0.0


def open_text(path: Path) -> TextIO:
    if path.suffix.lower() == ".gz":
        return gzip.open(path, mode="rt", encoding="utf-8", errors="replace")
    return path.open(encoding="utf-8", errors="replace")


def resolve_columns(header: list[str]) -> dict[str, str]:
    """Map canonical field -> actual column name present in this file."""
    lowered = {h.strip().lower(): h for h in header}
    resolved: dict[str, str] = {}
    for canonical, candidates in ALIASES.items():
        for cand in candidates:
            if cand in lowered:
                resolved[canonical] = lowered[cand]
                break
    missing = set(ALIASES) - set(resolved)
    if missing:
        raise ValueError(
            f"could not find column(s) for {sorted(missing)} in this file. "
            f"Saw columns: {header}. Add the spelling to ALIASES in scripts/clump.py."
        )
    return resolved


def clump(
    rows: list[dict[str, str]],
    cols: dict[str, str],
    window_bp: int,
    stats: ClumpStats,
) -> list[dict[str, str]]:
    """Greedy p-value-ordered distance clumping.

    Complexity is O(n log n) for the sort plus O(n * k) for the sweep, where k
    is the number of already-kept leads on the same chromosome within range.
    Kept leads are tracked per chromosome so an entire genome does not get
    rescanned for every candidate.
    """
    parsed: list[tuple[float, str, int, dict[str, str]]] = []
    for row in rows:
        stats.total_in += 1
        try:
            p = float(row[cols["pval"]])
            chrom = str(row[cols["chr"]]).strip().removeprefix("chr")
            pos = int(float(row[cols["pos"]]))
        except (KeyError, TypeError, ValueError):
            stats.unparseable += 1
            continue
        if not (0.0 < p <= 1.0):
            stats.unparseable += 1
            continue
        parsed.append((p, chrom, pos, row))

    # Most significant first: the strongest variant in a region becomes its lead.
    parsed.sort(key=lambda t: t[0])

    kept_by_chrom: dict[str, list[int]] = {}
    kept_rows: list[dict[str, str]] = []
    for p, chrom, pos, row in parsed:
        leads = kept_by_chrom.setdefault(chrom, [])
        if any(abs(pos - lead_pos) <= window_bp for lead_pos in leads):
            continue
        leads.append(pos)
        kept_rows.append(row)
        stats.kept += 1
    return kept_rows


def self_test() -> int:
    """Verify clumping keeps the lead variant and drops its correlated neighbours."""
    cols = {"snp": "SNP", "chr": "CHR", "pos": "BP", "pval": "P"}

    def mk(snp: str, chrom: str, pos: int, p: float) -> dict[str, str]:
        return {"SNP": snp, "CHR": chrom, "BP": str(pos), "P": str(p)}

    failures: list[str] = []

    # One locus: a lead plus two neighbours inside a 500kb window, plus one
    # independent variant far away on the same chromosome, plus one on chr2.
    rows = [
        mk("lead_a", "1", 1_000_000, 1e-20),
        mk("near_a1", "1", 1_100_000, 1e-15),   # 100kb away -> dropped
        mk("near_a2", "1", 1_400_000, 1e-10),   # 400kb away -> dropped
        mk("far_a", "1", 3_000_000, 1e-9),      # 2Mb away   -> kept
        mk("chr2_v", "2", 1_050_000, 1e-8),     # other chrom -> kept
    ]
    stats = ClumpStats()
    kept = clump(rows, cols, window_bp=500_000, stats=stats)
    kept_ids = [r["SNP"] for r in kept]
    if kept_ids != ["lead_a", "far_a", "chr2_v"]:
        failures.append(f"expected [lead_a, far_a, chr2_v], got {kept_ids}")
    if stats.removed != 2:
        failures.append(f"expected 2 removed, got {stats.removed}")

    # The lead must be chosen by p-value, not by input order or position.
    rows2 = [
        mk("weaker", "1", 1_000_000, 1e-5),
        mk("stronger", "1", 1_050_000, 1e-30),
    ]
    stats2 = ClumpStats()
    kept2 = clump(rows2, cols, window_bp=500_000, stats=stats2)
    if [r["SNP"] for r in kept2] != ["stronger"]:
        failures.append(f"lead not chosen by p-value: {[r['SNP'] for r in kept2]}")

    # A tighter window must retain more independent signals.
    stats3 = ClumpStats()
    kept3 = clump(rows, cols, window_bp=50_000, stats=stats3)
    if len(kept3) <= 3:
        failures.append(f"50kb window kept {len(kept3)}, expected more than the 500kb run")

    # Malformed rows are counted, never silently dropped or crashed on.
    stats4 = ClumpStats()
    clump([mk("bad", "1", 1000, 0.5) | {"P": "not-a-number"}], cols, 500_000, stats4)
    if stats4.unparseable != 1:
        failures.append(f"malformed row not counted (unparseable={stats4.unparseable})")

    # Column resolution must handle an alternative header spelling.
    try:
        r = resolve_columns(["rsID", "chromosome", "base_pair_location", "p_value"])
        if r["snp"] != "rsID" or r["pos"] != "base_pair_location":
            failures.append(f"alias resolution wrong: {r}")
    except ValueError as exc:
        failures.append(f"alias resolution failed: {exc}")

    # A file with no p-value column must fail loudly, not guess.
    try:
        resolve_columns(["rsid", "chr", "pos"])
        failures.append("missing p-value column did not raise")
    except ValueError:
        pass

    if failures:
        print("SELF-TEST FAILED:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1
    print("self-test OK: lead selection, window logic, aliases, and error paths correct")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--input", help="GWAS summary statistics (TSV/CSV, optionally .gz)")
    ap.add_argument("--output", help="clumped output path")
    ap.add_argument("--window-kb", type=int, default=500,
                    help="clumping window in kb (default 500)")
    ap.add_argument("--p-threshold", type=float, default=None,
                    help="optionally keep only variants below this p-value first")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return self_test()
    if not args.input or not args.output:
        ap.error("--input and --output are required (or use --self-test)")

    in_path = Path(args.input)
    if not in_path.exists():
        print(f"error: no such file: {in_path}", file=sys.stderr)
        return 2

    with open_text(in_path) as fh:
        sample = fh.read(8192)
        fh.seek(0)
        delimiter = "\t" if "\t" in sample.split("\n")[0] else ","
        reader = csv.DictReader(fh, delimiter=delimiter)
        if reader.fieldnames is None:
            print("error: input file has no header row", file=sys.stderr)
            return 2
        try:
            cols = resolve_columns(list(reader.fieldnames))
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        rows = list(reader)

    if args.p_threshold is not None:
        before = len(rows)
        rows = [
            r for r in rows
            if _safe_float(r.get(cols["pval"])) is not None
            and _safe_float(r.get(cols["pval"])) < args.p_threshold  # type: ignore[operator]
        ]
        print(f"p-value filter < {args.p_threshold}: {before:,} -> {len(rows):,} variants")

    stats = ClumpStats()
    kept = clump(rows, cols, window_bp=args.window_kb * 1000, stats=stats)

    out_path = Path(args.output)
    with out_path.open("w", encoding="utf-8", newline="") as fh:
        if kept:
            writer = csv.DictWriter(fh, fieldnames=list(kept[0].keys()), delimiter="\t")
            writer.writeheader()
            writer.writerows(kept)

    print(
        f"clumped at {args.window_kb}kb: {stats.total_in:,} in -> {stats.kept:,} "
        f"independent loci ({stats.removed:,} removed, {stats.unparseable:,} unparseable)"
    )
    if stats.ratio > 20:
        print(
            f"note: input:output ratio is {stats.ratio:.0f}x. A ratio this high means "
            "a few long-range-LD regions dominated the raw file -- which is exactly "
            "the inflation clumping exists to remove.",
        )
    return 0


def _safe_float(v: str | None) -> float | None:
    try:
        return float(v)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


if __name__ == "__main__":
    sys.exit(main())
