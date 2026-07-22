# Interpreting your results without fooling yourself

This is the most important file in this repository.

Computing a polygenic score is a dot product — a first-year programming
exercise. Knowing what the resulting number means, and more importantly what it
does **not** mean, is the entire discipline. Almost every bad outcome in consumer
genomics comes from a correctly-computed number that was confidently
misunderstood.

**None of this is medical advice.** Nothing here diagnoses, treats, or predicts
disease. Take clinically relevant findings to a licensed clinician or a certified
genetic counselor. Find one: https://findageneticcounselor.nsgc.org

---

## 1. A raw score by itself means nothing

`score_pgs.py` prints a raw sum. On its own, that number is uninterpretable.

A polygenic score is only meaningful **relative to a distribution** — you need to
know what the scores look like across a population, scored the same way, on the
same variant set, at the same coverage. Without that reference, "4.7" is not high
or low. It is just 4.7.

This is why the scorer refuses to print a percentile. Producing an honest one
requires scoring a reference population alongside you. Any tool that hands you
"you're in the 87th percentile" without having done that is showing you a number
it cannot support.

**What you can legitimately do with a raw score:**

- Compare *your own* score across different published scores for the same trait
  (do they agree?).
- Compare before and after imputation (does coverage change the answer?).
- Feed it into a reference distribution if you build one.

**What you cannot do:** convert it to a risk, a percentile, or a diagnosis.

---

## 2. Coverage is the first thing to check

The scorer reports what fraction of the score's variants exist in your data.

- **Below 50%**, the raw sum is not comparable to anything published. Impute
  first.
- Even at high coverage, missing variants are not missing at random — they
  cluster by chip design and by allele frequency, which biases the result in a
  direction you cannot easily predict.

Coverage is not a quality score, it is a prerequisite. Low coverage does not mean
"slightly less accurate"; it means "measuring something else."

---

## 3. The ancestry problem — the single biggest limitation

**Most genome-wide association studies were done in people of European ancestry.
Polygenic scores built from them predict substantially worse in everyone else.**

This is not a minor caveat, and it is not controversial. It is the central,
well-documented limitation of the entire field:

- Martin et al., *Clinical use of current polygenic risk scores may exacerbate
  health disparities*, **Nature Genetics** 51:584–591 (2019).
  https://pubmed.ncbi.nlm.nih.gov/30926966/ ·
  https://pmc.ncbi.nlm.nih.gov/articles/PMC6563838/

Why it happens: a GWAS does not usually find the causal variant. It finds a
marker correlated with the causal variant *in the population that was studied*.
Correlation patterns between variants (linkage disequilibrium) differ across
ancestries, so the marker travels with the causal variant in one population and
not in another. Allele frequencies and effect sizes differ too.

Practical consequences:

- If your ancestry is not well represented in the source GWAS, your score is less
  informative — sometimes barely informative at all.
- This applies to **most people in the world**, and it applies to people of mixed
  ancestry in ways that are hard to quantify per-individual.
- It compounds at the imputation step: a reference panel that under-represents
  your ancestry imputes you less accurately, before scoring even begins.

Check who was in the study. The PGS Catalog records the ancestry composition of
each score's development and validation samples. If a score was developed
entirely in European-ancestry cohorts and you are not of European ancestry, treat
the output as an interesting artifact, not information about you.

This is a reason to **participate** in research like *All of Us*, which is
explicitly recruiting for diversity — see
[contribute-to-research.md](contribute-to-research.md). The gap closes only when
the underlying data changes.

---

## 4. Common statistical traps

**Relative vs absolute risk.** "Double the risk" is meaningless without the
baseline. Doubling a 0.1% lifetime risk gives 0.2% — still very unlikely.
Doubling a 20% risk is a genuinely different life. Headlines and reports quote
relative risk because it sounds bigger. Always ask: double of *what*?

**Heritability is not destiny, and it is not personal.** "Trait X is 60%
heritable" is a statement about variance *in a population under specific
conditions*, not about how much of *your* trait came from genes. High
heritability is fully compatible with environment being the thing that changes
your outcome.

**Genes are not the only thing you inherit.** Families share diet, income, ZIP
code, stress, healthcare access, and exposure. A trait clustering in a family is
not evidence it is genetic.

**Most complex traits are thousands of tiny effects.** Individually most variants
shift risk by a fraction of a percent. Single-variant reports ("you have the
warrior gene") are almost always overstated. The exceptions are real but rare:
high-penetrance variants in genes like *BRCA1/2*, Lynch syndrome genes, and
familial hypercholesterolemia genes. **Those require clinical-grade confirmatory
testing, never a consumer chip.**

**Publication and winner's-curse bias.** Effect sizes in the original discovery
study are systematically larger than they turn out to be on replication.

**Multiple testing.** Run enough scores against yourself and something will look
extreme by chance alone. If you score 40 traits, expect a couple of eye-catching
results that mean nothing.

---

## 5. Consumer chips are not clinical tests

A consumer genotyping array is a research-grade instrument optimized for cost and
throughput at common variants. It is not a diagnostic device.

- **False positives at rare variants are common.** A chip reporting a rare
  pathogenic variant is more likely wrong than right — a well-documented failure
  mode when consumer raw data is run through third-party interpretation tools.
- **Imputed calls are statistical inferences**, not measurements. Never treat an
  imputed genotype as a clinical fact.
- **Coverage of clinically important genes is patchy.** Notably, *CYP2D6* — one
  of the most important drug-metabolism genes — involves structural variation
  that chips largely cannot see.

**Rule: if a result would change a medical decision, it must be confirmed by a
CLIA-certified clinical laboratory ordered through a clinician.** Consumer data
is a hypothesis generator. That is a genuinely useful role. It is not a diagnosis.

---

## 6. Before you act on anything

1. **Is this variant/score actually well-established?** Check ClinVar for
   clinical variants (and its review-status stars), the PGS Catalog for scores.
   One paper is not a finding.
2. **Was the study population like me?** See §3.
3. **What is my absolute risk, not relative?** See §4.
4. **Is it actionable?** Some findings change screening or prescribing. Many
   change nothing at all. Ask what you would do differently.
5. **Would I want to know?** Some findings — particularly for untreatable
   late-onset conditions — carry real psychological weight and can affect family
   members who never consented to the test. This is a legitimate reason not to
   look.
6. **Talk to a genetic counselor before acting.** They do exactly this for a
   living. https://findageneticcounselor.nsgc.org

---

## 7. What this data says about your relatives

Your genome is not only yours. It is roughly 50% shared with each parent, child,
and full sibling, and ~25% with grandparents, aunts, uncles, and half-siblings.

- A finding about you is often a finding about them — and they did not consent.
- Uploading your data to a matching database makes **them** findable too.
- Consumer DNA testing routinely uncovers misattributed parentage, unknown
  siblings, and undisclosed adoptions. This is common, not rare. It can be
  wonderful and it can detonate a family. Decide in advance how you would handle
  it, and think about who else has a stake before you upload.

---

## 8. Legal protections and their gaps

**GINA** (the Genetic Information Nondiscrimination Act of 2008) prohibits
genetic discrimination in **health insurance** and **employment**.

**GINA does not cover life insurance, disability insurance, or long-term care
insurance.** In most US states, those insurers may legally ask about and use
genetic test results — including results you generated yourself.

- EEOC on GINA: https://www.eeoc.gov/genetic-information-discrimination
- Federal summary: https://www.genome.gov/about-genomics/policy-issues/Genetic-Discrimination

GINA also does not apply to employers with fewer than 15 employees, and it does
not cover the US military. Some states add protections; most do not close the
life/disability/LTC gap. If you are considering buying life or disability
insurance, understand that testing first can affect that.

Consumer genetic databases have also been used in law-enforcement investigations,
often via relatives' uploads rather than the suspect's own. Policies differ
sharply by service and change over time — check the current policy of any
database before uploading, and remember you are making a decision on behalf of
biological relatives too.

---

## The honest summary

Consumer genomics is genuinely useful for:

- Ancestry and family discovery (the strongest, most reliable use).
- Pharmacogenomics — with clinical confirmation.
- Generating hypotheses worth discussing with a clinician.
- Contributing to research that makes all of this better.

It is not useful for predicting whether you will get a disease. Anyone who tells
you otherwise — including a slick report generated from your own raw data — is
selling certainty that the science does not currently support.

Curiosity is a good reason to do this. Just hold the results loosely.
