'use strict';
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
