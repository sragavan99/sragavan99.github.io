"""Generate the component-guide pages from bpl/data/guide.json (see manuscript.py)."""

import html
import json
import re
import xml.etree.ElementTree as ET

import manuscript
from chrome import page


SHARED = ["setup", "assembly", "finite-algebra"]
# The product walkthrough in the website specification: each step names a component and a short caption.
WALKTHROUGH = [
    ("L-FAMILY", None, "The logical contribution: the product family combines the two sampled factors."),
    ("P-CHILD", None, "Describe the two child queries. The right query uses the midpoint as its source."),
    ("P-CAP", "forward", "At the source, follow the correction's outgoing port to the midpoint. On success it returns the incoming port that identifies the edge in reverse."),
    ("P-ROW", None, "At the midpoint, read the requested digit of the transition entry and restore the cursor."),
    ("P-CAP", "inverse", "Return from the midpoint to the source."),
    ("P-ARRIVAL", None, "Supply the signed weighted digit for this record: the signed arrival."),
]
WALKTHROUGH_NEXT = ["group-arrivals", "compress-and-select", "final-row"]
# The guide's statement of the §1 toy problem, in TeX, drawn from the numbers and steps in §1.1.
TOY_PROBLEM = r"""The correction step needs the product \(EC\) of a correction matrix \(E\) and the transition matrix \(C\).
One term of its \((x,y)\) entry follows a correction edge from the source \(x\) to a sampled midpoint \(z\), then a transition
from \(z\) to the destination \(y\). In the example at stage \(l\), the two sampled entries are \(1/2\) and \(1/4\), so with the
midpoint retained the term contributes \(f_l/(8\pi_{f_l})\) to the logical sample.

\textbf{The problem:} produce the digits of this one contribution on demand, in low space. Starting at \(x\), the evaluator must
move to \(z\) along the correction edge, read the transition entry there, and return to \(x\). It keeps only a bounded port token
for the way back rather than the source's name, and it never stores either entry in full. The steps below show which routines do each part."""
KIND = {"logical": "Logical routine", "physical": "Physical routine", "terminal": "Terminal program"}
# The guide's own top-down grouping of the physical routines (not manuscript text). Every physical
# routine must appear exactly once; the build checks this.
LAYERS = [
    ("root", "Root", "Validate the input and fix the finite parameters, then return the median over seeds.",
     [("", "", ["P-ROOT", "P-SETUP"])]),
    ("derandomize", "Derandomization (§12)", "Enumerate every admitted seed and return the lower median of the trial values. "
     "Each candidate answer rescans the seeds and recomputes the trials, so no list of seeds or values is stored.",
     [("", "", ["P-MEDIAN", "P-SEEDS", "P-TRIAL"])]),
    ("queries", "The two recursive queries", "Every estimate is a digit of a row entry (P-ROW) or of a vector (P-VECTOR) for one "
     "task. Together they implement the logical estimator L-ESTIMATE. Answering a query asks only for queries at smaller budgets, "
     "which is where the recursion ends.", [("", "", ["P-ROW", "P-VECTOR"])]),
    ("inside", "Inside one query", "L-ESTIMATE builds a row bottom-up: sample terms, averaged differences, grouping, compression, "
     "final gates. A physical query runs that pipeline backwards on demand. The final gates ask for the compressed raw row, which asks "
     "for grouped sums, which ask for single arrivals, which ask for child queries at smaller budgets. A vector query skips grouping "
     "and compression and averages scalar arrivals directly.",
     [("gates", "Final gates (§6.2)", ["P-LOCAL", "P-INCOMING", "P-CAP", "P-CLASS", "P-RAWRANK"]),
      ("raw", "Compressed raw row (§8.2)", ["P-RAWNUM", "P-SELECT", "P-COMPRESS", "P-THRESHOLD", "P-INTERMEDIATERANK"]),
      ("grouping", "Grouping arrivals (§8.1, §9.4)", ["P-REPRESENTATIVE", "P-MERGE", "P-MATCH", "P-MATCH-HASH"]),
      ("arrivals", "Sample terms and arrivals (§3.3, §7)", ["P-SCALARPREFIX", "P-ARRIVAL", "P-VALID", "P-DESCRIPTOR",
                                                           "P-INTRINSICVALID", "P-INTRINSICVALUE"])]),
    ("infra", "Infrastructure", "Routines used at every level: digit-stream arithmetic, rebuilding tasks and seeds from short records, "
     "and moving between endpoints without saving vertex names.",
     [("arith", "Arithmetic (§11)", ["P-NUMSTEP", "P-NODESTEP", "P-AFFINE", "P-MULTIPLY", "P-RECIPROCAL", "P-RANK"]),
      ("rebuild", "Rebuilding tasks and seeds (§3, §7.1, §9.1)", ["P-REPLAY", "P-CHILD", "P-WORD", "P-SEEDSTEP", "P-MEMBER"]),
      ("navigate", "Moving without saving names (§2.2, §9, §10)", ["P-BASE", "T-INTRINSIC", "T-DESCRIPTOR", "T-RAW", "T-FINAL", "T-SCORE",
                                                                   "P-VISITPOOL", "P-VISITRAW", "P-VISITINTRINSIC", "P-ENDPOINT",
                                                                   "P-ENDPOINT-KEY", "P-KEY", "P-PROBE", "P-TOUR", "P-INCOMINGRANK"])]),
]
EDGE_KINDS = {"budget": "smaller budget", "slack": "previous slack level", "completed": "completed raw row"}
NO_PHYSICAL = ("This ingredient has no physical routines of its own. Its corrections and copies enter the physical algorithm through "
               "the task families: the pilot and actual corrections and the residual copies in D-ROWFAMILIES and D-CHILD, whose fields "
               "P-CHILD returns and whose sample terms P-INTRINSICVALUE evaluates.")


def edge_kind(callee, arguments):
    """Classify a call by its task argument, as written in the manuscript's pseudocode."""
    if callee in ("P-ROW", "P-VECTOR", "P-INCOMING") and re.search(r"\\rm leaf|_R\b|\\rm score|m-c", arguments):
        return "budget"
    if re.search(r"\[2d\]|^\\mathcal T,2d,", arguments):
        return "slack"
    if "[1]" in arguments:
        return "completed"
    return ""


def kind_of(c):
    return "terminal" if c["id"].startswith("T-") else c["kind"]


class Guide:
    def __init__(self, data, toy, svg_text, toy_body):
        self.data, self.toy, self.toy_body = data, toy, toy_body
        self.sections = {s["slug"]: s for s in data["sections"]}
        self.ops = {o["slug"]: o for o in data["operations"]}
        self.comps = {c["id"]: c for c in data["components"]}
        self.defs = {d["id"]: d for d in data["definitions"]}
        self.pages = data["pages"]
        # Map ingredients and manuscript sections share their names (up to case).
        names = {item["name"].casefold(): item for item in toy["ingredients"]}
        self.ingredient = {}
        for s in data["sections"]:
            if s["title"].casefold() in names:
                self.ingredient[s["slug"]] = names[s["title"].casefold()]
        if len(self.ingredient) != len(toy["ingredients"]):
            raise SystemExit("build.py: every map ingredient needs a manuscript section with the same name")
        self.by_ingredient_name = {s["title"].casefold(): slug for slug, s in self.sections.items()}
        self.map = map_relations(svg_text)
        self.called_by = {mode: {} for mode in ("exact", "full")}
        for c in data["components"]:
            for mode in ("exact", "full"):
                if c["full_only"] and mode == "exact":
                    continue
                for callee in c["callees"][mode]:
                    self.called_by[mode].setdefault(callee, []).append(c["id"])
        self.proof_refs = {o["slug"]: proof_targets(o["proof"] or "") for o in data["operations"]}
        self.def_refs = {c["id"]: sorted(set(re.findall(r"\\Dref\{([^}]+)\}", c["interface"] + c["preamble"]
                         + "".join(s["tex"] for s in c["steps"]) + c["after"]))) for c in data["components"]}

    # ------------------------------------------------------------ addresses
    def section_kind(self, slug):
        s = self.sections[slug]
        if slug == "walkthrough":
            return "walkthrough"
        if slug in self.ingredient:
            return "ingredient"
        return "shared" if s["operations"] else "reference"

    def url(self, kind, key):
        if kind == "component":
            return f"components/{key}.html" if key in self.comps else None
        if kind == "definition":
            return f"reference.html#{key}" if key in self.defs else None
        if kind == "operation":
            o = self.ops[key]
            return f"index.html#op-{key}" if o["section"] == "walkthrough" else f"operations/{key}.html"
        if kind == "section":
            k = self.section_kind(key)
            return {"walkthrough": "index.html#walkthrough", "ingredient": f"ingredients/{key}.html",
                    "shared": f"sections/{key}.html", "reference": f"reference.html#sec-{key}"}[k]
        if kind == "id":
            key = key[6:] if key.startswith("D-API-") else key
            return self.url("component", key) or self.url("definition", key)
        return None

    def converter(self, root):
        def links(kind, key):
            u = self.url(kind, key) if kind != "url" else None
            return root + u if u else None

        def refs(kind, key):
            if kind == "sec":
                return "§" + self.sections[key]["number"], root + self.url("section", key)
            return "§" + self.ops[key]["number"], root + self.url("operation", key)
        return manuscript.Converter(links, refs)

    def a(self, root, kind, key, label=None, cls="id"):
        label = html.escape(label if label is not None else key)
        return f'<a class="{cls}" href="{root}{self.url(kind, key)}">{label}</a>'

    def where(self, kind, key):
        """A plain-text manuscript location (the PDF itself is not published)."""
        page_no = self.pages.get(f"{kind}.{key}")
        return f"p. {page_no}" if page_no else ""

    # ------------------------------------------------------------ shared pieces
    def outline(self, root, slug, current_op=None, current_comp=None):
        s = self.sections[slug]
        rows = []
        for op_slug in s["operations"]:
            o = self.ops[op_slug]
            comps = "".join(
                f'<li class="{"full-only-entry" if self.comps[b["id"]]["full_only"] else ""}">'
                f'<a href="{root}{self.url("component", b["id"])}"{" aria-current=page" if b["id"] == current_comp else ""}>{b["id"]}</a></li>'
                for b in o["blocks"] if b["type"] == "component")
            here = " aria-current=page" if op_slug == current_op and not current_comp else ""
            rows.append(f'<details class="outline"{" open" if op_slug == current_op else ""}><summary>§{o["number"]} '
                        f'{html.escape(o["title"])}</summary><ul><li><a href="{root}{self.url("operation", op_slug)}"{here}>Operation overview</a></li>{comps}</ul></details>')
        title = f'§{s["number"]} {html.escape(s["title"])}'
        return (f'<aside aria-label="Section outline"><div class="outline-box"><h2><a href="{root}{self.url("section", slug)}">{title}</a></h2>'
                f'{"".join(rows)}<p><a href="{root}index.html#ingredients">All ingredients</a></p></div></aside>')

    def crumbs(self, root, slug, op=None, comp=None):
        parts = [f'<a href="{root}index.html">Guide</a>']
        s = self.sections[slug]
        parts.append(f'<a href="{root}{self.url("section", slug)}">§{s["number"]} {html.escape(s["title"])}</a>')
        if op:
            o = self.ops[op]
            parts.append(f'<a href="{root}{self.url("operation", op)}">§{o["number"]} {html.escape(o["title"])}</a>')
        if comp:
            parts.append(html.escape(comp))
        return f'<p class="crumbs">{" › ".join(parts)}</p>'

    def comp_line(self, root, cid, extra=""):
        c = self.comps[cid]
        full = c["full_only"]
        return (f'<li class="{"full-only-entry" if full else ""}">{self.a(root, "component", cid)} '
                f'<span class="t">{html.escape(c["title"])}</span>{" <span class=mode-tag>Full space only</span>" if full else ""}{extra}</li>')

    def comp_groups(self, root, o):
        ids = [b["id"] for b in o["blocks"] if b["type"] == "component"]
        logical = [i for i in ids if self.comps[i]["kind"] == "logical"]
        physical = [i for i in ids if self.comps[i]["kind"] != "logical"]
        out = []
        for label, group in [("Logical reference", logical), ("Physical queries", physical)]:
            if group:
                out.append(f'<p class="label">{label}</p><ul class="comp-list">{"".join(self.comp_line(root, i) for i in group)}</ul>')
        defs = [b["id"] for b in o["blocks"] if b["type"] == "definition"]
        if defs:
            items = "".join(f'<li>{self.a(root, "definition", d)} <span class="t">{html.escape(self.defs[d]["title"])}</span></li>' for d in defs)
            out.append(f'<p class="label">Definitions</p><ul class="comp-list">{items}</ul>')
        if any(self.comps[i]["full_only"] for i in ids):
            n = sum(self.comps[i]["full_only"] for i in ids)
            out.append(f'<p class="mode-note exact-note">{n} full-space-only component{"s" if n > 1 else ""} hidden. Switch to Full space to show {"them" if n > 1 else "it"}.</p>')
        return "".join(out)

    def proof_box(self, conv, o):
        if not o["proof"]:
            return ""
        return (f'<section class="panel proof" aria-labelledby="proof-{o["slug"]}"><h2 id="proof-{o["slug"]}">What to prove</h2>'
                f'<p class="kicker">Open proof obligation · §{o["number"]}</p>{conv(o["proof"])}</section>')

    # ------------------------------------------------------------ pages
    def component_page(self, cid):
        root = "../"
        conv = self.converter(root)
        c, o = self.comps[cid], self.ops[self.comps[cid]["operation"]]
        k = kind_of(c)
        has_full_parts = (any(s["full"] for s in c["steps"]) or "\\Lpart" in c["interface"] + c["preamble"]
                          + "".join(s["tex"] for s in c["steps"]) or c["callees"]["exact"] != c["callees"]["full"]
                          or any(m["full"] for m in c["mode_uses"]))
        banner = ""
        if c["full_only"]:
            banner = ('<p class="mode-note">Full-space mode only. This component is part of the logarithmic-space '
                      'evaluator\'s fingerprint comparison and is not used with exact name comparison.</p>')
        elif has_full_parts:
            banner = '<p class="mode-note exact-note">This component has full-space additions. Switch to Full space to show them.</p>'
        modes = ""
        if c["mode_uses"]:
            rows = "".join(
                f'<tr class="{"full-only-entry" if m["full"] else ""}"><td>{html.escape(m["mode"])}</td>'
                f'<td>{"Full-space evaluator only" if m["use"] == "L only" else "Both evaluators"}</td>'
                f'<td>{self.ingredient_link(root, m["ingredient"])}</td></tr>' for m in c["mode_uses"])
            modes = (f'<section class="panel"><h2>Modes</h2><div class="table-wrap"><table><tr><th>Mode</th><th>Used by</th>'
                     f'<th>Serves ingredient</th></tr>{rows}</table></div></section>')
        steps = "".join(
            f'<li{" class=full-only-step" if s["full"] else ""}>{"<span class=mode-tag>Full space</span> " if s["full"] else ""}'
            f'{conv(s["tex"], inline=True)}</li>' for s in c["steps"])
        body = f"""<div class="layout with-outline"><main id="content">
{self.crumbs(root, c["section"], o["slug"], cid)}
<p class="kicker">{KIND[k]} · {"Full space only" if c["full_only"] else "Both modes"}</p>
<h1><span class="id-title">{cid}</span><br>{html.escape(c["title"])}</h1>
<p class="where">Manuscript: Algorithm {cid}, §{o["number"]} {html.escape(o["title"])}, {self.where("component", cid)}.</p>
{banner}
<section class="panel" aria-labelledby="io"><h2 id="io">Input and output</h2>
<p class="kicker">Explicit interface · {html.escape(re.sub(r" interface$", "", c["interface_title"]))}</p>
{manuscript.signature_html(conv, cid, c["signature"]["arguments"], c["signature"]["returns"])}
{conv(c["interface"])}</section>
{modes}
<section class="panel" aria-labelledby="steps"><h2 id="steps">Algorithm</h2>
{conv(c["preamble"])}<ol class="steps">{steps}</ol>{conv(c["after"])}</section>
{self.proof_box(conv, o)}
{self.relationships(root, conv, c)}
</main>{self.outline(root, c["section"], o["slug"], cid)}</div>"""
        return page(f"{cid}: {c['title']}", "guide", body, root=root, math=True)

    def ingredient_link(self, root, name):
        slug = self.by_ingredient_name.get(name.casefold())
        if not slug:
            return html.escape(name)
        return f'<a href="{root}{self.url("section", slug)}">{html.escape(self.sections[slug]["title"])}</a>'

    def relationships(self, root, conv, c):
        cid = c["id"]
        groups = []

        def calls(ids_by_mode, steps_for=None):
            exact, full = ids_by_mode["exact"], ids_by_mode["full"]
            items = []
            for i in list(dict.fromkeys(exact + full)):
                extra = ""
                if steps_for:
                    steps = sorted({x["step"] for x in c["invokes"] if x["callee"] == i and x["step"]})
                    if steps:
                        extra = f' <span class="why">Step{"s" if len(steps) > 1 else ""} {", ".join(map(str, steps))}</span>'
                cls = "" if i in exact and i in full else ("full-only-entry" if i in full else "exact-only")
                line = self.comp_line(root, i, extra)
                if cls:
                    line = line.replace('<li class="', f'<li class="{cls} ', 1)
                    if cls == "full-only-entry" and "mode-tag" not in line:
                        line = line.replace("</li>", " <span class=mode-tag>Full space</span></li>")
                items.append(line)
            return items

        callees = calls(c["callees"], steps_for=True)
        groups.append(("Calls", "Runs another routine at runtime or in the explicit logical reference.", callees))
        callers = calls({m: sorted(self.called_by[m].get(cid, [])) for m in ("exact", "full")})
        groups.append(("Called by", "", callers))
        impl = [r for r in self.data["implements"] if r["source"] == cid]
        impl_by = [r for r in self.data["implements"] if r["target"] == cid]
        groups.append(("Implements", "Realizes a logical result under the stated correspondence.",
                       [self.impl_line(root, conv, r, r["target"]) for r in impl]))
        groups.append(("Implemented by", "", [self.impl_line(root, conv, r, r["source"]) for r in impl_by]))
        o = self.ops[c["operation"]]
        deps = []
        for kind, key in self.proof_refs[o["slug"]]:
            if (kind, key) == ("component", cid):
                continue
            label = key if kind != "operation" else f'§{self.ops[key]["number"]} {self.ops[key]["title"]}'
            title = (self.comps[key]["title"] if kind == "component" else self.defs[key]["title"] if kind == "definition" else "")
            deps.append(f'<li>{self.a(root, kind, key, label)} <span class="t">{html.escape(title)}</span></li>')
        why = f"From the proof note for §{o['number']} (What to prove, above)." if deps else ""
        groups.append(("Depends on for proof", why, deps))
        used = [f'<li><a href="{root}{self.url("operation", s)}#proof-{s}">§{self.ops[s]["number"]} {html.escape(self.ops[s]["title"])}</a></li>'
                for s, targets in self.proof_refs.items() if ("component", cid) in targets and s != o["slug"]]
        groups.append(("Cited by proof notes", "", used))
        defs = [f'<li>{self.a(root, "definition", d)} <span class="t">{html.escape(self.defs[d]["title"])}</span></li>'
                for d in self.def_refs[cid]]
        groups.append(("Uses definitions", "", defs))
        parts = []
        for title, why, items in groups:
            if not items and title not in ("Calls", "Called by"):
                continue
            inner = f'<ul>{"".join(items)}</ul>' if items else '<p class="none">None.</p>'
            parts.append(f'<h3>{title}</h3>{f"<p class=why>{why}</p>" if why else ""}{inner}')
        return f'<section class="panel rel" aria-labelledby="rel"><h2 id="rel">Relationships</h2>{"".join(parts)}</section>'

    def impl_line(self, root, conv, r, other):
        status = f' <span class="tag">{html.escape(r["status"])}</span>' if r.get("status") else ""
        source = r["where"]
        if source["kind"] == "spec":
            loc = "Stated in the website specification"
        else:
            loc = f'Stated in <a href="{root}{self.url(source["kind"], source["key"])}">{html.escape(source["label"])}</a>'
        quote = conv(r["quote"], inline=True)
        return f'<li>{self.a(root, "component", other)} <span class="t">{html.escape(self.comps[other]["title"])}</span>{status}<blockquote>{quote}</blockquote><span class="why">{loc}.</span></li>'

    def operation_page(self, slug):
        root = "../"
        conv = self.converter(root)
        o = self.ops[slug]
        blocks = []
        for b in o["blocks"]:
            if b["type"] == "prose":
                blocks.append(conv(b["tex"]))
            elif b["type"] == "heading":
                blocks.append(f'<h3>{html.escape(b["text"])}</h3>')
            elif b["type"] == "definition":
                d = self.defs[b["id"]]
                blocks.append(f'<article class="panel"><p class="kicker">Definition</p><h3>{self.a(root, "definition", d["id"])} {html.escape(d["title"])}</h3>'
                              f'<p class="where">Full text in the reference area.</p></article>')
            else:
                c = self.comps[b["id"]]
                interface = conv(c["interface"])
                first = interface.split("</p>", 1)[0] + "</p>" if interface.startswith("<p>") else ""
                blocks.append(
                    f'<article class="panel{" full-only-entry" if c["full_only"] else ""}"><p class="kicker">{KIND[kind_of(c)]}'
                    f'{" · <span class=mode-tag>Full space only</span>" if c["full_only"] else ""}</p>'
                    f'<h3>{self.a(root, "component", c["id"])} {html.escape(c["title"])}</h3>'
                    f'{manuscript.signature_html(conv, c["id"], c["signature"]["arguments"], c["signature"]["returns"])}{first}'
                    f'<p><a href="{root}{self.url("component", c["id"])}">Steps and relationships →</a></p></article>')
        full = [b["id"] for b in o["blocks"] if b["type"] == "component" and self.comps[b["id"]]["full_only"]]
        note = (f'<p class="mode-note exact-note">This operation has {len(full)} full-space-only component{"s" if len(full) > 1 else ""}. '
                'Switch to Full space to show them.</p>') if full else ""
        body = f"""<div class="layout with-outline"><main id="content">
{self.crumbs(root, o["section"], slug)}
<p class="kicker">Operation · §{o["number"]}</p><h1>{html.escape(o["title"])}</h1>
<p class="where">Manuscript: §{o["number"]}, {self.where("operation", slug)}.</p>
{note}<section class="panel">{self.comp_groups(root, o)}</section>
{"".join(blocks)}
{self.proof_box(conv, o)}
</main>{self.outline(root, o["section"], slug)}</div>"""
        return page(f"§{o['number']} {o['title']}", "guide", body, root=root, math=True)

    def section_page(self, slug):
        root = "../"
        conv = self.converter(root)
        s = self.sections[slug]
        item = self.ingredient.get(slug)
        big = ""
        if item:
            rel = self.map.get(f'i{item["id"]}', {})
            lists = []
            for label, key in [("Improves", "improves"), ("Introduces or worsens", "worsens"), ("Used by tasks", "tasks")]:
                values = rel.get(key, [])
                lists.append(f'<p class="label">{label}</p><p>{html.escape("; ".join(values)) if values else "None recorded."}</p>')
            big = f"""<section class="panel" aria-labelledby="big"><h2 id="big">The big picture</h2>
<p class="kicker">Map ingredient {item["id"]} · toy API</p><p class="where">{html.escape(item["description"])}</p>
{self.toy_body(item)}{"".join(lists)}
<p><a href="{root}map.html#on={item["id"]}&amp;api={item["id"]}">Show on the map →</a> · <a href="{root}toy_apis.html#ingredient-{item["id"]}">All toy APIs →</a></p></section>"""
        intro = "".join(conv(b["tex"]) for b in s["blocks"] if b["type"] == "prose")
        ops = []
        for op_slug in s["operations"]:
            o = self.ops[op_slug]
            first = next((b for b in o["blocks"] if b["type"] == "prose"), None)
            lead = conv(first["tex"]).split("</p>", 1)[0] + "</p>" if first else ""
            proof = f'<p class="label">What to prove</p>{conv(o["proof"])}' if o["proof"] else ""
            ops.append(f"""<details class="outline" id="op-{op_slug}"><summary>§{o["number"]} {html.escape(o["title"])}</summary>
{lead}{self.comp_groups(root, o)}{proof}<p><a href="{root}{self.url("operation", op_slug)}">Open the operation →</a></p></details>""")
        also = []
        for c in self.data["components"]:
            if c["section"] == slug:
                continue
            for m in c["mode_uses"]:
                if m["ingredient"].casefold() == s["title"].casefold():
                    extra = f' <span class="why">{html.escape(m["mode"])} mode · home: §{self.ops[c["operation"]]["number"]}</span>'
                    line = self.comp_line(root, c["id"], extra)
                    if m["full"] and "full-only-entry" not in line:
                        line = line.replace('<li class="', '<li class="full-only-entry ', 1)
                    also.append(line)
        also_html = (f'<section class="panel"><h2>Also used here</h2><p class="where">Routines whose canonical location is in another '
                     f'section, with a mode that serves this one.</p><ul class="comp-list">{"".join(also)}</ul></section>') if also else ""
        kicker = "Ingredient" if item else "Shared section"
        body = f"""<div class="layout with-outline"><main id="content">
<p class="crumbs"><a href="{root}index.html">Guide</a> › <a href="{root}index.html#ingredients">Ingredients</a></p>
<p class="kicker">{kicker} · §{s["number"]}</p><h1>{html.escape(s["title"])}</h1>
<p class="where">Manuscript: §{s["number"]}, from {self.where("section", slug)}.</p>
{big}{self.physical_note(root, slug)}{intro}
<section class="panel" aria-labelledby="ops"><h2 id="ops">Operations in manuscript order</h2>
<p class="where">Open an operation to see its logical reference and physical queries.</p>
<div class="toolbar-inline"><button type="button" data-expand="#content details.outline" data-open="1">Expand all</button>
<button type="button" data-expand="#content details.outline" data-open="0">Collapse all</button></div>
{"".join(ops)}</section>{also_html}
</main>{self.outline(root, slug)}</div>"""
        return page(f"§{s['number']} {s['title']}", "guide", body, root=root, math=True)

    def reference_page(self):
        root = ""
        conv = self.converter(root)
        groups = []
        for s in self.data["sections"]:
            items = [self.defs[d["id"]] for d in self.data["definitions"] if d["section"] == s["slug"]]
            prose = "".join(conv(b["tex"]) for b in s["blocks"] if b["type"] == "prose") if self.section_kind(s["slug"]) == "reference" else ""
            if not items and not prose:
                continue
            cards = "".join(
                f'<article class="panel" id="{d["id"]}"><p class="kicker">Definition{" · <span class=mode-tag>Full space only</span>" if d["full_only"] else ""}</p>'
                f'<h3><code class="id">{d["id"]}</code> {html.escape(d["title"])}</h3>{conv(d["tex"])}'
                f'<p class="where">Manuscript: §{s["number"]}, {self.where("definition", d["id"])}.</p></article>' for d in items)
            heading = f'§{s["number"]} {html.escape(s["title"])}'
            if s["slug"] == "setup":
                heading = f'§{self.ops["input-target"]["number"]} {html.escape(self.ops["input-target"]["title"])}'
            groups.append(f'<section id="sec-{s["slug"]}"><h2>{heading}</h2>{prose}{cards}</section>')
        toc = "".join(f'<li><a href="#{g.split(chr(34))[1]}">{re.search(r"<h2>(.*?)</h2>", g)[1]}</a></li>' for g in groups)
        body = f"""<main class="page" id="content"><p class="kicker">Reference</p><h1>Finite definitions</h1>
<p>The finite conventions used by the routines, in manuscript order. Each component page links here for the definitions it uses.</p>
<nav aria-label="Reference sections" class="panel"><ul>{toc}</ul></nav>{"".join(groups)}</main>"""
        return page("BPL guide reference", "reference", body, root=root, math=True)

    def home_page(self):
        root = ""
        conv = self.converter(root)
        walk = self.sections["walkthrough"]
        product, order = (self.ops[x] for x in walk["operations"])
        steps = []
        for cid, mode, caption in WALKTHROUGH:
            c, o = self.comps[cid], self.ops[self.comps[cid]["operation"]]
            label = f"{cid} ({mode})" if mode else cid
            show = (f' <button type="button" class="x-show" data-focus="{cid}">Show in the overview</button>'
                    if c["kind"] != "logical" else "")
            steps.append(f'<li><a class="id" href="components/{cid}.html">{label}</a> <span class="t">{html.escape(c["title"])}</span>{show}'
                         f'<span class="why">{html.escape(caption)} §{o["number"]}.</span></li>')
        nxt = " → ".join(f'<a href="{self.url("operation", s)}">§{self.ops[s]["number"]} {html.escape(self.ops[s]["title"])}</a>' for s in WALKTHROUGH_NEXT)
        outline = []
        for s in self.data["sections"]:
            kind = self.section_kind(s["slug"])
            if kind not in ("ingredient", "shared"):
                continue
            item = self.ingredient.get(s["slug"])
            ops = "".join(
                f'<li><a href="{self.url("operation", o)}">§{self.ops[o]["number"]} {html.escape(self.ops[o]["title"])}</a>'
                f'<ul class="comp-list">{"".join(self.comp_line(root, b["id"]) for b in self.ops[o]["blocks"] if b["type"] == "component")}</ul></li>'
                for o in s["operations"])
            tag = f' <span class="tag">Map ingredient {item["id"]}</span>' if item else ' <span class="tag">Shared</span>'
            outline.append((kind, f'<details class="outline" id="outline-{s["slug"]}"><summary>§{s["number"]} {html.escape(s["title"])}{tag}</summary>'
                                  f'<p><a href="{self.url("section", s["slug"])}">Open the {"ingredient" if item else "section"} page →</a></p><ul>{ops}</ul></details>'))
        ingredients = "".join(h for k, h in outline if k == "ingredient")
        shared = "".join(h for k, h in outline if k == "shared")
        toy_problem = conv(TOY_PROBLEM)
        body = f"""<main class="page" id="content">
<p class="kicker">Component guide</p><h1>A component guide to branching-program acceptance</h1>
<p class="where">Logical algorithms and their low-space implementations. A navigation layer for the manuscript; section and page numbers refer to it.</p>
{conv(self.data["front"])}
<section class="panel"><h2>Proof status</h2><p>Both end-to-end space bounds are <strong>conditional</strong> on the open proof obligations.</p>
<ul><li><strong>Exact names</strong>: compares vertex names exactly, using \\(O(\\log n\\log\\log n)\\) work bits. Conditional.</li>
<li><strong>Full space</strong>: the logarithmic-space proposal, using fingerprints at tight space budgets. Conditional.</li></ul>
<p class="where">Use the switch at the top to choose a comparison mode. Throughout the guide, an <em>explicit interface</em> is a component’s stated behavior, and <em>What to prove</em> marks an open proof obligation.</p></section>
<section class="panel"><h2>Start with the big picture</h2><p>The <a href="map.html">map</a> shows how tasks use the ten ingredients and which obstacles each one improves or worsens. The <a href="toy_apis.html">toy APIs</a> state what each ingredient accomplishes. Each ingredient page below joins that picture to its operations and routines.</p></section>
<section class="panel" aria-labelledby="overview-h"><h2 id="overview-h">How the physical algorithm fits together</h2>
<p>The physical algorithm, top-down from the root. The layers and their descriptions are this guide’s summary; the routines and calls come from the manuscript.</p>
{self.explorer(root)}</section>
<section class="panel" id="walkthrough" aria-labelledby="walk-h"><h2 id="walk-h">Worked example: one correction product</h2>
<details class="outline" id="worked-example"><summary>The toy problem from §1, step by step</summary>
<div class="toy-problem"><p class="kicker">The toy problem</p>{toy_problem}</div>
<h3 id="op-{product["slug"]}">§{product["number"]} {html.escape(product["title"])}</h3>
<ol class="steps">{"".join(steps)}</ol><p><strong>Then:</strong> {nxt}.</p>
<details class="outline"><summary>Read §{product["number"]} in full</summary>{"".join(conv(b["tex"]) for b in product["blocks"] if b["type"] == "prose")}</details>
<h3 id="op-{order["slug"]}">§{order["number"]} {html.escape(order["title"])}</h3>{"".join(conv(b["tex"]) for b in order["blocks"] if b["type"] == "prose")}</details></section>
<section class="panel" id="ingredients" aria-labelledby="ing-h"><h2 id="ing-h">Browse ingredients</h2>
<p class="where">In manuscript order. Open an ingredient to see its operations and their routines.</p>
<div class="toolbar-inline"><button type="button" data-expand="#ingredients details.outline" data-open="1">Expand all</button>
<button type="button" data-expand="#ingredients details.outline" data-open="0">Collapse all</button></div>
{ingredients}<h3>Shared setup and assembly</h3>{shared}
<p>The finite definitions are in the <a href="reference.html">reference area</a>.</p></section>
</main>"""
        script = """<script>if(/(^#|&)(on|api)=/.test(location.hash))location.replace('map.html'+location.search+location.hash);</script>"""
        return page("BPL proof ingredients", "guide", script + body, root=root, math=True, extra_scripts=["explorer.js"],
                    description="A component guide to the BPL construction")

    def layer_of(self):
        out = {}
        for key, title, _, groups in LAYERS:
            for gkey, gtitle, ids in groups:
                for i in ids:
                    if i in out or i not in self.comps or self.comps[i]["kind"] == "logical":
                        raise SystemExit(f"build.py: layer table lists {i} twice or as a non-physical routine")
                    out[i] = (key, title, gtitle)
        missing = sorted(i for i, c in self.comps.items() if c["kind"] != "logical" and i not in out)
        if missing:
            raise SystemExit(f"build.py: physical routines missing from the layer table: {missing}")
        return out

    def example_ids(self):
        """Physical routines named in §1.1, the worked example."""
        o = self.ops[self.sections["walkthrough"]["operations"][0]]
        tex = " ".join(b["tex"] for b in o["blocks"] if b["type"] == "prose")
        return [i for i in dict.fromkeys(re.findall(r"\\Aref\{([^}]+)\}", tex)) if self.comps[i]["kind"] != "logical"]

    def explorer(self, root):
        """Data, panel templates and markup for the interactive overview of the physical algorithm."""
        conv = self.converter(root)
        layers = self.layer_of()
        example = set(self.example_ids())
        nodes, templates = [], []
        for c in self.data["components"]:
            if c["kind"] == "logical":
                continue
            o = self.ops[c["operation"]]
            nodes.append(dict(id=c["id"], title=c["title"], layer=layers[c["id"]][0], full=c["full_only"],
                              example=c["id"] in example, url=self.url("component", c["id"])))
            interface = conv(c["interface"])
            first = interface.split("</p>", 1)[0] + "</p>" if interface.startswith("<p>") else ""
            where = f'{KIND[kind_of(c)]} · §{o["number"]} {html.escape(o["title"])}'
            templates.append(
                f'<template id="x-tpl-{c["id"]}"><p class="kicker">{where}{" · <span class=mode-tag>Full space only</span>" if c["full_only"] else ""}</p>'
                f'<h3><a href="{root}{self.url("component", c["id"])}">{c["id"]}</a> {html.escape(c["title"])}</h3>'
                f'{manuscript.signature_html(conv, c["id"], c["signature"]["arguments"], c["signature"]["returns"])}{first}</template>')
        edges = {}
        for c in self.data["components"]:
            if c["kind"] == "logical":
                continue
            for mode in ("exact", "full"):
                for callee in c["callees"][mode]:
                    e = edges.setdefault((c["id"], callee), dict(s=c["id"], t=callee, modes=[], steps=[], kind=""))
                    if mode not in e["modes"]:
                        e["modes"].append(mode)
            for inv in c["invokes"]:
                e = edges[(c["id"], inv["callee"])]
                if inv["step"] and inv["step"] not in e["steps"]:
                    e["steps"].append(inv["step"])
                k = edge_kind(inv["callee"], inv["arguments"])
                if k and not e["kind"]:
                    e["kind"] = k
        layer_data = [dict(key=k, title=t, desc=d, groups=[dict(key=gk or k, title=gt, ids=ids) for gk, gt, ids in g])
                      for k, t, d, g in LAYERS]
        payload = json.dumps(dict(nodes=nodes, edges=list(edges.values()), layers=layer_data, kinds=EDGE_KINDS),
                             ensure_ascii=False).replace("<", "\\u003c")
        return f"""<div class="explorer" id="explorer">
<div class="x-bar"><nav class="x-crumbs" id="x-crumbs" aria-label="Path through the call tree"></nav>
<label class="x-example"><input type="checkbox" id="x-example"> Mark the worked example</label></div>
<div class="x-body"><div class="x-stage" id="x-stage" aria-hidden="true"><svg class="x-lines" aria-hidden="true"></svg></div>
<aside class="x-panel" id="x-panel" aria-live="polite"></aside></div>
<p class="where">Click a routine to centre it: callers on the left, the routines it calls on the right, in step order. Labels mark calls to a
<strong>smaller budget</strong> (the recursion), to the <strong>previous slack level</strong> of the same task, and to its <strong>completed raw row</strong>.
Infrastructure calls are grouped; click a group to expand it. The panel lists the same links for keyboard use.</p>
<script type="application/json" id="explorer-data">{payload}</script>{"".join(templates)}</div>"""

    def physical_note(self, root, slug):
        """Where an ingredient's routines sit in the physical algorithm."""
        layers = self.layer_of()
        ids = [c["id"] for c in self.data["components"] if c["section"] == slug and c["kind"] != "logical"]
        if not ids:
            conv = self.converter(root)
            note = conv(re.sub(r"\b(D-ROWFAMILIES|D-CHILD)\b", r"\\Dref{\1}", re.sub(r"\b(P-CHILD|P-INTRINSICVALUE)\b", r"\\Aref{\1}", NO_PHYSICAL)))
            return f'<section class="panel"><h2>In the physical algorithm</h2>{note}</section>'
        items = "".join(
            f'<li class="{"full-only-entry" if self.comps[i]["full_only"] else ""}">{self.a(root, "component", i)} '
            f'<span class="t">{html.escape(self.comps[i]["title"])}</span><span class="why">{html.escape(layers[i][1])}'
            f'{" · " + html.escape(layers[i][2]) if layers[i][2] else ""} · <a href="{root}index.html#focus={i}">show in the overview</a></span></li>'
            for i in ids)
        return (f'<section class="panel"><h2>In the physical algorithm</h2><p class="where">Where this section’s physical routines sit '
                f'in the top-down overview on the home page.</p><ul class="comp-list">{items}</ul></section>')

    def search_index(self):
        entries = [dict(k="Page", i="Map", t="Map", u="map.html"), dict(k="Page", i="Toy APIs", t="Toy APIs", u="toy_apis.html")]
        for s in self.data["sections"]:
            kind = self.section_kind(s["slug"])
            entries.append(dict(k="Ingredient" if kind == "ingredient" else "Section", i=f'§{s["number"]}', t=s["title"], u=self.url("section", s["slug"])))
        for o in self.data["operations"]:
            entries.append(dict(k="Operation", i=f'§{o["number"]}', t=o["title"], u=self.url("operation", o["slug"])))
        for c in self.data["components"]:
            entries.append(dict(k=KIND[kind_of(c)], i=c["id"], t=c["title"], u=self.url("component", c["id"]), f=c["full_only"]))
        for d in self.data["definitions"]:
            entries.append(dict(k="Definition", i=d["id"], t=d["title"], u=self.url("definition", d["id"]), f=d["full_only"]))
        return entries


def proof_targets(tex):
    out = []
    for m in re.finditer(r"\\(Aref|Dref|ref)\{([^}]+)\}", tex):
        if m[1] == "Aref":
            out.append(("component", m[2]))
        elif m[1] == "Dref":
            out.append(("definition", m[2]))
        else:
            kind, key = m[2].split(":", 1)
            out.append(("operation" if kind == "op" else "section", key))
    return list(dict.fromkeys(out))


def map_relations(svg_text):
    root = ET.fromstring(svg_text)
    ns = "{http://www.w3.org/2000/svg}"
    labels = {}
    for el in root.iter():
        if "data-node" in el.attrib:
            title = el.find(f"{ns}title")
            labels[el.attrib["data-node"]] = title.text if title is not None else el.attrib["data-node"]
    out = {}
    for el in root.iter():
        if el.attrib.get("data-edge") == "true":
            s, t, sign = el.attrib["data-source"], el.attrib["data-target"], el.attrib["data-sign"]
            if sign == "uses":
                out.setdefault(t, {}).setdefault("tasks", []).append(labels[s])
            else:
                out.setdefault(s, {}).setdefault(sign, []).append(labels[t])
    return out
