"""Read the Run 08 component guide (main.tex) into plain data, and convert its TeX to HTML.

parse() turns the manuscript's declarations (GuideSection, Operation, Component,
DefinitionAnchor, ProofWork, the interface definitions and the algorithm boxes)
into a dictionary that build.py saves as bpl/data/guide.json. The TeX fragments
are kept verbatim there; to_html() converts them when the pages are built.
"""

import html
import re


class TexError(Exception):
    pass


def read_group(s, i, open_="{", close="}"):
    """Return (content, index after the closing brace) for the group starting at s[i] (after spaces)."""
    while i < len(s) and s[i] in " \t\n":
        i += 1
    if i >= len(s) or s[i] != open_:
        raise TexError(f"expected {open_!r} at …{s[i:i+60]!r}")
    depth, j = 0, i
    while j < len(s):
        c = s[j]
        if c == "\\":
            j += 2
            continue
        if c == "%":
            j = s.find("\n", j)
            j = len(s) if j < 0 else j
            continue
        if c == open_ or (open_ == "[" and c == "{"):
            depth += 1 if c == open_ else 0
            if c == "{" and open_ == "[":
                _, j = read_group(s, j)
                continue
        elif c == close:
            depth -= 1
            if depth == 0:
                return s[i+1:j], j+1
        j += 1
    raise TexError(f"unbalanced {open_!r} starting …{s[i:i+60]!r}")


def read_args(s, i, n):
    args = []
    for _ in range(n):
        arg, i = read_group(s, i)
        args.append(arg)
    return args, i


def environment(s, i, name):
    """With s[i:] starting at \\begin{name}, return (body, index after \\end{name})."""
    begin, end = f"\\begin{{{name}}}", f"\\end{{{name}}}"
    assert s.startswith(begin, i), s[i:i+40]
    depth, j = 0, i
    while True:
        b, e = s.find(begin, j), s.find(end, j)
        if e < 0:
            raise TexError(f"unterminated {name} at …{s[i:i+60]!r}")
        if 0 <= b < e:
            depth, j = depth+1, b+len(begin)
        else:
            depth, j = depth-1, e+len(end)
            if depth == 0:
                return s[i+len(begin):e], j


def strip_comments(tex):
    return re.sub(r"(?<!\\)%[^\n]*", "", tex)


def first_command(s, names, start=0):
    """Index and name of the next \\name (whole word) among names, or (-1, None)."""
    pattern = re.compile(r"\\(" + "|".join(re.escape(n) for n in names) + r")(?![A-Za-z])")
    m = pattern.search(s, start)
    return (m.start(), m[1]) if m else (-1, None)


# ---------------------------------------------------------------- structure

# Passages that point to other Run 08 versions are left out of the site. Each must match exactly once,
# so a change to the manuscript stops the build instead of silently publishing or dropping text.
EXCLUDED = [
    r"Revision 02 derives a gap for the finite action under the stated Shalom contracts\. ",
    r"Revision 02 gives the two conditional assembly deductions\. ",
    r"The two conditional assembly deductions in revision 02 isolate these premises\. ",
    r"The pseudocode and parameters follow \\href\{[^{}]*\}\{Run 08 revision 02\}\..*?\}\{project ingredient map\}\.\s*",
]


def exclude(tex):
    for pattern in EXCLUDED:
        regex = re.compile(pattern.replace(" ", r"\s+"), re.S)
        if len(regex.findall(tex)) != 1:
            raise TexError(f"excluded passage not found exactly once: {pattern[:60]!r}")
        tex = regex.sub("", tex)
    return tex


def parse(tex):
    tex = exclude(strip_comments(tex))
    body = tex.split("\\begin{document}", 1)[1].split("\\end{document}", 1)[0]
    front_end = body.find("\\GuideSection")
    front = body[:front_end]
    front = front[front.find("\\end{center}") + len("\\end{center}"):].strip()
    data = dict(front=front, sections=[], operations=[], components=[], definitions=[])
    numbers = dict(section=0, appendix=None)
    section = operation = None
    i = front_end
    markers = ["GuideSection", "Operation", "Component", "DefinitionAnchor", "ProofWork",
               "appendix", "subsubsection", "clearpage", "tableofcontents"]

    def add_prose(text):
        text = text.strip()
        if not text:
            return
        target = operation["blocks"] if operation else section["blocks"]
        target.append(dict(type="prose", tex=text))

    while True:
        j, name = first_command(body, markers, i)
        add_prose(body[i:j] if j >= 0 else body[i:])
        if j < 0:
            break
        k = j + len(name) + 1
        if name == "appendix":
            numbers["appendix"] = 0
            i = k
        elif name in ("clearpage", "tableofcontents"):
            i = k
        elif name == "GuideSection":
            (slug, title), i = read_args(body, k, 2)
            if numbers["appendix"] is None:
                numbers["section"] += 1
                number = str(numbers["section"])
            else:
                number = "ABCDEFGHIJ"[numbers["appendix"]]
                numbers["appendix"] += 1
            section = dict(slug=slug, title=title, number=number, appendix=numbers["appendix"] is not None,
                           blocks=[], operations=[])
            data["sections"].append(section)
            operation = None
        elif name == "Operation":
            (slug, title), i = read_args(body, k, 2)
            operation = dict(slug=slug, title=title, section=section["slug"],
                             number=f'{section["number"]}.{len(section["operations"])+1}', blocks=[], proof=None)
            section["operations"].append(slug)
            data["operations"].append(operation)
        elif name == "subsubsection":
            if body.startswith("*", k):
                k += 1
            (title,), i = read_args(body, k, 1)
            (operation or section)["blocks"].append(dict(type="heading", text=title))
        elif name == "ProofWork":
            (proof,), i = read_args(body, k, 1)
            if operation is None or operation["proof"] is not None:
                raise TexError(f"unexpected ProofWork near …{body[j:j+80]!r}")
            operation["proof"] = proof.strip()
        elif name == "DefinitionAnchor":
            (ident,), i = read_args(body, k, 1)
            i = skip_space(body, i)
            definition, i = parse_definition(body, i)
            if definition["id"] != ident:
                raise TexError(f"anchor {ident} precedes definition {definition['id']}")
            definition.update(section=section["slug"], operation=operation["slug"] if operation else None)
            data["definitions"].append(definition)
            (operation or section)["blocks"].append(dict(type="definition", id=ident))
        elif name == "Component":
            (ident, kind), i = read_args(body, k, 2)
            component, i = parse_component(body, skip_space(body, i), ident, kind)
            component.update(section=section["slug"], operation=operation["slug"] if operation else None)
            data["components"].append(component)
            (operation or section)["blocks"].append(dict(type="component", id=ident))
    return data


def skip_space(s, i):
    while i < len(s) and s[i] in " \t\n":
        i += 1
    return i


def parse_definition(s, i):
    body, i = environment(s, i, "definition")
    title_tex, rest = read_group(body, 0, "[", "]")
    m = re.match(r"\s*\\id\{([^}]+)\}\s*---\s*(.*)$", title_tex, re.S)
    if not m:
        raise TexError(f"definition title {title_tex!r}")
    rest_tex = body[rest:]
    full_only = "\\FullOnly" in rest_tex
    rest_tex = rest_tex.replace("\\FullOnly", "")
    return dict(id=m[1], title=m[2].strip(), tex=rest_tex.strip(), full_only=full_only), i


def take(pattern, tex):
    """Remove every match of a macro with brace arguments; return (matches, remaining tex)."""
    found, out, i = [], [], 0
    name, nargs = pattern
    while True:
        j, _ = first_command(tex, [name], i)
        if j < 0:
            out.append(tex[i:])
            break
        args, k = read_args(tex, j+len(name)+1, nargs)
        found.append((j, args))
        out.append(tex[i:j])
        i = k
    return found, "".join(out)


def parse_component(s, i, ident, kind):
    if not s.startswith("\\begin{definition}", i):
        raise TexError(f"{ident}: interface definition expected")
    interface, i = parse_definition(s, i)
    if interface["id"] != f"D-API-{ident}":
        raise TexError(f"{ident}: interface is {interface['id']}")
    itex = re.sub(r"\\label\{[^}]*\}", "", interface["tex"])
    # \Lpart{\ModeUse{...}} marks a full-space-only mode; record it, then drop both wrappers.
    mode_uses = []
    for m in re.finditer(r"\\Lpart\{\\ModeUse\{[^}]*\}\{([^}]*)\}\{([^}]*)\}\{([^}]*)\}\}", itex):
        mode_uses.append(dict(mode=m[1], use=m[2], ingredient=m[3], full=True))
    itex = re.sub(r"\\Lpart\{(\\ModeUse\{[^}]*\}\{[^}]*\}\{[^}]*\}\{[^}]*\})\}", "", itex)
    uses, itex = take(("ModeUse", 4), itex)
    mode_uses = [dict(mode=a[1], use=a[2], ingredient=a[3], full=False) for _, a in uses] + mode_uses
    sigs, itex = take(("Signature", 3), itex)
    if len(sigs) != 1 or sigs[0][1][0] != ident:
        raise TexError(f"{ident}: expected one signature")
    signature = dict(arguments=sigs[0][1][1], returns=sigs[0][1][2])

    if not s.startswith("\\begin{algorithm}", skip_space(s, i)):
        raise TexError(f"{ident}: algorithm expected")
    abody, i = environment(s, skip_space(s, i), "algorithm")
    (aid, title), k = read_args(abody, 0, 2)
    if aid != ident:
        raise TexError(f"algorithm {aid} follows component {ident}")
    abody = abody[k:]
    full_only = interface["full_only"] or "\\FullOnly" in abody
    abody = abody.replace("\\FullOnly", "")
    abody = re.sub(r"\\label\{[^}]*\}", "", abody)
    meta, abody = take(("ProcMeta", 3), abody)
    if len(meta) != 1 or meta[0][1][0] != ident or meta[0][1][1] != kind:
        raise TexError(f"{ident}: ProcMeta mismatch")
    declared = [x.strip() for x in meta[0][1][2].split(",") if x.strip()]
    deps, abody = take(("ModeDeps", 3), abody)
    mode_deps = {a[1]: [x.strip() for x in a[2].split(",") if x.strip()] for _, a in deps}
    begin, end = f"\\BeginCode{{{ident}}}", f"\\EndCode{{{ident}}}"
    if abody.count(begin) != 1 or abody.count(end) != 1:
        raise TexError(f"{ident}: BeginCode/EndCode")
    before, rest = abody.split(begin)
    code, after = rest.split(end)
    code = code.strip()
    if not code.startswith("\\begin{enumerate}"):
        raise TexError(f"{ident}: steps must be one enumerate")
    items_tex, k = environment(code, 0, "enumerate")
    if code[k:].strip():
        raise TexError(f"{ident}: text after the steps")
    steps = split_items(items_tex)
    invokes = []
    for n, step in enumerate(steps, 1):
        for full, m in iter_invokes(step["tex"]):
            invokes.append(dict(callee=m[0], arguments=m[1], binds=m[2], step=n, full=full or step["full"]))
    for full, m in iter_invokes(before):
        invokes.append(dict(callee=m[0], arguments=m[1], binds=m[2], step=None, full=full))
    if mode_deps:
        callees = dict(exact=mode_deps.get("exact", []), full=mode_deps.get("full", []))
        if sorted(set(callees["exact"]) | set(callees["full"])) != sorted(set(declared)):
            raise TexError(f"{ident}: ModeDeps disagree with ProcMeta")
    else:
        callees = dict(exact=list(declared), full=list(declared))
    invoked = {x["callee"] for x in invokes}
    if invoked - set(declared):
        raise TexError(f"{ident}: invokes {sorted(invoked - set(declared))} outside its declared callees")
    return dict(id=ident, kind=kind, title=title.strip(), interface_title=interface["title"],
                interface=itex.strip(), signature=signature, mode_uses=mode_uses, full_only=full_only,
                preamble=before.strip(), steps=steps, after=after.strip(), callees=callees,
                declared_callees=declared, invokes=invokes), i


def iter_invokes(tex):
    """Yield (inside a full-space part, (callee, arguments, binds)) for each \\Invoke in tex."""
    full_spans = []
    for j, _ in iter_commands(tex, "Lpart"):
        arg, k = read_group(tex, j+len("\\Lpart"))
        full_spans.append((j, k))
    i = 0
    while True:
        j, _ = first_command(tex, ["Invoke"], i)
        if j < 0:
            return
        args, i = read_args(tex, j+len("\\Invoke"), 3)
        yield any(a <= j < b for a, b in full_spans), args


def iter_commands(tex, name):
    i = 0
    while True:
        j, _ = first_command(tex, [name], i)
        if j < 0:
            return
        yield j, name
        i = j + 1


def split_items(tex):
    """Split an enumerate body at top-level \\item; Lonly items are marked full-space only."""
    tex = re.sub(r"\\begin\{Lonly\}\s*\\item", r"\\item\\LONLYITEM ", tex).replace("\\end{Lonly}", "")
    items, depth, i, start = [], 0, 0, None
    while i < len(tex):
        if tex.startswith("\\begin{", i):
            depth += 1
        elif tex.startswith("\\end{", i):
            depth -= 1
        elif depth == 0 and re.match(r"\\item(?![A-Za-z])", tex[i:]):
            if start is not None:
                items.append(tex[start:i])
            start = i + len("\\item")
        i += 1
    if start is not None:
        items.append(tex[start:])
    out = []
    for item in items:
        item = item.strip()
        full = item.startswith("\\LONLYITEM")
        out.append(dict(tex=item.replace("\\LONLYITEM", "").strip(), full=full))
    return out


# ---------------------------------------------------------------- TeX to HTML

SIMPLE = {"textbf": ("<strong>", "</strong>"), "textit": ("<em>", "</em>"), "emph": ("<em>", "</em>"),
          "texttt": ("<code>", "</code>"), "textsf": ('<span class="sf">', "</span>"),
          "Call": ('<span class="sf">', "</span>")}
DROP0 = {"par", "smallskip", "medskip", "bigskip", "noindent", "allowbreak", "clearpage", "phantomsection",
         "toprule", "midrule", "bottomrule", "endhead", "hline", "centering", "FullOnly", "tableofcontents"}
DROP1 = {"label", "hypertarget", "Needspace"}
SYMBOLS = {"%": "%", "&": "&amp;", "_": "_", "{": "{", "}": "}", "#": "#", "$": "$", ",": "\u2009",
           ";": " ", " ": " ", "!": "", "-": ""}
TEXT_MACROS = {"textquotesingle": "\u2019", "ldots": "…", "dots": "…", "S": "§"}


class Converter:
    """Convert manuscript TeX to HTML. links(kind, key) returns an href or None."""

    def __init__(self, links, refs):
        self.links, self.refs = links, refs

    def __call__(self, tex, inline=False):
        out = self.blocks(tex)
        if inline:
            if len(out) > 1 or (out and not out[0].startswith("<p>")):
                return "".join(out)
            return out[0][3:-4] if out else ""
        return "".join(out)

    # Paragraph assembly: inline pieces gather into a paragraph; blocks flush it.
    def blocks(self, tex):
        result, para = [], []

        def flush():
            text = "".join(para).strip()
            if text:
                result.append(f"<p>{text}</p>")
            para.clear()

        for kind, piece in self.pieces(tex):
            if kind == "break":
                flush()
            elif kind == "block":
                flush()
                result.append(piece)
            else:
                para.append(piece)
        flush()
        return result

    def pieces(self, s):
        i, n = 0, len(s)
        text = []

        def emit_text():
            if text:
                yield_list.append(("inline", self.text("".join(text))))
                text.clear()

        yield_list = []
        while i < n:
            c = s[i]
            if s.startswith("\n\n", i) or (c == "\n" and s[i+1:i+2].strip() == "" and "\n" in s[i+1:i+3]):
                emit_text()
                yield_list.append(("break", ""))
                i = skip_space(s, i)
                continue
            if s.startswith("\\(", i):
                j = s.find("\\)", i)
                emit_text()
                yield_list.append(("inline", self.math(s[i+2:j])))
                i = j + 2
            elif s.startswith("\\[", i):
                j = s.find("\\]", i)
                emit_text()
                yield_list.append(("block", self.math(s[i+2:j], display=True)))
                i = j + 2
            elif s.startswith("$$", i):
                j = s.find("$$", i+2)
                emit_text()
                yield_list.append(("block", self.math(s[i+2:j], display=True)))
                i = j + 2
            elif c == "$":
                j = i + 1
                while s[j] != "$" or s[j-1] == "\\":
                    j += 1
                emit_text()
                yield_list.append(("inline", self.math(s[i+1:j])))
                i = j + 1
            elif s.startswith("\\begin{", i):
                name = s[i+7:s.find("}", i)]
                body, j = environment(s, i, name)
                emit_text()
                yield_list.extend(self.env(name, body))
                i = j
            elif c == "\\":
                m = re.match(r"\\([A-Za-z]+|.)", s[i:])
                name = m[1]
                i += len(m[0])
                if name == "\\":
                    emit_text()
                    yield_list.append(("inline", "<br>"))
                    continue
                if name in SYMBOLS:
                    text.append("\x00" + SYMBOLS[name] + "\x01")
                    continue
                emit_text()
                piece, i = self.command(name, s, i)
                yield_list.extend(piece)
            elif c == "{":
                arg, i = read_group(s, i)
                emit_text()
                yield_list.extend(self.pieces(arg))
            elif c == "~":
                text.append("\x00\u00a0\x01")
                i += 1
            else:
                text.append(c)
                i += 1
        emit_text()
        return yield_list

    def text(self, raw):
        # \x00 … \x01 protects characters produced by escapes from further processing.
        parts = re.split(r"\x00(.*?)\x01", raw, flags=re.S)
        out = []
        for j, part in enumerate(parts):
            if j % 2:
                out.append(part if part == "&amp;" else html.escape(part))
                continue
            part = re.sub(r"\s+", " ", part)
            part = part.replace("---", "—").replace("--", "–").replace("``", "“").replace("''", "”")
            part = part.replace("`", "‘")
            out.append(self.autolink(html.escape(part, quote=False)))
        return "".join(out)

    def autolink(self, text):
        def repl(m):
            href = self.links("id", m[0])
            return f'<a class="id" href="{href}">{m[0]}</a>' if href else m[0]
        return re.sub(r"(?<![\w-])(?:D-API-)?[LPTD]-[A-Z0-9]+(?:-[A-Z0-9]+)*(?![\w-])", repl, text)

    def math(self, tex, display=False):
        if re.search(r"\\(Aref|Dref|Invoke|id|Lpart)\b", tex):
            raise TexError(f"guide macro inside math: {tex[:80]!r}")
        tex = html.escape(tex.strip(), quote=False)
        return f'<div class="math">\\[{tex}\\]</div>' if display else f"\\({tex}\\)"

    def link(self, kind, key, label):
        href = self.links(kind, key)
        if not href:
            raise TexError(f"no page for {kind} {key}")
        return f'<a class="id" href="{href}">{label}</a>'

    def command(self, name, s, i):
        if name in SIMPLE:
            (arg,), i = read_args(s, i, 1)
            a, b = SIMPLE[name]
            return [("inline", a + self(arg, inline=True) + b)], i
        if name in DROP0:
            if name == "par":
                return [("break", "")], i
            return [], i
        if name in DROP1:
            _, i = read_args(s, i, 2 if name == "hypertarget" else 1)
            return [], i
        if name in TEXT_MACROS:
            if s.startswith("{}", i):
                i += 2
            return [("inline", TEXT_MACROS[name])], i
        if name == "id":
            (arg,), i = read_args(s, i, 1)
            href = self.links("id", arg)
            label = html.escape(arg)
            return [("inline", f'<a class="id" href="{href}">{label}</a>' if href else f'<code class="id">{label}</code>')], i
        if name == "Aref":
            (arg,), i = read_args(s, i, 1)
            return [("inline", self.link("component", arg, html.escape(arg)))], i
        if name == "Dref":
            (arg,), i = read_args(s, i, 1)
            return [("inline", self.link("definition", arg, html.escape(arg)))], i
        if name == "Invoke":
            (callee, args, binds), i = read_args(s, i, 3)
            return [("inline", f'<span class="invoke">{self.math("(" + binds + ")" + chr(92) + "gets")} '
                     f'{self.link("component", callee, html.escape(callee))}{self.math("(" + args + ")")}</span>')], i
        if name == "Need":
            (a, b, c), i = read_args(s, i, 3)
            return [("inline", self.math(f"{c}\\gets\\mathrm{{REQUEST}}({a},{b})"))], i
        if name == "Signature":
            (ident, args, rets), i = read_args(s, i, 3)
            return [("inline", signature_html(self, ident, args, rets))], i
        if name == "Lpart":
            (arg,), i = read_args(s, i, 1)
            return [("inline", f'<span class="full-part"><span class="mode-tag">Full space</span> {self(arg, inline=True)}</span>')], i
        if name == "ref":
            (arg,), i = read_args(s, i, 1)
            kind, key = arg.split(":", 1)
            number, href = self.refs(kind, key)
            return [("inline", f'<a href="{href}">{number}</a>')], i
        if name == "href":
            (url, label), i = read_args(s, i, 2)
            href = self.links("url", url)
            inner = self(label, inline=True)
            return [("inline", f'<a href="{href}">{inner}</a>' if href else inner)], i
        if name == "paragraph":
            (arg,), i = read_args(s, i, 1)
            return [("break", ""), ("inline", f"<strong>{self(arg, inline=True)}</strong> ")], i
        if name == "LONLYITEM":
            return [], i
        raise TexError(f"unsupported command \\{name} near …{s[max(0, i-40):i+40]!r}")

    def env(self, name, body):
        if name == "enumerate":
            body = re.sub(r"^\s*\[[^\]]*\]", "", body)
            items = "".join(f"<li{' class=\"full-only-step\"' if it['full'] else ''}>"
                            f"{'<span class=\"mode-tag\">Full space</span> ' if it['full'] else ''}"
                            f"{self(it['tex'], inline=True)}</li>" for it in split_items(body))
            return [("block", f"<ol>{items}</ol>")]
        if name == "center":
            return [("block", self(body))]
        if name in ("tabular", "tabularx", "longtable"):
            _, k = read_group(body, 0)
            if name == "tabularx":
                _, k = read_group(body, k)
            return [("block", self.table(body[k:]))]
        if name in ("align*",):
            return [("block", f'<div class="math">\\[\\begin{{aligned}}{html.escape(body.strip(), quote=False)}\\end{{aligned}}\\]</div>')]
        if name == "Lonly":
            return [("inline", f'<span class="full-part"><span class="mode-tag">Full space</span> {self(body, inline=True)}</span>')]
        raise TexError(f"unsupported environment {name}")

    def table(self, body):
        head = None
        if "\\midrule" in body:
            head, body = body.split("\\midrule", 1)
        rows = []
        for part, tag in ([(head, "th")] if head else []) + [(body, "td")]:
            for row in split_top(part, "\\\\"):
                row = re.sub(r"\\(toprule|bottomrule|endhead|hline)", "", row).strip()
                if not row:
                    continue
                cells = "".join(f"<{tag}>{self(c.strip(), inline=True)}</{tag}>" for c in split_top(row, "&"))
                rows.append(f"<tr>{cells}</tr>")
        return f'<div class="table-wrap"><table>{"".join(rows)}</table></div>'


def split_top(s, sep):
    """Split s at sep outside braces and math."""
    parts, depth, i, start, math = [], 0, 0, 0, False
    while i < len(s):
        c = s[i]
        if s.startswith("\\(", i) or s.startswith("\\)", i):
            math = s.startswith("\\(", i)
            i += 2
            continue
        if c == "\\" and not s.startswith(sep, i):
            i += 2
            continue
        if c == "$":
            math = not math
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        elif depth == 0 and not math and s.startswith(sep, i):
            parts.append(s[start:i])
            i += len(sep)
            start = i
            continue
        i += 1
    parts.append(s[start:])
    return parts


def signature_html(convert, ident, args, rets):
    return (f'<span class="signature">{convert.math(chr(92) + "Call{" + ident + "}(" + args + ")" + chr(92) + "longrightarrow(" + rets + ")")}</span>')
