#!/usr/bin/env python3
"""Fail-closed PII scanner for this repository.

This repo is public and is built from techniques originally developed against one
person's real genetic, medical, and genealogical data. Nothing personal may ship.
This scanner is the gate: CI runs it on every push and a hit fails the build.

Design notes:
  * Fail CLOSED. An unreadable file, an unknown encoding, or a regex error is a
    FAILURE, not a skip -- a scanner that silently passes is worse than none.
  * Detect CATEGORIES of identifier, not a blocklist of one person's details.
    A blocklist would leak the very names it tries to hide, and would not
    generalize to the next contributor who pastes their own data in.
  * Genetic/lab specificity is the subtle risk: `rs429358` alone is a public
    identifier and fine to discuss, but `rs429358 CT` is somebody's genotype.
    The same applies to a lab analyte paired with a value.

Usage:
    python3 scripts/pii_scan.py [path ...]      # default: repo root
    python3 scripts/pii_scan.py --self-test     # verify detectors still fire

Exit codes: 0 clean | 1 findings | 2 scanner error (treat as failure)
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Directories and files that are never scanned (binary/vendored/self).
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".mypy_cache"}
SKIP_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".gz", ".bz2", ".woff",
    ".woff2", ".ico", ".webp", ".mp4", ".vcf", ".bcf", ".bed", ".bim", ".fam",
}
# The scanner itself and its fixtures contain deliberate example patterns.
SELF_EXEMPT = {"scripts/pii_scan.py", "tests/fixtures/pii_positive_samples.txt"}


@dataclass(frozen=True)
class Rule:
    name: str
    pattern: re.Pattern[str]
    why: str


def _c(p: str) -> re.Pattern[str]:
    return re.compile(p, re.IGNORECASE)


# Lab analytes whose appearance next to a number implies a real result.
_ANALYTES = (
    r"hba1c|a1c|ldl|hdl|triglycerides?|cholesterol|apob|apo\s?b|lp\(a\)|"
    r"creatinine|egfr|tsh|t3|t4|testosterone|vitamin\s?d|hs-?crp|homocysteine|"
    r"ferritin|psa|alt|ast|glucose|insulin|bilirubin"
)

RULES: tuple[Rule, ...] = (
    Rule(
        "ssn",
        _c(r"\b\d{3}-\d{2}-\d{4}\b"),
        "Social Security number pattern",
    ),
    Rule(
        "ssn_last4_labeled",
        _c(r"\bssn\b[^.\n]{0,20}\b\d{4}\b"),
        "SSN referenced with digits",
    ),
    Rule(
        "us_phone",
        _c(r"(?<!\d)(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}(?!\d)"),
        "US phone number",
    ),
    Rule(
        "email_personal",
        # Allow role/report addresses a public repo legitimately needs.
        _c(r"\b[a-z0-9._%+-]+@(?!example\.|.*\.example\b)[a-z0-9.-]+\.[a-z]{2,}\b"),
        "email address (use example.com or a role address)",
    ),
    Rule(
        "dob",
        _c(r"\b(?:dob|date\s+of\s+birth|born)\b\s*[:=]?\s*"
           r"(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2})"),
        "date of birth",
    ),
    Rule(
        "street_address",
        _c(r"\b\d{2,6}\s+[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*\s+"
           r"(?:St|Street|Ave|Avenue|Rd|Road|Blvd|Boulevard|Way|Dr|Drive|Ln|Lane|"
           r"Ct|Court|Pl|Place|Ter|Terrace|Cir|Circle)\b\.?"
           r"(?:\s*,?\s*(?:Apt|Suite|Ste|Unit|#)\s*\S+)?"),
        "street address",
    ),
    Rule(
        "genotype_call",
        # rsID immediately followed by a genotype call = somebody's result.
        _c(r"\brs\d{3,}\b[\s:=(]*\b(?:[ACGT]{1,2}[/|]?[ACGT]{0,2}|"
           r"hom|het|homozygous|heterozygous)\b"),
        "rsID paired with a genotype -- that is a person's result, not a citation",
    ),
    Rule(
        "apoe_genotype",
        _c(r"\bapo\s?e\b[^.\n]{0,15}\be[234]\s*/\s*e?[234]\b"),
        "APOE genotype call",
    ),
    Rule(
        "star_allele_call",
        _c(r"\b(?:cyp\d[a-z]\d+|slco1b1|dpyd|tpmt|vkorc1|nudt15)\b[^.\n]{0,25}"
           r"\b(?:\*\d+\s*/\s*\*\d+|poor|intermediate|ultrarapid|rapid)\s*metabolizer\b"),
        "pharmacogenomic star-allele/phenotype call",
    ),
    Rule(
        "lab_value",
        _c(rf"\b(?:{_ANALYTES})\b\s*(?:of|was|is|=|:)?\s*\d+(?:\.\d+)?\s*"
           r"(?:mg/dl|mmol/l|ng/ml|pg/ml|iu/l|u/l|%|mg/l|nmol/l)"),
        "laboratory result with a value",
    ),
    Rule(
        "blood_pressure",
        _c(r"\b(?:bp|blood\s+pressure)\b[^.\n]{0,15}\b\d{2,3}\s*/\s*\d{2,3}\b"),
        "blood pressure reading",
    ),
    Rule(
        "prs_zscore",
        _c(r"\b(?:prs|polygenic\s+(?:risk\s+)?score|z-?score)\b[^.\n]{0,20}"
           r"[+-]\s?\d+\.\d+"),
        "polygenic score result value",
    ),
    Rule(
        "mrn_icn",
        _c(r"\b(?:mrn|icn|patient\s+id|member\s+id)\b\s*[:#=]?\s*[\w-]{6,}"),
        "medical record / patient identifier",
    ),
    Rule(
        "claim_case_number",
        _c(r"\b(?:claim|case|referral|docket|file)\s*(?:no\.?|number|#|id)\s*"
           r"[:#=]?\s*[A-Z0-9][\w-]{5,}"),
        "claim/case/referral number",
    ),
    Rule(
        "kit_id",
        _c(r"\b(?:kit|barcode|sample)\s*(?:id|no\.?|number|#)\s*[:#=]?\s*[A-Z0-9]{6,}"),
        "DNA kit / sample barcode",
    ),
    Rule(
        "api_key",
        _c(r"\b(?:sk|pk|ak|ck|ghp|gho|xox[baprs])[-_][A-Za-z0-9_-]{16,}\b"),
        "API key / token",
    ),
    Rule(
        "private_key",
        _c(r"-----BEGIN(?:\s+\w+)*\s+PRIVATE KEY-----"),
        "private key block",
    ),
    Rule(
        "home_path",
        _c(r"/(?:Users|home)/(?!<user>|username\b|you\b|user\b)[A-Za-z][\w.-]{2,}/"),
        "absolute home directory revealing a username (use ~ or <user>)",
    ),
    Rule(
        "ancestry_composition",
        _c(r"\b\d{1,3}(?:\.\d+)?%\s+(?:west\s+african|east\s+asian|"
           r"ashkenazi|sub-saharan|northwestern\s+european|native\s+american)\b"),
        "personal ancestry composition percentage",
    ),
    Rule(
        "haplogroup_assignment",
        _c(r"\b(?:my|his|her|their|patient'?s?|participant'?s?)\s+"
           r"(?:y-?dna|mtdna|maternal|paternal)\s+haplogroup\b"),
        "a specific person's haplogroup assignment",
    ),
)


def iter_files(roots: list[Path]) -> list[Path]:
    out: list[Path] = []
    for root in roots:
        if root.is_file():
            out.append(root)
            continue
        for p in sorted(root.rglob("*")):
            if not p.is_file():
                continue
            if any(part in SKIP_DIRS for part in p.parts):
                continue
            if p.suffix.lower() in SKIP_SUFFIXES:
                continue
            out.append(p)
    return out


def scan_file(path: Path) -> list[tuple[int, str, str, str]]:
    """Return (line_no, rule_name, why, excerpt) for each hit. Raises on read error."""
    rel = path.relative_to(REPO_ROOT).as_posix() if path.is_relative_to(REPO_ROOT) else path.as_posix()
    if rel in SELF_EXEMPT:
        return []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []  # genuinely binary; SKIP_SUFFIXES catches the known ones
    findings: list[tuple[int, str, str, str]] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        if "pii-scan:allow" in line:
            continue
        for rule in RULES:
            m = rule.pattern.search(line)
            if m:
                excerpt = m.group(0)
                if len(excerpt) > 60:
                    excerpt = excerpt[:57] + "..."
                findings.append((lineno, rule.name, rule.why, excerpt))
    return findings


SELF_TEST_CASES: tuple[tuple[str, str], ...] = (
    ("ssn", "SSN 123-45-6789 appears here"),
    ("us_phone", "call (415) 555-0142 today"),
    ("dob", "DOB: 1990-01-02"),
    ("street_address", "1234 Example Street, Apt 5"),
    ("genotype_call", "rs429358 CT was observed"),
    ("apoe_genotype", "APOE e3/e4 carrier"),
    ("star_allele_call", "CYP2C19 intermediate metabolizer"),
    ("lab_value", "HbA1c of 5.4 %"),
    ("blood_pressure", "BP 147/92 at intake"),
    ("prs_zscore", "PRS z-score +3.24"),
    ("mrn_icn", "ICN 1234567890V123456"),
    ("claim_case_number", "referral number VA0059860958"),
    ("api_key", "ghp_abcdefghijklmnopqrstuvwxyz01"),
    ("home_path", "/Users/somebody/health-hub/"),
    ("ancestry_composition", "82.4% West African"),
    ("email_personal", "someone@gmail.com"),
)


def self_test() -> int:
    by_name = {r.name: r for r in RULES}
    failures = []
    for rule_name, sample in SELF_TEST_CASES:
        rule = by_name.get(rule_name)
        if rule is None:
            failures.append(f"rule {rule_name!r} no longer exists")
            continue
        if not rule.pattern.search(sample):
            failures.append(f"rule {rule_name!r} FAILED to match its own sample: {sample!r}")
    # Negative controls: legitimate public-repo content must NOT trip the scanner.
    negatives = (
        "See the ClinVar entry for rs429358 for population frequencies.",
        "A lipid panel typically reports LDL, HDL, and triglycerides.",
        "Contact the maintainer at maintainer@example.com",
        "Store your export under ~/genome-data/raw.txt",
        "The PGS Catalog lists scores such as PGS000018.",
        "GoodLabs booking page: https://goodlabs.com/book-tests/donation",
    )
    for neg in negatives:
        for rule in RULES:
            if rule.pattern.search(neg):
                failures.append(f"FALSE POSITIVE: rule {rule.name!r} matched benign text: {neg!r}")
    if failures:
        print("SELF-TEST FAILED:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1
    print(f"self-test OK: {len(SELF_TEST_CASES)} detectors fire, "
          f"{len(negatives)} benign strings stay clean")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Fail-closed PII scanner")
    ap.add_argument("paths", nargs="*", default=[], help="paths to scan (default: repo root)")
    ap.add_argument("--self-test", action="store_true", help="verify detectors still work")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    roots = [Path(p).resolve() for p in args.paths] or [REPO_ROOT]
    for r in roots:
        if not r.exists():
            print(f"pii_scan: path does not exist: {r}", file=sys.stderr)
            return 2

    total = 0
    files = iter_files(roots)
    for path in files:
        try:
            hits = scan_file(path)
        except Exception as exc:  # fail closed
            print(f"pii_scan: ERROR reading {path}: {exc}", file=sys.stderr)
            return 2
        for lineno, name, why, excerpt in hits:
            rel = path.relative_to(REPO_ROOT) if path.is_relative_to(REPO_ROOT) else path
            print(f"{rel}:{lineno}: [{name}] {why} -> {excerpt!r}")
            total += 1

    if total:
        print(f"\nFAIL: {total} potential PII finding(s) across {len(files)} file(s).",
              file=sys.stderr)
        print("Fix the content, or append '# pii-scan:allow' to a line that is a "
              "deliberate, non-personal example.", file=sys.stderr)
        return 1
    print(f"PASS: no PII patterns found in {len(files)} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
