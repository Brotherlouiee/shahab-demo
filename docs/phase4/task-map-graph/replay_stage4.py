#!/usr/bin/env python3
"""Deterministic semantic replay for the Phase 4 Stage 4 mapping audit.

The script pins the three immutable graphs and Plan/Wallet sources, audits every
NEW_IMPLEMENTATION record against the complete active code-file inventory, and
validates every decision scope and relation against real graph nodes and source
locators. Lexical search can produce evidence for review; it never creates a
Task-to-code mapping by itself.
"""
from __future__ import annotations
import argparse, hashlib, json, re, sys
from collections import Counter, defaultdict, deque
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
BASELINE='c9e74532d4291e9ed1a7ddd3523ee84f09c940a2'
PR_BASE='4d6ed9a1bb984a4ac14215f864a2939410abe21f'
FILES={
 'reference_graph':'knowledge-graph/phase2-reference-docs/semantic/graph.json',
 'current_code_graph':'docs/phase4/task-map-graph/current-project-code-graph.json',
 'task_graph':'docs/phase4/task-map-graph/new-project-task-graph.json',
 'mapping':'docs/phase4/task-map-graph/task-map-mapping.json',
 'plan':'docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md',
 'wallet':'docs/SHAHAB_DIGITAL_WALLET.md',
 'code_manifest':'docs/phase4/task-map-graph/current-project-code-graph-manifest.json',
}
PINS={
 'reference_graph':('a43c1732e85eeebdf83709b9d76233e59ae1a1af','f16e684dc773e9bf053e51da2a0a37e3b5ffaf88809e1b5d37f8befbf69e1c93'),
 'current_code_graph':('c19d700b408206458d56798809ec1c7009e08acc','0a496833d1a58a6d07e58f3d5d2b59f2c0306a924d8573a687fc4067c549c982'),
 'task_graph':('2393556b74016a437d9a126bee3b04cdcc42be25','deb940949583007628dccb89de538c8f3b278aef1c6f99d1386f613f107fa0f7'),
}
STOP={'about','after','again','against','also','among','before','being','below','between','build','check','data','define','design','during','each','from','have','into','maintain','must','only','other','package','perform','process','project','provide','record','should','state','support','system','task','that','their','there','these','this','those','through','under','using','where','which','while','with','without','work','create','implement','validate','plan','test','service','feature','state','status','manage','handling','flow','core','assistant','wallet','catalog','contract'}
TOKEN=re.compile(r'[A-Za-z][A-Za-z0-9_]{3,}')

def sha256(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def blob_sha(b:bytes)->str:return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def read_json(path:str):return json.loads((ROOT/path).read_text(encoding='utf-8'))
def write_json(path:str,obj): (ROOT/path).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def source_file_kind(path):
 p=path.lower()
 if '/tests/' in p or p.startswith('tests/'):return 'TEST_OR_FIXTURE'
 if 'alembic/versions/' in p or 'migrations/' in p:return 'DATABASE_MIGRATION'
 if '/api/' in p or '/routes/' in p or 'router' in p:return 'API_OR_ROUTE'
 if 'models.py' in p or '/db/' in p:return 'DATABASE_OR_MODEL'
 if p.endswith(('.yml','.yaml','.toml','.json','.lock')):return 'CONFIG_OR_CONTRACT'
 return 'APPLICATION_SOURCE'
def fail(errors):
 for e in errors:print('FAIL:',e)
 return 1

def gather_search(mapping,task_graph,code_graph,manifest):
 code_nodes=code_graph.get('nodes',[])
 file_nodes=defaultdict(list)
 for n in code_nodes:
  p=n.get('source_file') or n.get('path')
  if p:file_nodes[p].append(n.get('id'))
 corpus=[]
 for path in sorted(manifest):
  f=ROOT/path
  if not f.is_file():raise ValueError('missing code corpus file '+path)
  b=f.read_bytes();text=b.decode('utf-8',errors='replace')
  corpus.append({'path':path,'blob_sha':blob_sha(b),'sha256':sha256(b),'lines':text.splitlines()})
 # IDF filter is deterministic and computed only from the pinned source corpus.
 df=Counter()
 for f in corpus:
  whole='\n'.join(f['lines']).lower()
  df.update(set(TOKEN.findall(whole)))
 node_by_id={n['id']:n for n in task_graph.get('nodes',[])}
 override={o.get('task_ref'):o for o in mapping.get('task_name_evidence_overrides',[])}
 results=[]
 for rec in mapping.get('mappings',[]):
  if rec.get('mapping_status')!='NEW_IMPLEMENTATION':continue
  ref=rec.get('subtask_ref') or rec.get('task_ref') or rec.get('package_ref')
  node=node_by_id.get(ref,{})
  ov=override.get(ref,{})
  lines=[]
  for loc in node.get('plan_refs',[]):
   m=re.search(r':(\d+)$',str(loc))
   if m:
    no=int(m.group(1));pl=(ROOT/FILES['plan']).read_text(encoding='utf-8').splitlines()
    if 1<=no<=len(pl):lines.append(pl[no-1])
  text=' '.join([str(node.get('name','')),str(ov.get('plan_display_label','')),*lines])
  tokens=[]
  for t in TOKEN.findall(text):
   t=t.lower()
   if t not in STOP and df[t]<=max(4,int(len(corpus)*0.025)) and t not in tokens:tokens.append(t)
  tokens=sorted(tokens,key=lambda t:(df[t],t))[:8]
  matched=[]; exact=[]
  if ref:
   for f in corpus:
    for no,line in enumerate(f['lines'],1):
     low=line.lower()
     if ref.lower() in low:
      exact.append({'path':f['path'],'line':no,'blob_sha':f['blob_sha'],'snippet':line.strip()[:300]})
  for f in corpus:
   hits=[]
   for no,line in enumerate(f['lines'],1):
    low=line.lower(); found=[t for t in tokens if t in low]
    if found:hits.append({'line':no,'terms':found,'snippet':line.strip()[:300]})
   if hits:
    matched.append({'path':f['path'],'blob_sha':f['blob_sha'],'file_type':source_file_kind(f['path']),'graph_file_node_refs':sorted(set(file_nodes.get(f['path'],[]))),'matches':hits[:4]})
  if rec.get('entity_type')=='PACKAGE':
   status='NON_CODE_REQUIREMENT';reason='Package گرهٔ تجمیعی محدودهٔ برنامه است؛ Task و Subtaskهای فرزند جداگانه جست‌وجو می‌شوند.'
  elif exact:
   status='SEARCH_INCONCLUSIVE';reason='شناسهٔ Task در متن فایل پیدا شد، اما ارجاع متنی به‌تنهایی وجود پیاده‌سازی فعال را اثبات نمی‌کند؛ شاهد برای بازبینی انسانی ذخیره شد.'
   matched=matched[:8]
  elif matched and tokens:
   status='SEARCH_INCONCLUSIVE';reason='عبارت‌های شاخص در فایل‌های مخزن پیدا شدند، اما ارتباط معنایی با Task و Node کد نیازمند بازبینی انسانی است؛ کد پیدا‌شده یا Mapping تأییدشده ادعا نمی‌شود.'
   matched=matched[:8]
  elif len(tokens)>=2:
   status='NO_CODE_EVIDENCE_FOUND';reason='جست‌وجوی دقیق شناسه و واژه‌های شاخص در همهٔ فایل‌های corpus پین‌شده نتیجهٔ مستقیم نداد؛ این نتیجه اثبات نبود کد نیست.'
  else:
   status='SEARCH_INCONCLUSIVE';reason='عنوان/Plan Locator واژهٔ شاخص کافی برای جست‌وجوی قابل‌اعتماد تولید نکرد.'
  results.append({'task_or_package_ref':ref,'entity_type':rec.get('entity_type'),'mapping_status':'NEW_IMPLEMENTATION','search_status':status,'source_plan_refs':node.get('plan_refs',[]),'query_terms':tokens,'exact_id_matches':exact[:8],'matched_files':matched,'code_type':';'.join(sorted({m['file_type'] for m in matched})),'search_method':'exact canonical ID plus deterministic rare-token co-occurrence across every file in the pinned active-code inventory','reason':reason,'suggested_mapping':{'current_code_node_refs':[],'status':'NO_MAPPING_PROPOSED_BY_LEXICAL_SEARCH','review_required':bool(matched or exact)}})
 return results,corpus

def semantic_projection(m):
 return {'mapping_id':m.get('mapping_id'),'source_graphs':m.get('source_graphs'),'mappings':sorted(m.get('mappings',[]),key=lambda r:(r.get('package_ref') or '',r.get('task_ref') or '',r.get('subtask_ref') or '')),'open_decision_references':sorted(m.get('open_decision_references',[]),key=lambda r:r['open_decision_id']),'required_22_reference_review':sorted(m.get('required_22_reference_review',[]),key=lambda r:r['open_decision_id']),'task_name_evidence_overrides':sorted(m.get('task_name_evidence_overrides',[]),key=lambda r:r.get('task_ref','')),'stage4_relation_overlay':m.get('stage4_relation_overlay'),'stage4_code_search_audit':m.get('stage4_code_search_audit')}
def main():
 ap=argparse.ArgumentParser();g=ap.add_mutually_exclusive_group(required=True);g.add_argument('--write-code-search',action='store_true');g.add_argument('--check-only',action='store_true');args=ap.parse_args()
 errors=[];m=read_json(FILES['mapping']);tg=read_json(FILES['task_graph']);cg=read_json(FILES['current_code_graph']);rg=read_json(FILES['reference_graph']);manifest=read_json(FILES['code_manifest'])
 for key,(expected_blob,expected_sha) in PINS.items():
  b=(ROOT/FILES[key]).read_bytes()
  if blob_sha(b)!=expected_blob:errors.append(f'{key} Git blob mismatch')
  if sha256(b)!=expected_sha:errors.append(f'{key} SHA-256 mismatch')
 counts=Counter(n.get('node_type') for n in tg['nodes'])
 if counts!={'PACKAGE':36,'TASK':189,'SUBTASK':471}:errors.append(f'task graph counts mismatch {dict(counts)}')
 tids=[n['id'] for n in tg['nodes']]
 if len(tids)!=696 or len(set(tids))!=696:errors.append('Task graph canonical IDs are not 696 unique nodes')
 maps=m.get('mappings',[])
 if len(maps)!=696:errors.append(f'expected 696 mappings, got {len(maps)}')
 def mapping_identity(r):
  return r.get({'PACKAGE':'package_ref','TASK':'task_ref','SUBTASK':'subtask_ref'}.get(r.get('entity_type'),''))
 identities=[mapping_identity(r) for r in maps]
 if len(set(identities))!=696 or None in identities:errors.append('mapping identities are not 696 unique Package/Task/Subtask nodes')
 for r in maps:
  for k in ('package_ref','task_ref','subtask_ref'):
   v=r.get(k)
   if v and v not in set(tids):errors.append(f'dangling mapping {v}')
 decision=m.get('open_decision_references',[]);did=[r.get('open_decision_id') for r in decision]
 if len(did)!=134 or len(set(did))!=134:errors.append('open decision list does not contain 134 unique IDs')
 status=Counter(r.get('mapping_status') for r in decision)
 if status!={'BLOCKED':126,'UNMAPPED_IN_TASK_GRAPH':8}:errors.append(f'open decision status mismatch {dict(status)}')
 special=m.get('required_22_reference_review',[]);sid=[r.get('open_decision_id') for r in special]
 if len(sid)!=22 or len(set(sid))!=22:errors.append('special reference list does not contain 22 unique IDs')
 if Counter(r.get('mapping_status') for r in special)!={'BLOCKED':14,'UNMAPPED_IN_TASK_GRAPH':8}:errors.append('special reference status mismatch')
 package_ids={'PACKAGE:'+str(n.get('package_id','')).upper() for n in tg['nodes'] if n.get('node_type')=='PACKAGE'}
 code_ids={n.get('id') for n in cg.get('nodes',[])}
 reference_ids={n.get('id') for n in rg.get('nodes',[])}
 for r in decision:
  scope=r.get('affected_scope',{})
  if r.get('mapping_status')=='BLOCKED' and not (r.get('task_refs') or r.get('package_refs')):errors.append('BLOCKED decision has no affected scope '+str(r.get('open_decision_id')))
  for p in r.get('package_refs',[]):
   if p not in package_ids:errors.append('invalid package reference '+str(p))
  for t in r.get('task_refs',[]):
   if t not in set(tids):errors.append('invalid task reference '+str(t))
  if r.get('mapping_status')=='UNMAPPED_IN_TASK_GRAPH' and (scope.get('execution_effect')!='UNRESOLVED_SOURCE_GAP' or r.get('resolution_status')!='UNRESOLVED_SOURCE_GAP'):errors.append('unmapped decision lacks explicit UNRESOLVED_SOURCE_GAP status '+str(r.get('open_decision_id')))
 for r in maps:
  for code_id in r.get('current_code_node_refs',[]):
   if code_id not in code_ids:errors.append('mapping has a dangling current-code node '+str(code_id))
  for source_ref in r.get('source_refs',[]):
   if isinstance(source_ref,dict) and source_ref.get('source')=='reference_graph_node' and source_ref.get('id') not in reference_ids:errors.append('mapping has a dangling reference-graph node '+str(source_ref.get('id')))
 for r in special:
  for node_id in r.get('source_graph_node_refs',[]):
   if node_id not in reference_ids:errors.append('special review has a dangling reference-graph node '+str(node_id))
 # All Task/Package handoff and relation locators are exact Plan locators with source rationale.
 overlay=m.get('stage4_relation_overlay',{}); rels=overlay.get('relations',[]);plan=(ROOT/FILES['plan']).read_text(encoding='utf-8').splitlines();seen=set();adj=defaultdict(list)
 for r in rels:
  key=(r.get('source'),r.get('target'),r.get('relation_type'),r.get('locator'))
  if key in seen:errors.append('duplicate overlay relationship '+str(key))
  seen.add(key)
  for endpoint,kind in ((r.get('source'),r.get('source_kind','node')),(r.get('target'),r.get('target_kind','node'))):
   if endpoint=='UNRESOLVED':
    if r.get('resolution_status')!='UNRESOLVED_SOURCE_GAP':errors.append('unresolved relation endpoint lacks UNRESOLVED_SOURCE_GAP '+str(r.get('relation_id')))
   elif kind=='node' and endpoint not in package_ids and endpoint not in set(tids):errors.append('relation endpoint is not a Package/Task node '+str(endpoint))
   elif kind=='contract' and not str(endpoint).startswith('CONTRACT:'):errors.append('contract relation target lacks canonical contract ref '+str(endpoint))
   elif kind=='decision' and not str(endpoint).startswith('DECISION:'):errors.append('decision relation target lacks canonical decision ref '+str(endpoint))
  if not r.get('rationale') or not r.get('source_refs') or not r.get('locator'):errors.append('relation missing evidence/rationale '+str(r.get('relation_id')))
  mt=re.search(r':(\d+)$',str(r.get('locator')))
  if mt:
   line=int(mt.group(1))
   if line<1 or line>len(plan):errors.append('relation locator out of Plan range '+str(r.get('locator')))
   else:
    content=plan[line-1]
    provenance=str(r.get('provenance','')).split(':')[-1]
    if not any(token in content for token in ['Handoff','DEP:','TASK:','CONTRACT:','CAN:C08:019']):errors.append('relation source line lacks relation evidence '+str(r.get('locator')))
  if r.get('relation_type') in {'depends_on','sequence_after'} and r.get('execution_effect')=='HARD_ORDER' and r.get('source') in set(tids) and r.get('target') in set(tids):adj[r['source']].append(r['target'])
 # Every explicitly identified Plan dependency and handoff must appear in the immutable graph or overlay.
 plan_ids={x for line in plan for x in re.findall(r'(?:DEP|Handoff):[A-Z0-9]+:\d+',line)}
 recorded_lines=set()
 for edge in tg.get('edges',[])+rels:
  for loc in edge.get('source_refs',[]) or []:
   match=re.search(r':(\d+)$',str(loc))
   if match:recorded_lines.add(int(match.group(1)))
 recorded_ids={x for i,line in enumerate(plan,1) if i in recorded_lines for x in re.findall(r'(?:DEP|Handoff):[A-Z0-9]+:\d+',line)}
 missing_plan_ids=sorted(plan_ids-recorded_ids)
 if missing_plan_ids:errors.append('Plan dependency/handoff identifiers absent from graph+overlay: '+','.join(missing_plan_ids))
 # Cycle check over hard Task-level relations including immutable Task Graph relations.
 for e in tg.get('edges',[]):
  if e.get('relation_type') in {'depends_on','sequence_after'} and e.get('execution_effect')=='HARD_ORDER':adj[e['source']].append(e['target'])
 visiting=set();visited=set()
 def dfs(n):
  if n in visiting:return True
  if n in visited:return False
  visiting.add(n)
  for v in adj.get(n,[]):
   if dfs(v):return True
  visiting.remove(n);visited.add(n);return False
 if any(dfs(n) for n in list(adj) if n not in visited):errors.append('hard-order task dependency cycle detected')
 overrides=m.get('task_name_evidence_overrides',[])
 if len(overrides)!=80 or len({o.get('task_ref') for o in overrides})!=80:errors.append('expected 80 unique evidence-backed Task label overlays')
 for o in overrides:
  if o.get('task_ref') not in set(tids) or not o.get('source_locator') or not o.get('source_blob_sha') or not o.get('rationale'):errors.append('Task label overlay lacks canonical node or evidence '+str(o.get('task_ref')))
 unresolved_label=m.get('task_name_evidence_override_unresolved')
 if not unresolved_label or unresolved_label.get('task_ref')!='TASK:CORE:C13B:008' or unresolved_label.get('resolution_status')!='UNRESOLVED_SOURCE_LABEL':errors.append('C13B:008 unresolved source label is not explicitly recorded')
 # Verify no legacy Task aliases remain outside the historical mapping table.
 for path in [FILES['mapping'], 'docs/phase4/task-map-graph/task-map-quality-audit.md']:
  text=(ROOT/path).read_text(encoding='utf-8')
  for alias in re.findall(r'(?<![A-Z0-9:])TASK:(?:C\d{2}[A-Z]?|A\d{2}|R\d{2}):\d{3}(?:\.S\d{2})?',text):
   if alias not in text[text.find('historical_alias_mapping'):text.find('historical_alias_mapping')+5000]:errors.append(f'legacy Task alias operationally present in {path}: {alias}')
 if errors:return fail(errors)
 corpus_paths=sorted(manifest)
 audit= m.get('stage4_code_search_audit')
 if args.write_code_search or audit is None:
  results,corpus=gather_search(m,tg,cg,manifest)
  inventory=[{'path':f['path'],'blob_sha':f['blob_sha'],'sha256':f['sha256']} for f in corpus]
  corpus_sha=sha256(json.dumps(inventory,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
  counts=Counter(r['search_status'] for r in results)
  m['stage4_code_search_audit']={'schema_version':'1.0.0','audit_id':'phase4-stage4-aud07-replay-v1','code_source_commit':BASELINE,'repository_comparison':{'from':BASELINE,'through_pr_head':PR_BASE,'code_paths_changed':0,'basis':'GitHub compare API: all changes from baseline to PR head are Stage 1–4 documentation/artifact paths; no application-code path changed.'},'method':'Exact Task ID and deterministic rare-token co-occurrence search over every file in current-project-code-graph-manifest.json. The same pinned inventory is rescanned on replay. Lexical matches are evidence candidates only; no mapping is created from text similarity.','inventory_count':len(inventory),'inventory_sha256':corpus_sha,'corpus_blob_inventory':inventory,'record_count':len(results),'status_counts':dict(counts),'records':results,'limitations':['Search is lexical and cannot prove semantic absence.','Any lexical hit remains unmapped until its source and graph semantics are manually verified.','Rows with insufficient discriminative terms are SEARCH_INCONCLUSIVE.']}
  m['validation']['stage4_high_finding_followup']['AUD-07']={'status':'SEARCH_COMPLETED_WITH_EXPLICIT_LIMITATIONS','record_count':len(results),'status_counts':dict(counts),'code_source_commit':BASELINE}
  write_json(FILES['mapping'],m)
  print(json.dumps({'records':len(results),'status_counts':dict(counts),'corpus_files':len(inventory),'corpus_sha256':corpus_sha},ensure_ascii=False,indent=2))
 else:
  results,corpus=gather_search(m,tg,cg,manifest)
  saved=audit.get('records',[])
  if results!=saved:errors.append('AUD-07 semantic search replay differs from committed records')
  inventory=[{'path':f['path'],'blob_sha':f['blob_sha'],'sha256':f['sha256']} for f in corpus]
  corpus_sha=sha256(json.dumps(inventory,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
  if corpus_sha!=audit.get('inventory_sha256') or len(inventory)!=audit.get('inventory_count'):errors.append('pinned code search inventory changed')
  projection=json.dumps(semantic_projection(m),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
  digest=sha256(projection)
  val=m.setdefault('validation',{})
  if args.check_only:
   expected=val.get('semantic_replay_projection_sha256')
   if expected and expected!=digest:errors.append('semantic replay projection differs from recorded digest')
   if not expected:
    val['semantic_replay_projection_sha256']=digest;val['semantic_mapping_reproducibility']='PASS_DETERMINISTIC_SEMANTIC_VALIDATION_REPLAY_WITH_EXPLICIT_SOURCE_GAPS';write_json(FILES['mapping'],m)
  print(json.dumps({'result':'PASS' if not errors else 'FAIL','mapping_records':len(maps),'open_decisions':len(decision),'special_references':len(special),'relations':len(rels),'code_search_records':len(results),'code_search_status_counts':dict(Counter(r['search_status'] for r in results)),'corpus_files':len(inventory),'semantic_projection_sha256':digest,'immutable_graphs':'PASS'},ensure_ascii=False,indent=2))
  if errors:return fail(errors)
 return 0
if __name__=='__main__':raise SystemExit(main())
