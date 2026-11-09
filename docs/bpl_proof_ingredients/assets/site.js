'use strict';
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
