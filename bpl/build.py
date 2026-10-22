#!/usr/bin/env python3
"""Build the unlisted BPL proof-ingredients pages in docs/bpl_proof_ingredients/.

    python3 bpl/build.py --harness ../tcs-harness   # refresh bpl/data/ from tcs-harness, then build
    python3 bpl/build.py                            # rebuild the pages from bpl/data/ alone

The toy APIs are parsed from the "Toy APIs" section of
projects/bpl_rewrite/ingredients_obstacles_dependencies.md in tcs-harness; edit
them there, in that Markdown format, rather than in bpl/data/toy_apis.json.
The map is the SVG that tcs-harness's render.py generates. Python 3 only.
"""

import argparse
import html
import json
from pathlib import Path
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "bpl" / "data"
OUT = ROOT / "docs" / "bpl_proof_ingredients"
REDIRECT = ROOT / "docs" / "bpl_proof_ingredients.html"
MAP_DIR = Path("projects/bpl_rewrite")
MARKDOWN = MAP_DIR / "ingredients_obstacles_dependencies.md"
GRAPH = MAP_DIR / "ingredient_map" / "graph.json"
SVG = MAP_DIR / "ingredient_map" / "ingredients_obstacles.svg"
REQUIRED = ["Input", "Output", "Upstream purpose", "Approach"]


def fail(message):
    raise SystemExit(f"build.py: {message}")


def parse_toy_apis(markdown):
    """Return the intro paragraphs and one {id, name, fields, notes} entry per ingredient."""
    lines = markdown.splitlines()
    start = next((j for j, line in enumerate(lines) if re.match(r"## Toy APIs\b", line, re.I)), None)
    if start is None:
        fail(f"no '## Toy APIs' section in {MARKDOWN}")
    end = next((j for j in range(start+1, len(lines)) if lines[j].startswith("## ")), len(lines))
    intro, sections, current, block = [], [], None, None
    for line in lines[start+1:end]:
        heading = re.match(r"### (\d+)\. (.+)$", line)
        if heading:
            current = dict(id=int(heading[1]), name=heading[2].strip(), fields=[], notes=[])
            sections.append(current)
            block = None
            continue
        if line.startswith("#"):
            fail(f"unexpected heading in the toy API section: {line!r}")
        field = re.match(r"- \*\*(.+?):\*\*\s*(.*)$", line)
        if not line.strip():
            block = None
        elif field:
            if current is None:
                fail(f"toy API field before the first ingredient heading: {line!r}")
            current["fields"].append(dict(label=field[1], text=field[2].strip()))
            block = "field"
        elif re.match(r"\s*([-*+]|\d+\.)\s", line) and block != "field":
            fail(f"unsupported list item in the toy API section: {line!r}")
        elif block == "field":
            # Indented or lazy continuation of the current bullet.
            current["fields"][-1]["text"] += " " + line.strip()
        else:
            paragraphs = intro if current is None else current["notes"]
            if block == "para":
                paragraphs[-1] += " " + line.strip()
            else:
                paragraphs.append(line.strip())
            block = "para"
    return intro, sections


def refresh(harness):
    """Copy the map SVG and convert the toy APIs to JSON, checking them against graph.json."""
    for path in [MARKDOWN, GRAPH, SVG]:
        if not (harness / path).is_file():
            fail(f"missing {harness / path}; pass the tcs-harness checkout with --harness")
    graph = json.loads((harness / GRAPH).read_text(encoding="utf-8"))
    names = {x["id"]: x["name"] for x in graph["ingredients"]}
    descriptions = {x["id"]: x["description"] for x in graph["ingredients"]}
    intro, sections = parse_toy_apis((harness / MARKDOWN).read_text(encoding="utf-8"))
    ids = [s["id"] for s in sections]
    if sorted(ids) != sorted(names) or len(set(ids)) != len(ids):
        fail(f"toy API headings cover ingredients {ids}; graph.json has {sorted(names)}")
    for section in sections:
        if section["name"] != names[section["id"]]:
            fail(f'toy API {section["id"]} is named {section["name"]!r}; graph.json says {names[section["id"]]!r}')
        labels = [f["label"] for f in section["fields"]]
        missing = [label for label in REQUIRED if label not in labels]
        if missing or len(set(labels)) != len(labels):
            fail(f'toy API {section["id"]} has fields {labels}; it needs each of {REQUIRED} once')
        section["description"] = descriptions[section["id"]]
    try:
        commit = subprocess.run(["git", "-C", str(harness), "rev-parse", "HEAD"], check=True,
                                capture_output=True, text=True).stdout.strip()
        dirty = subprocess.run(["git", "-C", str(harness), "status", "--porcelain", "--",
                                str(MARKDOWN), str(GRAPH), str(SVG)],
                               check=True, capture_output=True, text=True).stdout.strip()
        commit += " (with uncommitted changes)" if dirty else ""
    except (OSError, subprocess.CalledProcessError):
        commit = "unknown"
    data = dict(source=dict(repository="tcs-harness", commit=commit, markdown=str(MARKDOWN),
                            graph=str(GRAPH), svg=str(SVG)),
                intro=intro, ingredients=sorted(sections, key=lambda s: s["id"]))
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / "toy_apis.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    shutil.copyfile(harness / SVG, DATA / "ingredients_obstacles.svg")
    return commit


def inline(text):
    """Render the inline Markdown used in the toy APIs: code, bold, italics, links, and "Toy:"."""
    parts = re.split(r"(`[^`]+`)", text)
    out = []
    for j, part in enumerate(parts):
        if j % 2:
            out.append(f"<code>{html.escape(part[1:-1])}</code>")
            continue
        s = html.escape(part, quote=False)
        # Only absolute links survive; anchors and repository paths do not exist on the site.
        s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)",
                   lambda m: f'<a href="{m[2].replace(chr(34), "%22")}">{m[1]}</a>'
                   if re.match(r"https?://", m[2]) else m[1], s)
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
        s = re.sub(r"(?<!\S)Toy:", '<span class="toy">Toy</span>', s)
        out.append(s)
    return "".join(out)


def api_body(item):
    rows = "".join(f'<div><dt>{html.escape(f["label"])}</dt><dd>{inline(f["text"])}</dd></div>'
                   for f in item["fields"])
    notes = "".join(f'<p class="note">{inline(p)}</p>' for p in item["notes"])
    return f'<dl class="api">{rows}</dl>{notes}'


BASE_CSS = """*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:#edf1f5;color:#183047;font:16px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
a{color:#1f5fa8}p{margin:8px 0}
.site{display:flex;align-items:flex-end;gap:8px 28px;flex-wrap:wrap;padding:12px 24px 0;background:#fff;border-bottom:1px solid #ccd6df}
.brand{font-weight:700;padding-bottom:10px}nav{display:flex;gap:22px}
nav a{padding:0 2px 8px;color:#506478;text-decoration:none;font-weight:600;border-bottom:3px solid transparent}
nav a:hover{color:#183047}nav a[aria-current=page]{color:#183047;border-color:#183047}
.badge{flex:none;display:inline-grid;place-items:center;width:28px;height:28px;border-radius:50%;background:#183047;color:#fff;font-weight:700;font-size:14px}
.card-head{display:flex;align-items:flex-start;gap:10px}.card-head h2{flex:1;margin:0;font-size:18px;line-height:28px}
dl.api{margin:10px 0 0}dl.api div+div{margin-top:10px}
dl.api dt{font-size:12px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:#506478}
dl.api dd{margin:2px 0 0}p.note{color:#506478;font-size:14px}
code{font:13px/1.4 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;background:#eef3f7;padding:1px 4px;border-radius:4px}
.toy{display:inline-block;padding:0 7px;border-radius:9px;background:#e3f2ef;color:#087D70;font-size:12px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;vertical-align:1px}
"""


def page(title, current, body, css="", script=""):
    tabs = "".join(f'<a href="{href}"{" aria-current=page" if key == current else ""}>{label}</a>'
                   for key, href, label in [("map", "index.html", "Map"), ("apis", "toy_apis.html", "Toy APIs")])
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>{title}</title>
<style>
{BASE_CSS}{css}</style></head><body>
<header class="site"><span class="brand">BPL proof ingredients</span><nav aria-label="Pages">{tabs}</nav></header>
{body}{script}</body></html>
"""


MAP_CSS = """.toolbar{display:flex;gap:12px;align-items:center;flex-wrap:wrap;padding:10px 24px;background:#fff;border-bottom:1px solid #ccd6df;position:sticky;top:0;z-index:3}
button{font:inherit;padding:7px 12px;border:1px solid #aebdca;border-radius:6px;background:#fff;color:#183047;cursor:pointer}
button:hover{background:#edf3f8}#summary{color:#506478;font-size:14px}
.help{padding:10px 24px 2px;background:#fff}.help p{max-width:118ch;margin:0 0 8px}
.teal{color:#087D70;font-weight:600}.orange{color:#B65F19;font-weight:600}
#viewport{overflow:auto;padding:16px}#drawing{position:relative;width:100%;min-width:1000px;margin:auto;background:#fff;border:1px solid #d7e0e7}
svg{display:block;width:100%;height:auto}
.node,.edge{transition:opacity .15s}.node.off{opacity:.22}.edge.off{opacity:.08}
.node[data-kind="ingredient"]{cursor:pointer;-webkit-user-select:none;user-select:none;-webkit-touch-callout:none}
.node[data-kind="ingredient"]:hover>rect{stroke:#173f8a;stroke-width:3}.node[data-kind="ingredient"].off:hover{opacity:.45}
.node:focus{outline:none}.node:focus-visible>rect{stroke:#173f8a;stroke-width:4}
.node.api-open{opacity:1}.node.api-open>rect{stroke:#173f8a;stroke-width:4}
#card{position:absolute;z-index:2;width:min(460px,calc(100% - 16px),calc(100vw - 48px));max-height:calc(100% - 16px);overflow:auto;padding:14px 16px 12px;
background:#fff;border:1px solid #9fb2c4;border-left:4px solid #173f8a;border-radius:10px;box-shadow:0 10px 30px rgba(24,48,71,.22);font-size:15px}
#card[hidden]{display:none}#card:focus{outline:none}
#card-close{flex:none;width:30px;height:30px;padding:0;font-size:20px;line-height:1;border-color:transparent;color:#506478}
#card-close:hover{border-color:#aebdca}#card-more{display:inline-block;margin-top:10px;font-size:14px;font-weight:600}
@media (max-width:700px){.toolbar{position:static}}
@media print{.site,.toolbar,.help,#card{display:none}#viewport{padding:0}#drawing{width:100%!important;min-width:0;border:0}}
"""


MAP_SCRIPT = """<script>
'use strict';
const svg=document.querySelector('#drawing svg'),drawing=document.getElementById('drawing'),summary=document.getElementById('summary');
const card=document.getElementById('card'),cardBadge=document.getElementById('card-badge'),cardTitle=document.getElementById('card-title');
const cardBody=document.getElementById('card-body'),cardMore=document.getElementById('card-more'),cardClose=document.getElementById('card-close');
const nodes=new Map(Array.from(svg.querySelectorAll('[data-node]'),el=>[el.dataset.node,el]));
const edges=Array.from(svg.querySelectorAll('[data-edge]'),el=>({el,source:el.dataset.source,target:el.dataset.target,sign:el.dataset.sign,
  ingredient:el.dataset.sign==='uses'?el.dataset.target:el.dataset.source}));
const ofKind=kind=>Array.from(nodes.keys()).filter(key=>nodes.get(key).dataset.kind===kind);
const ingredients=ofKind('ingredient'),tasks=ofKind('task'),obstacles=ofKind('obstacle');
const neighbours=(key,sign)=>edges.filter(e=>e.sign===sign&&(e.source===key||e.target===key)).map(e=>e.source===key?e.target:e.source);
const uses=new Map(tasks.map(key=>[key,neighbours(key,'uses')]));
const green=new Map(obstacles.map(key=>[key,neighbours(key,'improves')]));
const red=new Map(obstacles.map(key=>[key,neighbours(key,'worsens')]));
let selected=new Set(),api='';
function active(){
  const on=new Set(selected),has=key=>selected.has(key);
  for(const key of tasks)if(uses.get(key).every(has))on.add(key);
  for(const key of obstacles){const r=red.get(key);if(!green.get(key).every(has)&&(r.length===0||r.some(has)))on.add(key);}
  return on;
}
function writeHash(){
  const ids=ingredients.filter(key=>selected.has(key)).map(key=>key.slice(1)),parts=[];
  if(ids.length)parts.push('on='+ids.join(','));
  if(api)parts.push('api='+api.slice(1));
  history.replaceState(null,'',parts.length?'#'+parts.join('&'):location.pathname+location.search);
}
function render(){
  const on=active(),count=list=>list.filter(key=>on.has(key)).length;
  for(const [key,el] of nodes)el.classList.toggle('off',!on.has(key));
  for(const key of ingredients)nodes.get(key).setAttribute('aria-checked',String(on.has(key)));
  for(const e of edges)e.el.classList.toggle('off',!on.has(e.ingredient));
  summary.textContent=count(ingredients)+'/'+ingredients.length+' ingredients · '+count(tasks)+'/'+tasks.length+' tasks · '+count(obstacles)+'/'+obstacles.length+' obstacles on';
  writeHash();
}
function set(keys){selected=new Set(keys);render();}
function toggle(key){selected.has(key)?selected.delete(key):selected.add(key);render();}
// The toy API card sits beside its ingredient, over the arrows; it moves inside the drawing if it would overflow.
function place(){
  if(!api)return;
  const scale=svg.getBoundingClientRect().width/svg.viewBox.baseVal.width,rect=nodes.get(api).querySelector('rect');
  const x=rect.x.baseVal.value+rect.width.baseVal.value,y=rect.y.baseVal.value;
  const left=Math.max(8,Math.min(x*scale+14,drawing.clientWidth-card.offsetWidth-8));
  const top=Math.max(8,Math.min(y*scale,drawing.clientHeight-card.offsetHeight-8));
  card.style.left=left+'px';card.style.top=top+'px';
}
function openApi(key,focus){
  const template=document.getElementById('api-'+key);
  if(!template)return;
  if(api)nodes.get(api).classList.remove('api-open');
  api=key;nodes.get(key).classList.add('api-open');
  cardBadge.textContent=key.slice(1);cardTitle.textContent=template.dataset.title;
  cardBody.replaceChildren(template.content.cloneNode(true));
  cardMore.href='toy_apis.html#ingredient-'+key.slice(1);
  card.hidden=false;card.scrollTop=0;place();
  if(focus)cardClose.focus({preventScroll:true});
  reveal();
  writeHash();
}
// Scroll only as needed: sideways when the drawing is wider than the screen, and vertically only if the card's top is hidden or barely visible.
function reveal(){
  const viewport=document.getElementById('viewport'),v=viewport.getBoundingClientRect();
  let r=card.getBoundingClientRect();
  if(r.right>v.right)viewport.scrollLeft+=Math.min(r.right-v.right+16,r.left-v.left-16);
  else if(r.left<v.left)viewport.scrollLeft-=v.left-r.left+16;
  r=card.getBoundingClientRect();
  const toolbar=document.querySelector('.toolbar'),below=getComputedStyle(toolbar).position==='sticky'?toolbar.getBoundingClientRect().bottom:0;
  if(r.top<below+8||r.top>innerHeight-160)scrollBy(0,r.top-below-12);
}
function closeApi(){
  if(!api)return;
  const key=api,hadFocus=card.contains(document.activeElement);
  nodes.get(key).classList.remove('api-open');api='';card.hidden=true;
  if(hadFocus)nodes.get(key).focus();
  writeHash();
}
let pressTimer=0,pressStart=null,suppressClick=false;
for(const key of ingredients){
  const el=nodes.get(key);
  el.setAttribute('tabindex','0');el.setAttribute('role','switch');el.setAttribute('aria-haspopup','dialog');
  el.addEventListener('click',()=>{if(suppressClick){suppressClick=false;return;}toggle(key);});
  el.addEventListener('contextmenu',event=>{event.preventDefault();openApi(key,false);});
  el.addEventListener('keydown',event=>{
    if(event.key==='Enter'||event.key===' '){event.preventDefault();toggle(key);}
    else if(event.key==='ContextMenu'||(event.shiftKey&&event.key==='F10')){event.preventDefault();openApi(key,true);}
  });
  // Long-press for touch screens that do not fire contextmenu (iOS Safari).
  el.addEventListener('touchstart',event=>{
    suppressClick=false;clearTimeout(pressTimer);
    if(event.touches.length!==1)return;
    pressStart=[event.touches[0].clientX,event.touches[0].clientY];
    pressTimer=setTimeout(()=>{suppressClick=true;openApi(key,false);setTimeout(()=>{suppressClick=false;},800);},500);
  },{passive:true});
  el.addEventListener('touchmove',event=>{
    const t=event.touches[0];
    if(pressStart&&Math.hypot(t.clientX-pressStart[0],t.clientY-pressStart[1])>10)clearTimeout(pressTimer);
  },{passive:true});
  for(const type of ['touchend','touchcancel'])el.addEventListener(type,()=>clearTimeout(pressTimer));
}
cardClose.addEventListener('click',closeApi);
drawing.addEventListener('click',event=>{if(api&&!card.contains(event.target)&&!event.target.closest('[data-kind="ingredient"]'))closeApi();});
document.addEventListener('keydown',event=>{if(event.key==='Escape')closeApi();});
new ResizeObserver(place).observe(drawing);
document.getElementById('none').addEventListener('click',()=>set([]));
document.getElementById('all').addEventListener('click',()=>set(ingredients));
document.getElementById('fit').addEventListener('click',()=>{drawing.style.width='100%';});
document.getElementById('full').addEventListener('click',()=>{drawing.style.width=svg.viewBox.baseVal.width+'px';});
const params=new URLSearchParams(location.hash.slice(1));
set((params.get('on')||'').split(',').map(id=>'i'+id).filter(key=>ingredients.includes(key)));
if(params.get('api'))openApi('i'+params.get('api'),false);
</script>
"""


def build():
    data = json.loads((DATA / "toy_apis.json").read_text(encoding="utf-8"))
    svg_text = (DATA / "ingredients_obstacles.svg").read_text(encoding="utf-8")
    svg_ingredients = {el.attrib["data-node"] for el in ET.fromstring(svg_text).iter()
                       if el.attrib.get("data-kind") == "ingredient"}
    keys = {f'i{item["id"]}' for item in data["ingredients"]}
    if svg_ingredients != keys:
        fail(f"the map's ingredients {sorted(svg_ingredients)} differ from the toy APIs {sorted(keys)}")
    svg = svg_text.split("\n", 1)[1].replace('role="img"', 'role="group"', 1)
    templates = "".join(f'<template id="api-i{item["id"]}" data-title="{html.escape(item["name"])}">{api_body(item)}</template>\n'
                        for item in data["ingredients"])
    body = f"""<div class="help"><p>Click an ingredient to switch it on or off; right-click it (long-press on a touch screen,
Shift+F10 from the keyboard) to see its toy API. Faded boxes are off. A task is on when all its ingredients are on.
An obstacle is on when not all of its <span class="teal">improving</span> ingredients are on, and either it has no
<span class="orange">worsening</span> ingredients or at least one of them is on. An arrow is shown when its ingredient is on.</p></div>
<div class="toolbar"><button id="none" type="button">All off</button><button id="all" type="button">All on</button>
<button id="fit" type="button">Fit width</button><button id="full" type="button">Full size</button>
<span id="summary" aria-live="polite"></span></div>
<main><div id="viewport"><div id="drawing">{svg}<section id="card" role="dialog" aria-labelledby="card-title" tabindex="-1" hidden>
<div class="card-head"><span class="badge" id="card-badge"></span><h2 id="card-title"></h2><button id="card-close" type="button" aria-label="Close toy API">×</button></div>
<div id="card-body"></div><a id="card-more" href="toy_apis.html">All toy APIs →</a></section></div></div></main>
{templates}"""
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "index.html").write_text(page("BPL ingredient map", "map", body, MAP_CSS, MAP_SCRIPT), encoding="utf-8")

    cards = "".join(f"""<article class="card" id="ingredient-{item["id"]}"><div class="card-head"><span class="badge">{item["id"]}</span>
<h2>{html.escape(item["name"])}</h2></div><p class="desc">{inline(item["description"])}</p>{api_body(item)}
<a class="more" href="index.html#api={item["id"]}">Show on map →</a></article>
""" for item in data["ingredients"])
    intro = "".join(f"<p>{inline(p)}</p>" for p in data["intro"])
    css = """main{max-width:1240px;margin:0 auto;padding:20px 24px 40px}h1{font-size:28px;margin:4px 0 6px}.intro{max-width:90ch;color:#30475e}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(440px,100%),1fr));gap:16px;margin-top:18px}
.card{padding:16px 18px;background:#fff;border:1px solid #d7e0e7;border-radius:10px;scroll-margin-top:16px}
.card:target{border-color:#173f8a;box-shadow:0 0 0 2px #173f8a}.desc{margin:6px 0 0;color:#506478;font-style:italic}
.more{display:inline-block;margin-top:10px;font-size:14px;font-weight:600}
"""
    body = f'<main><h1>Toy APIs for each ingredient</h1><div class="intro">{intro}</div>\n<div class="grid">\n{cards}</div></main>\n'
    (OUT / "toy_apis.html").write_text(page("BPL toy APIs", "apis", body, css), encoding="utf-8")

    REDIRECT.write_text("""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex, nofollow">
<title>BPL proof ingredients</title>
<script>location.replace('bpl_proof_ingredients/'+location.hash);</script>
<meta http-equiv="refresh" content="0; url=bpl_proof_ingredients/">
</head><body><p><a href="bpl_proof_ingredients/">BPL proof ingredients</a></p></body></html>
""", encoding="utf-8")
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--harness", type=Path, help="tcs-harness checkout to refresh bpl/data/ from")
    args = parser.parse_args()
    if args.harness:
        print(f"Refreshed bpl/data/ from tcs-harness at {refresh(args.harness.resolve())}.")
    data = build()
    print(f'Built {len(data["ingredients"])} toy APIs into docs/bpl_proof_ingredients/ '
          "(index.html, toy_apis.html) and the redirect at docs/bpl_proof_ingredients.html.")


if __name__ == "__main__":
    main()
