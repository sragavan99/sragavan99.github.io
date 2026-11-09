"""Shared page chrome, stylesheet and scripts for the BPL proof-ingredients pages."""

import html


KATEX = "https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/"
TABS = [("guide", "index.html", "Guide"), ("map", "map.html", "Map"),
        ("apis", "toy_apis.html", "Toy APIs"), ("reference", "reference.html", "Reference")]


def page(title, current, body, root="", css="", script="", math=False, modes=True, description=""):
    """A complete page. root is the relative path from the page to the site folder ("" or "../")."""
    tabs = "".join(f'<a href="{root}{href}"{" aria-current=page" if key == current else ""}>{label}</a>'
                   for key, href, label in TABS)
    mode_switch = ("""<div class="mode-switch" role="group" aria-label="Comparison mode">
<button type="button" data-set-mode="exact" aria-pressed="true">Exact names</button><button type="button" data-set-mode="full" aria-pressed="false">Full space</button></div>"""
                   if modes else "")
    katex = (f'<link rel="stylesheet" href="{KATEX}katex.min.css">\n'
             f'<script defer src="{KATEX}katex.min.js"></script>\n'
             f'<script defer src="{KATEX}contrib/auto-render.min.js"></script>\n') if math else ""
    meta = f'<meta name="description" content="{html.escape(description)}">\n' if description else ""
    return f"""<!doctype html>
<html lang="en" data-root="{root}" data-mode="exact"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
{meta}<title>{html.escape(title)}</title>
<script>try{{if(new URLSearchParams(location.search).get('mode')==='full')document.documentElement.dataset.mode='full';}}catch(e){{}}</script>
<link rel="stylesheet" href="{root}assets/site.css">
{katex}<script defer src="{root}assets/search.js"></script>
<script defer src="{root}assets/site.js"></script>
{f"<style>{css}</style>" if css else ""}
</head><body>
<a class="skip" href="#content">Skip to content</a>
<header class="site"><div class="site-row"><a class="brand" href="{root}index.html">BPL proof ingredients</a>
<nav aria-label="Pages">{tabs}</nav>
<div class="search"><label class="visually-hidden" for="q">Search components</label>
<input id="q" type="search" placeholder="Search by ID or title" autocomplete="off" role="combobox" aria-expanded="false" aria-controls="q-results" aria-autocomplete="list">
<ul id="q-results" role="listbox" hidden></ul></div>
{mode_switch}</div></header>
{body}{script}</body></html>
"""


CSS = """*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:#edf1f5;color:#183047;font:16px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif}
a{color:#1f5fa8}a:hover{color:#123f75}p{margin:8px 0}h1,h2,h3,h4{line-height:1.25}
.skip{position:absolute;left:-999px;top:0;background:#fff;padding:8px 12px;z-index:10}.skip:focus{left:8px}
.visually-hidden{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.site{background:#fff;border-bottom:1px solid #ccd6df}
.site-row{display:flex;align-items:center;gap:10px 24px;flex-wrap:wrap;padding:10px 24px}
.brand{font-weight:700;color:#183047;text-decoration:none}
nav{display:flex;gap:18px;flex-wrap:wrap}
nav a{padding:4px 2px;color:#506478;text-decoration:none;font-weight:600;border-bottom:3px solid transparent}
nav a:hover{color:#183047}nav a[aria-current=page]{color:#183047;border-color:#183047}
.search{position:relative;margin-left:auto;flex:1 1 220px;max-width:340px}
#q{width:100%;font:inherit;font-size:15px;padding:6px 10px;border:1px solid #aebdca;border-radius:6px}
#q-results{position:absolute;right:0;left:0;top:calc(100% + 4px);z-index:20;margin:0;padding:4px;list-style:none;background:#fff;border:1px solid #aebdca;border-radius:8px;box-shadow:0 10px 30px rgba(24,48,71,.18);max-height:60vh;overflow:auto}
#q-results li{padding:6px 8px;border-radius:6px;cursor:pointer;font-size:14px;line-height:1.35}
#q-results li[aria-selected=true],#q-results li:hover{background:#e8eff6}
#q-results .k{display:block;font-size:11px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;color:#506478}
#q-results .none{color:#506478;cursor:default}
.mode-switch{display:inline-flex;border:1px solid #aebdca;border-radius:7px;overflow:hidden}
.mode-switch button{font:inherit;font-size:14px;padding:6px 10px;border:0;background:#fff;color:#506478;cursor:pointer}
.mode-switch button+button{border-left:1px solid #aebdca}
.mode-switch button[aria-pressed=true]{background:#183047;color:#fff}
button{font:inherit}
.badge{flex:none;display:inline-grid;place-items:center;width:28px;height:28px;border-radius:50%;background:#183047;color:#fff;font-weight:700;font-size:14px}
.card-head{display:flex;align-items:flex-start;gap:10px}.card-head h2{flex:1;margin:0;font-size:18px;line-height:28px}
dl.api{margin:10px 0 0}dl.api div+div{margin-top:10px}
dl.api dt{font-size:12px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:#506478}
dl.api dd{margin:2px 0 0}p.note{color:#506478;font-size:14px}
code{font:13px/1.4 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;background:#eef3f7;padding:1px 4px;border-radius:4px}
a.id,code.id{font:600 13px/1.4 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;white-space:nowrap}
a.id{text-decoration:none;background:#e8eff6;padding:1px 4px;border-radius:4px}a.id:hover{text-decoration:underline}
.sf{font-family:ui-sans-serif,system-ui,sans-serif;font-weight:600}
.toy{display:inline-block;padding:0 7px;border-radius:9px;background:#e3f2ef;color:#087D70;font-size:12px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;vertical-align:1px}
.math{overflow-x:auto;overflow-y:hidden;margin:8px 0}
.table-wrap{overflow-x:auto;margin:10px 0}.table-wrap table{border-collapse:collapse;font-size:14px}
.table-wrap th,.table-wrap td{border-bottom:1px solid #d7e0e7;padding:6px 10px;text-align:left;vertical-align:top}
/* Comparison modes */
.mode-tag{display:inline-block;padding:0 6px;border-radius:9px;background:#f6e7da;color:#8a4512;font-size:11px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;vertical-align:1px}
html[data-mode=exact] .full-part,html[data-mode=exact] .full-only-entry,html[data-mode=exact] li.full-only-step{display:none}
html[data-mode=full] .exact-only,html[data-mode=full] .exact-note{display:none}
html[data-mode=full] .full-part,html[data-mode=full] li.full-only-step{background:#fbf3ec;box-shadow:0 0 0 3px #fbf3ec;border-radius:3px}
.mode-note{font-size:14px;color:#8a4512;background:#fbf3ec;border:1px solid #efd5bf;border-radius:8px;padding:6px 10px}
/* Layout */
.layout{display:grid;grid-template-columns:minmax(0,1fr);gap:24px;max-width:1240px;margin:0 auto;padding:20px 24px 48px}
@media (min-width:980px){.layout.with-outline{grid-template-columns:260px minmax(0,1fr)}.layout.with-outline>aside{order:-1}}
main.page{max-width:1240px;margin:0 auto;padding:20px 24px 48px}
.panel{background:#fff;border:1px solid #d7e0e7;border-radius:10px;padding:16px 20px;margin:16px 0}
.panel>h2:first-child,.panel>h3:first-child{margin-top:0}
.crumbs{font-size:14px;color:#506478;margin:0 0 6px}.crumbs a{color:#506478}
.kicker{font-size:13px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;color:#506478;margin:0}
h1{font-size:28px;margin:4px 0 8px}h1 .id-title{color:#30475e}
.why{display:block;font-size:13px;color:#506478}
.where{font-size:14px;color:#506478}
.tag{display:inline-block;padding:1px 8px;border-radius:9px;background:#e8eff6;color:#30475e;font-size:12px;font-weight:700;letter-spacing:.03em;text-transform:uppercase;margin-right:6px}
.label{font-size:12px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:#506478;margin:14px 0 2px}
ol.steps{padding-left:1.6em}ol.steps li{margin:6px 0}ol.steps li::marker{font-weight:700;color:#506478}
.proof{border-left:4px solid #b65f19}
.rel h3{font-size:15px;margin:14px 0 4px}.rel ul{margin:0;padding-left:1.2em}.rel li{margin:4px 0}
.rel .none{color:#506478;font-size:14px;margin:0}
blockquote{margin:4px 0 0;padding:2px 10px;border-left:3px solid #ccd6df;color:#30475e;font-size:14px}
.comp-list{list-style:none;margin:6px 0;padding:0}.comp-list li{padding:3px 0}
.comp-list .t{color:#30475e}
details.outline{border-top:1px solid #e1e8ee}details.outline>summary{cursor:pointer;padding:8px 2px;font-weight:600}
details.outline[open]>summary{color:#183047}
aside .outline-box{position:sticky;top:12px;background:#fff;border:1px solid #d7e0e7;border-radius:10px;padding:10px 14px;font-size:14px;max-height:calc(100vh - 24px);overflow:auto}
aside h2{font-size:14px;margin:4px 0 6px}aside ul{list-style:none;margin:0 0 6px;padding-left:10px}aside li{margin:2px 0}
aside a[aria-current]{font-weight:700;color:#183047}
.toolbar-inline{display:flex;gap:8px;margin:8px 0}.toolbar-inline button{padding:4px 10px;border:1px solid #aebdca;border-radius:6px;background:#fff;cursor:pointer;font-size:14px}
@media (max-width:700px){.site-row{padding:10px 16px}.layout,main.page{padding:16px 16px 40px}.search{max-width:none;flex-basis:100%}}
"""


JS = r"""'use strict';
(function(){
const doc=document.documentElement,root=doc.dataset.root||'';
// Keep the comparison mode in internal links so a direct link restores it.
function withMode(href){
  if(!href||/^(https?:|mailto:|#)/.test(href))return href;
  const hash=href.includes('#')?href.slice(href.indexOf('#')):'',base=hash?href.slice(0,href.indexOf('#')):href;
  const [path,query='']=base.split('?'),params=new URLSearchParams(query);
  if(doc.dataset.mode==='full')params.set('mode','full');else params.delete('mode');
  const q=params.toString();return path+(q?'?'+q:'')+hash;
}
function rewriteLinks(){for(const a of document.querySelectorAll('a[href]')){if(!a.dataset.href)a.dataset.href=a.getAttribute('href');a.setAttribute('href',withMode(a.dataset.href));}}
function setMode(mode){
  doc.dataset.mode=mode==='full'?'full':'exact';
  for(const b of document.querySelectorAll('[data-set-mode]'))b.setAttribute('aria-pressed',String(b.dataset.setMode===doc.dataset.mode));
  const params=new URLSearchParams(location.search);
  if(doc.dataset.mode==='full')params.set('mode','full');else params.delete('mode');
  const q=params.toString();history.replaceState(history.state,'',location.pathname+(q?'?'+q:'')+location.hash);
  rewriteLinks();
}
document.addEventListener('DOMContentLoaded',()=>{
  setMode(doc.dataset.mode);
  for(const b of document.querySelectorAll('[data-set-mode]'))b.addEventListener('click',()=>setMode(b.dataset.setMode));
  if(window.renderMathInElement)renderMathInElement(document.body,{delimiters:[{left:'\\[',right:'\\]',display:true},{left:'\\(',right:'\\)',display:false}],
    macros:{'\\Call':'\\textsf{#1}'},throwOnError:false,ignoredClasses:['no-math']});
  // Outline: open only the selected branch (from the hash), with expand/collapse controls.
  const target=location.hash&&document.getElementById(decodeURIComponent(location.hash.slice(1)));
  if(target){let d=target.closest('details');while(d){d.open=true;d=d.parentElement.closest('details');}if(target.tagName==='DETAILS')target.open=true;}
  for(const b of document.querySelectorAll('[data-expand]'))b.addEventListener('click',()=>{for(const d of document.querySelectorAll(b.dataset.expand))d.open=b.dataset.open==='1';});
  search();
});
function search(){
  const input=document.getElementById('q'),list=document.getElementById('q-results'),index=window.BPL_INDEX||[];
  if(!input)return;
  let items=[],active=-1;
  function score(e,q){const id=e.i.toLowerCase(),t=e.t.toLowerCase();
    if(id===q)return 0;if(id.startsWith(q))return 1;if(id.includes(q))return 2;if(t.startsWith(q))return 3;if(t.includes(q))return 4;
    return q.split(/\s+/).every(w=>t.includes(w)||id.includes(w))?5:-1;}
  function show(){
    const q=input.value.trim().toLowerCase();list.replaceChildren();active=-1;
    if(!q){list.hidden=true;input.setAttribute('aria-expanded','false');return;}
    items=index.map(e=>[score(e,q),e]).filter(x=>x[0]>=0).sort((a,b)=>a[0]-b[0]||a[1].i.localeCompare(b[1].i)).slice(0,12).map(x=>x[1]);
    if(!items.length){const li=document.createElement('li');li.className='none';li.textContent='No matches';list.appendChild(li);}
    items.forEach((e,j)=>{const li=document.createElement('li');li.id='q-opt-'+j;li.setAttribute('role','option');
      const k=document.createElement('span');k.className='k';k.textContent=e.k+(e.f?' · full space only':'');
      const s=document.createElement('span');s.textContent=e.i===e.t?e.t:e.i+' — '+e.t;li.append(k,s);
      li.addEventListener('mousedown',ev=>{ev.preventDefault();go(e);});list.appendChild(li);});
    list.hidden=false;input.setAttribute('aria-expanded','true');
  }
  function mark(){[...list.children].forEach((li,j)=>li.setAttribute('aria-selected',String(j===active)));
    input.setAttribute('aria-activedescendant',active>=0?'q-opt-'+active:'');}
  function go(e){location.href=withMode(root+e.u);}
  input.addEventListener('input',show);
  input.addEventListener('keydown',ev=>{
    if(ev.key==='ArrowDown'&&items.length){ev.preventDefault();active=(active+1)%items.length;mark();}
    else if(ev.key==='ArrowUp'&&items.length){ev.preventDefault();active=(active-1+items.length)%items.length;mark();}
    else if(ev.key==='Enter'&&items.length){ev.preventDefault();go(items[Math.max(active,0)]);}
    else if(ev.key==='Escape'){input.value='';show();}
  });
  input.addEventListener('blur',()=>setTimeout(()=>{list.hidden=true;input.setAttribute('aria-expanded','false');},100));
  input.addEventListener('focus',show);
}
})();
"""
