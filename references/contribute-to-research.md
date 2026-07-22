# Contributing your data to science

Your data is more valuable to research than it is to you sitting on a hard drive
— and unlike most forms of donation, this one can pay you back with free
clinical-grade testing.

There is also a specific reason this matters more than usual right now.

---

## Why this actually matters: the diversity gap

Most genome-wide association studies were conducted in people of **European
ancestry**. As a direct result, polygenic scores and genetic risk predictions work
substantially worse for everyone else — see
[interpreting-results.md §3](interpreting-results.md).

This is not a problem that better math fixes. It is a problem that only more
representative **data** fixes. Every person of underrepresented ancestry who joins
a research program measurably improves the science for everyone who shares that
ancestry — including their own family.

If you have ever run a polygenic score and thought "this probably doesn't apply
to me," participating is the mechanism by which that stops being true.

---

## Where to contribute

### All of Us Research Program (NIH) — best overall

**https://joinallofus.org**

The strongest combination of real research value, protections, and return to you.

| | |
|---|---|
| **You give** | Surveys, EHR access, physical measurements, a blood or saliva sample |
| **You get** | Ancestry and traits reports; hereditary disease risk across **59 medically actionable genes**; pharmacogenetics; **free genetic counseling**; free confirmatory clinical testing if something concerning appears; **$25** for an in-person sample |
| **Access model** | Controlled access — approved researchers only, under a data-use agreement |
| **Eligibility** | US adults |

*All of Us* is explicitly recruiting for ancestral diversity, which makes it the
highest-leverage option in this entire document.

### Open Humans — best for control

**https://www.openhumans.org**

Free. You upload or connect data — consumer genetics, wearables, health records,
and more — and then **choose project by project what to share**. Granular consent
is the entire design of the platform, rather than an afterthought.

Best fit if you want to contribute but are not comfortable with a single
all-or-nothing consent.

### Health-system research programs — free clinical screening

If you live in the right region, joining costs nothing and returns clinical-grade
results:

- **Helix partner programs** — Healthy Nevada Project, myGenetics (HealthPartners,
  MN/WI), DNA Answers (St. Luke's, PA/NJ), WellSpan (PA).
  https://www.helix.com/health-systems/population-genomics-partners
- **Geisinger MyCode** (Geisinger patients, PA).
  https://www.geisinger.edu/gchs/research/mycode

### Personal Genome Project — maximum openness, read carefully

**https://www.personalgenomes.org**

The PGP model invites participants to **publicly share** their genome and health
data for the common good. Global network: Harvard PGP, PGP Canada, PGP UK, Genom
Austria, PGP China.

> **Understand what this means before enrolling.** PGP data is **public,
> non-anonymous, and irrevocable in practice.** You cannot un-publish a genome. It
> also permanently exposes information about your biological relatives, who did
> not consent.
>
> PGP is an admirable project and its participants are making a real
> contribution. It is only appropriate for people who genuinely accept permanent
> public identifiability.

### Sage Bionetworks / Synapse

**https://www.synapse.org** — a nonprofit collaborative platform for biomedical
data. Primarily a *researcher* platform; individuals contribute through specific
studies hosted there rather than by direct upload.

### Finding studies at a university near you

1. **ResearchMatch** — **https://www.researchmatch.org** — free NIH-funded
   nonprofit registry (122,000+ volunteers, 1,400+ studies, 280 institutions).
   You create a profile; researchers whose studies match contact you. **The best
   general starting point.**
2. **ClinicalTrials.gov** — https://clinicaltrials.gov — filter by *Recruiting*,
   your condition, and distance from your ZIP.
3. **University registries** — most academic medical centers run a local "join a
   study" registry. Search `"<university name>" research participant registry`.

---

## Questions to ask before you enroll

Read the **consent document**, not the marketing page. Then answer these:

1. **Do I get my own results back?** Many studies never return individual data.
   If that matters to you, filter on it first.
2. **Who can access my data, and under what terms?** Open public access,
   controlled access for approved researchers, or internal only?
3. **Can I withdraw?** And critically — **does withdrawal reach data already
   shared with other researchers?** Usually it does not.
4. **Is my data shared with commercial entities?** Many academic programs
   partner with industry. That is not automatically bad, but you should know.
5. **What happens if the program ends or the institution merges?** See the UK
   Biobank breach and the 23andMe bankruptcy in
   [privacy-and-law.md](privacy-and-law.md).
6. **Am I consenting for anyone else?** Your genome is ~50% shared with each
   parent, child, and sibling.

---

## An honest weighing

**Real benefits:**

- Free clinical-grade testing you would otherwise pay for, sometimes with free
  genetic counseling attached.
- Findings that change medical care for a small but real fraction of participants.
- A direct, measurable contribution to closing the diversity gap.

**Real costs:**

- Your genetic data exists in another institution's systems, permanently.
- Withdrawal is usually incomplete once data has been shared onward.
- You are making this choice for biological relatives who cannot weigh in.
- Institutional custody is not a security guarantee — UK Biobank, a
  government-backed biobank, was breached in April 2026.

**A reasonable default for most people:** join **All of Us** (controlled access,
returns results, actively addresses the diversity gap), use **Open Humans** for
anything where you want per-project control, and think very hard before anything
irrevocably public.

---

## After you contribute

You still keep your own copy. Export your raw data, run the pipeline in
[dna-analysis-pipeline.md](dna-analysis-pipeline.md), and read
[interpreting-results.md](interpreting-results.md) before drawing conclusions.

Contributing to research and understanding your own data are not in tension. Do
both.
