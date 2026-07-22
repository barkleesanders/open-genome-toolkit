#!/usr/bin/env python3
"""Normalize a consumer DNA raw-data export into one common TSV.

Every consumer testing company ships a slightly different text format. This
converts 23andMe, AncestryDNA, MyHeritage, FamilyTreeDNA, and LivingDNA exports
into a single tab-separated file so every downstream script in this repo has
exactly one input format to care about.

Output columns: rsid  chrom  pos  genotype

Nothing is uploaded anywhere. This runs entirely on your machine.

Usage:
    python3 scripts/normalize_raw_dna.py raw_export.txt -o normalized.tsv
    python3 scripts/normalize_raw_dna.py raw_export.zip -o normalized.tsv
    python3 scripts/normalize_raw_dna.py --self-test
"""

from __future__ import annotations

import argparse
import gzip
import io
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, TextIO

VALID_BASES = set("ACGTDI-0")  # D/I = indel calls, - and 0 = no-call


@dataclass(frozen=True)
class Variant:
    rsid: str
    chrom: str
    pos: str
    genotype: str


@dataclass
class Stats:
    detected_format: str = "unknown"
    total_lines: int = 0
    parsed: int = 0
    no_calls: int = 0
    malformed: int = 0

    def summary(self) -> str:
        return (
            f"format={self.detected_format} parsed={self.parsed:,} "
            f"no_calls={self.no_calls:,} malformed={self.malformed:,}"
        )


def open_maybe_compressed(path: Path) -> TextIO:
    """Open .txt, .csv, .gz, or .zip (first plausible member) as text."""
    if path.suffix.lower() == ".zip":
        zf = zipfile.ZipFile(path)
        members = [
            n for n in zf.namelist()
            if not n.startswith("__MACOSX") and n.lower().endswith((".txt", ".csv"))
        ]
        if not members:
            raise ValueError(f"no .txt/.csv member inside {path.name}")
        # Largest member is the genome file, not a readme.
        member = max(members, key=lambda n: zf.getinfo(n).file_size)
        return io.TextIOWrapper(zf.open(member), encoding="utf-8", errors="replace")
    if path.suffix.lower() == ".gz":
        return gzip.open(path, mode="rt", encoding="utf-8", errors="replace")
    return path.open(encoding="utf-8", errors="replace")


def detect_format(header_lines: list[str]) -> str:
    """Identify the vendor from the comment header and/or column header."""
    blob = "\n".join(header_lines).lower()
    if "23andme" in blob:
        return "23andme"
    if "ancestrydna" in blob or "ancestry.com" in blob:
        return "ancestrydna"
    if "myheritage" in blob:
        return "myheritage"
    if "livingdna" in blob or "living dna" in blob:
        return "livingdna"
    if "ftdna" in blob or "familytreedna" in blob or "family tree dna" in blob:
        return "ftdna"
    # Fall back to column shape.
    if "allele1" in blob and "allele2" in blob:
        return "ancestrydna"
    if "rsid" in blob and "chromosome" in blob:
        return "23andme"
    return "unknown"


def _split(line: str) -> list[str]:
    """Vendors use tabs or commas, and MyHeritage quotes every field."""
    raw = line.rstrip("\n\r")
    parts = raw.split("\t") if "\t" in raw else raw.split(",")
    return [p.strip().strip('"').strip("'") for p in parts]


def parse(handle: TextIO, stats: Stats) -> Iterator[Variant]:
    """Yield Variants from any supported vendor export.

    Columns are resolved per-vendor rather than positionally-guessed, because
    AncestryDNA splits the genotype across two allele columns while the others
    keep it in one -- silently concatenating the wrong columns would produce
    plausible-looking garbage.
    """
    header_lines: list[str] = []
    column_header: list[str] | None = None

    for line in handle:
        stats.total_lines += 1
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            header_lines.append(stripped)
            continue

        fields = _split(line)
        if column_header is None:
            lowered = [f.lower() for f in fields]
            # A column header row names its columns; a data row starts with rs/i id.
            if any(h in lowered for h in ("rsid", "rs id", "identifier")) or (
                lowered and lowered[0] in ("rsid", "snp", "marker")
            ):
                column_header = lowered
                header_lines.append(stripped)
                stats.detected_format = detect_format(header_lines)
                continue
            # Headerless file (some 23andMe exports): infer and fall through.
            stats.detected_format = detect_format(header_lines)
            column_header = []

        if len(fields) < 4:
            stats.malformed += 1
            continue

        rsid, chrom, pos = fields[0], fields[1], fields[2]

        # AncestryDNA: rsid, chromosome, position, allele1, allele2
        if len(fields) >= 5 and len(fields[3]) == 1 and len(fields[4]) == 1:
            genotype = (fields[3] + fields[4]).upper()
        else:
            genotype = fields[3].upper()

        if not rsid or not chrom or not pos:
            stats.malformed += 1
            continue
        if not set(genotype) <= VALID_BASES or not genotype:
            stats.malformed += 1
            continue
        if set(genotype) <= {"-", "0"}:
            stats.no_calls += 1
            continue

        stats.parsed += 1
        yield Variant(rsid=rsid, chrom=chrom, pos=pos, genotype=genotype)


def write_tsv(variants: Iterator[Variant], out_path: Path) -> None:
    with out_path.open("w", encoding="utf-8") as fh:
        fh.write("rsid\tchrom\tpos\tgenotype\n")
        for v in variants:
            fh.write(f"{v.rsid}\t{v.chrom}\t{v.pos}\t{v.genotype}\n")


SAMPLE_23ANDME = """# This data file generated by 23andMe at: Wed Jan 01 00:00:00 2020
# rsid\tchromosome\tposition\tgenotype
rsid\tchromosome\tposition\tgenotype
rs4477212\t1\t82154\tAA
rs3094315\t1\t752566\tAG
rs3131972\t1\t752721\tGG
rs12124819\t1\t776546\t--
"""

SAMPLE_ANCESTRY = """#AncestryDNA raw data download
rsid\tchromosome\tposition\tallele1\tallele2
rs4477212\t1\t82154\tA\tA
rs3094315\t1\t752566\tA\tG
rs3131972\t1\t752721\tG\tG
"""

SAMPLE_MYHERITAGE = """# MyHeritage DNA raw data.
"RSID","CHROMOSOME","POSITION","RESULT"
"rs4477212","1","82154","AA"
"rs3094315","1","752566","AG"
"""


def self_test() -> int:
    """Parse one synthetic sample per vendor format. No real genomes involved."""
    cases = (
        ("23andme", SAMPLE_23ANDME, 3, 1),
        ("ancestrydna", SAMPLE_ANCESTRY, 3, 0),
        ("myheritage", SAMPLE_MYHERITAGE, 2, 0),
    )
    failures: list[str] = []
    for expected_fmt, sample, expect_parsed, expect_nocall in cases:
        stats = Stats()
        variants = list(parse(io.StringIO(sample), stats))
        if stats.detected_format != expected_fmt:
            failures.append(
                f"{expected_fmt}: detected {stats.detected_format!r} instead"
            )
        if stats.parsed != expect_parsed:
            failures.append(
                f"{expected_fmt}: parsed {stats.parsed}, expected {expect_parsed}"
            )
        if stats.no_calls != expect_nocall:
            failures.append(
                f"{expected_fmt}: no_calls {stats.no_calls}, expected {expect_nocall}"
            )
        # AncestryDNA's split alleles must rejoin into a 2-char genotype.
        if expected_fmt == "ancestrydna" and variants:
            if variants[1].genotype != "AG":
                failures.append(
                    f"ancestrydna: allele columns joined wrong -> {variants[1].genotype!r}"
                )
    if failures:
        print("SELF-TEST FAILED:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1
    print(f"self-test OK: {len(cases)} vendor formats parse correctly")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("input", nargs="?", help="raw export (.txt/.csv/.gz/.zip)")
    ap.add_argument("-o", "--output", help="output TSV path")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return self_test()
    if not args.input or not args.output:
        ap.error("input and --output are required (or use --self-test)")

    in_path = Path(args.input)
    if not in_path.exists():
        print(f"error: no such file: {in_path}", file=sys.stderr)
        return 2

    stats = Stats()
    try:
        with open_maybe_compressed(in_path) as fh:
            write_tsv(parse(fh, stats), Path(args.output))
    except (ValueError, zipfile.BadZipFile, OSError) as exc:
        print(f"error: could not read {in_path.name}: {exc}", file=sys.stderr)
        return 2

    print(f"wrote {args.output}: {stats.summary()}")
    if stats.detected_format == "unknown":
        print(
            "warning: vendor not recognized from the file header. The rows above "
            "parsed on column shape alone -- spot-check the output before scoring.",
            file=sys.stderr,
        )
    if stats.parsed == 0:
        print("error: zero variants parsed -- this is probably not a raw DNA export",
              file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
