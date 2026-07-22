#!/usr/bin/env python3
"""Look up pharmacogenomic prescribing guidance from CPIC's public API.

Pharmacogenomics (PGx) is the part of consumer genomics with actual clinical
utility. Unlike polygenic risk scores, there are published prescribing
guidelines keyed to genotype -- the Clinical Pharmacogenetics Implementation
Consortium (CPIC) writes them, they are peer reviewed, free, and used in real
clinical practice.

CPIC rates each gene-drug pair by evidence level:

    A  = genetic information SHOULD be used to change prescribing. Actionable.
    B  = genetic information COULD be used; alternatives may be considered.
    C  = evidence is insufficient, or no prescribing change is recommended.
    D  = evidence is weak or conflicting.

Only levels A and B are worth acting on, and only with a prescriber.

This queries CPIC live, so it never goes stale. It looks up *guidance for a
drug or gene* -- it does NOT read your genotype and does NOT tell you what to
take. That conversation belongs with a pharmacist or prescriber.

Usage:
    python3 scripts/pgx_lookup.py --drug warfarin
    python3 scripts/pgx_lookup.py --gene CYP2D6
    python3 scripts/pgx_lookup.py --actionable          # all level-A pairs
    python3 scripts/pgx_lookup.py --self-test           # offline checks
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.cpicpgx.org/v1"
TIMEOUT = 25

DISCLAIMER = (
    "CPIC guidance describes how a genotype affects drug response at the "
    "population level. It is not a prescription and not medical advice. Never "
    "start, stop, or change a dose based on this. Bring it to a prescriber or "
    "pharmacist -- pharmacogenomics is one of the few genomic findings they can "
    "act on directly."
)


def fetch(path: str, params: dict[str, str]) -> list[dict]:
    """GET a CPIC endpoint. Network failure is reported, never swallowed."""
    url = f"{API}/{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            data = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"CPIC API returned HTTP {exc.code} for {path}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(
            f"could not reach the CPIC API ({exc}). Check your connection; "
            "this tool needs network access because it reads guidance live."
        ) from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"CPIC API returned malformed JSON: {exc}") from exc
    if not isinstance(data, list):
        raise RuntimeError(f"expected a JSON array from {path}, got {type(data).__name__}")
    return data


_DRUG_NAMES: dict[str, str] | None = None


def drug_names() -> dict[str, str]:
    """Map CPIC drugid (an RxNorm identifier) -> human drug name.

    The pair table stores identifiers like 'RxNorm:2556'. Printing those is
    useless to a reader, so the drug table is fetched once and cached.
    """
    global _DRUG_NAMES
    if _DRUG_NAMES is None:
        rows = fetch("drug", {"select": "drugid,name"})
        _DRUG_NAMES = {str(r["drugid"]): r["name"] for r in rows if r.get("drugid")}
    return _DRUG_NAMES


def label_drugs(pairs: list[dict]) -> list[dict]:
    names = drug_names()
    for p in pairs:
        did = str(p.get("drugid", ""))
        p["drugname"] = names.get(did, did)
    return pairs


LEVEL_NOTE = {
    "A": "ACTIONABLE - genetic information should change prescribing",
    "A/B": "ACTIONABLE for some drugs in this group",
    "B": "genetic information could be used; alternatives may be considered",
    "B/C": "borderline evidence",
    "C": "no prescribing change recommended on current evidence",
    "C/D": "weak evidence",
    "D": "evidence weak or conflicting",
}


def show_pairs(pairs: list[dict], title: str) -> None:
    if not pairs:
        print(f"No CPIC gene-drug pairs found for {title}.")
        print("\nThat is a real answer: most drugs have no actionable "
              "pharmacogenomic guidance. Check the spelling (use the generic "
              "name, e.g. 'clopidogrel' not 'Plavix') before concluding.")
        return

    order = {lv: i for i, lv in enumerate(["A", "A/B", "B", "B/C", "C", "C/D", "D"])}
    pairs.sort(key=lambda p: (order.get(p.get("cpiclevel") or "", 99),
                              str(p.get("drugname") or p.get("genesymbol") or "")))

    print(f"CPIC guidance for {title}")
    print("=" * (len(title) + 18))
    current = None
    for p in pairs:
        lv = p.get("cpiclevel") or "?"
        if lv != current:
            current = lv
            print(f"\n  Level {lv} - {LEVEL_NOTE.get(lv, 'see CPIC')}")
        gene = p.get("genesymbol", "?")
        drug = p.get("drugname") or p.get("drugid") or "?"
        flag = " [guideline published]" if p.get("guidelineid") else ""
        print(f"    {gene:<10} {drug}{flag}")

    actionable = sum(1 for p in pairs if (p.get("cpiclevel") or "").startswith("A"))
    print(f"\n  {len(pairs)} pair(s); {actionable} at level A (actionable).")
    print(f"\n  Full guidelines: https://cpicpgx.org/guidelines/")
    print(f"\n{DISCLAIMER}")


def lookup_drug(name: str) -> None:
    # CPIC keys pairs by RxNorm id, so resolve the name to ids first.
    drugs = fetch("drug", {"select": "drugid,name", "name": f"ilike.*{name}*"})
    if not drugs:
        show_pairs([], f"drug '{name}'")
        return
    ids = ",".join(f'"{d["drugid"]}"' for d in drugs[:40])
    pairs = fetch("pair", {
        "select": "genesymbol,drugid,cpiclevel,guidelineid",
        "drugid": f"in.({ids})",
    })
    show_pairs(label_drugs(pairs), f"drug '{name}'")


def lookup_gene(symbol: str) -> None:
    pairs = fetch("pair", {
        "select": "genesymbol,drugid,cpiclevel,guidelineid",
        "genesymbol": f"eq.{symbol.upper()}",
    })
    show_pairs(label_drugs(pairs), f"gene {symbol.upper()}")


def list_actionable() -> None:
    pairs = fetch("pair", {
        "select": "genesymbol,drugid,cpiclevel,guidelineid",
        "cpiclevel": "eq.A",
    })
    label_drugs(pairs)
    by_gene: dict[str, list[str]] = {}
    for p in pairs:
        by_gene.setdefault(p.get("genesymbol", "?"), []).append(str(p.get("drugname")))

    print("CPIC Level A gene-drug pairs (highest evidence, actionable)")
    print("=" * 58)
    for gene in sorted(by_gene, key=lambda g: (-len(by_gene[g]), g)):
        drugs = sorted(by_gene[gene])
        print(f"\n  {gene}  ({len(drugs)} drug(s))")
        for i in range(0, len(drugs), 3):
            print("    " + ", ".join(drugs[i:i + 3]))
    print(f"\n  {len(pairs)} level-A pairs across {len(by_gene)} genes.")
    print(f"\n{DISCLAIMER}")


def self_test() -> int:
    """Offline checks. Network behaviour is exercised by the live commands."""
    failures: list[str] = []

    if not all(lv in LEVEL_NOTE for lv in ("A", "B", "C", "D")):
        failures.append("LEVEL_NOTE is missing a core evidence level")
    if "not medical advice" not in DISCLAIMER.lower():
        failures.append("disclaimer does not say it is not medical advice")

    # An empty result must produce guidance, not a silent blank.
    import io
    import contextlib

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        show_pairs([], "drug 'nonexistent'")
    out = buf.getvalue()
    if "No CPIC gene-drug pairs found" not in out:
        failures.append("empty result did not report clearly")
    if "generic name" not in out:
        failures.append("empty result did not suggest checking the generic name")

    # Sorting must put actionable pairs first regardless of input order.
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        show_pairs(
            [
                {"genesymbol": "GENE_C", "drugname": "drug_c", "cpiclevel": "C"},
                {"genesymbol": "GENE_A", "drugname": "drug_a", "cpiclevel": "A"},
                {"genesymbol": "GENE_B", "drugname": "drug_b", "cpiclevel": "B"},
            ],
            "test",
        )
    out = buf.getvalue()
    # Level A is the most actionable, so it must appear first (lowest index).
    if not (out.index("GENE_A") < out.index("GENE_B") < out.index("GENE_C")):
        failures.append("pairs were not sorted by evidence level (A must lead)")
    if "1 at level A" not in out:
        failures.append("actionable count wrong")
    if "not medical advice" not in out.lower():
        failures.append("disclaimer missing from output")

    if failures:
        print("SELF-TEST FAILED:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1
    print("self-test OK: level ordering, empty-result guidance, disclaimer present")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--drug", help="generic drug name, e.g. clopidogrel")
    g.add_argument("--gene", help="gene symbol, e.g. CYP2C19")
    g.add_argument("--actionable", action="store_true",
                   help="list every CPIC level-A pair")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    try:
        if args.drug:
            lookup_drug(args.drug)
        elif args.gene:
            lookup_gene(args.gene)
        elif args.actionable:
            list_actionable()
        else:
            ap.print_help()
            return 1
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
