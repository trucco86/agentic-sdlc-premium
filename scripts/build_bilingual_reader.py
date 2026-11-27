"""Render the English reader for translation units approved by the editorial gate."""

import argparse
from base64 import b64encode
from html import escape
import json
from pathlib import Path
import re

import fitz

COVER_ART = Path(__file__).resolve().parents[1] / "editorial/assets/english-cover.webp"

EDITION = "Agentic SDLC Premium V0.6"
URL = re.compile(
    r"https?://[^\s<>]+|[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}"
    r"|(?<![\w@./-])(?:[\w-]+\.)+[a-zA-Z]{2,}/[^\s<>]+"
)
TITLE_LINE = re.compile(r"(?m)^(.+?)\s+(\d+)$")
STAMP = (
    "AGENTIC SDLC | PREMIUM EDITION V0.6",
    "VISUAL GUIDE | AGENTIC SDLC PREMIUM",
)
DESIGN = """
:root{font:17px/1.65 system-ui,sans-serif;color:#18253b;background:#f4f6fa;scroll-padding-top:5rem}
*{box-sizing:border-box}body{margin:0}a{color:#164b95;text-underline-offset:.16em}a:focus-visible{outline:3px solid #1677cc;outline-offset:3px}
header{position:sticky;top:0;z-index:1;background:#101e33;color:#fff;padding:.7rem max(1rem,calc((100vw - 59rem)/2));display:flex;align-items:center;justify-content:space-between;gap:1rem}
header a{color:#e1efff}header form{display:flex;align-items:center;gap:.45rem;white-space:nowrap}
header label{font-size:.86rem}header input,header button{font:inherit;font-size:.85rem;padding:.25rem .45rem}
header input{width:4.3rem}button{cursor:pointer}
main{max-width:59rem;margin:auto;padding:1.4rem 1rem 4rem}
.notice{color:#34445e;font-size:.94rem;margin:0 auto 1rem}
section{background:#fff;margin:0 0 1.25rem;padding:clamp(1.2rem,5vw,3.25rem);border:1px solid #dbe2ed;border-radius:12px}
.page-label{display:block;color:#44617c;font-size:.77rem;font-weight:650;letter-spacing:.05em;margin:0 0 .65rem;text-transform:uppercase}
.page-body{white-space:pre-wrap;overflow-wrap:anywhere;margin:0}
.page-body pre{background:#eef3f8;color:#162740;border-radius:8px;padding:1rem;font-size:.83rem;white-space:pre;overflow:auto}
.page-body table{width:100%;border-collapse:collapse;font-size:.9rem;white-space:normal;margin:1rem 0}
.page-body td,.page-body th{padding:.45rem .55rem;border:1px solid #dbe2ed;text-align:left;vertical-align:top}
.page-body th{background:#eef3f8}
h1,h2{font-weight:730;letter-spacing:-.025em;line-height:1.16;margin:.2rem 0 1rem}
h1{font-size:clamp(2.4rem,8vw,4.5rem)}h2{font-size:clamp(1.32rem,4vw,1.85rem)}
.cover{background:#10243f;border-color:#10243f;color:#f7fbff}
.cover .page-label{color:#bcd8f3}.cover a{color:#c0e5ff}
.toc{list-style:none;padding:0;margin:1.1rem 0;columns:2;column-gap:2rem}
.toc li{margin:0 0 .72rem;break-inside:avoid}.toc a{display:block}
.toc .number{color:#465b76;white-space:nowrap;font-size:.86em;margin-left:.35em}
.note{color:#465b76;font-size:.88rem;margin-top:1.2rem}
@media(max-width:640px){.toc{columns:1}header strong{font-size:.77rem}header label{font-size:0}header label::after{content:"Page";font-size:.8rem}}
@media print{header,.notice{display:none}main{padding:0;max-width:none}section{padding:0;border:none;page-break-before:always;border-radius:0;margin:0}section:first-child{page-break-before:auto}.cover{background:none;color:#18253b}.cover .page-label{color:#44617c}:root{font-size:10.5pt}}
"""


NAV_STYLE = """
html{scroll-padding-top:var(--reader-offset,6rem)}
.edition-language,.edition-back{display:inline-flex;align-items:center;gap:.35rem;border-radius:10px;
    padding:.47rem .75rem;font:650 .9rem/1.25 system-ui;text-decoration:none}
.edition-language{color:#11263d;background:#e5f1fd}
header a.edition-language{color:#11263d}
.edition-back{position:fixed;z-index:3;bottom:max(1rem,env(safe-area-inset-bottom));
    right:max(1rem,env(safe-area-inset-right));background:#10243f;color:#fff;
    border:1px solid #53749c;box-shadow:0 4px 18px #0e20363b}
.edition-back:focus-visible,.edition-language:focus-visible{outline:3px solid #489ce8;outline-offset:3px}
html:has(.edition-back) main{padding-bottom:4.5rem}
@media(max-width:620px){header{flex-wrap:wrap;gap:.55rem}.edition-language{padding:.4rem .53rem;font-size:.78rem}}
@media print{.edition-back,.edition-language{display:none}html:has(.edition-back) main{padding-bottom:0}}
"""
ART_STYLE = """
.cover-lead,.map-banner{border-radius:18px;padding:clamp(1.1rem,4vw,2.5rem)}
.cover-lead{background:radial-gradient(ellipse at 85% 25%,#24598a,#112842 65%);
    border:1px solid #4875a0;margin-bottom:1.2rem;display:grid;grid-template-columns:minmax(0,1.05fr) minmax(0,.95fr);gap:1.2rem;align-items:center}
.cover-art{display:block;width:100%;height:auto;border-radius:12px}
@media(max-width:620px){.cover-lead{grid-template-columns:1fr}}
.cover-lead h1{margin:.65rem 0;color:#fff}.cover-lead strong{color:#82c5ff}
.cover-lead p{margin:.4rem 0;color:#d3eaff}.cover-route,.flow-steps{display:flex;flex-wrap:wrap;gap:.55rem;
    list-style:none;padding:0;margin:1.15rem 0}
.cover-route li,.flow-steps li{border:1px solid #b6c9dd;border-radius:9px;padding:.5rem .75rem}
.cover-route li{background:#182f4b;border-color:#4b7198;color:#edf6ff;font-size:.76rem}
.map-banner{background:#eaf3fc;margin:0 0 1rem}.map-banner p{margin:.35rem 0}
.map-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,14rem),1fr));gap:.8rem;margin:1rem 0}
.map-card{border:1px solid #cbd9e8;border-top:3px solid #377eaa;border-radius:10px;
    background:#f6f9fc;padding:.85rem;font-size:.9rem}
.map-card h3{font-size:.98rem;line-height:1.35;margin:0 0 .55rem;color:#173c61}
.map-card ol{margin:0;padding-left:1.7rem}.map-card li+li{margin-top:.19rem}
.map-hub{max-width:26rem;margin:1.25rem auto 0;padding:.85rem 1rem;color:#fff;background:#173c61;
    text-align:center;border-radius:12px;white-space:pre-wrap}
.map-branch{width:2px;height:1.3rem;background:#377eaa;margin:auto}
.flow-figure{margin:1rem 0;padding:1rem 1.2rem;background:#edf5ff;border:1px solid #c0d4e7;border-radius:12px}
.flow-figure figcaption{font-size:.87rem;font-weight:700;letter-spacing:.03em;color:#244769}
.flow-steps{margin:.65rem 0 0}
.flow-steps li{background:#fff;color:#173652;font-size:.92rem}
.flow-steps b{display:inline-block;margin-right:.42rem;color:#215f95}
.atlas-diagram{margin-top:.65rem;font:500 .9rem/1.55 system-ui;color:#173652;white-space:pre-wrap}
.diagram-nodes{display:flex;flex-wrap:wrap;gap:.55rem;align-items:stretch;margin:.45rem 0}
.diagram-nodes>*{flex:1 1 8.5rem;display:grid;align-content:center;padding:.55rem .7rem;background:white;
    border:1px solid #b6c9dd;border-radius:8px;text-align:center}
.diagram-arrow{display:block;text-align:center;font-weight:700;color:#215f95}
#page-080 th:last-child,#page-080 td:last-child{min-width:7.1rem;overflow-wrap:normal}
@media print{.cover-lead{background:#10243f;print-color-adjust:exact}.map-card,.flow-figure{break-inside:avoid}}
"""
SCRIPT = """
(() => {
    const header = document.querySelector('header');
    const switcher = document.querySelector('.edition-language');
    const syncHeader = () => document.documentElement.style.setProperty(
        '--reader-offset', (header.getBoundingClientRect().height + 14) + 'px');
    syncHeader();
    if (window.ResizeObserver) new ResizeObserver(syncHeader).observe(header);
    if (!switcher) return;
    switcher.addEventListener('click', () => {
        const headerBottom = header.getBoundingClientRect().bottom;
        const nearTop = headerBottom + 42;
        const anchored = document.getElementById(window.location.hash.slice(1));
        const anchoredBox = anchored?.getBoundingClientRect();
        const readingPage = anchored?.matches('main > section') && anchoredBox.bottom > nearTop
            && anchoredBox.top < window.innerHeight - 40 ? anchored
            : Array.from(document.querySelectorAll('main > section'))
                .find(node => node.getBoundingClientRect().bottom > nearTop);
        const toc = document.getElementById('sumario') ?? document.getElementById('page-004');
        const atContents = toc.getBoundingClientRect().top <= nearTop &&
            toc.getBoundingClientRect().bottom > nearTop;
        const number = atContents ? null : Number(readingPage?.id.match(/\\d+$/)?.[0]);
        const target = new URL(switcher.href);
        const english = switcher.hreflang === 'en';
        target.hash = number
            ? (english ? 'page-' + String(number).padStart(3, '0') : 'p' + number)
            : (english ? 'page-004' : 'sumario');
        switcher.href = target.href;
    });
})();
"""
FLOW = re.compile(
    r"(?m)^(STEPS AND DEPENDENCIES|[A-Z][A-Z /&-]{4,56}(?:SEQUENCE|FLOW|STEPS|WORKFLOW))\n+\n?"
    r"((?:\d+\.\s+[^\n]+\n?){3,9})(?=\n|$)"
)
NUMBERED = re.compile(r"(?m)^(\d+)\.\s+(.+)$")


def link_text(value):
    output = []
    cursor = 0
    for match in URL.finditer(value):
        output.append(escape(value[cursor:match.start()]))
        label = match.group().rstrip(".,;:)'”")
        if label.startswith(("https://", "http://")):
            target = label
        elif "@" in label:
            target = "mailto:" + label
        else:
            target = "https://" + label
        output.append(f'<a href="{escape(target, quote=True)}">{escape(label)}</a>')
        cursor = match.start() + len(label)
    output.append(escape(value[cursor:]))
    return "".join(output)


def toc_markup(value, destinations):
    rows = TITLE_LINE.findall(value)
    if len(rows) != len(destinations) or any(page < 1 for page in destinations):
        raise ValueError("The translated table of contents does not match the source links")
    links = "".join(
        f'<li><a href="#page-{page:03}">{escape(label)}'
        f'<span class="number">{printed}</span></a></li>'
        for (label, printed), page in zip(rows, destinations, strict=True)
    )
    return (
        "<h2>Interactive Table of Contents</h2>"
        '<p class="note">V0.6 Preview</p>'
        "<p>Select a topic to jump to its section.</p>"
        f'<ol class="toc">{links}</ol>'
        '<p class="note">The numbers in this table of contents follow the source’s printed numbering. '
        'The page selector uses PDF page positions, including inserted pages.</p>'
    )


def body_markup(page, content, destinations):
    if page == 4:
        return toc_markup(content, destinations)
    lines = content.splitlines()
    if lines[0] in STAMP:
        lines.pop(0)
    if page == 1:
        lines = [line for line in lines if line != "Agentic SDLC"]
        heading = "<h1>Agentic SDLC</h1>"
    elif page == 2:
        lines = [line for line in lines if line != "MIND MAP"]
        heading = "<h2>Mind Map</h2>"
    else:
        heading = ""
    blocks = []
    for chunk in re.split(r"(?m)(^```[^\n]*\n[\s\S]*?^```[ \t]*$)", "\n".join(lines).strip()):
        if chunk.startswith("```"):
            blocks.append(chunk.rstrip())
        else:
            blocks.extend(block for block in re.split(r"\n[ \t]*\n+", chunk.strip("\n")) if block.strip())
    rendered = []
    for block in blocks:
        rows = [line.strip().strip("|").strip().split(" | ") for line in block.splitlines()]
        column_count = len(rows[0])
        if block.startswith("```") and block.endswith("\n```"):
            code = block.split("\n", 1)[1].removesuffix("\n```")
            rendered.append(f"<pre><code>{escape(code)}</code></pre>")
        elif block.startswith(("    ", "\t")) and all(
            not line or line.startswith(("    ", "\t")) for line in block.splitlines()
        ):
            code = "\n".join(line[4:] if line.startswith("    ") else line[1:]
                             for line in block.splitlines())
            rendered.append(f"<pre><code>{escape(code)}</code></pre>")
        elif (len(rows) >= 3 and column_count > 1
                and all(len(row) == column_count for row in rows)
                and not block.startswith(" ")):
            head, *body = rows
            if body and all(re.fullmatch(r":?-{3,}:?", cell) for cell in body[0]):
                body.pop(0)
            cells = "".join(f"<th scope=\"col\">{link_text(cell)}</th>" for cell in head)
            entries = "".join(
                "<tr>" + "".join(f"<td>{link_text(cell)}</td>" for cell in row) + "</tr>"
                for row in body
            )
            rendered.append(f"<table><thead><tr>{cells}</tr></thead><tbody>{entries}</tbody></table>")
        else:
            rendered.append(link_text(block))
    joined = "\n\n".join(rendered)
    return f'{heading}<div class="page-body">{joined}</div>'


def insert_once(document, anchor, replacement):
    if document.count(anchor) != 1:
        raise ValueError(f"Expected one HTML insertion point: {anchor}")
    return document.replace(anchor, replacement, 1)


def nav(document, language, bilingual=True):
    english = language == "en"
    alternate = "../index.html" if english else "en/index.html"
    alternative_language = "pt-BR" if english else "en"
    alternative_label = "Português" if english else "English"
    toc = "#page-004" if english else "#sumario"
    back = "Back to contents" if english else "Voltar ao sumário"
    switch = (
        f'<a class="edition-language" href="{alternate}" hreflang="{alternative_language}" '
        f'lang="{alternative_language}">{alternative_label} <span aria-hidden="true">↔</span></a>'
    )
    if bilingual:
        document = insert_once(document, "</header>", switch + "</header>")
    document = insert_once(document, "</head>", f"<style>{NAV_STYLE}</style></head>")
    return insert_once(
        document, "</body>",
        f'<a class="edition-back" href="{toc}"><span aria-hidden="true">↑</span> {back}</a>'
        f"<script>{SCRIPT}</script></body>",
    )


def lines(markdown):
    return [line.strip() for line in markdown.splitlines() if line.strip()]


def build_cover(markdown):
    cover = lines(markdown)
    route_index = next(i for i, line in enumerate(cover) if " → " in line)
    route = "".join(f"<li>{escape(stop.title())}</li>" for stop in cover[route_index].split(" → "))
    artwork = b64encode(COVER_ART.read_bytes()).decode("ascii")
    visual = (
        '<div class="cover-lead"><div>'
        f'<p>{escape(cover[0])}</p><p><strong>{escape(cover[1])}</strong></p>'
        f'<h1>{escape(cover[2])}</h1><p>{escape(cover[3])}</p><p>{escape(cover[4])}</p>'
        f'<p>{escape(cover[5])}</p><p>{escape(cover[6])}</p></div>'
        f'<img class="cover-art" src="data:image/webp;base64,{artwork}" width="1122" height="1402" '
        'alt="A luminous blue circuit profile overlooks an amber road climbing a mountain at sunrise."></div>'
        f'<ul class="cover-route">{route}</ul>'
        + "".join(f"<p>{escape(line)}</p>" for line in cover[route_index + 1:])
    )
    return visual


def build_map(markdown):
    deck = re.split(r"\n[ \t]*\n+", markdown.strip())
    cards = []
    for block in deck[4:16]:
        heading, *entries = block.splitlines()
        entries = [NUMBERED.fullmatch(entry) for entry in entries]
        if len(entries) != 5 or not all(entries):
            raise ValueError(f"Mind map card is incomplete: {heading}")
        items = "".join(f"<li>{escape(m[2])}</li>" for m in entries)
        cards.append(
            f'<div class="map-card"><h3>{escape(heading)}</h3>'
            f'<ol start="{entries[0][1]}">{items}</ol></div>'
        )
    if len(cards) != 12:
        raise ValueError("Mind map must contain twelve sections")
    intro = lines("\n".join(deck[1:4]))
    hub = f'<div class="map-hub">{escape(deck[16])}</div><div class="map-branch" aria-hidden="true"></div>'
    closing = "".join(f'<p class="page-body">{escape(block)}</p>' for block in deck[17:])
    return (
        '<div class="map-banner"><h2>Agentic SDLC Mind Map</h2>'
        + "".join(f"<p>{escape(line)}</p>" for line in intro[2:])
        + '</div><div role="group" aria-label="Twelve branches of the Agentic SDLC mind map">'
        + hub + '<div class="map-grid">' + "".join(cards) + "</div></div>" + closing
    )


def embed_page_visual(document, number, contents):
    start = re.search(rf'<section[^>]* id="page-{number:03}"[^>]*><p class="page-label">[^<]+</p>', document)
    if not start:
        raise ValueError(f"Missing source page {number}")
    end = document.index("</section>", start.end())
    return document[:start.end()] + contents + document[end:]


def flow_figure(match):
    steps = "".join(f"<li><b>{m[1]}</b>{m[2]}</li>" for m in NUMBERED.finditer(match[2]))
    return (
        f'<figure class="flow-figure"><figcaption>{match[1]}</figcaption>'
        f'<ol class="flow-steps">{steps}</ol></figure>'
    )


def build_special_figure(document, page, caption, pattern):
    section = re.search(rf'(<section[^>]* id="page-{page:03}"[^>]*>)([\s\S]*?)(</section>)', document)
    if not section:
        raise ValueError(f"Missing diagram page {page}")
    body, count = re.subn(
        pattern,
        lambda match: f'<figure class="flow-figure"><figcaption>{caption}</figcaption>'
                      f'<div class="atlas-diagram">{diagram_nodes(page, match[1])}</div></figure>',
        section[2],
    )
    if count != 1:
        raise ValueError(f"Could not identify diagram content on page {page}")
    return document[:section.start(2)] + body + document[section.end(2):]


def diagram_nodes(page, content):
    def nodes(values):
        return '<div class="diagram-nodes">' + "".join(f"<span>{value}</span>" for value in values) + "</div>"

    arrow = '<span class="diagram-arrow" aria-hidden="true">↓</span>'
    if page == 16:
        return arrow.join(nodes([line]) for line in content.splitlines())
    if page in (50, 317):
        stages = [line.strip() for line in content.splitlines() if line.strip() != "↓"]
        paths = stages[2].removeprefix("Parallel validation paths: ").split(" | ")
        return arrow.join([nodes([stages[0]]), nodes([stages[1]]), nodes(paths)]
                          + [nodes([stage]) for stage in stages[3:]])
    if page in (51, 53):
        stages = content.split(" → ")
        return arrow.join(nodes(stage.split(" | ")) for stage in stages)
    if page == 280:
        route, results = content.split("\n↓\n", 1)
        return arrow.join([*(nodes([stage]) for stage in route.split(" → ")), nodes(results.splitlines())])
    return content


def add_visuals(document, units):
    for number, builder in ((1, build_cover), (2, build_map)):
        document = embed_page_visual(document, number, builder(units[number - 1]["translated_text"]))
    document, figures = FLOW.subn(flow_figure, document)
    if figures < 8:
        raise ValueError(f"Expected the translated flow diagrams to render, got {figures}")
    figures_by_page = {
        16: ("Agent → Harness → MCP tools", r"(Planning agent —[^\n]+\nExecution harness —[^\n]+\nMCP tools —[^\n]+)"),
        50: ("Validation fan-out", r"(Spec and acceptance criteria\n[\s\S]*?Contract / OpenAPI)"),
        51: ("Payment call sequence", r"(Customer → Checkout → Gateway → Ledger)"),
        53: ("Release decision", r"(Build and critical tests → Deterministic gate → Fail: Block \| Pass: Approve)"),
        280: ("Budget, cost, and acceptance", r"(Task Contract → Risk Gate → Budget Ledger → Model Router\n[\s\S]*?ACCEPTANCE — Merge / rework)"),
        317: ("Reference architecture", r"(Versioned spec \+ acceptance criteria\n[\s\S]*?Evidence \+ CI Gate)"),
        318: ("Payment sequence", r"(Customer \| Checkout \| Gateway \| Persistence\n[\s\S]*?6\. Checkout → Customer:[^\n]*)"),
        320: ("Release decision", r"(Build \+ tests \+ evidence\n[\s\S]*?YES → Approve with an audit trail)"),
    }
    for page, (caption, pattern) in figures_by_page.items():
        document = build_special_figure(document, page, caption, pattern)
    document = insert_once(document, "</head>", f"<style>{ART_STYLE}</style></head>")
    return document

def render(edition, source):
    with fitz.open(source) as pdf:
        links = [link for link in pdf[3].get_links() if link["kind"] == fitz.LINK_GOTO]
    links.sort(key=lambda link: (link["from"].x0, link["from"].y0))
    destinations = [link["page"] + 1 for link in links]
    units = edition["units"]
    pages = []
    for unit in units:
        number = unit["page"]
        page_class = ' class="cover"' if number == 1 else ""
        pages.append(
            f'<section{page_class} id="page-{number:03}" aria-label="Source page {number}">'
            f'<p class="page-label">Source page {number} of {len(units)}</p>'
            f'{body_markup(number, unit["translated_text"], destinations)}</section>'
        )
    document = (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<meta name="source-sha256" content="{edition["source_sha256"]}">'
        f'<title>{EDITION} | English Edition</title><style>{DESIGN}</style></head>'
        '<body><header><strong>Agentic SDLC Premium V0.6</strong><a href="#page-004">Contents</a>'
        '<form id="jump"><label for="page">Source page</label>'
        f'<input id="page" type="number" min="1" max="{len(units)}" required><button>Go</button></form>'
        '</header><main>'
        + "\n".join(pages)
        + '</main><script>document.getElementById("jump").addEventListener("submit", (event) => {'
        'event.preventDefault(); const page = document.getElementById("page");'
        'const target = document.getElementById("page-" + String(page.valueAsNumber).padStart(3, "0"));'
        'if (target) window.location.hash = target.id; });</script></body></html>'
    )
    return nav(add_visuals(document, units), "en")


def build(output, source, manifest, english_edition):
    portuguese = output / "index.html"
    english = output / "en" / "index.html"
    if english.exists():
        raise ValueError("Use a clean site build to avoid a stale English edition")
    pt_html = portuguese.read_text(encoding="utf-8")
    if english_edition is not None:
        from translation_gate import validate
        from translation_inventory import inventory

        edition = json.loads(english_edition.read_text(encoding="utf-8"))
        validate(inventory(source, manifest), edition)
        en_html = render(edition, source)
        pt_html = nav(pt_html, "pt-BR")
        english.parent.mkdir(parents=True, exist_ok=True)
        english.write_text(en_html, encoding="utf-8")
    else:
        pt_html = nav(pt_html, "pt-BR", bilingual=False)
    portuguese.write_text(pt_html, encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("build/full-html"))
    parser.add_argument("--source", type=Path, default=Path("source/current.pdf"))
    parser.add_argument("--manifest", type=Path, default=Path("editorial/source_manifest.json"))
    parser.add_argument("--english-edition", type=Path)
    args = parser.parse_args()
    build(args.output, args.source, args.manifest, args.english_edition)

