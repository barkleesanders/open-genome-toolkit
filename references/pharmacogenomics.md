# Pharmacogenomics: how your genes affect your medications

**If you read only one guide here, make it this one.**

Most of consumer genomics is interesting but not actionable. Pharmacogenomics
(PGx) is the exception. It is the one area where your DNA can change a real
clinical decision *today*, using peer-reviewed prescribing guidelines that
clinicians already follow.

The difference matters. A polygenic risk score says "people with your genotype
have somewhat elevated odds of X." A pharmacogenomic result says "at your
genotype, the standard starting dose of this drug is likely wrong for you." One
is a statistic. The other is a prescription change.

> **Still not medical advice.** Never start, stop, or change a dose based on
> anything here or on a consumer test. Bring results to a prescriber or
> pharmacist — this is one of the few genomic findings they can act on directly.

---

## What PGx actually is

Your body processes drugs using enzymes, mostly in the liver. The genes coding
those enzymes vary between people. Depending on your variants you may be a:

| Metabolizer type | What it means |
|---|---|
| **Poor** | The drug builds up. Standard dose can be an overdose. |
| **Intermediate** | Reduced processing; may need a lower dose. |
| **Normal** | Standard dosing was designed for you. |
| **Rapid / Ultrarapid** | You clear the drug fast. It may not work — or, for a *prodrug* that your body must activate, you may get a dangerous overdose from a normal dose. |

That last case is genuinely counterintuitive and it is why this matters.
**Codeine** is inert until CYP2D6 converts it to morphine. An ultrarapid
metabolizer converts too much, too fast. This is not theoretical — it is why
codeine carries restrictions for children and for breastfeeding mothers.

---

## The evidence base: CPIC

The **Clinical Pharmacogenetics Implementation Consortium** publishes free,
peer-reviewed, genotype-keyed prescribing guidelines. This is the authority.

**https://www.clinpgx.org/cpic/guidelines** (the older
`cpicpgx.org/guidelines/` path now redirects here — CPIC, PharmGKB and PharmCAT
have merged under the ClinPGx umbrella)

CPIC grades every gene–drug pair by evidence level:

| Level | Meaning | Act on it? |
|---|---|---|
| **A** | Genetic information **should** be used to change prescribing | **Yes**, with a prescriber |
| **B** | Genetic information **could** be used; alternatives may be considered | Maybe |
| **C** | Insufficient evidence, or no prescribing change recommended | No |
| **D** | Weak or conflicting evidence | No |

**Verified live from CPIC's public API on 2026-07-21:** 635 gene–drug pairs
total, of which **96 are Level A** across **21 genes**. That is the real size of
the actionable set — large enough to matter, small enough that "PGx will optimize
all your medications" is marketing, not science.

### Look it up yourself

This repo queries CPIC live, so the guidance is never stale:

```bash
python3 scripts/pgx_lookup.py --drug clopidogrel   # which genes affect this drug
python3 scripts/pgx_lookup.py --gene CYP2D6        # which drugs this gene affects
python3 scripts/pgx_lookup.py --actionable         # all 96 Level A pairs
```

Use **generic** names (`clopidogrel`, not `Plavix`).

---

## The genes that matter most

Verified Level-A drug counts from the CPIC API, 2026-07-21:

| Gene | Level-A drugs | Notable examples |
|---|---|---|
| **CYP2C9** | 12 | warfarin, phenytoin, celecoxib, ibuprofen, meloxicam, piroxicam, fluvastatin |
| **CYP2D6** | 11 | codeine, tramadol, tamoxifen, amitriptyline, nortriptyline, paroxetine, atomoxetine, ondansetron |
| **MT-RNR1** | 11 | gentamicin, tobramycin, amikacin, streptomycin and other aminoglycoside antibiotics |
| **CYP2C19** | 9 | clopidogrel, and several antidepressants and antifungals |
| **G6PD** | 8 | — |
| **SLCO1B1** | 7 | statins (simvastatin especially) |
| **CACNA1S**, **RYR1** | 7 each | anesthesia agents (malignant hyperthermia risk) |

A few pairings worth knowing by name:

- **CYP2C19 + clopidogrel (Plavix).** Poor metabolizers don't activate the drug
  properly, so a stent patient can be taking a blood thinner that isn't thinning.
  The FDA label carries a boxed warning about this.
- **CYP2C9 + VKORC1 + warfarin.** Warfarin has a narrow therapeutic window —
  too little and you clot, too much and you bleed. Genotype meaningfully predicts
  starting dose.
- **SLCO1B1 + simvastatin.** Predicts risk of statin-induced muscle damage
  (myopathy), the most common reason people quit statins.
- **DPYD + fluorouracil/capecitabine.** Deficient metabolizers can suffer
  **fatal** toxicity from standard chemotherapy doses. Testing before treatment
  is increasingly standard of care.
- **TPMT and NUDT15 + thiopurines** (azathioprine, mercaptopurine). Severe,
  potentially fatal bone-marrow suppression at standard doses.
- **HLA-B\*57:01 + abacavir.** Predicts a life-threatening hypersensitivity
  reaction. Testing before prescribing is *required*, not optional.
- **MT-RNR1 + aminoglycoside antibiotics.** A single dose can cause permanent
  hearing loss in people with the relevant mitochondrial variant.
- **CACNA1S / RYR1 + anesthesia.** Malignant hyperthermia — a surgical
  emergency. Worth knowing before an operation, not after.

Note how many of these are not about "optimization" at all. They are about
avoiding a specific, severe, documented harm.

---

## How to get PGx testing

### Free — and the free option most guides still list is gone

⚠️ **All of Us no longer returns its "Medicine and Your DNA" report.** From 2020
to 2024 the NIH *All of Us* program gave participants a free pharmacogenetics
report covering seven drug-metabolism genes. Its own site now states plainly that
**All of Us is no longer returning research DNA results** (verified
2026-07-21 at https://www.joinallofus.org/DNA-and-Research). Nearly every "free
pharmacogenomic testing" article online still recommends it. They are stale.

**There is currently no verified, generally-available free PGx test in the US.**
Saying so is more useful than sending you to sign up for something that ended.

The closest things to free:

- **Helix health-system programs** (Nevada, Minnesota/Wisconsin, Pennsylvania,
  New Jersey) return clinical-grade results at no cost if you live in a partner
  region. Confirm whether their panel includes pharmacogenes before assuming.
- **Insurance coverage through a prescriber** is the realistic route to $0 —
  see below.

### Through a clinician

Ask your prescriber or pharmacist directly, especially if you:

- Are starting warfarin, clopidogrel, a statin, an antidepressant, or chemotherapy
- Have had an unusual reaction, no response, or bad side effects on a normal dose
- Are about to have surgery (anesthesia genes)
- Take several medications at once

Insurance coverage varies a lot by test, indication, and payer. Coverage is
generally better when tied to a specific drug decision than when ordered as a
general panel. **Ask about coverage before the test, not after.**

### Commercial panels

| Panel | Cost | Notes |
|---|---|---|
| **OneOme RightMed** | **$199** out-of-pocket cap via their financial assistance program; **$399** via telemedicine including the lab order and consult | Best-documented option. **Publishes its CLIA and CAP numbers on the report itself** — a transparency signal worth looking for. |
| **GeneSight** (Myriad) | Company states it will contact you before processing if your cost would exceed **$330** | Psychiatry-focused. See the caution below. |
| **Genomind** | **$599** one-time; HSA/FSA eligible | At-home kit, provider-mediated |
| **23andMe pharmacogenetics** | Bundled in Health+Ancestry | ⚠️ **Only 6 variants across 3 genes** (CYP2C19, DPYD, SLCO1B1). 23andMe's own materials say results *"should not be used to make medical decisions"* and should be confirmed with independent clinical testing. |

All are provider-ordered. **Ask for both the cash price and the
insurance-adjusted price in writing before consenting.**

**Medicare** covers PGx under a specific policy (MolDX L38394) when the drug is
medically necessary and the gene-drug pair is clinically actionable per FDA
labeling or CPIC level A/B — though that policy explicitly does not address
anticoagulation dosing. Check your own coverage before assuming.

> **A caution on psychiatric PGx specifically.** Panels marketed for
> antidepressant selection are the most aggressively advertised and the most
> contested. **The FDA has taken enforcement action here** — in April 2019 it
> issued a warning letter to a genomics laboratory for illegally marketing PGx
> tests claiming to predict medication response, warning that *"selecting or
> changing drug treatment in response to the test results could lead to
> potentially serious health consequences."*
> ([FDA announcement](https://www.fda.gov/news-events/press-announcements/fda-issues-warning-letter-genomics-lab-illegally-marketing-genetic-test-claims-predict-patients),
> verified 2026-07-21.)
>
> Treat "this test will find your right antidepressant" as a marketing claim,
> not an established one. The metabolizer genotypes themselves (CYP2D6,
> CYP2C19) are real and useful; the leap to "therefore take drug X" is where the
> evidence thins.

---

## The DIY route — and its one big limitation

If you already have sequencing data, **PharmCAT** generates a CPIC-based report
for free:

**https://pharmcat.clinpgx.org** (note: the old `pharmcat.org` and
`pharmgkb.org` domains now redirect to ClinPGx — update any old bookmarks)

PharmCAT takes a **VCF** and outputs genotype-based CPIC recommendations. It is
open source, actively maintained, and it is what you want if you have whole-genome
or whole-exome data.

### ⚠ Why consumer chip data is not good enough for PGx

**CYP2D6 — the single most important pharmacogene — is the one consumer arrays
handle worst.**

CYP2D6 varies not just by single letters but by **structural variation**: whole
gene deletions, duplications, multiplications (some people carry three or more
functional copies), and hybrid genes formed with the neighboring pseudogene
CYP2D7. Determining your CYP2D6 status requires **copy-number** information.

**PharmCAT says this itself**, in its own documentation
(https://pharmcat.clinpgx.org/using/Calling-CYP2D6, verified 2026-07-21):

> *"While PharmCAT supports CYP2D6, we do NOT recommend calling CYP2D6 from VCF
> due to the large influence of structural variation (SV) and copy number
> variation (CNV) on inferring CYP2D6 phenotype, which is beyond the scope of
> what can be called from SNPs or INDELs in a VCF file."*

Note that this warning applies to a **whole-genome-derived VCF** — a far richer
input than a consumer chip. A genotyping array reads single positions and cannot
count gene copies at all. So:

- A consumer chip typically **cannot** call CYP2D6 correctly.
- **Imputed** data cannot fix this — imputation infers single variants from
  linkage patterns, not structural rearrangements.
- A chip-derived "CYP2D6 normal metabolizer" call may simply mean *the chip
  couldn't see the duplication*.

The same caution applies more broadly: consumer arrays produce **false positives
at rare variants**, and PGx star-alleles are exactly the kind of rare, structured
variation they handle badly.

**A second PharmCAT trap worth knowing:** any position absent from your input VCF
is treated as a **no-call**, not as a reference (normal) genotype. Feed it a
sparse array-derived VCF and it will quietly return "no call" across most of the
panel rather than erroring. Silence is not reassurance.

If you do have whole-genome data and want CYP2D6 properly, PharmCAT points to
**StellarPGx**, which calls structural variation from the **BAM/CRAM** rather
than the VCF — one concrete reason to keep your alignment files, not just your
variant calls.

**The rule:** DIY PGx from consumer data is a *hypothesis generator*. It is
useful for knowing what to ask about. It is **not** a basis for changing a
medication. Anything actionable gets confirmed by a CLIA-certified clinical
laboratory ordered through a clinician.

---

## Is Sequencing.com worth it?

Asked frequently, so here is what could be verified directly from their own store
and product pages in a real browser on **2026-07-21** (their site blocks
automated fetching, so these figures were read from the rendered pages):

| What | Verified price |
|---|---|
| **Upload existing 23andMe/Ancestry/MyHeritage data** | **Free** — includes a free "Next-Gen Disease Screen" |
| Standard WGS bundle | **$559** list, **$389** on a promotion running at the time |
| Advanced WGS bundle | **$859** list, **$489** promo |
| Professional WGS bundle | **$1,659** list, **$789** promo |
| Build-your-own tiers | **$399** (1–10 reports) · **$499** (11–20) · **$799** (21–30) · **$999** (31+) |
| **Membership (recurring)** | Free tier exists; paid plans **$19 / $39 / $129 per month** |
| **Raw data** | **FASTQ, BAM, and VCF downloadable at no additional fee**; their terms state you keep your reports and raw data if you drop to the Free plan |
| Lab | "US-based CLIA-certified, CAP-accredited" — but **the lab is never named and no CLIA/CAP number is published** |

**Verdict: the free upload tier is worth using. The $399 kit is a legitimate
raw-data buy if you treat it as a one-time purchase. Neither is the budget
option, and it is not a pharmacogenomics answer.**

- **If you want raw data to analyze** — this is actually competitive. **$399 for
  30× whole-genome sequencing with FASTQ + BAM + VCF included** is a real offer,
  and notably it is the only WGS price in this space that could be verified from
  a live vendor page rather than an aggregator. Nebula's and Dante's current
  prices are hidden behind JavaScript and could not be confirmed at all, so
  "Nebula is cheaper" is an assertion nobody can currently demonstrate.
  **Practical protocol: buy the kit, download FASTQ/BAM/VCF immediately, then
  downgrade to the Free plan.**
- **⚠️ Defend your credit card.** Their BBB profile shows **66 complaints over
  three years**, concentrated on annual plans presented as monthly, trials
  auto-converting to paid, and difficulty cancelling. Trustpilot rates them 4.6,
  which is the classic split of a decent product with an aggressive subscription
  funnel. Use a virtual or single-use card and diary the trial end date the day
  you order.
- **Ignore every crossed-out "list" price.** The same $399 bundle was anchored
  against two *different* "was" prices on two pages of their own site on the same
  day, both under countdown timers reading zero. The $399 floor is the only
  number that means anything.
- **If you already have 23andMe or Ancestry data** — their **free upload** is a
  legitimate free option alongside GEDmatch, Genetic Genie, and Open Humans.
- **For pharmacogenomics specifically — do not buy this for PGx.** Their PGx
  appears only as one unlabeled health area ("Medication & Drug Response") with
  **no published gene list, no star-allele coverage statement, no CPIC
  conformance claim, and no statement of whether the report is clinical-grade or
  research-use-only.** Note that CLIA/CAP *sequencing* does not make an
  *interpretive report* clinical-grade — those are separate regulatory
  questions, and conflating them is exactly what the FDA acted against in 2019.
  If you want the WGS as a **data source** and intend to run PharmCAT yourself,
  that is defensible — just remember CYP2D6 still won't call properly from the
  VCF.

**Still unverified:** which laboratory actually performs the sequencing and its
CLIA/CAP numbers (they publish the claim but not the identifiers — compare
OneOme, which prints both on the report), and the regulatory grade of their PGx
report. Their site is JavaScript-rendered and bot-blocked, so treat any price
quoted anywhere — here included — as needing a fresh check before you spend.

Compare against [testing-access.md §5](testing-access.md#5-consumer-dna-kits-and-raw-data)
before deciding.

---

## What to do with a PGx result

1. **Bring it to a pharmacist.** Pharmacists are often the most PGx-literate
   people in the healthcare system and are usually easier to reach than a
   physician.
2. **Ask for it to go in your chart**, so it is there the next time anyone
   prescribes for you. A result that lives in your email is a result nobody
   consults during an actual prescribing decision.
3. **Never self-adjust.** A "poor metabolizer" result does not mean halve your
   dose. It means have a conversation.
4. **Confirm before acting**, if the result came from consumer data.
5. **Keep it — it does not expire.** Your genotype is the same at 70 as at 30.
   This is one of the few tests you genuinely take once.

---

## Sources

- **CPIC / ClinPGx** — guidelines and evidence levels:
  https://www.clinpgx.org/cpic/guidelines (29 guidelines, free, peer-reviewed).
  API: https://api.cpicpgx.org/v1 — queried live 2026-07-21: 635 pairs, 96 at
  Level A across 21 genes
- **ClinPGx** (formerly PharmGKB) — https://www.clinpgx.org
- **PharmCAT** — https://pharmcat.clinpgx.org
- **FDA Table of Pharmacogenetic Associations** —
  https://www.fda.gov/medical-devices/precision-medicine/table-pharmacogenetic-associations
- **FDA Table of Pharmacogenomic Biomarkers in Drug Labeling** —
  https://www.fda.gov/drugs/science-and-research-drugs/table-pharmacogenomic-biomarkers-drug-labeling
- **PharmCAT CYP2D6 limitation** — https://pharmcat.clinpgx.org/using/Calling-CYP2D6
- **Find a genetic counselor** — https://findageneticcounselor.nsgc.org
