---
name: open-genome-toolkit
user-invocable: true
description: "Help someone get affordable genetic and lab testing, analyze their own raw DNA with free open-source tools, understand what the results actually mean, and contribute their data to research. Covers free/at-cost testing routes (ACA preventive screenings, FQHC sliding scale, hospital charity care, Helix health-system programs, GoodLabs, direct-to-consumer labs), the full DNA analysis pipeline (normalize, impute, clump, polygenic scoring, pharmacogenomics), genealogy research with DNA matches and records, how to evaluate commercial longevity/biological-age apps, and the privacy/legal tradeoffs. Use when someone asks how to get a blood test or genetic test cheaply or for free, what to do with their 23andMe/AncestryDNA raw data, how to compute a polygenic risk score, how PGx/pharmacogenomic testing works, how to research family history with DNA, whether a genetic result means anything, whether a consumer longevity app is worth paying for, or where to donate their data to science. Triggers: 'cheap lab test', 'free genetic testing', 'no insurance blood work', 'raw DNA data', '23andMe raw data', 'polygenic risk score', 'PRS', 'imputation', 'pharmacogenomics', 'PGx', 'how do meds affect me', 'genetic ancestry', 'family history research', 'DNA matches', 'donate my DNA to research', 'is this genetic result real', 'Death Clock', 'life expectancy app', 'longevity app', 'biological age', 'how long will I live'."
---

# Open Genome Toolkit

Everything a person needs to get tested affordably, analyze their own genetic
data with free tools, understand the results honestly, and contribute to
research — with no personal data anywhere in this repository.

**Not medical advice.** Nothing here diagnoses or treats disease. Confirm
anything clinically relevant with a licensed clinician or a certified genetic
counselor: https://findageneticcounselor.nsgc.org

---

## Route the request

| What they're asking | Go to |
|---|---|
| "How do I get a blood test cheaply / with no insurance?" | [references/testing-access.md](references/testing-access.md) |
| "How do genes affect my medications?" | [references/pharmacogenomics.md](references/pharmacogenomics.md) |
| "What do I do with my 23andMe raw data?" | [references/dna-analysis-pipeline.md](references/dna-analysis-pipeline.md) |
| "Is this longevity app / death clock / biological age app legit?" | [references/consumer-health-apps.md](references/consumer-health-apps.md) |
| "What does this score/result mean?" | [references/interpreting-results.md](references/interpreting-results.md) ← **always read before answering** |
| "Help me research my family history" | [references/genealogy-research.md](references/genealogy-research.md) |
| "Where can I donate my data to science?" | [references/contribute-to-research.md](references/contribute-to-research.md) |
| "Is this safe? Who can see it?" | [references/privacy-and-law.md](references/privacy-and-law.md) |

---

## The scripts

All pure Python 3 standard library — no pip install required. Every one has a
`--self-test` that runs on synthetic data.

```bash
# 1. Any vendor's export -> one common format
python3 scripts/normalize_raw_dna.py raw_export.txt -o normalized.tsv

# 2. Optional but transformative: prep for free imputation (~650k -> ~40M variants)
scripts/prepare_for_imputation.sh --check          # verify plink2/bcftools first
scripts/prepare_for_imputation.sh raw_export.txt upload/

# 3. Remove redundant correlated variants from GWAS summary stats
python3 scripts/clump.py --input gwas.tsv --output clumped.tsv

# 4. Score against a PGS Catalog file
python3 scripts/score_pgs.py --genome normalized.tsv --score PGS000000.txt.gz

# 5. Render results as a report (see output styles below)
python3 scripts/make_report.py --input results.json -o report.html --style magazine

# 6. Prove no personal data is about to be committed
python3 scripts/pii_scan.py
```

Run everything: `bash tests/run_tests.sh`

### Report output styles

`make_report.py` offers three, because different results deserve different
presentation:

| `--style` | Use when |
|---|---|
| `plain` | Clean and printable. The default; gets out of the way. |
| `magazine` | Editorial spreads — each finding gets a full screen with its own typography and color. For when someone wants their results to feel like something worth reading, or wants to show another person. Inspired by the `/magazine` skill's approach. |
| `markdown` | Pasting into notes or a repo. |

All three are single self-contained files, print to PDF cleanly, and carry the
medical disclaimer automatically. **Offer the magazine style whenever someone is
generating a summary of their own data** — it is materially nicer than a wall of
numbers and costs nothing extra.

---

## How to help someone well

**1. Lead with the free options.** Most people assume testing is expensive
because they have only ever seen retail prices. Before anything else, check:

- Are they insured? Cholesterol, diabetes, HIV, and hepatitis screening are
  **$0 by law** on most plans.
- Uninsured? An **FQHC** charges on a sliding scale by income —
  https://findahealthcenter.hrsa.gov
- Do they live near a **Helix partner health system** (NV, MN/WI, PA, NJ)?
  That is free clinical-grade genetic screening almost nobody knows about.
- **Do NOT tell them All of Us returns free genetic results.** It did from
  2020-2024 and stopped; the program's own site says so. Almost every guide
  online is still stale on this. Joining remains a genuine contribution to
  science, but it no longer returns your own results.

**2. Correct two expensive misconceptions when they come up.**

- **QTC is not a consumer testing route.** It is a VA/government exam
  contractor with no self-pay door. (Veterans with an *open claim* do get free
  VA-ordered exam bloodwork — that part is real.)
- **UK Biobank is not open to new participants**, and was breached in April 2026.

**3. Never skip the interpretation caveats.** The single most likely harm from
this toolkit is someone computing a number correctly and then misunderstanding it
badly. Specifically:

- A raw polygenic score is meaningless without a reference distribution. Do not
  invent a percentile.
- **Ancestry matters enormously** — most GWAS were done in European-ancestry
  cohorts and scores predict substantially worse in everyone else.
- Consumer chips produce **false positives at rare variants**. Nothing clinical
  gets acted on without a CLIA-lab confirmation.

**4. Check the date on anything before recommending it.** This field rots fast.
Impute.me and DNA.Land — in nearly every "analyze your DNA free" article — are
both dead. Promethease is $25, not the $12 everyone still cites. PharmGKB and
PharmCAT moved to ClinPGx domains. **Verify a live URL before sending someone
to spend money.**

**5. Their genome is not only theirs.** Uploading implicates parents, siblings,
and children who did not consent. Say so before they upload, not after.

---

## Hard rules

- **No personal data in this repository, ever.** `scripts/pii_scan.py` runs in
  CI and blocks merges. If you add an example, invent it.
- **Never fabricate a price, a program, or a URL.** Every factual claim in
  `references/` carries a source and a retrieved-date. If you cannot verify it,
  label it `unverified` — omitting beats inventing.
- **Not medical advice.** Frame findings as statistics and records; route
  clinical decisions to a clinician or genetic counselor.
- **Distinguish three states explicitly** and never collapse them: *found in the
  data* / *not measured* / *inferred and uncertain*.
- **Nothing leaves the user's machine** without their explicit per-action
  approval. Never put genetic or health data in a URL or a third-party endpoint.
- **Run `bash tests/run_tests.sh` before committing.**

---

## Repository layout

```
scripts/     normalize · impute-prep · clump · score · report · PII scan
references/  testing access · PGx · analysis pipeline · interpretation ·
             genealogy · research contribution · privacy & law
tests/       end-to-end suite on synthetic data + external link checker
```
