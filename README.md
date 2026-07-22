# Open Genome Toolkit

**Get tested affordably. Analyze your own DNA with free tools. Understand what
the results actually mean. Contribute to research.**

Genetic and lab testing is far cheaper — often free — than most people realize,
and the tools to analyze your own data are open source and run on a laptop. The
hard parts are knowing which door to walk through and not misreading the answer.
That is what this repository is for.

No personal data is in this repository. An automated scanner blocks it in CI.

> **Not medical advice.** Nothing here diagnoses, treats, or predicts disease.
> Polygenic scores are population statistics, not predictions about you. Confirm
> anything clinically relevant with a licensed clinician or a certified genetic
> counselor: https://findageneticcounselor.nsgc.org

---

## Start here

**"I want a blood test but it's too expensive."**
→ [Testing access guide](references/testing-access.md)

Short version: if you have insurance, cholesterol, diabetes, HIV, and hepatitis
screening are **$0 by law**. If you don't, a
[community health center](https://findahealthcenter.hrsa.gov) charges on a
sliding scale by income. If you just want the numbers without a doctor's visit, a
lipid panel is **$33**. Every nonprofit hospital is legally required to have a
financial assistance policy that most people never ask for.

**"I want genetic testing but can't pay for it."**
→ [Testing access §4](references/testing-access.md#4-free-genetic-testing-through-research)

If you live in Nevada, Minnesota, Wisconsin, Pennsylvania, or New Jersey, your
health system may run a free
[Helix screening program](https://www.helix.com/health-systems/population-genomics-partners)
that almost nobody knows about — clinical-grade screening, no insurance required.

⚠️ **Correction most guides have missed:** *All of Us* **stopped returning DNA
results to participants** after 2024. Nearly every "free genetic testing"
article still recommends it for that. Joining is still a real contribution to
science — just not a way to get your own results.
[Details](references/testing-access.md)

**"How do my genes affect my medications?"**
→ [Pharmacogenomics guide](references/pharmacogenomics.md)

This is the area of consumer genomics with real, established clinical utility —
there are published prescribing guidelines keyed to genotype.

**"I have my 23andMe/Ancestry raw data. Now what?"**
→ [Analysis pipeline](references/dna-analysis-pipeline.md)

**"What does this result actually mean?"**
→ [Interpreting results](references/interpreting-results.md) — **read this one.**

---

## Quick start

No dependencies beyond Python 3. Nothing is uploaded anywhere.

```bash
git clone https://github.com/barkleesanders/open-genome-toolkit
cd open-genome-toolkit

# Verify everything works (runs on synthetic data)
bash tests/run_tests.sh

# Convert any vendor's raw export into one common format
python3 scripts/normalize_raw_dna.py ~/Downloads/genome_export.txt -o normalized.tsv

# Score it against a published polygenic score from pgscatalog.org
python3 scripts/score_pgs.py --genome normalized.tsv --score PGS000000.txt.gz
```

### The scripts

| Script | What it does |
|---|---|
| `normalize_raw_dna.py` | 23andMe / AncestryDNA / MyHeritage / FTDNA / LivingDNA → one TSV |
| `prepare_for_imputation.sh` | Chip → per-chromosome VCFs for a free imputation server (~650k → ~40M variants) |
| `clump.py` | Removes redundant correlated variants from GWAS summary statistics |
| `score_pgs.py` | Computes a polygenic score, handling strand ambiguity and odds ratios |
| `make_report.py` | Renders results as plain, **magazine-style**, or markdown |
| `pii_scan.py` | Blocks personal data from ever being committed |

Every script has a `--self-test` that runs on synthetic data.

### Make your results readable

```bash
python3 scripts/make_report.py --demo -o report.html --style magazine
```

Three styles: `plain` (clean and printable), `magazine` (editorial spreads — each
finding gets its own full screen), and `markdown`. Single self-contained files
that print to PDF cleanly and carry the disclaimer automatically.

---

## What's in the guides

| Guide | Covers |
|---|---|
| [**Testing access**](references/testing-access.md) | Free/at-cost routes: ACA $0 screenings, FQHC sliding scale, hospital charity care under IRS §501(r), Helix programs, GoodLabs blood-donation model, direct-to-consumer lab prices. Plus which widely-repeated claims are wrong. |
| [**Pharmacogenomics**](references/pharmacogenomics.md) | How your genes affect drug response, which gene/drug pairs have real prescribing guidance, and how to get tested. |
| [**Analysis pipeline**](references/dna-analysis-pipeline.md) | Raw data → imputation → clumping → scoring. Free tools, real commands, and the traps (genome build mismatch, imputation quality filtering). |
| [**Interpreting results**](references/interpreting-results.md) | Why a raw score means nothing alone, the ancestry portability problem, relative vs absolute risk, why consumer chips aren't clinical tests. |
| [**Genealogy research**](references/genealogy-research.md) | The source ladder, the heuristics that actually break cases, using DNA matches properly, evidence discipline. |
| [**Contribute to research**](references/contribute-to-research.md) | Where to donate your data, what you get back, and the honest tradeoffs. |
| [**Privacy and law**](references/privacy-and-law.md) | What GINA does and does not protect, law enforcement access, and why your data outlives the company holding it. |

---

## Three things worth knowing before you start

**1. GINA does not protect you from life, disability, or long-term-care
insurers.** It covers health insurance and employment. That's the whole list. If
you're considering buying those policies, many genetic counselors advise doing it
*before* testing. → [details](references/privacy-and-law.md)

**2. Most genetic research was done in people of European ancestry**, so
polygenic scores predict substantially worse for everyone else. This isn't a
footnote — it's the central limitation of the field, and it's the reason
participating in diverse research programs actually matters.
→ [details](references/interpreting-results.md)

**3. Your genome isn't only yours.** It's ~50% shared with each parent, sibling,
and child. Uploading it makes them findable too, and they didn't consent.

---

## Using this with Claude Code

This repository is also a [Claude Code](https://claude.com/claude-code) skill.
Clone it into your skills directory and the assistant will route questions to the
right guide, run the scripts, and apply the interpretation caveats automatically:

```bash
git clone https://github.com/barkleesanders/open-genome-toolkit \
  ~/.claude/skills/open-genome-toolkit
```

Then ask things like *"how do I get a cholesterol test without insurance"* or
*"score my raw DNA against a PGS Catalog file."* `SKILL.md` is the entry point.

It works fine as plain documentation without Claude Code.

---

## Contributing

Especially wanted:

- **Corrections.** This field rots fast — programs shut down, prices change,
  URLs move. If something here is stale, open an issue. `tests/check_links.sh`
  catches dead links; it can't catch a price that quietly doubled.
- **Non-US testing routes.** This guide is US-centric because that's what could
  be verified. NHS, provincial, and EU equivalents would help a lot of people.
- **More vendor formats** in `normalize_raw_dna.py`.

Two rules:

1. **No personal data, ever.** `python3 scripts/pii_scan.py` must pass. Invent
   your examples.
2. **Cite live sources with a retrieved-date.** Never a fabricated price,
   program, or URL. If you can't verify it, mark it `unverified` — omitting beats
   inventing.

```bash
bash tests/run_tests.sh     # must pass before you open a PR
```

---

## License

MIT — see [LICENSE](LICENSE). Use it, fork it, adapt it.

Built because this information exists but is scattered across government PDFs,
academic tool docs, and forum posts, and because the people who most need free
testing are least likely to know it's available.
