# Tracing your family with DNA and records

DNA tells you **which family** you belong to. Only a document or a living person
tells you **which individual**. Almost every unsuccessful search comes from
expecting the DNA to do the second job.

This file is the research methodology: the source ladder, the linkage heuristics
that actually break cases open, how to use DNA matches properly, and the evidence
discipline that keeps a family tree from filling up with confident errors.

---

## Set up before you search

Research is driven by a **queue of specific questions**, not by browsing. Browsing
feels productive and produces nothing.

Create a plain folder of Markdown files:

```
my-research/
  _Index.md              # what this is, where everything lives
  Family_Tree.md         # current structure, with a confidence tier per link
  Timeline.md            # dated events across the whole family
  Open_Questions.md      # THE QUEUE. numbered, specific, one unknown each
  Research_Log.md        # every search: what, where, when, and the result
  Data_Inventory.md      # what documents you already physically have
  Unresolved_Persons.md  # people who appear in records but are not yet placed
  Documents/             # scans and downloads
```

Two habits do most of the work:

1. **Every unknown becomes a numbered question** in `Open_Questions.md`, phrased
   specifically. "Who were the parents of the person born about 1880 in county X"
   is workable. "Research the family" is not.
2. **Log negative results.** "Searched the 1900 census for this county under three
   spellings on 2026-07-21, found nothing" is real data. Without it you will
   re-walk the same ground for years.

> Your vault will contain living people's names, birthdates, and addresses. Keep
> it out of any public repository. The `.gitignore` in this project already
> excludes `vault/`, `family-tree/`, and `*.ged`.

---

## The source ladder — work it in order

### Tier 1: primary sources

Created at or near the time of the event, ideally by someone present.

| Source | Access | What it gives |
|---|---|---|
| **FamilySearch** | Free account. https://www.familysearch.org | The largest free collection of digitized vital records, plus a shared tree. Start here. |
| **Chronicling America** (Library of Congress) | Free, **no account, public API**. https://www.loc.gov/collections/chronicling-america/ | Digitized historic US newspapers. Obituaries name surviving relatives — often the single richest record type. |
| **National Archives (NARA)** | https://www.archives.gov | Census, military service and pension files, immigration, naturalization. |
| **Find a Grave** | https://www.findagrave.com | Burials, headstone photos, and family links. Free. |
| **BillionGraves** | https://billiongraves.com | GPS-tagged headstones; complements Find a Grave. |
| **State vital records** | Varies by state | Birth/death/marriage certificates. Access rules and fees vary; recent records are usually restricted to next of kin. |
| **County courthouses** | Varies | Probate, land, and court records — underused and often decisive. A will names heirs. |

Chronicling America's API is free and needs no account. **Note: the site migrated
into loc.gov in August 2025 and the old `chroniclingamerica.loc.gov/search/...`
API now returns 404.** Guides published before that date will send you to the dead
endpoint. The current form is:

```
https://www.loc.gov/collections/chronicling-america/?q=SURNAME&fo=json
```

Add `&start_date=1900&end_date=1920` to bound the years, and `&c=100` to raise the
page size. Verified working 2026-07-21 (returns JSON with a `results` array).
Migration notice: https://www.loc.gov/ndnp/migration ·
API docs: https://www.loc.gov/apis/additional-apis/chronicling-america-api/

Each result carries the page image and its OCR text, so you can grep the actual
words rather than paging through scans by hand.

### Tier 2: secondary sources

Compiled later or at a remove: published genealogies, compiled indexes,
transcriptions, most newspaper articles about past events. Useful, frequently
wrong. Trace them back to the primary source.

### Tier 3: tertiary

User-contributed online trees, oral history, forum posts, photo captions.

**Treat these as leads, never as evidence.** An error in a popular online tree
gets copied across thousands of trees and starts to look like consensus through
sheer repetition.

Free tier-2/3 sources worth knowing: **WikiTree** (https://www.wikitree.com),
**USGenWeb** (http://usgenweb.org), and **HathiTrust** and **Google Books** for
digitized county histories.

For African-American research specifically: **Slave Voyages**
(https://www.slavevoyages.org) for the transatlantic and intra-American slave
trade databases, the **Freedmen's Bureau Records** digitized through
FamilySearch, and the **1870 census** — the first to enumerate formerly enslaved
people by name, and the wall most African-American research hits going backward.
Crossing that wall usually means shifting from census records to **probate,
estate, and property records of the enslaving family**, where enslaved people
were listed as property. (AfriGeneas, recommended in many older guides, is
**gone** — the domain no longer resolves.)

> **A 403 is not a 404.** Cemetery, archive, and government sites frequently block
> automated fetches while serving the page fine in a normal browser. A `403` or an
> empty body means "try it by hand," not "the record does not exist." A genuine
> `404`/`410` means it is actually gone.

---

## The heuristics that actually break cases

Searching your ancestor's name directly is the obvious move and usually the one
that fails. These work better:

**1. Search the children, not the subject.** Descendants' obituaries and marriage
records name parents and grandparents. When you cannot find a person, find their
kids and read what was written when the kids died.

**2. Search confirmed siblings forward.** A sibling's death certificate names the
same parents you are looking for. Build the sibling set — it multiplies your
chances of one good record.

**3. Search by neighbors, not by surname.** Communities moved and lived together.
Pull the neighboring households from one census year, then search *those* names in
the next decade. This relocates a family whose own surname was mis-indexed or
mis-transcribed — extremely common with handwritten records and OCR.

**4. Pull the military file.** Service and pension files for deceased veterans
name parents, birthplace, and next of kin, and are among the most detailed records
that exist for ordinary people.

**5. Search name variants, always.** This is the one that most often unlocks a
stuck search. Surnames were translated, phonetically re-spelled by clerks, and
re-indexed by OCR:

- Immigrant surnames get **translated** into English (a name meaning "green wood"
  indexed as *Greenwood*; a name meaning "liberty" indexed as *Liberty*).
- French-Canadian families carry ***dit* names** — an alternate family name used
  interchangeably for generations. The records may use either.
- Scandinavian **patronymics** change every generation (a father's given name
  becomes the child's surname). You can often predict the surname from the
  father's given name. Each country fixed hereditary surnames by law on a
  different date — know the date for your country.
- Norwegian **farm names** were used as surnames and *changed when the family
  moved*.
- Clerks spelled phonetically. Search how the name **sounds**, not how it is
  spelled today.

**6. Check whether the place still exists under that name.** County lines moved,
towns were renamed and absorbed. The record may sit in a county that no longer
exists.

---

## Using DNA matches properly

Consumer testing services show you relatives who share DNA with you. Used
correctly this is powerful — including for adoption searches and unknown
parentage. Used carelessly it produces confident nonsense.

### What shared DNA means

| Shared | Typical relationships |
|---|---|
| ~50% | Parent, child, or full sibling |
| ~25% | Grandparent, aunt/uncle, half-sibling, double first cousin |
| ~12.5% | Great-grandparent, first cousin, great-aunt/uncle, half-aunt/uncle |
| ~6.25% | First cousin once removed, second cousin range begins |
| ~3% | Second cousin |
| <1% | Third cousin and beyond — increasingly unreliable |

**A percentage maps to several possible relationships, not one.** The service's
predicted label is a guess and is routinely off by a generation. Always
cross-check against the match's **birth year** — a person 40 years older than you
sharing 12% is a different relationship than a peer sharing 12%.

The reference tool for this is the **Shared cM Project** at DNA Painter
(https://dnapainter.com/tools/sharedcmv4) — enter shared centimorgans and it
returns every statistically consistent relationship with probabilities. Free.

### The method for an unknown parent or grandparent

1. **Fix the side.** Find the closest matches and determine which ones are
   maternal vs paternal (services flag this; if not, matches who match each other
   but not your known relatives are on the unknown side).
2. **Build the surname cluster.** Look at your closest unknown-side matches. Note
   their surnames and their grandparents' birthplaces. A geographic and surname
   cluster will emerge.
3. **Triangulate.** Use the "shared matches" / "in common with" feature on one
   close match. Everyone matching both of you belongs to that branch — this
   isolates one line out of the noise.
4. **Fix each match's generation** using shared percentage plus birth year.
5. **Move to records.** Take the surname cluster and birthplaces into
   FamilySearch, Find a Grave, and newspaper archives — **searching every name
   variant** from the heuristics above.
6. **Prioritize obituaries of deceased elders.** Living matches leave no public
   record trail; their deceased grandparents do, and those obituaries name the
   whole family structure.
7. **Accept the last mile.** DNA plus records will identify the *family*. Naming
   the *specific individual* usually needs either an actual document (an original
   or pre-adoption birth certificate, a court record) or contact with a living
   match who knows. There is often no way around this, and that is not a failure
   of method.

### Guardrails

- **Continental ancestry estimates are reliable. Sub-regional percentages are
  not.** Report ranges, not decimals; the "42.7% from region X" precision is
  false confidence, and estimates change when companies update their reference
  panels.
- **Haplogroups (Y and mtDNA) describe deep ancestry over thousands of years**,
  not genealogical relationships. A shared haplogroup does not mean a documentable
  common ancestor.
- **Assigning a genetic component to a specific ancestor is a hypothesis**
  requiring independent genealogical support. DNA cannot tell you *which* ancestor
  contributed a segment without a documented tree.
- **Contact living matches with care.** They may not know what you know. Unknown
  parentage, undisclosed adoption, and misattributed paternity are common
  discoveries. Lead gently, accept silence as an answer, and never publish a
  living person's information.

---

## Evidence discipline

Grade every claim and write the grade down:

| Tier | Standard |
|---|---|
| **Strong** | Two or more independent sources agree, or one primary source, and nothing contradicts |
| **Moderate** | One primary source, or several agreeing secondary sources; minor explainable conflicts |
| **Speculative** | A single tertiary source, or pure inference |

Rules that keep a tree honest:

- **Every fact cites a specific record.** Not "FamilySearch" — the specific
  record, with its identifier and the date you accessed it.
- **Mark unverified additions inline** as `(unverified)`. Un-marked speculation
  becomes fact within a year purely through familiarity.
- **Resolve conflicts by tier**, and within a tier by how close the informant was
  to the event. A death certificate's birth date came from a grieving relative
  guessing; a baptism record came from someone present.
- **Even primary sources are wrong.** Ages get rounded, names get misheard, and
  people lied about age for marriage, enlistment, and immigration.
- **Negative results go in the log.**

---

## When you are ready to publish

Export to **GEDCOM**, the universal genealogy interchange format — every major
program reads and writes it. It keeps your work portable if a service shuts down
or changes its terms.

**Before publishing anything publicly, strip living people.** Standard practice is
to include no details for anyone who may still be alive, or who died within the
last ~10 years without a public record. Names, birthdates, and locations of living
people are exactly the material used for identity theft, and your relatives did
not consent to publication.
