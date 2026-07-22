# The DNA analysis pipeline

How to get from "I spat in a tube" to real, defensible results — using only free
and open tools, on your own machine.

Read [interpreting-results.md](interpreting-results.md) **before** you believe any
number this pipeline produces. The analysis is the easy part; not fooling
yourself is the hard part.

---

## The short version

```
raw export (~650k variants)
   → normalize          scripts/normalize_raw_dna.py
   → [optional] impute  scripts/prepare_for_imputation.sh → free server → ~40M variants
   → clump the GWAS     scripts/clump.py
   → score              scripts/score_pgs.py
   → interpret          references/interpreting-results.md
```

Steps 1, 3, 4 run in seconds on a laptop. Imputation takes hours and is what
separates a toy result from a real one.

---

## Step 1 — Get your raw data

Every major consumer testing company lets you download your raw genotypes. This
is your data; export it and keep a copy offline. Companies get acquired, go
bankrupt, and change their terms.

| Company | Where the download lives |
|---|---|
| 23andMe | Account settings → "23andMe Data" → Download raw data |
| AncestryDNA | DNA settings → Download raw DNA data (email confirmation required) |
| MyHeritage | DNA → Manage DNA kits → Download raw data |
| FamilyTreeDNA | Sign in → Data download |
| Nebula / Dante (WGS) | Provides VCF and often BAM/FASTQ — far more data than a chip |

**Do this today, not later.** A raw-data export is a small text file. Store it
encrypted, offline, and out of any folder that syncs to a cloud drive by default.

### What you actually got

A genotyping **chip** measures a pre-chosen set of roughly 600,000–700,000
positions out of ~3 billion base pairs in your genome. That is about **0.02%**.
It is not "your genome sequenced." Whole-genome sequencing (Nebula, Dante, or a
clinical lab) reads essentially all of it and produces a VCF instead.

This distinction drives everything downstream: a chip can only answer questions
about positions it measured, which is why imputation matters so much.

---

## Step 2 — Normalize

```bash
python3 scripts/normalize_raw_dna.py ~/Downloads/genome_export.txt -o normalized.tsv
```

Accepts `.txt`, `.csv`, `.gz`, and `.zip` from 23andMe, AncestryDNA, MyHeritage,
FamilyTreeDNA, and LivingDNA. Output is one tab-separated format
(`rsid, chrom, pos, genotype`) so every later step has exactly one input shape.

The script reports how many variants parsed, how many were no-calls, and how many
rows were malformed. **If the vendor was not recognized, it says so** — spot-check
the output before trusting it rather than assuming.

One real trap it handles: AncestryDNA splits your genotype across two separate
allele columns while everyone else uses one. Concatenating the wrong columns
produces a file that looks fine and is wrong.

---

## Step 3 — Imputation (the step that decides whether your results mean anything)

### Why bother

Your chip measured ~650k positions. A published polygenic score often uses
hundreds of thousands to **millions** of variants. Score a raw chip file against
one and you may be covering a small fraction of the score — and a fraction is not
a scaled-down version of the answer, it is a different and largely meaningless
number.

Imputation fixes this. Because DNA is inherited in blocks, the variants your chip
did measure statistically predict the ones it did not. Using a reference panel of
tens of thousands of sequenced genomes, imputation infers your genotype at tens
of millions of positions. **~650k → ~40M** is typical.

### The build trap — read this before submitting anything

Genomic coordinates differ between reference builds (GRCh37/hg19 vs GRCh38/hg38).
Imputation servers ask which build you are submitting. Choose wrong and the
output is silently garbage: the job succeeds, the files load, the scores compute,
and every position is misaligned.

Most consumer exports are **GRCh37/hg19**. Confirm from your file's own comment
header. Do not guess.

### Preparing your files

```bash
scripts/prepare_for_imputation.sh --check          # verify plink2/bcftools present
scripts/prepare_for_imputation.sh raw_export.txt imputation_upload/
```

This converts to per-chromosome bgzipped VCFs, drops indels and unplaced contigs
(servers reject them), applies basic QC, and sorts/indexes the output. It drives
`plink2` and `bcftools` rather than reimplementing genomics badly, and it fails
loudly when a prerequisite is missing.

### Free imputation servers

| Server | Reference panel | URL |
|---|---|---|
| TOPMed Imputation Server | TOPMed (largest, most ancestrally diverse) | https://imputation.biodatacatalyst.nhlbi.nih.gov/ |
| Michigan Imputation Server | HRC, 1000G Phase 3, CAAPA | https://imputationserver.sph.umich.edu/ |

Both are academic, free, and require a registered account. Both process your
genome **on their infrastructure** — read their terms and decide if that trade is
acceptable to you before uploading.

Panel choice matters and is ancestry-dependent:

- **TOPMed** — the most diverse panel; generally the best default, and clearly
  the best choice for anyone of non-European ancestry.
- **HRC** — large but predominantly European.
- **CAAPA** — built specifically for African-ancestry populations.
- **1000G Phase 3** — multi-ancestry but smallest; use when the others do not fit.

An imputation panel that does not represent your ancestry imputes you worse. This
is the same structural bias described in
[interpreting-results.md](interpreting-results.md).

### Operational notes that will save you a day

- Results come back **AES-encrypted**, with the password sent separately. Record
  it. Without it the download is unusable.
- Expect hours, sometimes a day. This is a queue, not an API call.
- Some servers enforce a **minimum sample count** and may reject a single-genome
  submission. If that happens, impute locally (below).
- The command-line client `imputationbot` automates submission and download
  against both servers.

### Local imputation (no upload)

If you would rather not send your genome anywhere, **Beagle 5.5** imputes locally
against a public 1000 Genomes reference panel:

```bash
java -Xmx5g -jar beagle.jar \
    gt=chr1.vcf.gz ref=chr1.1000G.bref3 map=plink.chr1.GRCh37.map \
    impute=true nthreads=2 out=chr1.imputed
```

Slower, needs ~4–6 GB RAM per chromosome and a large panel download, and the
public panel is smaller than TOPMed — so accuracy is lower, especially for rare
variants. But nothing leaves your machine.

### After imputation

Merge, then **filter on imputation quality**. Every imputed genotype carries a
confidence score (`DR2` or `R2`); low-confidence calls are guesses:

```bash
bcftools concat $(ls -v chr*.dose.vcf.gz) -Oz -o merged.vcf.gz
bcftools index merged.vcf.gz
bcftools view -i 'INFO/DR2>=0.8' merged.vcf.gz -Oz -o merged.qc.vcf.gz
```

`DR2 >= 0.8` is a common threshold. Skipping this filter means scoring yourself
on coin flips.

---

## Step 4 — Get GWAS summary statistics or a PGS Catalog score

Two routes:

**A. PGS Catalog (easier).** https://www.pgscatalog.org publishes thousands of
already-built polygenic scores as plain files: one row per variant with an effect
allele and a weight. Search a trait, download the scoring file, feed it straight
to `score_pgs.py`. No clumping needed — published scores are already built.

**B. Raw GWAS summary statistics (more control).** Public sources include the
GWAS Catalog (https://www.ebi.ac.uk/gwas/), FinnGen
(https://www.finngen.fi/en/access_results), the UK Biobank GWAS releases, and
consortium sites. You must clump these yourself — see Step 5.

Match the genome build. A GRCh38 scoring file against GRCh37 data needs a
liftOver first, or the positions do not line up.

---

## Step 5 — Clump (only for raw GWAS summary statistics)

```bash
python3 scripts/clump.py --input gwas_sumstats.tsv --output clumped.tsv --window-kb 500
```

**This is the step people skip, and skipping it is the single most common way to
produce a wildly wrong polygenic score.**

Variants near each other are inherited together, so one real association appears
in the summary statistics as hundreds or thousands of correlated variants. Sum
all of them and you count the same signal repeatedly. The MHC/HLA region on
chromosome 6 has such long-range correlation that it alone can dominate an
unclumped score.

Clumping keeps the most significant variant per region and discards its
correlated neighbours. Window guidance: 250kb aggressive, **500kb default**,
1000kb conservative.

If the script reports a very high input:output ratio, that is not a bug — it is
the measure of how much redundancy was inflating your raw file.

> This is distance-based clumping, which uses physical proximity as a proxy for
> correlation. PLINK's `--clump` uses a real r² matrix from a reference panel and
> is more precise, at the cost of a multi-gigabyte download. Distance-based
> clumping needs nothing and removes most of the problem.

---

## Step 6 — Score

```bash
python3 scripts/score_pgs.py --genome normalized.tsv --score PGS000000.txt.gz
```

Scoring is a dot product: count your copies of each effect allele, multiply by
that variant's weight, sum.

The script reports the raw sum **and your coverage** — what fraction of the
score's variants exist in your data. It also handles two things that quietly
corrupt hand-rolled scoring code:

- **Strand ambiguity.** For A/T and C/G variants you cannot tell which DNA strand
  a call was reported on, so a match is a coin flip. These are **skipped**, not
  guessed.
- **Odds ratios vs betas.** Some files supply odds ratios, which must be
  log-transformed before summing. Summing raw ORs is meaningless. The script
  detects and converts, and tells you it did.

**The script deliberately does not print a percentile or a risk multiple.**
Converting a raw sum into "you are in the 80th percentile" honestly requires a
reference population scored on the same variant set with the same coverage. Tools
that skip that step and hand you a percentile anyway are showing you a number
they cannot support.

---

## Step 7 — Other things worth running

Once you have imputed data:

| Question | Tool | Notes |
|---|---|---|
| Do I carry known pathogenic variants? | ClinVar VCF + `bcftools view -i 'INFO/CLNSIG~"Pathogenic"'` | Consumer chips genotype poorly at rare clinical variants. **Never act on a chip or imputed result clinically — confirm with a clinical-grade test.** |
| How do I metabolize medications? | PharmCAT (https://pharmcat.org), CPIC guidelines (https://cpicpgx.org) | Pharmacogenomics is one of the few areas with actual clinical guidelines. Many chips miss key variants (notably CYP2D6 structural variants). |
| Paternal deep ancestry (Y) | yhaplo, YFull | Y chromosome; people without a Y have no result. Describes ancestry over millennia, not genealogy. |
| Maternal deep ancestry (mtDNA) | HaploGrep3 (https://haplogrep.i-med.ac.at) | Same caveat. |
| Ancestry proportions | ADMIXTURE + 1000 Genomes reference | Results depend heavily on which reference populations you include. |
| What does this variant do? | Ensembl, gnomAD, MyVariant.info, ClinVar, dbSNP | All free, all have public APIs. |

---

## Tool reference

Free, open source, actively maintained:

| Tool | Purpose | URL |
|---|---|---|
| PLINK 2 | Genotype file conversion, QC, real LD clumping | https://www.cog-genomics.org/plink/2.0/ |
| bcftools / htslib | VCF manipulation — the workhorse | https://samtools.github.io/bcftools/ |
| Beagle | Local imputation and phasing | https://faculty.washington.edu/browning/beagle/beagle.html |
| PGS Catalog | Published polygenic scores | https://www.pgscatalog.org |
| GWAS Catalog | Published GWAS summary statistics | https://www.ebi.ac.uk/gwas/ |
| ClinVar | Clinical variant interpretations | https://www.ncbi.nlm.nih.gov/clinvar/ |
| gnomAD | Population allele frequencies | https://gnomad.broadinstitute.org |
| PharmCAT | Pharmacogenomics from a VCF | https://pharmcat.org |
| CPIC | Prescribing guidelines by genotype | https://cpicpgx.org |
| Ensembl | Genome browser and REST API | https://rest.ensembl.org |

Install the core set:

```bash
# macOS
brew install plink2 bcftools htslib

# Debian / Ubuntu
sudo apt install plink2 bcftools tabix

# conda
conda install -c bioconda plink2 bcftools htslib
```

---

## A note on scale

Working with imputed data means tens of millions of rows. Loading that into a
dataframe will exhaust memory on a laptop. Either stream with `bcftools`, or use
a columnar engine like **DuckDB**, which queries compressed files on disk and
handles genome-scale joins comfortably in a few gigabytes of RAM.
