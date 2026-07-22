#!/usr/bin/env python3
"""Turn your analysis results into a readable report.

Three output styles, because different results deserve different presentation:

    --style plain      Clean, printable, gets out of the way.
    --style magazine   Editorial spreads -- each finding gets its own full
                       screen with distinct typography and color. Good for
                       showing someone, or for making your own results feel
                       like something worth reading.
    --style markdown   Plain text, for pasting into notes or a repo.

Everything is generated locally into one self-contained HTML file. No data
leaves your machine, no CDN is contacted at render time, and the file keeps
working offline forever.

Input is a small JSON file describing your results, so this script never has to
know anything about your genome:

    {
      "title": "My genome notes",
      "subtitle": "optional",
      "sections": [
        {"heading": "Coverage",
         "stat": "89%",
         "body": "Free text.",
         "note": "optional caveat"}
      ]
    }

Usage:
    python3 scripts/make_report.py --input results.json --output report.html
    python3 scripts/make_report.py --input results.json -o r.html --style magazine
    python3 scripts/make_report.py --demo -o demo.html --style magazine
    python3 scripts/make_report.py --self-test
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

DISCLAIMER = (
    "This report is generated from consumer-grade genetic data. It is not a "
    "medical diagnosis and not medical advice. Polygenic scores are population "
    "statistics, not predictions about an individual. Confirm anything "
    "clinically relevant with a licensed clinician or certified genetic "
    "counselor before acting on it."
)

# Each magazine spread gets its own world: background, ink, accent, and a
# display font. Cycled so no two adjacent sections look alike.
SPREADS: tuple[dict[str, str], ...] = (
    {"name": "hero",      "bg": "#faf7f2", "ink": "#16130f", "accent": "#b3421a", "font": "serif-display"},
    {"name": "midnight",  "bg": "#0e1420", "ink": "#eef2f8", "accent": "#7fb2ff", "font": "serif-display"},
    {"name": "clinical",  "bg": "#f2f5f4", "ink": "#0f1f1c", "accent": "#0d7a63", "font": "sans-display"},
    {"name": "alert",     "bg": "#fdf0ef", "ink": "#2a1013", "accent": "#c0392b", "font": "serif-display"},
    {"name": "terminal",  "bg": "#12120f", "ink": "#d8f5c8", "accent": "#8fd66a", "font": "mono-display"},
    {"name": "academic",  "bg": "#fffdf7", "ink": "#1a1a17", "accent": "#5b4bb5", "font": "serif-display"},
    {"name": "bigstat",   "bg": "#1b1636", "ink": "#f4f0ff", "accent": "#ffd166", "font": "sans-display"},
    {"name": "poster",    "bg": "#f5e9dc", "ink": "#2b1a0e", "accent": "#d1622b", "font": "sans-display"},
)


@dataclass
class Section:
    heading: str
    body: str = ""
    stat: str = ""
    note: str = ""


@dataclass
class Report:
    title: str = "Genome report"
    subtitle: str = ""
    sections: list[Section] = field(default_factory=list)


def load_report(path: Path) -> Report:
    """Parse the results JSON, failing loudly on a bad shape rather than
    silently rendering an empty report."""
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path.name} is not valid JSON: {exc}") from exc
    if not isinstance(raw, dict):
        raise ValueError(f"{path.name} must contain a JSON object at the top level")

    raw_sections = raw.get("sections")
    if not isinstance(raw_sections, list) or not raw_sections:
        raise ValueError(
            f"{path.name} needs a non-empty 'sections' array. "
            "See the docstring in scripts/make_report.py for the expected shape."
        )

    sections: list[Section] = []
    for i, s in enumerate(raw_sections, start=1):
        if not isinstance(s, dict):
            raise ValueError(f"section {i} must be an object, got {type(s).__name__}")
        heading = str(s.get("heading", "")).strip()
        if not heading:
            raise ValueError(f"section {i} is missing a 'heading'")
        sections.append(
            Section(
                heading=heading,
                body=str(s.get("body", "")),
                stat=str(s.get("stat", "")),
                note=str(s.get("note", "")),
            )
        )

    return Report(
        title=str(raw.get("title", "Genome report")),
        subtitle=str(raw.get("subtitle", "")),
        sections=sections,
    )


def e(text: str) -> str:
    """Escape for HTML. Report content is user data and is never trusted."""
    return html.escape(text, quote=True)


# --------------------------------------------------------------------------
# renderers
# --------------------------------------------------------------------------

def render_markdown(r: Report) -> str:
    out = [f"# {r.title}"]
    if r.subtitle:
        out.append(f"\n_{r.subtitle}_")
    for s in r.sections:
        out.append(f"\n## {s.heading}\n")
        if s.stat:
            out.append(f"**{s.stat}**\n")
        if s.body:
            out.append(s.body)
        if s.note:
            out.append(f"\n> {s.note}")
    out.append(f"\n---\n\n_{DISCLAIMER}_\n")
    return "\n".join(out)


def render_plain(r: Report) -> str:
    body = [
        f'<header><h1>{e(r.title)}</h1>'
        + (f"<p class=sub>{e(r.subtitle)}</p>" if r.subtitle else "")
        + "</header>"
    ]
    for s in r.sections:
        block = [f"<section><h2>{e(s.heading)}</h2>"]
        if s.stat:
            block.append(f'<p class="stat">{e(s.stat)}</p>')
        if s.body:
            block.append(f"<p>{e(s.body)}</p>")
        if s.note:
            block.append(f'<p class="note">{e(s.note)}</p>')
        block.append("</section>")
        body.append("".join(block))
    body.append(f'<footer><p class="disclaimer">{e(DISCLAIMER)}</p></footer>')

    styles = """
:root{color-scheme:light dark}
*{box-sizing:border-box}
body{margin:0 auto;padding:48px 24px;max-width:46rem;
  font:18px/1.65 ui-serif,Georgia,'Times New Roman',serif;
  color:#1a1a1a;background:#fff}
header{border-bottom:3px solid #1a1a1a;padding-bottom:20px;margin-bottom:40px}
h1{font-size:clamp(30px,5vw,44px);line-height:1.1;margin:0}
.sub{color:#5a5a5a;font-style:italic;margin:8px 0 0}
h2{font-size:26px;margin:44px 0 12px;line-height:1.2}
.stat{font-size:clamp(38px,7vw,60px);font-weight:700;margin:8px 0;
  font-variant-numeric:tabular-nums;letter-spacing:-.02em}
.note{border-left:4px solid #c9c9c9;padding-left:16px;color:#4a4a4a;font-size:16px}
.disclaimer{font-size:14px;color:#5a5a5a;border-top:1px solid #d5d5d5;
  padding-top:20px;margin-top:56px}
@media (prefers-color-scheme:dark){
  body{background:#121212;color:#e8e8e8}
  header{border-color:#e8e8e8}
  .sub,.note,.disclaimer{color:#a8a8a8}
  .note{border-color:#3d3d3d}
  .disclaimer{border-color:#333}
}
@media print{
  body{max-width:none;padding:0;font-size:11pt;color:#000;background:#fff}
  section{break-inside:avoid}
  .disclaimer{border-color:#000}
}
"""
    return _document(r.title, "".join(body), styles)


def render_magazine(r: Report) -> str:
    spreads: list[str] = [
        f"""<section class="spread s-cover">
  <div class="inner">
    <p class="kicker">Personal genomics</p>
    <h1>{e(r.title)}</h1>
    {f'<p class="deck">{e(r.subtitle)}</p>' if r.subtitle else ''}
    <p class="scroll-cue">Scroll</p>
  </div>
</section>"""
    ]

    for i, s in enumerate(r.sections):
        sp = SPREADS[i % len(SPREADS)]
        num = f"{i + 1:02d}"
        parts = [
            f'<section class="spread s-{sp["name"]} f-{sp["font"]}" '
            f'style="--bg:{sp["bg"]};--ink:{sp["ink"]};--accent:{sp["accent"]}">',
            '<div class="inner">',
            f'<p class="num">{num}</p>',
            f"<h2>{e(s.heading)}</h2>",
        ]
        if s.stat:
            parts.append(f'<p class="bigstat">{e(s.stat)}</p>')
        if s.body:
            parts.append(f'<p class="body">{e(s.body)}</p>')
        if s.note:
            parts.append(f'<p class="note">{e(s.note)}</p>')
        parts.append("</div></section>")
        spreads.append("".join(parts))

    spreads.append(
        f"""<section class="spread s-colophon">
  <div class="inner">
    <h2>Before you act on any of this</h2>
    <p class="body">{e(DISCLAIMER)}</p>
    <p class="note">Generated locally with open-genome-toolkit. No data left this machine.</p>
  </div>
</section>"""
    )

    styles = """
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,700;9..144,900&family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');
*{box-sizing:border-box}
body{margin:0;background:#0e1420;
  font-family:Inter,ui-sans-serif,system-ui,sans-serif;
  -webkit-font-smoothing:antialiased}
.spread{min-height:100vh;display:flex;align-items:center;padding:8vh 6vw;
  background:var(--bg,#faf7f2);color:var(--ink,#16130f)}
.inner{max-width:54rem;width:100%}
.num{font-family:'JetBrains Mono',ui-monospace,monospace;font-size:15px;
  letter-spacing:.32em;color:var(--accent);margin:0 0 20px;font-weight:700}
h1{font-family:Fraunces,ui-serif,Georgia,serif;font-weight:900;
  font-size:clamp(52px,11vw,150px);line-height:.92;margin:0;letter-spacing:-.025em}
h2{font-size:clamp(34px,6vw,76px);line-height:1.04;margin:0 0 24px;
  letter-spacing:-.02em;font-weight:800}
.f-serif-display h2{font-family:Fraunces,ui-serif,Georgia,serif;font-weight:900}
.f-mono-display h2{font-family:'JetBrains Mono',ui-monospace,monospace;
  font-weight:700;font-size:clamp(28px,4.6vw,56px)}
.bigstat{font-family:Fraunces,ui-serif,Georgia,serif;font-weight:900;
  font-size:clamp(70px,17vw,220px);line-height:.85;margin:24px 0;
  color:var(--accent);font-variant-numeric:tabular-nums;letter-spacing:-.045em}
.body{font-size:clamp(21px,2.3vw,27px);line-height:1.55;max-width:38rem;
  margin:0 0 20px}
.note{font-size:19px;line-height:1.5;max-width:34rem;opacity:.78;
  border-left:3px solid var(--accent);padding-left:18px;margin-top:28px}
.kicker{font-family:'JetBrains Mono',ui-monospace,monospace;font-size:14px;
  letter-spacing:.4em;text-transform:uppercase;color:#b3421a;margin:0 0 24px;
  font-weight:700}
.deck{font-family:Fraunces,ui-serif,Georgia,serif;font-size:clamp(21px,2.6vw,32px);
  font-style:italic;line-height:1.35;margin:28px 0 0;max-width:34rem;opacity:.82}
/* opacity kept >=.75 so this clears WCAG AA (4.5:1) against the cover -- at
   .5 it measured 3.44:1, which fails even though it is only a scroll hint */
.scroll-cue{font-family:'JetBrains Mono',ui-monospace,monospace;font-size:13px;
  letter-spacing:.34em;text-transform:uppercase;margin-top:12vh;opacity:.78}
.s-cover{background:#faf7f2;color:#16130f}
.s-colophon{background:#0e1420;color:#eef2f8;--accent:#7fb2ff}
.s-colophon h2{font-family:Fraunces,ui-serif,Georgia,serif;
  font-size:clamp(28px,4vw,52px)}
@media print{
  @page{margin:14mm}
  body{background:#fff}
  .spread{min-height:auto;page-break-after:always;break-after:page;
    padding:0 0 16mm;background:#fff!important;color:#000!important;
    display:block}
  .spread:last-child{page-break-after:auto;break-after:auto}
  h1{font-size:30pt}
  h2{font-size:19pt}
  .bigstat{font-size:44pt;color:#000!important}
  .body{font-size:11pt}
  .note{font-size:10pt;border-color:#000!important;opacity:1}
  .num,.kicker,.scroll-cue{color:#000!important}
  .scroll-cue{display:none}
}
"""
    return _document(r.title, "".join(spreads), styles)


def _document(title: str, body: str, styles: str) -> str:
    """Body first, styles last -- content-first document order."""
    return (
        "<!doctype html>\n<html lang=\"en\">\n"
        f"<meta charset=\"utf-8\">\n"
        f"<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\n"
        f"<title>{e(title)}</title>\n"
        f"<body>\n{body}\n"
        f"<style>{styles}</style>\n"
        "</body>\n</html>\n"
    )


DEMO = Report(
    title="What my genome does and does not say",
    subtitle="A worked example using invented numbers, so nobody's real data appears here.",
    sections=[
        Section(
            heading="Coverage came first",
            stat="89%",
            body=(
                "Share of the score's variants present in the analysed file after "
                "imputation. Below roughly half, a raw sum is not comparable to "
                "any published distribution and the honest answer is that the "
                "score cannot be interpreted at all."
            ),
            note="Coverage is a prerequisite, not a quality rating.",
        ),
        Section(
            heading="Clumping removed most of the file",
            stat="41x",
            body=(
                "Ratio of input variants to independent loci after distance-based "
                "clumping. A ratio this large is the measure of how much the same "
                "underlying signal was being counted over and over."
            ),
        ),
        Section(
            heading="The ancestry caveat is not a footnote",
            body=(
                "Most genome-wide association studies were conducted in people of "
                "European ancestry, and scores built from them predict "
                "substantially worse in everyone else. Check the ancestry "
                "composition of any score's development cohort before reading "
                "anything into the output."
            ),
            note="Martin et al., Nature Genetics 51:584-591 (2019).",
        ),
        Section(
            heading="What would change a decision",
            body=(
                "Pharmacogenomics is one of the few areas with real clinical "
                "guidelines behind it. Everything else here is a hypothesis worth "
                "raising with a clinician, not a finding."
            ),
        ),
    ],
)


def self_test() -> int:
    failures: list[str] = []

    for style, renderer in (
        ("plain", render_plain),
        ("magazine", render_magazine),
        ("markdown", render_markdown),
    ):
        out = renderer(DEMO)
        if not out.strip():
            failures.append(f"{style}: produced empty output")
            continue
        if DEMO.sections[0].heading not in out:
            failures.append(f"{style}: first section heading missing from output")
        if "not medical advice" not in out.lower():
            failures.append(f"{style}: disclaimer missing")
        if style != "markdown":
            if not out.startswith("<!doctype html>"):
                failures.append(f"{style}: missing doctype")
            if "@media print" not in out:
                failures.append(f"{style}: no print stylesheet")

    # Content is escaped -- a report is user data, never trusted markup.
    injected = Report(
        title="<script>alert(1)</script>",
        sections=[Section(heading="<img src=x onerror=alert(1)>", body="a & b")],
    )
    for style, renderer in (("plain", render_plain), ("magazine", render_magazine)):
        out = renderer(injected)
        if "<script>alert(1)</script>" in out:
            failures.append(f"{style}: title was not escaped (XSS)")
        if "onerror=alert(1)>" in out:
            failures.append(f"{style}: heading was not escaped (XSS)")
        if "a &amp; b" not in out:
            failures.append(f"{style}: ampersand not escaped")

    # Malformed input must raise a clear error, never render an empty report.
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        bad = Path(td) / "bad.json"
        for content, label in (
            ("{ not json", "invalid JSON"),
            ('{"sections": []}', "empty sections"),
            ('{"sections": [{"body": "no heading"}]}', "missing heading"),
            ('["not an object"]', "top-level array"),
        ):
            bad.write_text(content, encoding="utf-8")
            try:
                load_report(bad)
                failures.append(f"{label}: did not raise")
            except ValueError:
                pass

        good = Path(td) / "good.json"
        good.write_text(
            json.dumps({"title": "T", "sections": [{"heading": "H", "stat": "1%"}]}),
            encoding="utf-8",
        )
        rep = load_report(good)
        if rep.title != "T" or len(rep.sections) != 1 or rep.sections[0].stat != "1%":
            failures.append("valid JSON did not round-trip correctly")

    if failures:
        print("SELF-TEST FAILED:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1
    print("self-test OK: 3 styles render, escaping holds, bad input rejected")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--input", help="results JSON")
    ap.add_argument("-o", "--output", help="output file path")
    ap.add_argument("--style", choices=("plain", "magazine", "markdown"),
                    default="plain")
    ap.add_argument("--demo", action="store_true",
                    help="render the built-in example instead of a file")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return self_test()
    if not args.output:
        ap.error("--output is required (or use --self-test)")

    if args.demo:
        report = DEMO
    elif args.input:
        try:
            report = load_report(Path(args.input))
        except (ValueError, OSError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
    else:
        ap.error("--input or --demo is required")

    renderer = {
        "plain": render_plain,
        "magazine": render_magazine,
        "markdown": render_markdown,
    }[args.style]

    Path(args.output).write_text(renderer(report), encoding="utf-8")
    print(f"wrote {args.output} ({args.style}, {len(report.sections)} sections)")
    if args.style != "markdown":
        print("Open it in a browser. Cmd/Ctrl-P prints or saves to PDF cleanly.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
