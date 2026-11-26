#!/usr/bin/env python3
"""Build a deterministic combined Task Map Graph from the three canonical inputs."""
from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from os import fsync as file_fsync
from os import replace as atomic_replace
from os import fsync as directory_fsync
from pathlib import Path
from stat import S_IMODE
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
CODE_PATH = Path("docs/phase4/task-map-graph/current-project-code-graph.json")
TASK_PATH = Path("docs/phase4/task-map-graph/new-project-task-graph.json")
MAPPING_PATH = Path("docs/phase4/task-map-graph/task-map-mapping.json")
OUT_PATH = Path("docs/phase4/task-map-graph/task-map-graph.json")
HTML_PATH = Path("docs/phase4/task-map-graph/task-map-graph.html")
EXPECTED_IMMUTABLE = {
    "knowledge-graph/phase2-reference-docs/semantic/graph.json": {
        "blob": "a43c1732e85eeebdf83709b9d76233e59ae1a1af",
        "sha256": "f16e684dc773e9bf053e51da2a0a37e3b5ffaf88809e1b5d37f8befbf69e1c93",
    },
    str(CODE_PATH): {
        "blob": "c19d700b408206458d56798809ec1c7009e08acc",
        "sha256": "0a496833d1a58a6d07e58f3d5d2b59f2c0306a924d8573a687fc4067c549c982",
    },
    str(TASK_PATH): {
        "blob": "2393556b74016a437d9a126bee3b04cdcc42be25",
        "sha256": "deb940949583007628dccb89de538c8f3b278aef1c6f99d1386f613f107fa0f7",
    },
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha(path: Path) -> str:
    return subprocess.check_output(["git", "hash-object", str(path)], cwd=ROOT, text=True).strip()


def stable_id(prefix: str, value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return f"{prefix}:{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:20]}"


def source_node_id(kind: str, node_id: str) -> str:
    return f"CODE:{node_id}" if kind == "code" else node_id


def source_ref(artifact: str, collection: str, index: int) -> dict[str, Any]:
    return {"artifact": artifact, "collection": collection, "index": index}


def publish_outputs(outputs: list[tuple[Path, bytes]]) -> None:
    """Stage all outputs before replacement and roll back ordinary replace failures."""
    staged: list[dict[str, Any]] = []
    published: list[Path] = []
    try:
        for target, payload in outputs:
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                previous_bytes = target.read_bytes()
                mode = S_IMODE(target.stat().st_mode)
            else:
                previous_bytes = None
                mode = 0o644
            with tempfile.NamedTemporaryFile(
                dir=target.parent, prefix=f".{target.name}.", delete=False
            ) as handle:
                temporary = Path(handle.name)
                entry = {"temporary": temporary, "target": target, "backup": None}
                staged.append(entry)
                os.chmod(temporary, mode)
                handle.write(payload)
                handle.flush()
                file_fsync(handle.fileno())
            if previous_bytes is not None:
                with tempfile.NamedTemporaryFile(
                    dir=target.parent, prefix=f".{target.name}.backup.", delete=False
                ) as handle:
                    backup = Path(handle.name)
                    entry["backup"] = backup
                    os.chmod(backup, mode)
                    handle.write(previous_bytes)
                    handle.flush()
                    file_fsync(handle.fileno())

        for entry in staged:
            atomic_replace(entry["temporary"], entry["target"])
            target = entry["target"]
            published.append(target)

        for parent in {entry["target"].parent for entry in staged}:
            if hasattr(os, "O_DIRECTORY"):
                descriptor = os.open(parent, os.O_RDONLY | os.O_DIRECTORY)
                try:
                    directory_fsync(descriptor)
                finally:
                    os.close(descriptor)
    except BaseException as error:
        rollback_errors = []
        for target in reversed(published):
            entry = next(item for item in staged if item["target"] == target)
            backup = entry["backup"]
            try:
                if backup is None:
                    target.unlink(missing_ok=True)
                else:
                    atomic_replace(backup, target)
                    entry["backup"] = None
            except OSError as rollback_error:
                rollback_errors.append(f"{target}: {rollback_error}")
        if rollback_errors:
            raise OSError(
                f"publication failed: {error}; rollback also failed: {'; '.join(rollback_errors)}"
            ) from error
        raise
    finally:
        for entry in staged:
            entry["temporary"].unlink(missing_ok=True)
            if entry["backup"] is not None:
                entry["backup"].unlink(missing_ok=True)


def html_document(graph_json: str) -> str:
    # Escape HTML closing tags in source text before placing JSON in a script
    # element. This keeps the document standalone and safe to open with file://.
    safe_json = graph_json.replace("</", "<\\/")
    return r'''<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>گراف ترکیبی نقشهٔ تسک شهاب</title>
<style>
:root{color-scheme:dark;--bg:#101519;--panel:#182126;--line:#2d3b40;--text:#e8f0ed;--muted:#9aacaa;--accent:#24c49a;--blue:#65a9ff;--orange:#ffb45c;--purple:#c69aff;--red:#ff7182}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:14px/1.55 system-ui,"Segoe UI",sans-serif;overflow:hidden}header{height:56px;padding:10px 16px;border-bottom:1px solid var(--line);display:flex;align-items:center;gap:14px;background:#121a1e}header strong{font-size:17px}header span{color:var(--muted);font-size:12px}.layout{height:calc(100vh - 56px);display:grid;grid-template-columns:310px minmax(0,1fr) 350px}.panel{overflow:auto;background:var(--panel);padding:14px;border-inline-start:1px solid var(--line)}.panel h2{font-size:15px;margin:0 0 12px}.field{margin:0 0 10px}.field label{display:block;font-size:12px;color:var(--muted);margin-bottom:4px}.field input,.field select{width:100%;padding:8px 9px;background:#0e1518;border:1px solid #35454a;border-radius:7px;color:var(--text);outline:none}.field input:focus,.field select:focus{border-color:var(--accent)}.check{display:flex;align-items:center;gap:8px;margin:6px 0;color:var(--muted);font-size:12px}.actions{display:flex;gap:6px;flex-wrap:wrap;margin:10px 0}.actions button{padding:6px 9px;border-radius:6px;border:1px solid #3b4b50;background:#202d32;color:var(--text);cursor:pointer}.actions button:hover{border-color:var(--accent)}.canvasWrap{position:relative;min-width:0;min-height:0;background:#0c1114}.canvasWrap canvas{display:block;width:100%;height:100%;cursor:grab}.canvasWrap canvas.dragging{cursor:grabbing}.hud{position:absolute;bottom:10px;right:12px;background:#10191ddd;border:1px solid #304146;border-radius:7px;padding:6px 10px;color:var(--muted);font-size:11px;pointer-events:none}.legend{display:flex;gap:8px;flex-wrap:wrap;font-size:11px;color:var(--muted);margin:10px 0}.dot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-left:4px}.card{border-top:1px solid var(--line);padding-top:10px;margin-top:10px}.meta{color:var(--muted);font-size:12px;overflow-wrap:anywhere}.pill{display:inline-block;border:1px solid #3c5055;border-radius:999px;padding:2px 7px;font-size:11px;margin:2px;color:#c7d7d2}.linklist{display:grid;gap:4px;max-height:180px;overflow:auto}.linklist button{background:#11191c;border:1px solid #2b3a3f;color:var(--text);text-align:right;padding:6px;border-radius:5px;cursor:pointer;font-size:11px}.linklist button:hover{border-color:var(--accent)}pre{white-space:pre-wrap;word-break:break-word;font-size:11px;color:#c3d1cd;background:#101619;padding:8px;border-radius:6px;max-height:300px;overflow:auto}.stats{font-size:12px;color:var(--muted);line-height:1.8}.hint{font-size:11px;color:var(--muted)}.empty{color:var(--muted);font-size:12px}.badge{color:var(--accent)}@media(max-width:1050px){.layout{grid-template-columns:260px minmax(0,1fr)}.right{display:none}}@media(max-width:650px){body{overflow:auto}.layout{height:auto;min-height:calc(100vh - 56px);grid-template-columns:1fr}.left{max-height:42vh}.canvasWrap{height:60vh}.right{display:block;max-height:55vh}}
</style>
</head>
<body>
<header><strong>گراف ترکیبی نقشهٔ تسک شهاب</strong><span id="summary"></span></header>
<main class="layout">
<aside class="panel left">
<h2>جست‌وجو و فیلتر</h2>
<div class="field"><label for="search">شناسه یا نام گره</label><input id="search" placeholder="مثلاً C05A:003 یا نام..." autocomplete="off"></div>
<div class="field"><label for="domain">Domain</label><select id="domain"><option value="">همه</option></select></div>
<div class="field"><label for="package">Package</label><select id="package"><option value="">همه</option></select></div>
<div class="field"><label for="community">Community</label><select id="community"><option value="">همه</option></select></div>
<div class="field"><label for="nodeType">نوع گره</label><select id="nodeType"><option value="">همه</option></select></div>
<div class="field"><label for="relation">نوع رابطه</label><select id="relation"><option value="">همه</option></select></div>
<div class="field"><label for="mapping">وضعیت Mapping</label><select id="mapping"><option value="">همه</option><option>MAPPED</option><option>PARTIALLY_MAPPED</option><option>NEW_IMPLEMENTATION</option></select></div>
<label class="check"><input type="checkbox" id="decisions" checked> نمایش تصمیم‌های باز</label>
<label class="check"><input type="checkbox" id="crossOnly"> فقط اتصال به کد، دامنهٔ تصمیم یا روابط میان بسته‌ها و مراجع</label>
<div class="actions"><button id="fit">نمایش کل</button><button id="zin">بزرگ‌نمایی +</button><button id="zout">کوچک‌نمایی −</button><button id="clear">پاک‌کردن انتخاب</button></div>
<div class="legend"><span><i class="dot" style="background:#65a9ff"></i>کد فعلی</span><span><i class="dot" style="background:#24c49a"></i>Package/Task</span><span><i class="dot" style="background:#ffb45c"></i>تصمیم باز</span><span><i class="dot" style="background:#c69aff"></i>مرجع قرارداد/تصمیم</span></div>
<div class="legend"><span>خط ممتد: CONFIRMED</span><span>خط‌چین: OPEN/BLOCKED/SOURCE_SCOPED</span></div>
<div class="card stats" id="stats"></div>
<p class="hint">برای حرکت، بکشید؛ برای بزرگ‌نمایی از چرخ ماوس استفاده کنید. انتخاب گره یا خط، شواهد و همسایه‌ها را نشان می‌دهد.</p>
</aside>
<section class="canvasWrap"><canvas id="graph"></canvas><div class="hud" id="hud">در حال آماده‌سازی نمایش…</div></section>
<aside class="panel right"><h2>جزئیات انتخاب</h2><div id="details" class="empty">گره یا رابطه‌ای را انتخاب کنید.</div></aside>
</main>
<script id="graph-data" type="application/json">''' + safe_json + r'''</script>
<script>
window.taskMapGraphReady=(async()=>{
const G=JSON.parse(document.getElementById('graph-data').textContent), nodes=G.nodes, edges=G.edges;
const sourceSnapshots={};
for(const [key,payload] of Object.entries(G.source_payloads||{})){
 const bytes=Uint8Array.from(atob(payload.data),c=>c.charCodeAt(0));
 const stream=new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'));
 const text=await new Response(stream).text();
 if(text.length===0)throw new Error('Source snapshot decompressed empty: '+key);
 sourceSnapshots[key]=JSON.parse(text);
}
function resolveSource(ref){if(!ref)return null;let obj=sourceSnapshots[ref.artifact];if(!obj)return null;for(const key of String(ref.collection||'').split('.'))obj=obj?.[key];return obj?.[ref.index]??null}
const byId=new Map(nodes.map(n=>[n.id,n])), pos=new Map(), out=new Map(), inc=new Map();
for(const e of edges){if(!out.has(e.source))out.set(e.source,[]);if(!inc.has(e.target))inc.set(e.target,[]);out.get(e.source).push(e);inc.get(e.target).push(e)}
const cvs=document.getElementById('graph'),ctx=cvs.getContext('2d'),wrap=cvs.parentElement;
let dpr=1,scale=.48,tx=0,ty=0,selected=null,selectedEdge=null,drag=null,frame=null,visibleNodes=[],visibleEdges=[],crossOnly=false,visibleEdgeSet=new Set();
const world={w:2600,h:1850};
function hash(s){let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)}return h>>>0}
const codeGroups=new Map();for(const n of nodes)if(n.node_type==='CODE'){const k=n.community_id||'unknown';if(!codeGroups.has(k))codeGroups.set(k,[]);codeGroups.get(k).push(n)}
const groups=[...codeGroups.entries()].sort((a,b)=>String(a[0]).localeCompare(String(b[0]),undefined,{numeric:true}));
const cols=14, codeX0=80, codeY0=100, cellW=76, cellH=126;
groups.forEach(([k,arr],gi)=>{const cx=codeX0+(gi%cols)*cellW,cy=codeY0+Math.floor(gi/cols)*cellH;arr.forEach((n,i)=>{const h=hash(n.id),ang=(i*2.399963)+(h%1000)/1000,rad=10+Math.sqrt(i+1)*7+(h%13);pos.set(n.id,{x:cx+Math.cos(ang)*rad,y:cy+Math.sin(ang)*rad})})});
const packageNodes=nodes.filter(n=>n.node_type==='PACKAGE').sort((a,b)=>String(a.package_id).localeCompare(String(b.package_id),undefined,{numeric:true}));
const taskGroups=new Map();for(const n of nodes){if(['TASK','SUBTASK'].includes(n.node_type)){const p=n.package_id||(n.source_data&&n.source_data.package_id)||((n.parent_id||'').startsWith('PACKAGE:')?(n.parent_id||'').split(':').slice(1).join(':'):null);if(p){if(!taskGroups.has(p))taskGroups.set(p,[]);taskGroups.get(p).push(n)}}}
const gridCols=7, packageCenters=new Map();packageNodes.forEach((p,i)=>{const col=i%gridCols,row=Math.floor(i/gridCols),cx=1350+col*175,cy=140+row*285;packageCenters.set(p.package_id,{x:cx,y:cy});pos.set(p.id,{x:cx,y:cy});const arr=(taskGroups.get(p.package_id)||[]).filter(n=>n.node_type==='TASK');arr.forEach((n,j)=>{const h=hash(n.id),ang=2*Math.PI*j/Math.max(arr.length,1),r=43+(h%22);pos.set(n.id,{x:cx+Math.cos(ang)*r,y:cy+Math.sin(ang)*r});for(const s of (taskGroups.get(p.package_id)||[]).filter(s=>s.node_type==='SUBTASK'&&s.parent_id===n.id)){const sh=hash(s.id),sa=(sh%6283)/1000,sr=67+(sh%38);pos.set(s.id,{x:cx+Math.cos(ang)*r+Math.cos(sa)*sr,y:cy+Math.sin(ang)*r+Math.sin(sa)*sr})}})});
for(const n of nodes)if(n.node_type==='OPEN_DECISION'||n.node_type.endsWith('_REFERENCE')){const es=[...(out.get(n.id)||[]),...(inc.get(n.id)||[])];let targets=es.map(e=>byId.get(e.source===n.id?e.target:e.source)).filter(Boolean),p=targets.map(x=>pos.get(x.id)).filter(Boolean);if(p.length){pos.set(n.id,{x:p.reduce((a,v)=>a+v.x,0)/p.length+(hash(n.id)%40)-20,y:p.reduce((a,v)=>a+v.y,0)/p.length+(hash(n.id)%34)-17})}else pos.set(n.id,{x:1250+(hash(n.id)%200),y:1600+(hash(n.id)%180)})}
for(const n of nodes)if(!pos.has(n.id)){const h=hash(n.id);pos.set(n.id,{x:80+h%1050,y:100+(h>>>10)%1600})}
function val(id){return document.getElementById(id).value}
function matchesNode(n){if(document.getElementById('decisions').checked===false&&n.node_type==='OPEN_DECISION')return false;if(val('domain')&&n.domain!==val('domain'))return false;if(val('package')){const p=val('package');if(n.package_id!==p&&!(n.mapped_package_refs||[]).includes('PACKAGE:'+p)&&!(n.id==='PACKAGE:'+p))return false}if(val('community')&&n.community_id!==val('community'))return false;if(val('nodeType')&&n.node_type!==val('nodeType'))return false;if(val('mapping')&&n.mapping_status!==val('mapping')&&!(n.mapping_statuses||[]).includes(val('mapping')))return false;return true}
function isCrossEdge(e){
 if(e.origin_graph==='task_mapping'||e.origin_graph==='decision_scope')return true;
 if(e.origin_graph!=='relation_overlay'&&e.origin_graph!=='new_project_task_graph')return false;
 const source=byId.get(e.source),target=byId.get(e.target);
 return e.relation_type!=='contains'&&(
  (source.package_id&&target.package_id&&source.package_id!==target.package_id)||
  (e.origin_graph==='relation_overlay'&&(source.node_type.endsWith('_REFERENCE')||target.node_type.endsWith('_REFERENCE')))
 );
}
function rebuild(){
 const wasCrossOnly=crossOnly;
 crossOnly=document.getElementById('crossOnly').checked;
 visibleNodes=nodes.filter(matchesNode);
 const eligible=new Set(visibleNodes.map(n=>n.id)),rel=val('relation');
 visibleEdges=edges.filter(e=>eligible.has(e.source)&&eligible.has(e.target)&&(!rel||e.relation_type===rel)&&(!crossOnly||isCrossEdge(e)));
 visibleEdgeSet=new Set(crossOnly?visibleEdges:[]);
 if(crossOnly){
  const endpoints=new Set(visibleEdges.flatMap(e=>[e.source,e.target]));
  visibleNodes=visibleNodes.filter(n=>endpoints.has(n.id));
 }
 const selectedNodeVisible=selected&&visibleNodes.some(n=>n.id===selected);
 const selectedEdgeVisible=selectedEdge&&visibleEdges.includes(selectedEdge);
 if((selected&&!selectedNodeVisible)||(selectedEdge&&!selectedEdgeVisible)){
  selected=null;selectedEdge=null;showSelection(null);
 }else if(crossOnly||wasCrossOnly){
  if(selected)showSelection({node:byId.get(selected)});
  else if(selectedEdge)showSelection({edge:selectedEdge});
 }
 document.getElementById('hud').textContent=`${visibleNodes.length.toLocaleString()} گره · ${visibleEdges.length.toLocaleString()} رابطه`;
 invalidate();
}
function selectionEdges(index,id){const incident=index.get(id)||[];return crossOnly?incident.filter(e=>visibleEdgeSet.has(e)):incident}
function invalidate(){if(frame===null)frame=requestAnimationFrame(draw)}
function resize(){dpr=window.devicePixelRatio||1;cvs.width=Math.max(1,wrap.clientWidth*dpr);cvs.height=Math.max(1,wrap.clientHeight*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);invalidate()}new ResizeObserver(resize).observe(wrap);resize();
function color(n){if(n.node_type==='CODE')return '#65a9ff';if(n.node_type==='OPEN_DECISION')return '#ffb45c';if(n.node_type.endsWith('_REFERENCE'))return '#c69aff';if(n.node_type==='PACKAGE')return '#16d6a1';if(n.node_type==='TASK')return '#4ce0b5';if(n.node_type==='SUBTASK')return '#8ce9d0';return '#a8b8b2'}
function radius(n){return n.node_type==='PACKAGE'?8:n.node_type==='TASK'?4.5:n.node_type==='SUBTASK'?2.4:n.node_type==='OPEN_DECISION'?4:n.node_type==='CODE'?2.2:5}
function resizeTransform(){const w=wrap.clientWidth,h=wrap.clientHeight;return {w,h}}
function draw(){frame=null;const {w,h}=resizeTransform();ctx.clearRect(0,0,w,h);ctx.save();ctx.translate(tx,ty);ctx.scale(scale,scale);
const focus=selected||selectedEdge?.source||null;const neighbors=focus?new Set([focus,...selectionEdges(out,focus).map(e=>e.target),...selectionEdges(inc,focus).map(e=>e.source)]):null;
ctx.lineWidth=1/scale;
for(const e of visibleEdges){const a=pos.get(e.source),b=pos.get(e.target);if(!a||!b)continue;const emph=selectedEdge?.id===e.id||(neighbors&&e.source===focus||neighbors&&e.target===focus);ctx.globalAlpha=emph?.9:(e.origin_graph==='relation_overlay'||e.origin_graph==='task_mapping'||e.origin_graph==='decision_scope'?.45:.12);ctx.strokeStyle=e.origin_graph==='current_project_code_graph'?'#66829a':e.origin_graph==='decision_scope'?'#c99b62':e.origin_graph==='task_mapping'?'#51d7b2':'#89a99d';ctx.setLineDash(['OPEN','BLOCKED','SOURCE_SCOPED','BLOCKED_BY_DECISION'].includes(e.confidence)||['SOURCE_SCOPED','BLOCKED_BY_DECISION'].includes(e.resolution_status)?[5/scale,4/scale]:[]);ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();if(emph){const ang=Math.atan2(b.y-a.y,b.x-a.x),r=radius(byId.get(e.target)||{node_type:'TASK'})+3;ctx.setLineDash([]);ctx.fillStyle=ctx.strokeStyle;ctx.beginPath();ctx.moveTo(b.x,b.y);ctx.lineTo(b.x-r*Math.cos(ang-.45),b.y-r*Math.sin(ang-.45));ctx.lineTo(b.x-r*Math.cos(ang+.45),b.y-r*Math.sin(ang+.45));ctx.closePath();ctx.fill()}}
const q=document.getElementById('search').value.trim().toLowerCase();for(const n of visibleNodes){const p=pos.get(n.id);if(!p)continue;const match=q&&(n.id.toLowerCase().includes(q)||String(n.label||'').toLowerCase().includes(q));ctx.globalAlpha=(focus&&neighbors&&!neighbors.has(n.id))?.22:(q&&!match?.18:1);ctx.fillStyle=color(n);ctx.beginPath();ctx.arc(p.x,p.y,radius(n)+(selected===n.id?3:match?2:0),0,Math.PI*2);ctx.fill();if(selected===n.id||match){ctx.strokeStyle='#fff';ctx.lineWidth=1.5/scale;ctx.stroke()}}
ctx.restore()}
function fit(){const {w,h}=resizeTransform(),pad=40;scale=Math.min((w-pad*2)/world.w,(h-pad*2)/world.h);tx=(w-world.w*scale)/2;ty=(h-world.h*scale)/2;invalidate()}setTimeout(fit,0);
function screenToWorld(x,y){return {x:(x-tx)/scale,y:(y-ty)/scale}}
function pick(x,y){const p=screenToWorld(x,y);let best=null,bd=Infinity;for(const n of visibleNodes){const q=pos.get(n.id),d=Math.hypot(p.x-q.x,p.y-q.y);if(d<Math.max(8/scale,radius(n)+4)&&d<bd){best=n;bd=d}}if(best)return {node:best};let be=null;bd=Infinity;for(const e of visibleEdges){const a=pos.get(e.source),b=pos.get(e.target),dx=b.x-a.x,dy=b.y-a.y,l=dx*dx+dy*dy,t=Math.max(0,Math.min(1,((p.x-a.x)*dx+(p.y-a.y)*dy)/(l||1))),d=Math.hypot(p.x-(a.x+t*dx),p.y-(a.y+t*dy));if(d<5/scale&&d<bd){be=e;bd=d}}return be?{edge:be}:null}
cvs.addEventListener('pointerdown',e=>{cvs.setPointerCapture(e.pointerId);drag={x:e.offsetX,y:e.offsetY,tx,ty,moved:false};cvs.classList.add('dragging')});cvs.addEventListener('pointermove',e=>{if(drag){const dx=e.offsetX-drag.x,dy=e.offsetY-drag.y;if(Math.abs(dx)+Math.abs(dy)>3)drag.moved=true;tx=drag.tx+dx;ty=drag.ty+dy;invalidate()}});cvs.addEventListener('pointerup',e=>{cvs.classList.remove('dragging');if(drag&&!drag.moved){const p=pick(e.offsetX,e.offsetY);selected=p?.node?.id||null;selectedEdge=p?.edge||null;showSelection(p)}drag=null});cvs.addEventListener('wheel',e=>{e.preventDefault();const old=scale,f=e.deltaY<0?1.12:.89,wx=(e.offsetX-tx)/old,wy=(e.offsetY-ty)/old;scale=Math.max(.08,Math.min(3,scale*f));tx=e.offsetX-wx*scale;ty=e.offsetY-wy*scale;invalidate()},{passive:false});
function esc(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function showSelection(p){const box=document.getElementById('details');if(!p){box.innerHTML='<div class="empty">گره یا رابطه‌ای را انتخاب کنید.</div>';invalidate();return}let obj=p.node||p.edge,id=p.node?.id||p.edge?.id,title=p.node?.label||p.edge?.relation_type||id;let details=`<div><span class="pill">${esc(p.node?.node_type||'RELATION')}</span><span class="pill">${esc(p.node?.mapping_status||p.edge?.execution_effect||'')}</span></div><h3>${esc(title)}</h3><div class="meta">${esc(id)}</div>`;if(p.node){const list=[...selectionEdges(out,id).map(e=>({n:byId.get(e.target),e,direction:'خروجی'})),...selectionEdges(inc,id).map(e=>({n:byId.get(e.source),e,direction:'ورودی'}))];details+=`<div class="card"><b>همسایه‌ها (${list.length})</b><div class="linklist">${list.slice(0,250).map(x=>`<button data-node="${esc(x.n?.id)}">${esc(x.direction)} · ${esc(x.e.relation_type)} · ${esc(x.n?.label||x.n?.id)}</button>`).join('')}${list.length>250?'<span class="hint">برای کارایی فقط ۲۵۰ مورد نخست نمایش داده شده است.</span>':''}</div></div>`;const sourceData=resolveSource(p.node.source_ref)??p.node.source_data??null,mappingData=resolveSource(p.node.mapping_ref),labelEvidence=resolveSource(p.node.label_evidence_ref),specialReview=resolveSource(p.node.special_reference_review_ref);details+=`<div class="card"><b>جزئیات و شواهد منبع</b><pre>${esc(JSON.stringify({mapping_status:p.node.mapping_status,mapping_type:p.node.mapping_type,domain:p.node.domain,package_id:p.node.package_id,community_id:p.node.community_id,decision_status:p.node.decision_status,source_data:sourceData,mapping_data: mappingData ?? p.node.mapping_data ?? null,label_evidence:labelEvidence,special_reference_review:specialReview},null,2))}</pre></div>`}else{const sourceData=resolveSource(obj.source_ref);details+=`<div class="card"><b>مبدأ ← مقصد</b><p class="meta">${esc(byId.get(obj.source)?.label||obj.source)} ← ${esc(byId.get(obj.target)?.label||obj.target)}</p></div><div class="card"><b>جزئیات رابطه و شواهد</b><pre>${esc(JSON.stringify(sourceData||obj,null,2))}</pre></div>`}box.innerHTML=details;box.querySelectorAll('[data-node]').forEach(b=>b.addEventListener('click',()=>{selected=b.dataset.node;selectedEdge=null;showSelection({node:byId.get(selected)})}));invalidate()}
function focusSearch(){const q=document.getElementById('search').value.trim().toLowerCase();if(!q)return;const found=visibleNodes.filter(n=>n.id.toLowerCase()===q||String(n.label||'').toLowerCase()===q);const matches=found.length?found:visibleNodes.filter(n=>n.id.toLowerCase().includes(q)||String(n.label||'').toLowerCase().includes(q));if(matches.length!==1)return;const n=matches[0],p=pos.get(n.id),w=wrap.clientWidth,h=wrap.clientHeight;selected=n.id;selectedEdge=null;scale=Math.max(scale,.65);tx=w/2-p.x*scale;ty=h/2-p.y*scale;showSelection({node:n})}
for(const id of ['search','domain','package','community','nodeType','relation','mapping','decisions','crossOnly'])document.getElementById(id).addEventListener('input',rebuild);for(const id of ['domain','package','community','nodeType','relation','mapping','decisions','crossOnly'])document.getElementById(id).addEventListener('change',rebuild);document.getElementById('search').addEventListener('keydown',e=>{if(e.key==='Enter')focusSearch()});
document.getElementById('fit').onclick=fit;document.getElementById('zin').onclick=()=>{scale=Math.min(3,scale*1.2);invalidate()};document.getElementById('zout').onclick=()=>{scale=Math.max(.08,scale/1.2);invalidate()};document.getElementById('clear').onclick=()=>{selected=null;selectedEdge=null;showSelection(null)};
function addOptions(id,values){const s=document.getElementById(id);for(const v of [...new Set(values.filter(Boolean))].sort((a,b)=>String(a).localeCompare(String(b),undefined,{numeric:true}))){const o=document.createElement('option');o.value=v;o.textContent=v;s.appendChild(o)}}
addOptions('domain',nodes.map(n=>n.domain));addOptions('package',nodes.map(n=>n.package_id||n.mapped_package_refs?.map(x=>x.replace('PACKAGE:',''))||[]).flat());addOptions('community',nodes.map(n=>n.community_id));addOptions('nodeType',nodes.map(n=>n.node_type));addOptions('relation',edges.map(e=>e.relation_type));
document.getElementById('summary').textContent=`${G.counts.node_total.toLocaleString()} گره · ${G.counts.edge_total.toLocaleString()} رابطه · ${G.counts.communities} Community`;
document.getElementById('stats').innerHTML=`<b class="badge">ورودی‌ها</b><br>کد فعلی: ${G.source_inputs.current_project_code_graph.node_count.toLocaleString()} گره / ${G.source_inputs.current_project_code_graph.edge_count.toLocaleString()} رابطه<br>گراف تسک: ${G.source_inputs.new_project_task_graph.node_count.toLocaleString()} گره / ${G.source_inputs.new_project_task_graph.edge_count.toLocaleString()} رابطه<br>Overlay: ${G.source_inputs.task_map_mapping.relation_overlay_count} رابطه<br>تصمیم باز: ${G.source_inputs.task_map_mapping.open_decision_count}<br><br><b class="badge">Mapping</b><br>MAPPED: ${nodes.filter(n=>n.mapping_status==='MAPPED').length}<br>PARTIALLY_MAPPED: ${nodes.filter(n=>n.mapping_status==='PARTIALLY_MAPPED').length}<br>NEW_IMPLEMENTATION: ${nodes.filter(n=>n.mapping_status==='NEW_IMPLEMENTATION').length}`;
rebuild();
})().catch(e=>{const h=document.getElementById('hud');if(h)h.textContent='خطا در آماده‌سازی منبع گراف: '+e.message;throw e});
</script>
</body></html>
'''


def build() -> dict[str, Any]:
    code = load_json(ROOT / CODE_PATH)
    task = load_json(ROOT / TASK_PATH)
    mapping = load_json(ROOT / MAPPING_PATH)
    errors: list[str] = []

    # These are immutable source artifacts. The task graph and code graph are
    # included byte-for-byte as source_data; the semantic graph is SHA-checked.
    source_fingerprints = {}
    for rel, expected in EXPECTED_IMMUTABLE.items():
        path = ROOT / rel
        actual_sha = sha256(path)
        actual_blob = git_blob_sha(path)
        source_fingerprints[rel] = {"git_blob_sha": actual_blob, "sha256": actual_sha}
        if actual_blob != expected["blob"] or actual_sha != expected["sha256"]:
            errors.append(f"immutable input changed: {rel}")

    code_nodes = code.get("nodes", [])
    code_links = code.get("links", [])
    task_nodes = task.get("nodes", [])
    task_edges = task.get("edges", [])
    mappings = mapping.get("mappings", [])
    overlay = mapping.get("stage4_relation_overlay", {}).get("relations", [])
    decisions = mapping.get("open_decision_references", [])
    task_label_overrides = {str(x.get("task_ref")): x for x in mapping.get("task_name_evidence_overrides", []) if x.get("task_ref")}
    special_decision_reviews = {str(x.get("open_decision_id")): x for x in mapping.get("required_22_reference_review", []) if x.get("open_decision_id")}

    code_by_id = {str(n.get("id")): n for n in code_nodes}
    task_by_id = {str(n.get("id")): n for n in task_nodes}
    if len(code_by_id) != len(code_nodes):
        errors.append("duplicate code-node ids")
    if len(task_by_id) != len(task_nodes):
        errors.append("duplicate task-graph node ids")
    if len({m.get("entity_ref") or m.get("task_ref") or m.get("package_ref") or m.get("subtask_ref") for m in mappings}) < len(mappings):
        # Different mapping schemas use entity-specific refs; exact duplicate check below is canonical.
        pass
    mapping_by_id: dict[str, dict[str, Any]] = {}
    mapping_index_by_id: dict[str, int] = {}
    for mapping_index, m in enumerate(mappings):
        mid = m.get("entity_ref") or m.get("subtask_ref") or m.get("task_ref") or m.get("package_ref")
        if not mid:
            errors.append("mapping row missing canonical entity reference")
        elif mid in mapping_by_id:
            errors.append(f"duplicate mapping entity: {mid}")
        else:
            mapping_by_id[mid] = m
            mapping_index_by_id[mid] = mapping_index
    if set(mapping_by_id) != set(task_by_id):
        errors.append(f"mapping/task node coverage mismatch: mapping_only={len(set(mapping_by_id)-set(task_by_id))}, task_only={len(set(task_by_id)-set(mapping_by_id))}")

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    code_ids = set(code_by_id)
    task_ids = set(task_by_id)
    community_members: dict[str, list[str]] = defaultdict(list)

    for index, item in enumerate(code_nodes):
        raw_id = str(item["id"])
        cid = source_node_id("code", raw_id)
        community = item.get("community")
        community_key = str(community) if community is not None else None
        if community_key is not None:
            community_members[community_key].append(cid)
        nodes.append({
            "id": cid,
            "canonical_id": raw_id,
            "source_id": raw_id,
            "node_type": "CODE",
            "origin_graph": "current_project_code_graph",
            "label": item.get("label") or raw_id,
            "domain": None,
            "package_id": None,
            "community_id": community_key,
            "mapping_status": None,
            "source_index": index,
            "source_ref": source_ref("current_project_code_graph", "nodes", index),
        })

    for index, item in enumerate(task_nodes):
        raw_id = str(item["id"])
        m = mapping_by_id.get(raw_id, {})
        node_type = str(item.get("node_type", "UNKNOWN"))
        label_override = task_label_overrides.get(raw_id)
        nodes.append({
            "id": raw_id,
            "canonical_id": raw_id,
            "source_id": raw_id,
            "node_type": node_type,
            "origin_graph": "new_project_task_graph",
            "label": (label_override or {}).get("resolved_label") or item.get("name") or raw_id,
            "label_evidence_ref": source_ref("task_map_mapping", "task_name_evidence_overrides", next((j for j, x in enumerate(mapping.get("task_name_evidence_overrides", [])) if x.get("task_ref") == raw_id), -1)) if label_override else None,
            "domain": item.get("domain"),
            "package_id": item.get("package_id") or (raw_id.split(":", 1)[-1] if node_type == "PACKAGE" else None),
            "parent_id": item.get("parent_id"),
            "community_id": None,
            "mapping_status": m.get("mapping_status"),
            "mapping_type": m.get("mapping_type"),
            "mapping_confidence": m.get("confidence"),
            "current_code_node_refs": m.get("current_code_node_refs", []),
            "source_index": index,
            "source_ref": source_ref("new_project_task_graph", "nodes", index),
            "mapping_ref": source_ref("task_map_mapping", "mappings", mapping_index_by_id[raw_id]),
        })

    # The prior audit intentionally kept some explicit contract/decision
    # endpoints as references rather than adding them to the task graph. Keep
    # those endpoints visible as reference nodes in the combined graph.
    external_refs: dict[str, dict[str, Any]] = {}
    for relation in overlay:
        for field in ("source_node", "target_node"):
            ref = relation.get(field)
            if not ref or ref in task_by_id:
                continue
            kind = relation.get("target_kind") if field == "target_node" else None
            if str(ref).startswith("CONTRACT:"):
                node_type = "CONTRACT_REFERENCE"
            elif str(ref).startswith("DECISION:"):
                node_type = "DECISION_REFERENCE"
            else:
                continue
            entry = external_refs.setdefault(str(ref), {"id": str(ref), "node_type": node_type, "labels": [], "relation_ids": []})
            entry["labels"].append(str(relation.get("rationale", "")))
            entry["relation_ids"].append(relation.get("relation_id"))
            if kind:
                entry["declared_target_kind"] = kind
    for ref in sorted(external_refs):
        item = external_refs[ref]
        nodes.append({
            "id": ref,
            "canonical_id": ref,
            "source_id": ref,
            "node_type": item["node_type"],
            "origin_graph": "relation_overlay_reference",
            "label": ref,
            "domain": None,
            "package_id": None,
            "community_id": None,
            "mapping_status": None,
            "declared_target_kind": item.get("declared_target_kind"),
            "source_data": {"canonical_reference": ref, "relation_ids": item["relation_ids"]},
        })

    # Code communities are retained as first-class graph metadata, preserving
    # the source community identifiers and labels without inventing clusters.
    communities = []
    community_labels = {}
    community_canonical_ids = {}
    for n in code_nodes:
        if n.get("community") is not None:
            key = str(n["community"])
            community_labels.setdefault(key, n.get("community_name") or f"Community {n['community']}")
            community_canonical_ids.setdefault(key, n["community"])
    for key in sorted(community_members, key=lambda x: (not x.isdigit(), int(x) if x.isdigit() else x)):
        communities.append({
            "id": key,
            "canonical_id": community_canonical_ids.get(key, key),
            "label": community_labels.get(key, f"Community {key}"),
            "origin_graph": "current_project_code_graph",
            "member_node_ids": community_members[key],
            "source_data": {"community": community_canonical_ids.get(key, key), "community_name": community_labels.get(key)},
        })

    def add_edge(origin: str, raw: dict[str, Any], source_id: str, target_id: str,
                 edge_type: str, index: int, certainty: str | None = None,
                 raw_ref: dict[str, Any] | None = None) -> None:
        if source_id not in node_id_set or target_id not in node_id_set:
            errors.append(f"invalid edge endpoint in {origin}[{index}]: {source_id} -> {target_id}")
            return
        eid = stable_id("EDGE", {"origin": origin, "index": index, "raw": raw})
        edges.append({
            "id": eid,
            "source": source_id,
            "target": target_id,
            "edge_type": edge_type,
            "relation_type": raw.get("relation_type") or raw.get("relation") or edge_type,
            "origin_graph": origin,
            "certainty": certainty or raw.get("confidence") or raw.get("resolution_status") or "SOURCE_RECORDED",
            "confidence": raw.get("confidence"),
            "execution_effect": raw.get("execution_effect"),
            "resolution_status": raw.get("resolution_status"),
            "locator": raw.get("locator") or raw.get("plan_locator") or raw.get("source_locator"),
            "source_refs": raw.get("source_refs", []),
            "source_index": index,
            "source_ref": raw_ref,
        })

    node_id_set = {n["id"] for n in nodes}
    # Keep each source edge intact and namespace only the code-graph endpoints.
    for i, edge in enumerate(code_links):
        src = source_node_id("code", str(edge.get("source")))
        dst = source_node_id("code", str(edge.get("target")))
        add_edge("current_project_code_graph", edge, src, dst, "code_relation", i,
                 str(edge.get("confidence") or edge.get("_origin") or "EXTRACTED"),
                 source_ref("current_project_code_graph", "links", i))

    for i, edge in enumerate(task_edges):
        add_edge("new_project_task_graph", edge, str(edge.get("source")), str(edge.get("target")),
                 str(edge.get("relation_type", "task_relation")), i,
                 str(edge.get("confidence") or edge.get("resolution_status") or "SOURCE_RECORDED"),
                 source_ref("new_project_task_graph", "edges", i))

    # Relation Overlay endpoints are canonical package/task/subtask IDs.
    for i, edge in enumerate(overlay):
        src = str(edge.get("source_node") or edge.get("source"))
        dst = str(edge.get("target_node") or edge.get("target"))
        add_edge("relation_overlay", edge, src, dst, str(edge.get("relation_type", "overlay_relation")), i,
                 str(edge.get("confidence") or edge.get("resolution_status") or "SOURCE_SCOPED"),
                 source_ref("task_map_mapping", "stage4_relation_overlay.relations", i))

    # Connect explicitly mapped task-graph entities to their code nodes.
    mapping_edges = 0
    for task_id, m in mapping_by_id.items():
        for j, code_ref in enumerate(m.get("current_code_node_refs", [])):
            code_ref = str(code_ref)
            if code_ref not in code_by_id:
                errors.append(f"mapping references missing current-code node: {task_id} -> {code_ref}")
                continue
            raw = {
                "mapping_status": m.get("mapping_status"),
                "mapping_type": m.get("mapping_type"),
                "confidence": m.get("confidence"),
                "mapping_entity_ref": task_id,
                "current_code_node_ref": code_ref,
                "mapping_index": j,
            }
            add_edge("task_mapping", raw, task_id, source_node_id("code", code_ref), "maps_to_code",
                     mapping_edges, str(m.get("mapping_status") or "MAPPING_RECORDED"),
                     source_ref("task_map_mapping", "mappings", mapping_index_by_id[task_id]))
            mapping_edges += 1

    # Product decisions remain OPEN. Their declared Package/Task scope is
    # represented as a relation; no decision is converted into a task edge.
    decision_node_ids: set[str] = set()
    decision_edges = 0
    decision_ids = set()
    decision_index_by_id: dict[str, int] = {}
    for i, decision in enumerate(decisions):
        did = str(decision.get("open_decision_id") or decision.get("decision_id") or "")
        if not did:
            errors.append(f"open decision row {i} lacks canonical id")
            continue
        if did in decision_ids:
            errors.append(f"duplicate open decision id: {did}")
            continue
        decision_ids.add(did)
        decision_index_by_id[did] = i
        decision_node_id = f"DECISION:{did}"
        decision_node_ids.add(decision_node_id)
        node = {
            "id": decision_node_id,
            "canonical_id": did,
            "source_id": did,
            "node_type": "OPEN_DECISION",
            "origin_graph": "task_map_mapping",
            "label": decision.get("decision_reference") or decision.get("candidate_id") or did,
            "domain": None,
            "package_id": None,
            "community_id": None,
            "decision_status": decision.get("decision_status", "OPEN"),
            "mapping_status": decision.get("mapping_status"),
            "mapping_type": decision.get("mapping_type"),
            "confidence": decision.get("confidence"),
            "source_ref": source_ref("task_map_mapping", "open_decision_references", i),
            "special_reference_review_ref": source_ref("task_map_mapping", "required_22_reference_review", next((j for j, x in enumerate(mapping.get("required_22_reference_review", [])) if x.get("open_decision_id") == did), -1)) if did in special_decision_reviews else None,
        }
        nodes.append(node)
        node_id_set.add(decision_node_id)
        if node["decision_status"] != "OPEN":
            errors.append(f"product decision is not OPEN: {did}={node['decision_status']}")
        targets = [(str(x), "decision_scope_task") for x in decision.get("task_refs", [])]
        targets += [(str(x), "decision_scope_package") for x in decision.get("package_refs", [])]
        targets += [(source_node_id("code", str(x)), "decision_code_reference") for x in decision.get("current_code_node_refs", [])]
        targets += [(source_node_id("code", str(x)), "decision_source_graph_reference") for x in decision.get("source_graph_node_refs", []) if str(x) in code_by_id]
        for j, (target, rel) in enumerate(targets):
            if target not in node_id_set:
                errors.append(f"decision scope endpoint missing: {did} -> {target}")
                continue
            raw = {
                "open_decision_id": did,
                "decision_status": node["decision_status"],
                "mapping_status": decision.get("mapping_status"),
                "confidence": decision.get("confidence"),
                "decision_scope_source": "task_map_mapping.open_decision_references",
                "scope_ref": target,
            }
            add_edge("decision_scope", raw, decision_node_id, target, rel, decision_edges, "DECLARED_OPEN_SCOPE")
            edges[-1]["source_ref"] = source_ref("task_map_mapping", "open_decision_references", i)
            decision_edges += 1

    if len(decisions) != 134:
        errors.append(f"expected 134 open decisions, found {len(decisions)}")
    if set(decision_ids) != {str(d.get("open_decision_id") or d.get("decision_id")) for d in decisions}:
        errors.append("decision id coverage mismatch")

    # Validate all relation and code mapping endpoints against the unified IDs.
    if len({n["id"] for n in nodes}) != len(nodes):
        errors.append("duplicate unified node ids")
    all_node_ids = {n["id"] for n in nodes}
    invalid = [e["id"] for e in edges if e["source"] not in all_node_ids or e["target"] not in all_node_ids]
    if invalid:
        errors.append(f"{len(invalid)} unified edge(s) have invalid endpoints")
    if errors:
        raise ValueError("\n".join(errors))

    # Aggregate explicit code mappings onto code nodes for filters and counts.
    reverse_mapping: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for task_id, m in mapping_by_id.items():
        for code_ref in m.get("current_code_node_refs", []):
            reverse_mapping[str(code_ref)].append({
                "task_ref": task_id,
                "package_ref": m.get("package_ref"),
                "mapping_status": m.get("mapping_status"),
            })
    for node in nodes:
        if node["node_type"] == "CODE":
            refs = reverse_mapping.get(node["canonical_id"], [])
            node["mapping_statuses"] = sorted({x["mapping_status"] for x in refs})
            node["mapped_task_refs"] = sorted({x["task_ref"] for x in refs})
            node["mapped_package_refs"] = sorted({x["package_ref"] for x in refs if x.get("package_ref")})

    node_counts = Counter(n["node_type"] for n in nodes)
    node_origin_type: dict[str, Counter[str]] = defaultdict(Counter)
    for node in nodes:
        node_origin_type[node["origin_graph"]][node["node_type"]] += 1
    edge_counts_origin = Counter(e["origin_graph"] for e in edges)
    edge_counts_type = Counter(e["relation_type"] for e in edges)
    edge_origin_type: dict[str, Counter[str]] = defaultdict(Counter)
    for edge in edges:
        edge_origin_type[edge["origin_graph"]][edge["relation_type"]] += 1
    edge_counts_confidence = Counter(e["certainty"] for e in edges)
    edge_counts_execution = Counter(e["execution_effect"] or "UNSPECIFIED" for e in edges)
    code_graph_meta = code.get("graph", {})
    source_payloads = {}
    payloads_lossless = True
    for name, relpath in (("current_project_code_graph", CODE_PATH), ("new_project_task_graph", TASK_PATH), ("task_map_mapping", MAPPING_PATH)):
        raw_bytes = (ROOT / relpath).read_bytes()
        compressed = gzip.compress(raw_bytes, compresslevel=9, mtime=0)
        payloads_lossless = payloads_lossless and gzip.decompress(compressed) == raw_bytes
        source_payloads[name] = {
            "encoding": "gzip+base64",
            "media_type": "application/json",
            "sha256_uncompressed": hashlib.sha256(raw_bytes).hexdigest(),
            "bytes_uncompressed": len(raw_bytes),
            "bytes_compressed": len(compressed),
            "data": base64.b64encode(compressed).decode("ascii"),
        }

    input_objects = {
        "current_project_code_graph": code,
        "new_project_task_graph": task,
        "task_map_mapping": mapping,
    }
    def resolves(ref: dict[str, Any] | None) -> bool:
        if not ref:
            return False
        obj = input_objects.get(ref.get("artifact"))
        if obj is None:
            return False
        for part in str(ref.get("collection", "")).split("."):
            if isinstance(obj, dict):
                obj = obj.get(part)
            else:
                return False
        return isinstance(obj, list) and isinstance(ref.get("index"), int) and 0 <= ref["index"] < len(obj)
    source_refs = [n.get("source_ref") for n in nodes if n.get("source_ref")]
    source_refs += [n.get(k) for n in nodes for k in ("mapping_ref", "label_evidence_ref", "special_reference_review_ref") if n.get(k)]
    source_refs += [e.get("source_ref") for e in edges if e.get("source_ref")]
    invalid_source_refs = [ref for ref in source_refs if not resolves(ref)]
    if invalid_source_refs:
        errors.append(f"{len(invalid_source_refs)} source-data reference(s) do not resolve")
    if not payloads_lossless:
        errors.append("compressed source snapshot failed lossless round-trip")
    if errors:
        raise ValueError("\n".join(errors))

    return {
        "schema_version": "1.0",
        "graph_id": "shahab-stage4-combined-task-map",
        "generated_by": "build_task_map_graph.py",
        "source_inputs": {
            "current_project_code_graph": {"path": str(CODE_PATH), "node_count": len(code_nodes), "edge_count": len(code_links), "source_graph_metadata": code_graph_meta, "directed": code.get("directed"), "multigraph": code.get("multigraph"), "fingerprint": source_fingerprints[str(CODE_PATH)]},
            "new_project_task_graph": {"path": str(TASK_PATH), "node_count": len(task_nodes), "edge_count": len(task_edges), "graph_id": task.get("graph_id"), "source_metadata": {k: v for k, v in task.items() if k not in ("nodes", "edges", "validation")}, "fingerprint": source_fingerprints[str(TASK_PATH)]},
            "task_map_mapping": {"path": str(MAPPING_PATH), "mapping_count": len(mappings), "relation_overlay_count": len(overlay), "open_decision_count": len(decisions), "sha256": sha256(ROOT / MAPPING_PATH), "git_blob_sha": git_blob_sha(ROOT / MAPPING_PATH)},
            "read_only_reference_graph": {"path": "knowledge-graph/phase2-reference-docs/semantic/graph.json", "fingerprint": source_fingerprints["knowledge-graph/phase2-reference-docs/semantic/graph.json"]},
        },
        "mapping_source_metadata": {k: mapping[k] for k in ("schema_version", "mapping_id", "stage", "created_from_head", "source_graphs") if k in mapping},
        "source_payloads": source_payloads,
        "counts": {
            "nodes": dict(sorted(node_counts.items())),
            "nodes_by_origin_and_type": {origin: dict(sorted(counts.items())) for origin, counts in sorted(node_origin_type.items())},
            "node_total": len(nodes),
            "edges_by_origin": dict(sorted(edge_counts_origin.items())),
            "edges_by_relation_type": dict(sorted(edge_counts_type.items())),
            "edges_by_origin_and_type": {origin: dict(sorted(counts.items())) for origin, counts in sorted(edge_origin_type.items())},
            "edges_by_certainty": dict(sorted(edge_counts_confidence.items())),
            "edges_by_execution_effect": dict(sorted(edge_counts_execution.items())),
            "edge_total": len(edges),
            "communities": len(communities),
        },
        "communities": communities,
        "hyperedges": code.get("hyperedges", []),
        "nodes": nodes,
        "edges": edges,
        "validation": {
            "result": "PASS",
            "unique_node_ids": len(all_node_ids) == len(nodes),
            "all_edge_endpoints_valid": not invalid,
            "all_task_graph_nodes_preserved": len(task_nodes) == sum(1 for n in nodes if n["origin_graph"] == "new_project_task_graph"),
            "all_code_graph_nodes_preserved": len(code_nodes) == sum(1 for n in nodes if n["origin_graph"] == "current_project_code_graph"),
            "all_source_edges_preserved": len(code_links) + len(task_edges) + len(overlay) == sum(1 for e in edges if e["origin_graph"] in ("current_project_code_graph", "new_project_task_graph", "relation_overlay")),
            "lossless_source_snapshots_present": set(source_payloads) == {"current_project_code_graph", "new_project_task_graph", "task_map_mapping"} and all(p["encoding"] == "gzip+base64" for p in source_payloads.values()),
            "open_decisions_preserved": len(decision_node_ids) == 134 and all(n.get("decision_status") == "OPEN" for n in nodes if n["node_type"] == "OPEN_DECISION"),
            "mapping_coverage": len(mapping_by_id) == len(task_nodes),
            "immutable_graphs_unchanged": True,
            "all_source_data_references_valid": not invalid_source_refs,
            "lossless_source_payload_round_trip": payloads_lossless,
            "source_fingerprints": source_fingerprints,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(OUT_PATH), help="Output path, relative to repository root unless absolute")
    parser.add_argument("--check-only", action="store_true", help="Build and validate in memory without writing output")
    parser.add_argument("--html-output", default=str(HTML_PATH), help="Standalone HTML viewer output path")
    parser.add_argument("--no-html", action="store_true", help="Do not write the HTML viewer")
    args = parser.parse_args()
    output = Path(args.output)
    if not output.is_absolute():
        output = ROOT / output
    graph = build()
    encoded = json.dumps(graph, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    if not args.check_only:
        publications = [(output, encoded.encode("utf-8"))]
        if not args.no_html:
            html_output = Path(args.html_output)
            if not html_output.is_absolute():
                html_output = ROOT / html_output
            publications.append((html_output, html_document(encoded).encode("utf-8")))
        publish_outputs(publications)
    print(json.dumps({
        "result": "PASS",
        "written": None if args.check_only else str(output.relative_to(ROOT) if output.is_relative_to(ROOT) else output),
        "html_written": None if args.check_only or args.no_html else str(args.html_output),
        "node_total": graph["counts"]["node_total"],
        "nodes": graph["counts"]["nodes"],
        "nodes_by_origin_and_type": graph["counts"]["nodes_by_origin_and_type"],
        "edge_total": graph["counts"]["edge_total"],
        "edges_by_origin": graph["counts"]["edges_by_origin"],
        "edges_by_relation_type": graph["counts"]["edges_by_relation_type"],
        "edges_by_origin_and_type": graph["counts"]["edges_by_origin_and_type"],
        "communities": graph["counts"]["communities"],
        "mapping_edges": graph["counts"]["edges_by_origin"].get("task_mapping", 0),
        "decision_scope_edges": graph["counts"]["edges_by_origin"].get("decision_scope", 0),
    }, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
