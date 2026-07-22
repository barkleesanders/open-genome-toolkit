# Privacy, law, and what you are actually giving up

Read this before you upload your genome anywhere.

Genetic data is unlike any other personal data in three ways: **you cannot change
it** when it leaks, **it identifies your relatives** who never consented, and
**it outlives the company that holds it**. Every decision below follows from
those three facts.

---

## 1. GINA protects less than almost everyone assumes

The **Genetic Information Nondiscrimination Act (2008)** covers exactly two
things:

- **Health insurance** (Title I)
- **Employment** (Title II)

That is the whole list.

### What GINA does NOT cover **[confirmed — NIH/NHGRI]**

- **Life insurance**
- **Disability insurance**
- **Long-term care insurance**

The National Human Genome Research Institute states it directly: *GINA's health
insurance protections do not cover long-term care insurance, life insurance, or
disability insurance.*
https://www.genome.gov/about-genomics/policy-issues/Genetic-Discrimination

**In most states, those insurers may legally ask about and use genetic test
results — including results you generated yourself from a $29 kit.**

### Two more gaps worth knowing

- **GINA does not apply to employers with fewer than 15 employees.**
- **The US military may use genetic information in employment decisions.** Since
  TRICARE eligibility flows from military employment and GINA's employment title
  does not reach the military, results can matter indirectly. (The Veterans
  Health Administration carries stronger protections than TRICARE.)

Some states add protections on top of GINA. Most do not close the
life/disability/long-term-care gap.

> ### If you are considering buying life, disability, or long-term care insurance
>
> **Many genetic counselors advise securing those policies *before* testing.**
> Once a result exists, it may be discoverable, and the federal protection you
> are probably assuming you have does not extend to those products.
>
> This is not a reason never to test. It is a reason to sequence the two
> decisions in the right order.

---

## 2. Law enforcement can search consumer genetic databases

Investigative genetic genealogy — identifying a suspect through their
**relatives'** DNA in consumer databases — is now routine police practice.

Current policies:

- **FamilyTreeDNA** operates Investigative Genetic Genealogy Matching with an
  explicit opt-in/opt-out setting and a published law-enforcement guide:
  https://www.familytreedna.com/legal/law-enforcement-guide
- **GEDmatch** runs a **Genetic Witness Program** with law-enforcement opt-in:
  https://www.gedmatch.com/join-the-genetic-witness-program

### The opt-out has been circumvented in practice

The Intercept reported in August 2023 that forensic genetic genealogists *"skirted
GEDmatch privacy rules by searching users who explicitly opted out of sharing DNA
with law enforcement."*
https://theintercept.com/2023/08/18/gedmatch-dna-police-forensic-genetic-genealogy

Treat an opt-out as a stated policy, not a technical guarantee.

### You are deciding for your relatives

You do not need to have tested to be findable. A cousin's upload can identify
you. When you upload, you are making that decision on behalf of every biological
relative you have — including ones you have never met and ones not yet born.

There is no framework for obtaining their consent, and no way to withdraw it once
matches have been made.

---

## 3. Your data outlives the company holding it

Two verified events tell this story better than any argument:

### 23andMe was auctioned in bankruptcy court

23andMe filed for bankruptcy in 2025. Regeneron announced a $256M acquisition; a
judge ultimately approved sale to **TTAM Research Institute**, a nonprofit led by
co-founder Anne Wojcicki. Multiple state attorneys general objected to genetic
data being treated as a saleable bankruptcy asset.

Millions of people gave their DNA to one company under one privacy policy. Which
entity holds it, and under what terms, was then decided in a courtroom.

### UK Biobank was breached in April 2026

UK Biobank is a gold-standard, government-backed research biobank — the kind of
institution invoked whenever someone says "your data will be safely
de-identified and held by responsible researchers."

In April 2026, data on **~500,000 participants** was found **listed for sale on a
Chinese e-commerce platform**. UK Biobank temporarily suspended access to its
research platform and restricted export sizes. Reporting indicates the leak came
through academic institutions that had been *granted legitimate access*.
(Washington Post and three other outlets, April 2026.)

**The lesson is not "never share your data."** Research participation is genuinely
valuable and this repo actively encourages it. The lesson is: *assume any genetic
data you upload may someday be held by an entity you did not choose, under terms
you did not agree to.* Decide with that as the baseline, not the worst case.

### Free tools die too

**Impute.me** was a free, nonprofit imputation and polygenic-score service beloved
by hobbyists. It is now a redirect to a commercial company. **DNA.Land** simply
vanished — the domain serves an empty page.

Whatever you build, keep your own local copy of your own data.

---

## 4. What testing can reveal about your family

Consumer DNA testing routinely uncovers:

- **Misattributed parentage** — the father on the birth certificate is not the
  biological father. Common enough to have its own acronym in the genealogy
  community (NPE).
- **Unknown siblings**, often from donor conception or earlier relationships.
- **Undisclosed adoptions.**
- **Donor-conceived status** the person was never told about.

These discoveries are frequently wonderful. They also detonate families, and they
arrive without warning in a results email on a Tuesday.

**Before you test, decide how you would handle it** — and consider that the
discovery may land on someone else in your family who did not choose to look.

---

## 5. Practical privacy hygiene

**Do this the day you get your results:**

1. **Download your raw data and back it up locally**, encrypted, offline. Not in
   a cloud folder that syncs by default.
2. **Read what you consented to.** Is research use opt-in or opt-out? Is that
   consent revocable? Is de-identified data shared with commercial partners?
3. **Prefer opt-in over opt-out** for every matching and law-enforcement feature.
4. **If you stop using a service, exercise your deletion rights — and verify
   deletion happened.** Do not assume.
5. **Consider what name and email you register with.** Using something other than
   your real name limits genealogical usefulness, so this is a real trade-off,
   not a free win.
6. **Never commit your genome to a public repository.** This project's
   `.gitignore` blocks the common filenames, and `scripts/pii_scan.py` scans for
   personal data — but neither can save you from `git add -f`.

---

## 6. When you share for research

Contributing your data to science is genuinely good, and the diversity gap in
genomics research only closes if people do it. See
[contribute-to-research.md](contribute-to-research.md).

But the destinations differ enormously in what you are giving up:

| Destination | Exposure |
|---|---|
| **All of Us (NIH)** | Controlled access for approved researchers. Strongest formal protections of the group. Note: as of 2025 it no longer returns results to you. |
| **Open Humans** | You choose per-project what to share. Granular consent is the entire design. |
| **Personal Genome Project** | **Maximum exposure by design** — public, non-anonymous, and irrevocable in practice. Only for people who genuinely accept permanent public identifiability. |

Read the consent document. Not the marketing page — the actual consent document.

---

## The honest bottom line

Genetic testing is worth doing. The knowledge is real, the ancestry findings are
often deeply meaningful, the pharmacogenomics can change a prescription, and
research participation helps people who look like you get better science.

But go in knowing three things:

1. **Federal law does not protect you from life, disability, or long-term-care
   insurers.** Sequence those decisions accordingly.
2. **You are deciding for your relatives too**, and you cannot get their consent
   or take it back.
3. **The company holding your data today may not be the one holding it in five
   years**, and that transfer can happen in a bankruptcy court.

None of that is a reason not to look. It is a reason to look with your eyes open.

---

*Not legal advice. Laws vary by state and change. For decisions with real stakes,
consult a lawyer or a certified genetic counselor:
https://findageneticcounselor.nsgc.org*
