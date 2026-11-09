"""Shared page chrome, stylesheet and scripts for the BPL proof-ingredients pages."""

import html


KATEX = "https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/"
TABS = [("guide", "index.html", "Guide"), ("map", "map.html", "Map"),
        ("apis", "toy_apis.html", "Toy APIs"), ("reference", "reference.html", "Reference")]


def page(title, current, body, root="", css="", script="", math=False, modes=True, description="", extra_scripts=()):
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
{"".join(f'<script defer src="{root}assets/{name}"></script>' for name in extra_scripts)}
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
  document.dispatchEvent(new CustomEvent('bpl:mode'));
}
window.bplRewriteLinks=rewriteLinks;
const mathOptions={delimiters:[{left:'\\[',right:'\\]',display:true},{left:'\\(',right:'\\)',display:false}],
  macros:{'\\Call':'\\textsf{#1}'},throwOnError:false,ignoredClasses:['no-math']};
window.bplRenderMath=el=>{if(window.renderMathInElement)renderMathInElement(el,mathOptions);};
document.addEventListener('DOMContentLoaded',()=>{
  setMode(doc.dataset.mode);
  for(const b of document.querySelectorAll('[data-set-mode]'))b.addEventListener('click',()=>setMode(b.dataset.setMode));
  window.bplRenderMath(document.body);
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


EXPLORER_CSS = """
/* Physical-algorithm overview */
.explorer{margin-top:8px}
.x-bar{display:flex;align-items:center;justify-content:space-between;gap:8px 16px;flex-wrap:wrap;margin-bottom:8px}
.x-crumbs{display:flex;flex-wrap:wrap;align-items:center;gap:4px;font-size:14px}
.x-crumbs button{font:600 13px/1.3 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;padding:3px 7px;border:1px solid #c9d5df;border-radius:6px;background:#fff;color:#1f5fa8;cursor:pointer}
.x-crumbs button[aria-current=true]{background:#183047;color:#fff;border-color:#183047}
.x-crumbs .sep{color:#8a9aab}.x-crumbs .x-overview{font-family:inherit}
.x-example{font-size:14px;color:#30475e;display:flex;align-items:center;gap:6px}
.x-body{display:grid;grid-template-columns:minmax(0,1fr);gap:16px}
@media (min-width:1100px){.x-body{grid-template-columns:minmax(0,1fr) 320px}}
.x-stage{position:relative;min-height:220px;border:1px solid #d7e0e7;border-radius:10px;background:#f7f9fb;overflow:hidden;transition:height .3s}
.x-lines{position:absolute;inset:0;width:100%;height:100%;pointer-events:none;transition:opacity .15s}
.x-lines path{fill:none;stroke:#9fb2c4;stroke-width:1.5}.x-lines path.budget{stroke:#b65f19;stroke-dasharray:5 3}
.x-node{position:absolute;left:0;top:0;display:flex;flex-direction:column;justify-content:center;gap:1px;padding:4px 9px;text-align:left;
 background:#fff;border:1px solid #b8c6d3;border-radius:8px;cursor:pointer;color:#183047;overflow:hidden;
 transition:transform .35s ease,width .35s ease,height .35s ease,opacity .25s ease,box-shadow .2s;font:inherit}
.x-node:hover{border-color:#173f8a;box-shadow:0 0 0 2px #c9d9ee}
.x-node .xid{font:700 12.5px/1.25 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;white-space:nowrap}
.x-node .xt{font-size:12px;line-height:1.25;color:#30475e;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.x-node .xtop{display:flex;align-items:center;gap:6px;min-width:0}
.x-node .xf{margin-left:auto;font-size:9.5px;font-weight:700;text-transform:uppercase;color:#8a4512;white-space:nowrap}
.x-node .xk{flex:none;font-size:10px;white-space:nowrap;font-weight:700;letter-spacing:.03em;text-transform:uppercase;padding:0 6px;border-radius:8px;background:#e8eff6;color:#30475e}
.x-node .xk.budget{background:#f6e7da;color:#8a4512}
.x-node.center{border:2px solid #183047;box-shadow:0 6px 18px rgba(24,48,71,.15)}
.x-node.center .xid{font-size:15px}.x-node.center .xt{font-size:13px;white-space:normal}
.x-node.compact{padding:2px 7px}.x-node.compact .xt,.x-node.compact .xk,.x-node.compact .xf{display:none}
.x-node.compact.full-node{border:1.5px dashed #b65f19}.x-node .xid{overflow:hidden;text-overflow:ellipsis}
.x-node.group{background:#eef3f7;border-style:dashed}
.x-node.gone{opacity:0;pointer-events:none;visibility:hidden;transition:transform .35s ease,opacity .2s ease,visibility 0s .35s}
.show-example .x-node.ex{box-shadow:0 0 0 3px #e0a43a}
.x-label{position:absolute;left:0;top:0;font-size:12px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;color:#506478;white-space:nowrap;transition:transform .35s,opacity .2s}
.x-label.band{font-size:13px;color:#183047}
.x-panel{background:#fff;border:1px solid #d7e0e7;border-radius:10px;padding:12px 14px;font-size:14px;align-self:start}
.x-panel h3{font-size:16px;margin:4px 0 6px}.x-panel h4{font-size:13px;margin:12px 0 4px;text-transform:uppercase;letter-spacing:.05em;color:#506478}
.x-panel ul{list-style:none;margin:0;padding:0}.x-panel li{margin:3px 0}
.x-panel li button{font:600 12.5px/1.3 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;padding:2px 6px;border:1px solid #c9d5df;border-radius:5px;background:#e8eff6;color:#1f5fa8;cursor:pointer}
.x-panel .xk{font-size:11px;font-weight:700;text-transform:uppercase;color:#8a4512;margin-left:4px}
.x-panel .layer{color:#30475e}
.x-show{font-size:12px;padding:1px 7px;margin-left:6px;border:1px solid #aebdca;border-radius:6px;background:#fff;cursor:pointer}
.toy-problem{background:#f3f7f6;border:1px solid #cfe1dd;border-left:4px solid #087D70;border-radius:8px;padding:8px 14px;margin:10px 0}
"""


EXPLORER_JS = r"""'use strict';
document.addEventListener('DOMContentLoaded',()=>{
const data=JSON.parse(document.getElementById('explorer-data').textContent);
const stage=document.getElementById('x-stage'),lines=stage.querySelector('.x-lines'),panel=document.getElementById('x-panel');
const crumbs=document.getElementById('x-crumbs'),root=document.documentElement.dataset.root||'';
const byId=new Map(data.nodes.map(n=>[n.id,n])),layerOf=new Map(),groupOf=new Map(),order=new Map();
data.layers.forEach((L,i)=>L.groups.forEach(g=>g.ids.forEach((id,j)=>{layerOf.set(id,L);groupOf.set(id,g);order.set(id,i*100+j);})));
const isInfra=id=>layerOf.get(id).key==='infra';
const mode=()=>document.documentElement.dataset.mode;
const live=id=>!(byId.get(id).full&&mode()==='exact');
const edges=()=>data.edges.filter(e=>e.modes.includes(mode())&&live(e.s)&&live(e.t));
const kindLabel=k=>data.kinds[k]||'';
const els=new Map(),labels=[];
function el(key,make){if(!els.has(key)){const b=make();stage.appendChild(b);els.set(key,b);}return els.get(key);}
function nodeEl(id){return el(id,()=>{const n=byId.get(id),b=document.createElement('button');b.type='button';b.className='x-node gone'+(n.full?' full-node':'')+(n.example?' ex':'');
  b.tabIndex=-1;b.title=n.id+' — '+n.title;
  const top=document.createElement('span');top.className='xtop';
  const a=document.createElement('span');a.className='xid';a.textContent=n.id;const k=document.createElement('span');k.className='xk';top.append(a,k);
  if(n.full){const f=document.createElement('span');f.className='xf';f.textContent='full space';top.append(f);}
  const t=document.createElement('span');t.className='xt';t.textContent=n.title;b.append(top,t);b.addEventListener('click',()=>focus(id));return b;});}
function groupEl(g){return el('g:'+g.key,()=>{const b=document.createElement('button');b.type='button';b.className='x-node group gone';b.tabIndex=-1;
  const top=document.createElement('span');top.className='xtop';const a=document.createElement('span');a.className='xid';
  const k=document.createElement('span');k.className='xk';top.append(a,k);const t=document.createElement('span');t.className='xt';t.textContent='Click to show these routines';b.append(top,t);b.addEventListener('click',()=>{expanded.add(g.key);layout();});return b;});}
function place(b,x,y,w,h,cls){b.style.transform=`translate(${x}px,${y}px)`;b.style.width=w+'px';b.style.height=h+'px';
  b.classList.remove('gone','center','compact');if(cls)b.classList.add(cls);}
function label(text,x,y,cls){const d=document.createElement('div');d.className='x-label'+(cls?' '+cls:'');d.textContent=text;d.style.transform=`translate(${x}px,${y}px)`;stage.appendChild(d);labels.push(d);}
let current='P-ROOT',view='focus',path=['P-ROOT'],expanded=new Set(),touched=/^#(focus=|overview)/.test(location.hash);
function uniq(a){return [...new Set(a)];}
function callersOf(id){return uniq(edges().filter(e=>e.t===id&&e.s!==id).map(e=>e.s)).sort((a,b)=>order.get(a)-order.get(b));}
function calleesOf(id){return edges().filter(e=>e.s===id&&e.t!==id).sort((a,b)=>(Math.min(...a.steps,99)-Math.min(...b.steps,99))||(order.get(a.t)-order.get(b.t)));}
function edge(s,t){return data.edges.find(e=>e.s===s&&e.t===t);}
function layout(){
  labels.splice(0).forEach(d=>d.remove());
  const used=new Set(),W=stage.clientWidth,linesOut=[];
  if(view==='overview'){
    const cw=W<560?130:156,ch=28,gap=8;let y=14;
    data.layers.forEach((L,i)=>{
      label(L.title,14,y,'band');y+=24;
      L.groups.forEach(g=>{const ids=g.ids.filter(live);if(!ids.length)return;
        if(g.title){label(g.title,14,y);y+=20;}
        const per=Math.max(1,Math.floor((W-28+gap)/(cw+gap)));
        ids.forEach((id,j)=>{const b=nodeEl(id);place(b,14+(j%per)*(cw+gap),y+Math.floor(j/per)*(ch+gap),cw,ch,'compact');b.querySelector('.xk').textContent='';used.add(id);});
        y+=Math.ceil(ids.length/per)*(ch+gap)+6;});
      y+=10;});
    stage.style.height=y+'px';
    panel.replaceChildren();const h=document.createElement('h3');h.textContent='The layers, top-down';panel.append(h);
    data.layers.forEach(L=>{const t=document.createElement('h4');t.textContent=L.title;const d=document.createElement('p');d.className='where';d.textContent=L.desc;panel.append(t,d);});
  }else{
    const id=current,narrow=W<760,nw=narrow?W-28:Math.min(240,(W-80)/3),nh=50,gap=8,cw=narrow?W-28:Math.min(270,(W-80)/3),chh=70;
    const callers=callersOf(id).map(s=>({key:s,id:s,kind:edge(s,id).kind}));
    const callees=[];const groups=new Map();
    for(const e of calleesOf(id)){
      const g=groupOf.get(e.t);
      if(!isInfra(id)&&isInfra(e.t)&&!expanded.has(g.key)){if(!groups.has(g.key)){groups.set(g.key,{key:'g:'+g.key,group:g,ids:[]});callees.push(groups.get(g.key));}groups.get(g.key).ids.push(e.t);}
      else callees.push({key:e.t,id:e.t,kind:e.kind});
    }
    const self=edge(id,id);
    function put(item,x,y,w){
      if(item.group){const b=groupEl(item.group);place(b,x,y,w,nh);b.querySelector('.xid').textContent=item.group.title.replace(/ \(.*\)$/,'');
        b.querySelector('.xk').textContent=item.ids.length+' routine'+(item.ids.length>1?'s':'');b.title=item.ids.join(', ');used.add(item.key);return;}
      const b=nodeEl(item.id);place(b,x,y,w,nh);const k=b.querySelector('.xk');k.textContent=kindLabel(item.kind);k.className='xk '+(item.kind||'');k.hidden=!item.kind;used.add(item.id);
    }
    let H;
    if(narrow){
      let y=10;
      if(callers.length){label('Called by',14,y);y+=20;callers.forEach(c=>{put(c,14,y,nw);y+=nh+gap;});y+=6;}
      const b=nodeEl(id);place(b,14,y,cw,chh,'center');b.querySelector('.xk').hidden=true;used.add(id);y+=chh+14;
      if(callees.length){label('Calls',14,y);y+=20;callees.forEach(c=>{put(c,14,y,nw);y+=nh+gap;});}
      H=y+8;
    }else{
      const rows=Math.max(callers.length,callees.length,1);H=Math.max(220,40+rows*(nh+gap)+10);
      const colY=n=>Math.max(36,(H-n*(nh+gap))/2+10),cx=(W-cw)/2,cy=(H-chh)/2,rx=W-14-nw;
      if(callers.length)label('Called by',14,12);if(callees.length)label('Calls',rx,12);
      callers.forEach((c,i)=>{const y=colY(callers.length)+i*(nh+gap);put(c,14,y,nw);linesOut.push([14+nw,y+nh/2,cx,cy+chh/2,c.kind]);});
      callees.forEach((c,i)=>{const y=colY(callees.length)+i*(nh+gap);put(c,rx,y,nw);linesOut.push([cx+cw,cy+chh/2,rx,y+nh/2,c.kind]);});
      const b=nodeEl(id);place(b,cx,cy,cw,chh,'center');b.querySelector('.xk').hidden=true;used.add(id);
    }
    stage.style.height=H+'px';
    renderPanel(id,callers,calleesOf(id),self);
  }
  for(const [key,b] of els)if(!used.has(key))b.classList.add('gone'),b.classList.remove('center');
  lines.style.opacity=0;lines.replaceChildren();
  clearTimeout(layout.t);layout.t=setTimeout(()=>{
    for(const [x1,y1,x2,y2,k] of linesOut){const p=document.createElementNS('http://www.w3.org/2000/svg','path');const m=(x1+x2)/2;
      p.setAttribute('d',`M${x1} ${y1}C${m} ${y1} ${m} ${y2} ${x2} ${y2}`);if(k)p.setAttribute('class',k);lines.appendChild(p);}
    lines.style.opacity=1;},360);
  renderCrumbs();
  if(touched)history.replaceState(history.state,'',location.pathname+location.search+(view==='overview'?'#overview':'#focus='+current));
}
function button(id,extra){const li=document.createElement('li'),b=document.createElement('button');b.type='button';b.textContent=id;b.title=byId.get(id).title;
  b.addEventListener('click',()=>{focus(id);b.blur();});li.append(b,' ',byId.get(id).title);
  if(extra){const s=document.createElement('span');s.className='xk';s.textContent=extra;li.append(s);}return li;}
function renderPanel(id,callers,callees,self){
  const tpl=document.getElementById('x-tpl-'+id);panel.replaceChildren(tpl.content.cloneNode(true));
  const L=layerOf.get(id),g=groupOf.get(id),p=document.createElement('p');p.className='layer';
  p.innerHTML='<strong>Layer:</strong> ';p.append(L.title+(g.title?' · '+g.title:''));
  const d=document.createElement('p');d.className='where';d.textContent=L.desc;panel.append(p,d);
  if(callers.length){const h=document.createElement('h4');h.textContent='Called by';const ul=document.createElement('ul');
    callers.forEach(c=>ul.append(button(c.id,kindLabel(c.kind))));panel.append(h,ul);}
  if(callees.length){const h=document.createElement('h4');h.textContent='Calls, in step order';const ul=document.createElement('ul');
    callees.forEach(e=>ul.append(button(e.t,[kindLabel(e.kind),e.steps.length?'step'+(e.steps.length>1?'s ':' ')+e.steps.sort((a,b)=>a-b).join(', '):''].filter(Boolean).join(' · '))));panel.append(h,ul);}
  if(self){const s=document.createElement('p');s.className='where';s.textContent='Also calls itself'+(self.kind?' at the '+kindLabel(self.kind):'')+'.';panel.append(s);}
  const a=document.createElement('p');a.innerHTML=`<a href="${root}${byId.get(id).url}">Full page: steps and relationships →</a>`;panel.append(a);
  if(window.bplRenderMath)window.bplRenderMath(panel);
  if(window.bplRewriteLinks)window.bplRewriteLinks();
}
function renderCrumbs(){
  crumbs.replaceChildren();
  const o=document.createElement('button');o.type='button';o.className='x-overview';o.textContent='Overview';o.setAttribute('aria-current',String(view==='overview'));
  o.addEventListener('click',()=>{view='overview';touched=true;layout();});crumbs.append(o);
  path.forEach((id,i)=>{const s=document.createElement('span');s.className='sep';s.textContent=i?'›':'|';
    const b=document.createElement('button');b.type='button';b.textContent=id;b.setAttribute('aria-current',String(view==='focus'&&id===current));
    b.addEventListener('click',()=>focus(id));crumbs.append(s,b);});
}
function focus(id){
  if(!byId.has(id))return;
  const i=path.indexOf(id);if(i>=0)path=path.slice(0,i+1);else path.push(id);
  current=id;view='focus';expanded=new Set();touched=true;layout();
}
document.getElementById('x-example').addEventListener('change',e=>stage.classList.toggle('show-example',e.target.checked));
for(const b of document.querySelectorAll('[data-focus]'))b.addEventListener('click',()=>{path=['P-ROOT'];focus(b.dataset.focus);
  document.getElementById('explorer').scrollIntoView({behavior:'smooth',block:'start'});});
document.addEventListener('bpl:mode',()=>layout());
let lastW=stage.clientWidth;new ResizeObserver(()=>{if(Math.abs(stage.clientWidth-lastW)>4){lastW=stage.clientWidth;layout();}}).observe(stage);
// Follow #focus= links within the page too (e.g. from the browser's address bar or an in-page link).
addEventListener('hashchange',()=>{const h=/^#focus=([A-Z0-9-]+)$/.exec(location.hash);if(h&&h[1]!==current&&byId.has(h[1]))focus(h[1]);
  else if(location.hash==='#overview'&&view!=='overview'){view='overview';layout();}});
const m=/^#(focus=([A-Z0-9-]+)|overview)$/.exec(location.hash);
if(m&&m[2]&&byId.has(m[2])){if(m[2]!=='P-ROOT')path.push(m[2]);current=m[2];layout();document.getElementById('explorer').scrollIntoView({block:'start'});}
else if(m&&m[1]==='overview'){view='overview';layout();}
else layout();
});
"""
