# Consumer longevity and health apps

Commercial apps that sell a number about your health — a "biological age," a
longevity score, a projected death date — sit next door to everything else in
this repository, and people ask about them constantly. This page covers how to
evaluate them and what specific ones actually do.

**Everything here was verified against the operator's own live pages on
2026-07-22.** These products change pricing and features fast. Re-check before
you subscribe.

| Label | Meaning |
|---|---|
| **confirmed** | Verified on the operator's own page or App Store listing |
| **single-sourced** | One source only — provisional |
| **unverified** | Could not confirm; do not rely on it |

---

## The five questions to ask any of them

Ask these before you pay. They are the same questions this repository asks of a
polygenic score, because these apps are selling the same kind of thing: a
population statistic dressed up as a fact about you.

**1. Does it read your DNA, or does it just ask you questions?**
Most of them do not touch genetics at all. Marketing that leans on "clinical
grade" and "precision" can leave that entirely unclear. If it never asks for a
raw data file or a saliva kit, it is not doing genomics.

**2. Is the number a measurement or a model output?**
A cholesterol value is a measurement. A "biological age" or a projected death
date is a model's guess, built from actuarial tables and population averages. It
moves when the model is retuned, not only when your health changes.
→ [Interpreting results](interpreting-results.md) applies here in full.

**3. What does the free tier actually get you?**
"Free to try" usually means the questionnaire is free and everything downstream —
the labs, the plan, the follow-up — is a subscription.

**4. Where does the health data go?**
Check the App Store privacy card against the privacy policy; they are written by
different teams and often disagree in tone. Look specifically for whether
advertising partners receive anything, and whether HIPAA applies. Most of these
apps are **not** HIPAA-covered entities for most of what they collect — HIPAA
binds providers, plans, and clearinghouses, not app developers.
→ [Privacy and law](privacy-and-law.md)

**5. Could you buy the underlying labs directly for less?**
Usually yes. The blood panel is the part with real information in it, and
[§3 of the testing access guide](testing-access.md#3-order-your-own-labs-no-doctors-visit)
lists self-order prices — a lipid panel is **$33** at Walk-In Lab. What the
subscription adds is interpretation, tracking, and packaging. That may be worth
it to you. Decide knowing the split.

---

## Death Clock: The Life Lab **[confirmed]**

- App Store: https://apps.apple.com/us/app/death-clock-the-life-lab/id6499554412
- Google Play: https://play.google.com/store/apps/details?id=com.deathclock
- Site: https://deathclock.co
- Developer: **Most Days Inc** — https://www.mostdays.com
- Category: Health & Fitness. Age rating 13+.

### ⚠️ It does not analyze DNA

**This is the correction that matters for anyone arriving from this repository.**
Death Clock does no genetic analysis of any kind. There is no saliva kit, no raw
data upload, no variant interpretation. Its own privacy policy does not mention
genetic information anywhere.

The inputs are a **29-question lifestyle and history assessment**, **blood
biomarkers**, and optional **Apple Health / WHOOP / Oura** sync. The output is a
life-expectancy projection derived from those, described by the company as being
built on CDC and global mortality data.

So it is not an alternative to anything in
[the analysis pipeline](dna-analysis-pipeline.md) or
[pharmacogenomics](pharmacogenomics.md). It is a different product in a
neighboring aisle.

### What it actually is

An AI health-concierge subscription built around a longevity estimate. The
company positions it as preventive rather than diagnostic, and cites affiliations
with researchers at Stanford, Berkeley, UCLA, and NYU. It reports over one
million users — **that figure is the company's own and is not independently
verified.**

The genuinely useful component is lab access: it orders blood work through
**Quest and Labcorp** draw sites (the site says **4,500+** locations; a company
press release says 4,800 — take the smaller, and check your own ZIP), and it lets
you upload existing records from your own physician instead of retesting.

### Cost **[confirmed]**

There is a free entry point — the 29-question assessment — and everything past it
is paid. Apple lists these in-app purchases:

| Item | Price |
|---|---|
| Death Clock AI Membership | $9.99 / $39.99 / $69.99 |
| Death Clock Digital Membership | $69.99 |
| Digital only, annual | $49.99 |
| Death Clock Membership | $39.99 / $59.99 / $79.99 / $99.99 |
| "$99 Baseline," 3-day trial | $99.99 |

The site advertises a **baseline blood panel for under $100**. Exact membership
tiers are not published on the marketing page — they appear at checkout and in
the App Store listing above, which is why the table cites Apple rather than the
site.

### Privacy **[confirmed]**

Apple's App Privacy card reports **Usage Data used to track you**, and **contact
info (email, name, phone) linked to your identity**. Identifiers, usage, and
diagnostics are collected but reported as not linked to you. The company states
data is encrypted and never sold.

The privacy policy is more specific and worth reading before you sync Apple
Health: it says information is shared with **advertising partners**, while
**health-related personal information is withheld from marketers**. Those two
statements coexist — the health data is fenced off, the rest of the account and
usage data is not. There is a separate HIPAA authorization document, which
implies HIPAA applies selectively rather than across the whole service.

Deletion is by email request to the support address published in their
[privacy policy](https://deathclock.co/privacy-policy) (`help@` at
`mostdays.com`). No fixed retention period is published.

### Read the number correctly

A projected death date is a **population statistic with your name printed on it**
— the same category as a polygenic score, and it deserves the same skepticism.
It is not a prognosis, it does not know about you specifically, and it will move
if the underlying model is revised. The marketing site carries no "not medical
advice" or FDA-status disclaimer that could be found on 2026-07-22, so supply
that framing yourself.

If a number like this would be distressing rather than motivating, that is a
sufficient reason not to buy it. Nothing here is diagnostic.

### Where it fits

**Reasonable use:** you want blood biomarkers tracked over time with the
interpretation handled for you, you would not otherwise get tested, and the
subscription is what gets you to actually do it. Behavior change is the whole
value proposition and it is not a trivial one.

**Skip it if:** you came here for genetics — it does none. Or if you mainly want
the lab numbers, in which case self-ordering the same Quest or Labcorp panel is
substantially cheaper.
→ [Testing access §3](testing-access.md#3-order-your-own-labs-no-doctors-visit)

---

## Adding another app to this page

Same two rules as the rest of the repository: cite the operator's own live page
with a retrieved-date, and label your confidence. Marketing copy is a claim, not
a source. If a price or a capability cannot be verified, mark it `unverified` —
omitting beats inventing.

Worth documenting: what data it actually ingests, whether the headline number is
measured or modeled, the real cost past the free tier, what the privacy policy
says versus what the App Store card says, and whether the underlying tests can be
bought directly for less.
