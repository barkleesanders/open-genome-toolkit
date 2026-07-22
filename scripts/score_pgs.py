#!/usr/bin/env python3
"""Score normalized DNA against a PGS Catalog scoring file.

The PGS Catalog (https://www.pgscatalog.org) publishes thousands of published
polygenic scores as plain scoring files: one row per variant, with an effect
allele and a weight. Scoring is a dot product -- count your effect alleles at
each variant, multiply by its weight, sum.

    raw score = sum over variants of (effect_allele_dosage x effect_weight)

WHAT THIS SCRIPT WILL AND WILL NOT TELL YOU
    It reports your raw sum and what fraction of the score's variants your chip
    actually covers. It deliberately does NOT convert that into a percentile or
    a risk multiple, because doing so honestly requires a reference population
    scored on the same variant set, and a score computed on a different ancestry
    background than the source GWAS is not interpretable as an absolute risk.
    A raw sum is only meaningful compared with a distribution. See
    references/interpreting-results.md before you believe any number here.

Usage:
    python3 scripts/score_pgs.py --genome normalized.tsv --score PGS000000.txt.gz
    python3 scripts/score_pgs.py --self-test
"""

from __future__ import annotations

import argparse
import gzip
import io
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import TextIO

COMPLEMENT = {"A": "T", "T": "A", "C": "G", "G": "C"}
# Palindromic (strand-ambiguous) pairs: you cannot tell which strand a call is
# on, so flipping is a coin toss. These are excluded rather than guessed.
AMBIGUOUS = {frozenset("AT"), frozenset("CG")}


@dataclass
class ScoreResult:
    raw_score: float = 0.0
    variants_in_score: int = 0
    variants_matched: int = 0
    variants_missing: int = 0
    variants_strand_flipped: int = 0
    variants_ambiguous_skipped: int = 0
    variants_allele_mismatch: int = 0
    effect_alleles_counted: int = 0
    warnings: list[str] = field(default_factory=list)

    @property
    def coverage(self) -> float:
        if self.variants_in_score == 0:
            return 0.0
        return self.variants_matched / self.variants_in_score

    def report(self) -> str:
        lines = [
            "PGS scoring result",
            "==================",
            f"  raw score (sum of weighted dosages) : {self.raw_score:.6f}",
            f"  effect alleles counted              : {self.effect_alleles_counted:,}",
            "",
            f"  variants in scoring file            : {self.variants_in_score:,}",
            f"  matched in your genome              : {self.variants_matched:,} "
            f"({self.coverage:.1%})",
            f"  absent from your genome             : {self.variants_missing:,}",
            f"  matched after strand flip           : {self.variants_strand_flipped:,}",
            f"  skipped, strand-ambiguous (A/T,C/G) : {self.variants_ambiguous_skipped:,}",
            f"  skipped, alleles disagree           : {self.variants_allele_mismatch:,}",
        ]
        if self.warnings:
            lines += ["", "Warnings:"] + [f"  ! {w}" for w in self.warnings]
        lines += [
            "",
            "This raw sum is NOT a risk estimate and NOT a percentile.",
            "Read references/interpreting-results.md before drawing any conclusion.",
        ]
        return "\n".join(lines)


def open_text(path: Path) -> TextIO:
    if path.suffix.lower() == ".gz":
        return gzip.open(path, mode="rt", encoding="utf-8", errors="replace")
    return path.open(encoding="utf-8", errors="replace")


def load_genome(path: Path) -> dict[str, str]:
    """Load normalized.tsv into {rsid: genotype}."""
    genome: dict[str, str] = {}
    with open_text(path) as fh:
        header = fh.readline()
        if not header.lower().startswith("rsid"):
            raise ValueError(
                "genome file must be the output of normalize_raw_dna.py "
                "(expected a header starting with 'rsid')"
            )
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 4:
                continue
            genome[parts[0]] = parts[3].upper()
    return genome


def parse_scoring_file(fh: TextIO) -> tuple[list[dict[str, str]], list[str]]:
    """Parse a PGS Catalog scoring file. Returns (rows, header_comment_lines).

    PGS Catalog files are TSV with '#' metadata lines above a column header.
    Column names vary across releases, so they are resolved by name, not index.
    """
    comments: list[str] = []
    columns: list[str] | None = None
    rows: list[dict[str, str]] = []
    for line in fh:
        if line.startswith("#"):
            comments.append(line.strip())
            continue
        stripped = line.rstrip("\n\r")
        if not stripped:
            continue
        fields = stripped.split("\t") if "\t" in stripped else stripped.split(",")
        if columns is None:
            columns = [f.strip().lower() for f in fields]
            continue
        rows.append(dict(zip(columns, (f.strip() for f in fields))))
    return rows, comments


def _dosage(genotype: str, effect_allele: str) -> int:
    return sum(1 for base in genotype if base == effect_allele)


def score(genome: dict[str, str], rows: list[dict[str, str]]) -> ScoreResult:
    res = ScoreResult(variants_in_score=len(rows))

    if rows:
        first = rows[0]
        rsid_key = next(
            (k for k in ("rsid", "rsids", "variant_id", "snpid") if k in first), None
        )
        effect_key = next(
            (k for k in ("effect_allele", "a1", "allele1") if k in first), None
        )
        other_key = next(
            (k for k in ("other_allele", "reference_allele", "a2", "allele2")
             if k in first), None
        )
        weight_key = next(
            (k for k in ("effect_weight", "beta", "weight", "or") if k in first), None
        )
        if not (rsid_key and effect_key and weight_key):
            raise ValueError(
                "scoring file is missing required columns. Need an rsID column, an "
                f"effect_allele column, and an effect_weight column. Saw: {sorted(first)}"
            )
        if weight_key == "or":
            res.warnings.append(
                "scoring file supplies odds ratios, not betas; weights were "
                "log-transformed so they sum on the same scale"
            )
        if other_key is None:
            # Palindrome detection needs both alleles to know the pair is A/T or
            # C/G. Without the other allele the check cannot run, and silently
            # not running it is exactly the kind of invisible gap that makes a
            # score wrong in a way nobody notices. Say so.
            res.warnings.append(
                "scoring file has no other_allele column, so strand-ambiguity "
                "(A/T, C/G) detection is DISABLED for this run -- any variant "
                "reported on the opposite strand may be counted wrongly"
            )
    else:
        return res

    import math

    for row in rows:
        rsid = row.get(rsid_key, "")
        effect_allele = row.get(effect_key, "").upper()
        other_allele = (row.get(other_key, "") or "").upper()
        raw_weight = row.get(weight_key, "")

        try:
            weight = float(raw_weight)
        except (TypeError, ValueError):
            res.variants_allele_mismatch += 1
            continue
        if weight_key == "or":
            if weight <= 0:
                res.variants_allele_mismatch += 1
                continue
            weight = math.log(weight)

        genotype = genome.get(rsid)
        if genotype is None:
            res.variants_missing += 1
            continue
        if len(effect_allele) != 1 or effect_allele not in COMPLEMENT:
            # Indel or multi-base effect allele: dosage counting does not apply.
            res.variants_allele_mismatch += 1
            continue

        observed = set(genotype)

        # Strand-ambiguous variants are dropped BEFORE any dosage counting.
        # For an A/T or C/G SNP the effect allele can look present while the
        # call is simply reported on the opposite strand, so a match here is
        # a coin flip, not evidence. Resolving these needs allele frequencies;
        # dropping them is the conservative choice.
        if other_allele and frozenset({effect_allele, other_allele}) in AMBIGUOUS:
            res.variants_ambiguous_skipped += 1
            continue

        if effect_allele in observed:
            dosage = _dosage(genotype, effect_allele)
        else:
            # The call may simply be reported on the opposite strand.
            flipped = COMPLEMENT[effect_allele]
            if flipped in observed:
                dosage = _dosage(genotype, flipped)
                res.variants_strand_flipped += 1
            else:
                # Homozygous for the other allele is a legitimate zero dosage;
                # anything else means the alleles genuinely disagree.
                if other_allele and observed <= {
                    other_allele, COMPLEMENT.get(other_allele, "")
                }:
                    dosage = 0
                else:
                    res.variants_allele_mismatch += 1
                    continue

        res.variants_matched += 1
        res.effect_alleles_counted += dosage
        res.raw_score += dosage * weight

    if res.coverage < 0.5 and res.variants_in_score:
        res.warnings.append(
            f"only {res.coverage:.1%} of this score's variants are on your chip; "
            "the raw sum is not comparable to a published distribution. Impute "
            "first (see references/dna-analysis-pipeline.md)"
        )
    return res


SAMPLE_SCORE_FILE = """\
### PGS CATALOG SCORING FILE - synthetic test fixture
#pgs_id=PGS999999
rsid\tchr_name\tchr_position\teffect_allele\tother_allele\teffect_weight
rs0000001\t1\t1000\tA\tG\t0.10
rs0000002\t1\t2000\tC\tT\t0.20
rs0000003\t1\t3000\tG\tC\t0.30
rs0000004\t1\t4000\tT\tA\t0.40
rs0000005\t1\t5000\tA\tG\t0.50
"""


def self_test() -> int:
    """Score a synthetic genome against a synthetic scoring file.

    Hand-computed expectation, by variant:
      1st (weight 0.10) homozygous for the effect allele -> dosage 2 -> 0.20
      2nd (weight 0.20) heterozygous                     -> dosage 1 -> 0.20
      3rd (weight 0.30) palindromic C/G                  -> skipped
      4th (weight 0.40) palindromic A/T                  -> skipped
      5th (weight 0.50) absent from the genome           -> missing
      total = 0.40, matched 2, ambiguous 2, missing 1, effect alleles 3
    """
    genome = {
        "rs0000001": "AA",
        "rs0000002": "CT",
        "rs0000003": "GC",
        "rs0000004": "TA",
    }
    rows, comments = parse_scoring_file(io.StringIO(SAMPLE_SCORE_FILE))
    res = score(genome, rows)

    failures: list[str] = []
    if len(rows) != 5:
        failures.append(f"parsed {len(rows)} score rows, expected 5")
    if not comments:
        failures.append("dropped the '#' metadata header lines")
    if abs(res.raw_score - 0.40) > 1e-9:
        failures.append(f"raw_score {res.raw_score}, expected 0.40")
    if res.variants_matched != 2:
        failures.append(f"matched {res.variants_matched}, expected 2")
    if res.variants_ambiguous_skipped != 2:
        failures.append(
            f"ambiguous_skipped {res.variants_ambiguous_skipped}, expected 2"
        )
    if res.variants_missing != 1:
        failures.append(f"missing {res.variants_missing}, expected 1")
    if res.effect_alleles_counted != 3:
        failures.append(f"effect_alleles {res.effect_alleles_counted}, expected 3")

    # Strand-flip path: genome reported on the opposite strand must still match.
    flip_rows, _ = parse_scoring_file(io.StringIO(SAMPLE_SCORE_FILE))
    flip_res = score({"rs0000001": "TT"}, flip_rows)  # A/G score, T/T call = flipped A
    if flip_res.variants_strand_flipped != 1:
        failures.append(
            f"strand flip not detected (got {flip_res.variants_strand_flipped})"
        )
    if abs(flip_res.raw_score - 0.20) > 1e-9:
        failures.append(f"strand-flipped score {flip_res.raw_score}, expected 0.20")

    # Odds-ratio files must be log-transformed, not summed raw.
    or_file = SAMPLE_SCORE_FILE.replace("effect_weight", "OR").replace(
        "\t0.10", "\t1.0"
    )
    or_rows, _ = parse_scoring_file(io.StringIO(or_file))
    or_res = score({"rs0000001": "AA"}, or_rows)
    if abs(or_res.raw_score) > 1e-9:  # log(1.0) == 0
        failures.append(f"OR not log-transformed: got {or_res.raw_score}, expected 0")
    if not any("odds ratio" in w for w in or_res.warnings):
        failures.append("OR file did not raise the log-transform warning")

    if failures:
        print("SELF-TEST FAILED:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1
    print("self-test OK: dosage, strand-flip, palindrome skip, OR transform all correct")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--genome", help="normalized.tsv from normalize_raw_dna.py")
    ap.add_argument("--score", help="PGS Catalog scoring file (.txt or .txt.gz)")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return self_test()
    if not args.genome or not args.score:
        ap.error("--genome and --score are required (or use --self-test)")

    genome_path, score_path = Path(args.genome), Path(args.score)
    for p in (genome_path, score_path):
        if not p.exists():
            print(f"error: no such file: {p}", file=sys.stderr)
            return 2

    try:
        genome = load_genome(genome_path)
        with open_text(score_path) as fh:
            rows, _ = parse_scoring_file(fh)
        result = score(genome, rows)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(f"loaded {len(genome):,} variants from your genome\n")
    print(result.report())
    return 0


if __name__ == "__main__":
    sys.exit(main())
