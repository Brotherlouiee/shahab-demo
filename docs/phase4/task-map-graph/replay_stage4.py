#!/usr/bin/env python3
"""Versioned deterministic Stage 4 search, mapping validation and semantic replay."""
from __future__ import annotations
import argparse, hashlib, json, os, re, tempfile
from collections import Counter, defaultdict, deque
from os import replace
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
BASELINE='c9e74532d4291e9ed1a7ddd3523ee84f09c940a2'
PR_BASE='655daa9d349f00718b0c93ae2016decb4ffbb510'
FILES={'reference_graph':'knowledge-graph/phase2-reference-docs/semantic/graph.json','current_code_graph':'docs/phase4/task-map-graph/current-project-code-graph.json','task_graph':'docs/phase4/task-map-graph/new-project-task-graph.json','mapping':'docs/phase4/task-map-graph/task-map-mapping.json','plan':'docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md','wallet':'docs/SHAHAB_DIGITAL_WALLET.md','code_manifest':'docs/phase4/task-map-graph/current-project-code-graph-manifest.json'}
PINS={
 'reference_graph':('a43c1732e85eeebdf83709b9d76233e59ae1a1af','f16e684dc773e9bf053e51da2a0a37e3b5ffaf88809e1b5d37f8befbf69e1c93'),
 'current_code_graph':('c19d700b408206458d56798809ec1c7009e08acc','0a496833d1a58a6d07e58f3d5d2b59f2c0306a924d8573a687fc4067c549c982'),
 'task_graph':('2393556b74016a437d9a126bee3b04cdcc42be25','deb940949583007628dccb89de538c8f3b278aef1c6f99d1386f613f107fa0f7')}
SPECIAL_IDS={'AO:BP-C-0217:01','AO:BP-C-0219:01',*[f'AO:BP-C-0129:{i:02}' for i in range(1,8)],'AO:BP-C-0149:01','AO:BP-C-0289:01',*[f'AO:BP-C-{i:04d}:01' for i in range(291,301)],'AO:BP-C-0328:01'}
STOP=set('about after again against also among before being below between build check data define design during each from have into maintain must only other package perform process project provide record should state support system task that their there these this those through under using where which while with without work create implement validate plan test service feature status manage handling flow core assistant wallet catalog contract request current source response requirement requirements candidate candidates acceptance criteria enabler result owner actual source refs reference graph'.split())
TOKEN=re.compile(r'(?<![A-Za-z0-9_])[A-Za-z][A-Za-z0-9_]{4,}(?![A-Za-z0-9_])')
PARTIAL={
 'TASK:RAG:R10:001':('backend_app_recommendation_application_use_cases_recommendcanonicalloans','backend_app_recommendation_engine_canonical_scoring_score_official_categories','backend_app_api_v1_recommendations_recommend'),
 'TASK:RAG:R10:002':('backend_app_recommendation_domain_entities_recommendationsnapshot','backend_app_recommendation_infrastructure_sqlalchemy_snapshot_sqlalchemyrecommendationsnapshotrepository_read_approved_snapshot'),
 'TASK:RAG:R10:003':('backend_app_recommendation_engine_canonical_scoring_score_official_categories','backend_app_recommendation_engine_canonical_scoring_canonicalpartition','backend_app_recommendation_domain_entities_recommendationpartition')}
PARTIAL_RATIONALE={
 'TASK:RAG:R10:001':'Plan §R10 صریحاً مالکیت محاسبهٔ قطعی و API را به Core/C01 می‌دهد و می‌گوید Adviser scorer موجود را بازاستفاده کند؛ مسیر use case، scorer و API توصیه در کد فعال وجود دارد. adapter نسخه‌دار Adviser و قرارداد ورودی همچنان جدید است.',
 'TASK:RAG:R10:002':'Plan برای Task:RAG:R10:002 Snapshot سازگار و provenance می‌خواهد و مالک Snapshot را Core/C05b می‌داند؛ مدل RecommendationSnapshot و خواندن Snapshot مصوب در کد فعال وجود دارد. ClaimEvidenceLink و envelope مخصوص Adviser هنوز تکمیل نشده‌اند.',
 'TASK:RAG:R10:003':'Plan تفکیک computed value، eligibility و ranking را می‌خواهد؛ scorer موجود خروجی ranked/needs-review/below-threshold/evidence را جدا می‌کند. disposition اقدام/transaction و سیاست خطای Adviser هنوز جدید است.'}
PARTIAL_FILES={
 'backend_app_recommendation_application_use_cases_recommendcanonicalloans':('backend/app/recommendation/application/use_cases.py',95),
 'backend_app_recommendation_engine_canonical_scoring_score_official_categories':('backend/app/recommendation/engine/canonical_scoring.py',38),
 'backend_app_api_v1_recommendations_recommend':('backend/app/api/v1/recommendations.py',95),
 'backend_app_recommendation_domain_entities_recommendationsnapshot':('backend/app/recommendation/domain/entities.py',93),
 'backend_app_recommendation_infrastructure_sqlalchemy_snapshot_sqlalchemyrecommendationsnapshotrepository_read_approved_snapshot':('backend/app/recommendation/infrastructure/sqlalchemy_snapshot.py',53),
 'backend_app_recommendation_engine_canonical_scoring_canonicalpartition':('backend/app/recommendation/engine/canonical_scoring.py',30),
 'backend_app_recommendation_domain_entities_recommendationpartition':('backend/app/recommendation/domain/entities.py',54),
}


def title_search_tokens(text):
 return [token.lower() for token in TOKEN.findall(text)]


def exact_title_matches(title, corpus, token_files):
 tokens=title_search_tokens(title)
 if len(tokens)<3:
  return []
 indexes=set.intersection(*(set(token_files.get(token, ())) for token in tokens))
 phrase=' '+' '.join(tokens)+' '
 return [
  {'file':corpus[ix]['path'],'blob_sha':corpus[ix]['blob_sha'],'title':title}
  for ix in sorted(indexes)
  if phrase in ' '+' '.join(title_search_tokens(corpus[ix]['text']))+' '
 ]


def validate_partial_files(partial, evidence_files, code_nodes, corpus_by_path):
 expected={code_id for ids in partial.values() for code_id in ids}
 missing=expected-evidence_files.keys()
 extra=evidence_files.keys()-expected
 if missing or extra:
  raise ValueError(f'partial evidence IDs: missing {sorted(missing)}, unexpected {sorted(extra)}')
 for ref,ids in partial.items():
  if not ids or len(set(ids))!=len(ids):
   raise ValueError(f'missing or duplicate partial code IDs for {ref}')
 for code_id,(path,line) in evidence_files.items():
  node=code_nodes.get(code_id)
  if node is None or node.get('source_file')!=path:
   raise ValueError(f'partial evidence code ID/file mismatch: {code_id} -> {path}')
  source=corpus_by_path.get(path)
  if source is None or not 1<=line<=len(source['lines']) or not source['lines'][line-1].strip():
   raise ValueError(f'partial code evidence not found: {code_id} at {path}:{line}')


def sha256(b):return hashlib.sha256(b).hexdigest()
def blob_sha(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def readj(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))
def writej(path,obj):
 target=ROOT/path
 payload=(json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
 temporary=None
 try:
  with tempfile.NamedTemporaryFile(dir=target.parent,prefix='.'+target.name+'.',delete=False) as handle:
   temporary=Path(handle.name)
   temporary.chmod(target.stat().st_mode & 0o777)
   handle.write(payload)
   handle.flush()
   os.fsync(handle.fileno())
  replace(temporary,target)
 finally:
  if temporary is not None:
   temporary.unlink(missing_ok=True)
def fail(errors):
 for e in errors:print('FAIL:',e)
 return 1
def short_alias(ref):
 # Confirmed legacy form is TASK:<PACKAGE>:<NNN>[.Snn].
 p=re.fullmatch(r'TASK:(?:CORE|RAG|ASSISTANT):([A-Z0-9]+):(\d{3}(?:\.S\d{2})?)',ref)
 return f'TASK:{p.group(1)}:{p.group(2)}' if p else None
def build_search(m,tg,cg,manifest,audit):
 corpus=[]; file_tokens=[]; token_files=defaultdict(set); plan=(ROOT/FILES['plan']).read_text(encoding='utf-8').splitlines()
 for path in sorted(manifest):
  p=ROOT/path
  if not p.is_file():raise ValueError('missing pinned corpus file '+path)
  b=p.read_bytes();txt=b.decode('utf-8',errors='replace');lines=txt.splitlines(); toks=set(title_search_tokens(txt))
  index=len(corpus); corpus.append({'path':path,'blob_sha':blob_sha(b),'sha256':sha256(b),'text':txt,'lines':lines,'tokens':toks})
  file_tokens.append(toks)
  for t in toks:token_files[t].add(index)
 inv=[{'path':x['path'],'blob_sha':x['blob_sha'],'sha256':x['sha256']} for x in corpus]
 invsha=sha256(json.dumps(inv,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
 if len(corpus)!=347:raise ValueError(f'expected 347 pinned active-code files, got {len(corpus)}')
 tg_by={n['id']:n for n in tg['nodes']}; mapping_by={r.get('task_ref') or r.get('subtask_ref') or r.get('package_ref'):r for r in m['mappings']}
 previous={r['task_or_package_ref']:r for r in audit.get('records',[])}
 scope=audit.get('search_scope_refs') or [r['task_or_package_ref'] for r in audit.get('records',[])]
 if not scope:scope=[r.get('task_ref') or r.get('subtask_ref') or r.get('package_ref') for r in m['mappings'] if r['mapping_status']=='NEW_IMPLEMENTATION']
 corpus_by_path={item['path']:item for item in corpus}
 validate_partial_files(PARTIAL,PARTIAL_FILES,{node['id']:node for node in cg['nodes']},corpus_by_path)
 for ref in PARTIAL:
  locators=tg_by.get(ref,{}).get('plan_refs',[])
  prefix,line=locators[0].rsplit(':',1) if locators and ':' in locators[0] else ('','')
  if ref not in scope or prefix!=FILES['plan'] or not line.isdecimal() or not 1<=int(line)<=len(plan) or not plan[int(line)-1].strip():
   raise ValueError('missing partial mapping search scope or Plan evidence: '+ref)
 # Search exact canonical and confirmed shortened aliases in one pass over all pinned source lines.
 id_to_refs={}
 for ref in scope:
  for q in (ref,short_alias(ref)):
   if q:id_to_refs.setdefault(q,[]).append(ref)
 id_pattern=re.compile(r'(?<![A-Za-z0-9_:])(?P<id>'+('|'.join(re.escape(x) for x in sorted(id_to_refs,key=len,reverse=True)))+r')(?![A-Za-z0-9_.])')
 exact_by_ref=defaultdict(list)
 for f in corpus:
  for no,line in enumerate(f['lines'],1):
   for match in id_pattern.finditer(line):
    for ref in id_to_refs[match.group('id')]:exact_by_ref[ref].append({'file':f['path'],'line':no,'blob_sha':f['blob_sha'],'sha256':f['sha256'],'matched_id':match.group('id'),'snippet':line.strip()[:240]})
 results=[]
 for ref in scope:
  node=tg_by.get(ref,{});prior=previous.get(ref,{});kind=node.get('node_type','PACKAGE' if ref.startswith('PACKAGE:') else 'UNKNOWN')
  direct_lines=[]
  for loc in node.get('plan_refs',[]):
   mm=re.search(r':(\d+)$',str(loc))
   if mm:
    ix=int(mm.group(1))-1
    if 0<=ix<len(plan):direct_lines.extend(plan[max(0,ix-1):min(len(plan),ix+2)])
  display=str(node.get('name',''))
  prior_terms=[str(t) for t in prior.get('query_terms',[]) if str(t).isalpha() and len(str(t))>=5]
  raw=' '.join([display,*direct_lines,*prior_terms]).lower()
  raw=re.sub(r'(?i)(?:TASK|PACKAGE|REQ|AC|TEST|CAND|AO|BP|WL|EN|TC|DECISION):[A-Z0-9:._/-]+',' ',raw)
  terms=[]
  for t in TOKEN.findall(raw):
   t=t.lower()
   if t in STOP or t.startswith('docs_') or t in terms or len(token_files[t])>5:continue
   terms.append(t)
  terms=sorted(terms,key=lambda t:(len(token_files[t]),t))[:12]
  # Descriptive title phrase search is narrowed through an inverted index, then exact-checked.
  title=re.sub(r'^(?:AC|REQ|TEST|TASK):[^ ]+\s*[-/|]*\s*','',display,flags=re.I).strip()
  phrase=exact_title_matches(title,corpus,token_files)
  candidate_counts=Counter()
  for term in terms:
   for ix in token_files.get(term,()):candidate_counts[ix]+=1
  candidates=[]
  for ix,num in candidate_counts.items():
   if num>=2:
    found=sorted(t for t in terms if t in file_tokens[ix])
    candidates.append({'file':corpus[ix]['path'],'blob_sha':corpus[ix]['blob_sha'],'matched_terms':found})
  candidates.sort(key=lambda x:(-len(x['matched_terms']),x['file']))
  if kind=='PACKAGE':status='NON_CODE_REQUIREMENT';rationale='Package is a planning scope/ownership boundary rather than an independently executable code unit; its child Tasks/Subtasks were searched separately.'
  elif ref in PARTIAL:status='CODE_PARTIALLY_FOUND';rationale=PARTIAL_RATIONALE[ref]
  else:status='NO_CODE_EVIDENCE_FOUND';rationale='No direct active-code implementation was found after exact canonical/short-ID, descriptive title and discriminative-term scans. Generic co-occurrence in unrelated source/tests/workflows was rejected; this does not claim future reuse is impossible.'
  hits=[]
  for code_id in PARTIAL.get(ref,()):
   path,line_no=PARTIAL_FILES[code_id]
   f=corpus_by_path[path]
   hits.append({'file':path,'line':line_no,'blob_sha':f['blob_sha'],'sha256':f['sha256'],'code_type':'APPLICATION_SOURCE','code_node_ref':code_id,'plan_locator':node.get('plan_refs',[])[0]})
  exact=exact_by_ref.get(ref,[])
  results.append({'task_or_package_ref':ref,'entity_type':kind,'mapping_status_at_review':mapping_by.get(ref,{}).get('mapping_status'),'search_status':status,
   'source_plan_refs':node.get('plan_refs',[]),'query_terms':terms,'searched_file_count':len(corpus),'searched_inventory_sha256':invsha,
   'exact_canonical_or_alias_matches':exact,'exact_plan_title_matches':phrase,'discriminative_candidate_file_count':len(candidates),
   'reviewed_lexical_candidates':candidates[:5] if ref in PARTIAL else [],'code_search_hits':hits,
   'search_method':'Exact canonical and confirmed short alias scan; normalized task-title scan; then discriminative Plan-derived technical-term scan across all 347 pinned files. Includes application code, API/routes, models, migrations, YAML/config/contracts, tests/fixtures, Docker and workflows. Lexical candidates alone never establish mapping.',
   'reason':rationale,'adjudication':'Explicit Plan ownership plus corresponding active-code implementation' if ref in PARTIAL else ('Package scope is non-code; executable children are searched as separate records.' if kind=='PACKAGE' else 'No direct functionally corresponding implementation; generic word matches are not accepted as evidence.'),
   'evidence_file_line':hits[0]['file']+':'+str(hits[0]['line']) if hits else None,'file_blob_sha':hits[0]['blob_sha'] if hits else None,'code_node_ref':hits[0]['code_node_ref'] if hits else None,
   'suggested_mapping':{'current_code_node_refs':list(PARTIAL.get(ref,[])),'status':'PARTIALLY_MAPPED','review_required':False,'rationale':rationale} if ref in PARTIAL else {'current_code_node_refs':[],'status':'NO_MAPPING_PROPOSED','review_required':False}})
 return results,inv,invsha
def semantic_projection(m):
 audit=m.get('stage4_code_search_audit',{})
 return {'mapping_id':m.get('mapping_id'),'source_graphs':m.get('source_graphs'),
  'mappings':sorted(m.get('mappings',[]),key=lambda r:(r.get('package_ref') or '',r.get('task_ref') or '',r.get('subtask_ref') or '')),
  'open_decision_references':sorted(m.get('open_decision_references',[]),key=lambda r:r['open_decision_id']),
  'required_22_reference_review':sorted(m.get('required_22_reference_review',[]),key=lambda r:r['open_decision_id']),
  'task_name_evidence_overrides':sorted(m.get('task_name_evidence_overrides',[]),key=lambda r:r.get('task_ref','')),
  'task_name_evidence_override_unresolved':m.get('task_name_evidence_override_unresolved'),
  'stage4_relation_overlay':m.get('stage4_relation_overlay'),
  'stage4_code_search_audit':{k:v for k,v in audit.items() if k!='semantic_projection_sha256'}}
def projection_digest(m):
 return sha256(json.dumps(semantic_projection(m),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())

def main():
 ap=argparse.ArgumentParser();g=ap.add_mutually_exclusive_group(required=True);g.add_argument('--write-code-search',action='store_true');g.add_argument('--check-only',action='store_true');args=ap.parse_args()
 errors=[];m=readj(FILES['mapping']);tg=readj(FILES['task_graph']);cg=readj(FILES['current_code_graph']);rg=readj(FILES['reference_graph']);manifest=readj(FILES['code_manifest'])
 for key,(expected_blob,expected_sha) in PINS.items():
  b=(ROOT/FILES[key]).read_bytes()
  if blob_sha(b)!=expected_blob:errors.append(f'{key}: Git Blob SHA changed')
  if sha256(b)!=expected_sha:errors.append(f'{key}: SHA-256 changed')
 nodes=tg.get('nodes',[]); tids=[n.get('id') for n in nodes]; ids=set(tids)
 counts=Counter(n.get('node_type') for n in nodes)
 if counts!={'PACKAGE':36,'TASK':189,'SUBTASK':471}:errors.append('Task graph must remain 36/189/471')
 if len(ids)!=696:errors.append('Task graph canonical ID is duplicated or missing')
 by={n['id']:n for n in nodes}; package_ids={'PACKAGE:'+n['package_id'] for n in nodes if n.get('node_type')=='PACKAGE'}
 for n in nodes:
  if n.get('node_type')=='SUBTASK' and n.get('parent_id') not in ids:errors.append('invalid Subtask parent '+str(n.get('id')))
  if n.get('node_type')=='TASK' and n.get('parent_id') not in package_ids:errors.append('invalid Task package parent '+str(n.get('id')))
 maps=m.get('mappings',[])
 if len(maps)!=696:errors.append('mapping does not contain exactly 696 records')
 def mid(r):return r.get({'PACKAGE':'package_ref','TASK':'task_ref','SUBTASK':'subtask_ref'}.get(r.get('entity_type'),''))
 mapids=[mid(r) for r in maps]
 if len(set(mapids))!=696 or set(mapids)!=ids:errors.append('mapping identifiers do not cover all canonical Task graph nodes exactly once')
 codeids={n.get('id') for n in cg.get('nodes',[])}; refids={n.get('id') for n in rg.get('nodes',[])}
 for r in maps:
  for c in r.get('current_code_node_refs',[]):
   if c not in codeids:errors.append('mapping has non-existent current-code Node '+str(c))
  for c in r.get('source_graph_refs',[]) if isinstance(r.get('source_graph_refs'),list) else []:
   if c not in refids:errors.append('mapping has non-existent reference Node '+str(c))
  if r.get('mapping_status')=='PARTIALLY_MAPPED' and not r.get('current_code_node_refs'):errors.append('partial mapping has no code-node evidence '+str(mid(r)))
  for e in r.get('code_node_evidence',[]):
   if e.get('node_ref') not in codeids:errors.append('code evidence points to missing graph node '+str(mid(r)))
   path=e.get('file') or e.get('source_file');p=ROOT/path;b=p.read_bytes()
   if e.get('blob_sha') and blob_sha(b)!=e['blob_sha']:errors.append('code evidence Blob SHA changed '+path)
   if e.get('sha256') and sha256(b)!=e['sha256']:errors.append('code evidence SHA-256 changed '+path)
   if e.get('line') is not None and not (1<=e['line']<=len(b.decode('utf-8').splitlines())):errors.append('code evidence locator out of range '+path)
 # Open decisions remain open but every scope is linked to valid Package/Task nodes.
 decisions=m.get('open_decision_references',[]); did=[d.get('open_decision_id') for d in decisions]
 if len(did)!=134 or len(set(did))!=134:errors.append('134 Open Decisions are not unique and complete')
 if any(d.get('decision_status','OPEN') not in ('OPEN',None) for d in decisions):errors.append('an Open Decision was marked resolved')
 if any(d.get('mapping_status')!='BLOCKED' for d in decisions):errors.append('every Open Decision must have an execution scope; mapping scope is not resolution')
 for d in decisions:
  scope=d.get('affected_scope',{})
  if scope.get('execution_effect')!='BLOCKED_BY_DECISION' or scope.get('decision_status')!='OPEN':errors.append('decision missing open decision impact '+str(d.get('open_decision_id')))
  if not d.get('task_refs') and not d.get('package_refs'):errors.append('decision lacks package/task scope '+str(d.get('open_decision_id')))
  if not scope.get('plan_locators'):errors.append('decision lacks direct Plan/package scope locator '+str(d.get('open_decision_id')))
  if any(x not in ids for x in d.get('task_refs',[])):errors.append('decision references invalid Task '+str(d.get('open_decision_id')))
  if any(x not in package_ids for x in d.get('package_refs',[])):errors.append('decision references invalid Package '+str(d.get('open_decision_id')))
  for loc in scope.get('plan_locators',[]):
   mm=re.search(r':(\d+)$',loc)
   if not mm or int(mm.group(1))>len((ROOT/FILES['plan']).read_text(encoding='utf-8').splitlines()):errors.append('invalid Plan locator in decision scope '+str(d.get('open_decision_id')))
 special=m.get('required_22_reference_review',[]);sids=[x.get('open_decision_id') for x in special]
 if len(sids)!=22 or set(sids)!=SPECIAL_IDS:errors.append('the 22 required references are incomplete or duplicated')
 if any(x.get('mapping_status')!='BLOCKED' or (not x.get('task_refs') and not x.get('package_refs')) for x in special):errors.append('special reference lacks exact Package/Task scope')
 for r in special:
  if any(x not in refids for x in r.get('source_graph_node_refs',[])):errors.append('special review contains invalid source Graphify Node')
 # Relation Overlay validation: no unresolved endpoint; every endpoint and evidence locator must be real.
 overlay=m.get('stage4_relation_overlay',{});rels=overlay.get('relations',[]);plan=(ROOT/FILES['plan']).read_text(encoding='utf-8').splitlines();seen=set();adj=defaultdict(set)
 structural=[e for e in tg.get('edges',[]) if e.get('relation_type')!='contains']
 if len(structural)!=28:errors.append(f'expected 28 non-structural task graph edges, got {len(structural)}')
 for r in rels:
  key=(r.get('source'),r.get('target'),r.get('relation_type'),r.get('relation_id'))
  if key in seen:errors.append('duplicate relation '+str(key))
  seen.add(key)
  for endpoint in (r.get('source'),r.get('target')):
   if endpoint not in package_ids|ids and not endpoint.startswith(('CONTRACT:','DECISION:')):errors.append('relation endpoint is not a Package/Task/Contract/Decision ref '+str(r.get('relation_id')))
  if r.get('execution_effect')=='UNRESOLVED_SOURCE_GAP' or r.get('resolution_status')=='UNRESOLVED_SOURCE_GAP':errors.append('unresolved endpoint remains '+str(r.get('relation_id')))
  for k in ('relation_id','source_node','target_node','relation_type','execution_effect','confidence','source_locator','plan_locator','graph_reference','rationale'):
   if not r.get(k):errors.append('relation missing required semantic field '+str(r.get('relation_id'))+'/'+k)
  if r.get('source_node')!=r.get('source') or r.get('target_node')!=r.get('target'):errors.append('relation endpoint aliases disagree '+str(r.get('relation_id')))
  if r.get('source_locator')!=r.get('plan_locator') or not r.get('source_locator','').startswith('docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:'):errors.append('relation source/Plan locator is not exact '+str(r.get('relation_id')))
  if r.get('confidence') not in ('CONFIRMED','INFERRED','AMBIGUOUS','OPEN','BLOCKED'):errors.append('invalid relation confidence '+str(r.get('relation_id')))
  loc=r.get('source_locator','');mm=re.search(r':(\d+)$',loc)
  if not mm or not 1<=int(mm.group(1))<=len(plan):errors.append('invalid relation source locator '+str(r.get('relation_id')))
  elif not any(k in plan[int(mm.group(1))-1] for k in ('Handoff','DEP:','TASK:','CONTRACT:','CAN:')):errors.append('relation locator does not contain a relation/source ref '+str(r.get('relation_id')))
  if r.get('relation_type') in ('depends_on','sequence_after') and r.get('execution_effect')=='HARD_ORDER' and r.get('source') in ids and r.get('target') in ids:adj[r['source']].add(r['target'])
 # Include immutable graph's hard Task-level ordering edges.
 for e in tg.get('edges',[]):
  if e.get('relation_type') in ('depends_on','sequence_after') and e.get('execution_effect')=='HARD_ORDER' and e.get('source') in ids and e.get('target') in ids:adj[e['source']].add(e['target'])
 indeg={i:0 for i in ids}
 for u,vs in adj.items():
  for v in vs:indeg[v]+=1
 q=deque(sorted(i for i,d in indeg.items() if d==0));order=[]
 while q:
  u=q.popleft();order.append(u)
  for v in sorted(adj.get(u,())):
   indeg[v]-=1
   if indeg[v]==0:q.append(v)
 if len(order)!=len(ids):errors.append('HARD_ORDER cycle detected in Task graph + Relation Overlay')
 # Task label overlay: 80 prior labels + newly evidenced C13B:008.
 labels=m.get('task_name_evidence_overrides',[]);label_ids=[x.get('task_ref') for x in labels]
 if len(labels)!=81 or len(set(label_ids))!=81:errors.append('expected 81 unique evidence-backed Task label overlays')
 for x in labels:
  if x.get('task_ref') not in ids or not x.get('resolved_label') or not x.get('source_locator') or not x.get('source_blob_sha') or not x.get('rationale'):errors.append('invalid Task label overlay '+str(x.get('task_ref')))
 unresolved=m.get('task_name_evidence_override_unresolved',{})
 if unresolved.get('task_ref')!='TASK:CORE:C13B:008' or unresolved.get('resolution_status')!='RESOLVED_CONTEXT_DERIVED' or unresolved.get('resolved_label')!='مسیر مالی مجاز را بررسی کند':errors.append('C13B:008 context-derived label not resolved')
 if any(r.get('target')=='UNRESOLVED' or r.get('source')=='UNRESOLVED' for r in rels):errors.append('UNRESOLVED relation endpoint remains')
 package_rows=[r for r in rels if r.get('scope_level')=='PACKAGE']
 for r in package_rows:
  if r.get('resolution_status')!='SOURCE_SCOPED' and not (r.get('resolution_status')=='PACKAGE_ONLY' and r.get('execution_effect')=='BLOCKED_BY_DECISION'):errors.append('Package-scope relation lacks explicit source-scoped status '+str(r.get('relation_id')))
  if not r.get('scope_limitation') or not r.get('task_allocation_status') or not r.get('execution_order_note'):errors.append('Package-scope relation lacks its allocation/order limitation '+str(r.get('relation_id')))
 expected_h05b={'REL-STAGE4-028-A02-013':('TASK:ASSISTANT:A02:001.S04','docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:7751','REQ:ASSISTANT:A02:013'),'REL-STAGE4-028-A02-014':('TASK:ASSISTANT:A02:003.S04','docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:7752','REQ:ASSISTANT:A02:014'),'REL-STAGE4-028-A02-015':('TASK:ASSISTANT:A02:002.S04','docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:7753','REQ:ASSISTANT:A02:015')}
 h05b=[r for r in rels if 'Handoff:H05B:004' in r.get('source_relation_refs',[])]
 if len(h05b)!=3:errors.append('H05B:004 must resolve to its three explicitly mapped A02 subtask requirements')
 for rid,(target,loc,req) in expected_h05b.items():
  r=next((x for x in h05b if x.get('relation_id')==rid),None)
  if not r or r.get('source_node')!='PACKAGE:C05B' or r.get('target_node')!=target or r.get('scope_level')!='SUBTASK' or r.get('resolution_status')!='TASK_MAPPED' or r.get('task_endpoint_evidence',{}).get('requirement_ref')!=req or loc not in r.get('source_refs',[]):errors.append('H05B:004 direct A02 subtask crosswalk invalid '+rid)
 # Preserve explicit package scopes where the Plan lacks a Task crosswalk; validate the Task-level refinements that are directly evidenced.
 task_ids={n.get('id') for n in nodes if n.get('node_type') in ('TASK','SUBTASK')}
 for relation_ref in ('Handoff:H04:003',):
  rows=[r for r in rels if relation_ref in r.get('source_relation_refs',[])]
  if not rows:errors.append('required source relation has no overlay rows '+relation_ref)
  for r in rows:
   if r.get('resolution_status')!='SOURCE_SCOPED' or r.get('scope_level')!='PACKAGE':errors.append('source-scoped relation status/scope missing '+str(r.get('relation_id')))
   if r.get('source_node') in task_ids or r.get('target_node') in task_ids:errors.append('H04:003 package-only source was assigned a Task endpoint '+str(r.get('relation_id')))
 rows=[r for r in rels if 'DEP:C05A:003' in r.get('source_relation_refs',[])]
 if not rows:errors.append('required source relation has no overlay rows DEP:C05A:003')
 for r in rows:
  if r.get('relation_id') in ('REL-STAGE4-057','REL-STAGE4-058'):
   if r.get('scope_level')!='TASK' or r.get('resolution_status')!='RESOLVED' or r.get('source_node') not in ('TASK:CORE:C04:001','TASK:CORE:C04:006') or r.get('target_node')!='TASK:CORE:C05A:003':errors.append('DEP:C05A:003 C04 consumer/provider Task crosswalk invalid '+str(r.get('relation_id')))
   if 'docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:4262' not in r.get('source_refs',[]):errors.append('DEP:C05A:003 C04 cross-reference evidence missing '+str(r.get('relation_id')))
  elif r.get('relation_id') in ('REL-STAGE4-063','REL-STAGE4-064-A01'):
   expected={'REL-STAGE4-063':('TASK:CORE:C06:001','TASK:CORE:C05A:003'),'REL-STAGE4-064-A01':('TASK:ASSISTANT:A01:002','TASK:CORE:C05A:003')}[r['relation_id']]
   if r.get('scope_level')!='TASK' or r.get('resolution_status')!='RESOLVED' or (r.get('source_node'),r.get('target_node'))!=expected:errors.append('DEP:C05A:003 exact consumer/provider crosswalk invalid '+str(r.get('relation_id')))
  elif r.get('resolution_status')!='SOURCE_SCOPED' or r.get('scope_level')!='PACKAGE':errors.append('future/unmapped DEP:C05A:003 consumer must remain source-scoped '+str(r.get('relation_id')))
 rows=[r for r in rels if 'DEP:C05A:004' in r.get('source_relation_refs',[])]
 if not rows:errors.append('required source relation has no overlay rows DEP:C05A:004')
 expected={'REL-STAGE4-066':('TASK:ASSISTANT:A01:001','docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:7623'),'REL-STAGE4-067':('TASK:ASSISTANT:A02:001','docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:7766')}
 for r in rows:
  if r.get('relation_id') in expected:
   task,loc=expected[r['relation_id']]
   if r.get('scope_level')!='TASK' or r.get('resolution_status')!='RESOLVED' or r.get('source_node')!=task or r.get('target_node')!='TASK:CORE:C05A:004':errors.append('DEP:C05A:004 exact provider Task refinement invalid '+str(r.get('relation_id')))
   if loc not in r.get('source_refs',[]) or r.get('task_endpoint_evidence',{}).get('consumer_task_ref')!=task:errors.append('DEP:C05A:004 task locator/reference missing '+str(r.get('relation_id')))
  elif r.get('relation_id')=='REL-STAGE4-068':
   if r.get('scope_level')!='TASK' or r.get('resolution_status')!='RESOLVED' or (r.get('source_node'),r.get('target_node'))!=('TASK:CORE:C06:001','TASK:CORE:C05A:004'):errors.append('DEP:C05A:004 C06 exact Task crosswalk invalid')
  elif r.get('resolution_status')!='SOURCE_SCOPED' or r.get('scope_level')!='PACKAGE':errors.append('unallocated DEP:C05A:004 endpoint must remain source-scoped '+str(r.get('relation_id')))
 # Explicitly separate H04 entitlement, C05A route, and C05A workflow handoffs; never cross-attribute their source IDs.
 expected_h04={'REL-STAGE4-001':('TASK:ASSISTANT:A01:003','docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:7625'),'REL-STAGE4-002':('TASK:ASSISTANT:A02:003','docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:7768')}
 for rid,(task,loc) in expected_h04.items():
  r=next((x for x in rels if x.get('relation_id')==rid),None)
  if not r or r.get('source_relation_refs')!=['Handoff:H04:001'] or r.get('source_node')!='PACKAGE:C04' or r.get('target_node')!=task or r.get('scope_level')!='TASK' or r.get('resolution_status')!='RESOLVED' or r.get('confidence')!='CONFIRMED' or r.get('execution_effect')!='CONTRACT_ORDER' or loc not in r.get('source_refs',[]) or 'Handoff:H04:003' not in r.get('rationale',''):errors.append('H04:001 confirmed C04 entitlement consumer mapping invalid '+rid)
 if any('Handoff:H04:001' in x.get('source_relation_refs',[]) for x in rels if x.get('source_node')=='PACKAGE:C05A'):errors.append('H04:001 was incorrectly attributed to C05A provider')
 expected_c05a_handoffs={'REL-STAGE4-070':('TASK:CORE:C05A:004','TASK:ASSISTANT:A01:001','docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:7623'),'REL-STAGE4-071':('TASK:CORE:C05A:004','TASK:ASSISTANT:A02:001','docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:7766')}
 for rid,(provider,consumer,loc) in expected_c05a_handoffs.items():
  r=next((x for x in rels if x.get('relation_id')==rid),None)
  if not r or r.get('source_relation_refs')!=['Handoff:C05A:004'] or (r.get('source_node'),r.get('target_node'))!=(provider,consumer) or r.get('scope_level')!='TASK' or r.get('resolution_status')!='RESOLVED' or loc not in r.get('source_refs',[]):errors.append('C05A:004 exact provider/consumer Task handoff invalid '+rid)
 for rid in ('REL-STAGE4-069',):
  r=next((x for x in rels if x.get('relation_id')==rid),None)
  if not r or r.get('source_relation_refs')!=['Handoff:C05A:004'] or r.get('scope_level')!='PACKAGE':errors.append('C05A:004 unallocated Package handoff attribution invalid '+rid)
 r=next((x for x in rels if x.get('relation_id')=='REL-STAGE4-072'),None)
 if not r or r.get('source_relation_refs')!=['Handoff:C05A:004'] or (r.get('source_node'),r.get('target_node'))!=('TASK:CORE:C05A:004','TASK:CORE:C06:001') or r.get('scope_level')!='TASK' or r.get('resolution_status')!='RESOLVED':errors.append('C05A:004 C06 Task handoff crosswalk invalid')
 # Three missing Task-level C05B dependencies found by reviewing the Plan row against
 # the 36-package Task/Subtask locator inventory.
 expected_c05b={
  'REL-STAGE4-097':('TASK:CORE:C05B:005','TASK:CORE:C05B:003','depends_on','HARD_ORDER'),
  'REL-STAGE4-098':('TASK:CORE:C05B:005','TASK:CORE:C05B:004','requires_contract','CONTRACT_ORDER'),
  'REL-STAGE4-099':('TASK:CORE:C05B:005','TASK:CORE:C01:004','requires_contract','CONTRACT_ORDER')}
 for rid,expected in expected_c05b.items():
  r=next((x for x in rels if x.get('relation_id')==rid),None)
  if not r or (r.get('source'),r.get('target'),r.get('relation_type'),r.get('execution_effect'))!=expected or r.get('source_relation_refs')!=['DEP:C05B:005'] or r.get('scope_level')!='TASK' or r.get('resolution_status')!='RESOLVED':errors.append('C05B explicit Task dependency missing/invalid '+rid)
 review=overlay.get('review_summary',{}).get('implicit_relation_review',{})
 coverage=review.get('packages_reviewed',[])
 if (review.get('package_count')!=36 or len(coverage)!=36
     or {x.get('package') for x in coverage}!=set(n.get('package_id') for n in nodes if n.get('node_type')=='PACKAGE')
     or sum(x.get('stories',0) for x in coverage)!=34
     or sum(x.get('tasks',0) for x in coverage)!=189
     or sum(x.get('subtasks',0) for x in coverage)!=471
     or sum(x.get('acceptance_criteria',0) for x in coverage)!=588
     or sum(x.get('tests',0) for x in coverage)!=610):errors.append('36-package implicit relation review coverage inventory is incomplete')
 if review.get('new_relation_count')!=3 or set(review.get('new_relations',[]))!=set(expected_c05b):errors.append('new cross-package relation review set differs from explicit C05B findings')
 workflow=[x for x in rels if 'Handoff:C05A:006' in x.get('source_relation_refs',[])]
 if len(workflow)!=1 or workflow[0].get('relation_id')!='REL-STAGE4-073' or workflow[0].get('source_node')!='PACKAGE:C05A' or workflow[0].get('target_node')!='PACKAGE:A02' or workflow[0].get('scope_level')!='PACKAGE' or workflow[0].get('resolution_status')!='SOURCE_SCOPED':errors.append('C05A workflow handoff must be separate and package-scoped')
 for rid in ('REL-STAGE4-069','REL-STAGE4-070','REL-STAGE4-071','REL-STAGE4-072','REL-STAGE4-073'):
  r=next((x for x in rels if x.get('relation_id')==rid),None)
  if r and 'Handoff:H04:001' in r.get('source_relation_refs',[]):errors.append('H04 entitlement handoff cross-attributed to C05A '+rid)
 # Four previously package-only decisions were re-reviewed against their exact
 # Plan Task rows. Two now have evidence-backed affected Task scopes; the
 # decision itself remains OPEN and BLOCKED. Keep the other two package-only
 # because their source questions do not allocate an execution Task.
 special_scopes={
  'AO:BP-C-0291:01':('PACKAGE',[],['PACKAGE:A04'],[]),
  'AO:BP-C-0294:01':('TASK',['TASK:ASSISTANT:A06:002'],['PACKAGE:A04','PACKAGE:A06'],['docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:8273']),
  'AO:BP-C-0298:01':('PACKAGE',[],['PACKAGE:A02','PACKAGE:A04','PACKAGE:C01'],[]),
  'AO:BP-C-0300:01':('MULTI_TASK',['TASK:ASSISTANT:A01:002','TASK:CORE:C04:001','TASK:CORE:C05A:001','TASK:CORE:C05B:001'],['PACKAGE:A01','PACKAGE:C04','PACKAGE:C05A','PACKAGE:C05B'],['docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:7624','docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:3892','docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:4204','docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:4483'])}
 special_review={x.get('open_decision_id'):x for x in special}
 for oid,(scope,tasks,packages,locators) in special_scopes.items():
  d=next((x for x in decisions if x.get('open_decision_id')==oid),None)
  review=special_review.get(oid)
  actual=d.get('affected_scope',{}) if d else {}
  if (not d or d.get('decision_status','OPEN')!='OPEN' or d.get('mapping_status')!='BLOCKED'
      or d.get('task_refs',[])!=tasks or actual.get('scope_level')!=scope
      or actual.get('task_refs',[])!=tasks or d.get('package_refs',[])!=packages
      or actual.get('package_refs',[])!=packages):
   errors.append('special open-decision scope mismatch '+oid)
  if any(loc not in actual.get('plan_locators',[]) for loc in locators):
   errors.append('special open-decision Plan Task evidence missing '+oid)
  if not review or review.get('decision_status')!='OPEN' or review.get('task_refs',[])!=tasks or review.get('package_refs',[])!=packages:
   errors.append('special open-decision review crosswalk mismatch '+oid)
 if m.get('validation',{}).get('stage4_audit',{}).get('open_decisions_without_plan_locator')!=0:errors.append('current audit snapshot has open decisions without Plan locator')
 # Search/replay complete corpus, deterministically.
 if args.write_code_search and errors:
  return fail(errors)
 audit=m.get('stage4_code_search_audit',{});results,inventory,inventory_sha=build_search(m,tg,cg,manifest,audit)
 if inventory_sha!=audit.get('inventory_sha256') or inventory!=audit.get('corpus_blob_inventory'):errors.append('pinned 347-file code inventory changed')
 counts=Counter(x['search_status'] for x in results)
 if counts.get('SEARCH_INCONCLUSIVE',0):errors.append('SEARCH_INCONCLUSIVE remains in the 657-record audit')
 if len(results)!=657:errors.append(f'expected 657 audited original NEW_IMPLEMENTATION units, got {len(results)}')
 if counts!={'NON_CODE_REQUIREMENT':30,'NO_CODE_EVIDENCE_FOUND':624,'CODE_PARTIALLY_FOUND':3}:errors.append('AUD-07 result distribution differs from reviewed 30/624/3')
 # Every Stage 4 partial code link must point to code represented in immutable Graphify.
 for ref,nids in PARTIAL.items():
  r=next((x for x in maps if x.get('task_ref')==ref),None)
  if not r or r.get('mapping_status')!='PARTIALLY_MAPPED' or set(r.get('current_code_node_refs',[]))!=set(nids):errors.append('evidence-backed partial mapping mismatch '+ref)
 if args.write_code_search and errors:
  return fail(errors)
 if args.write_code_search:
  audit.update({'schema_version':'2.0.0','audit_id':'phase4-stage4-aud07-full-replay-v2','code_source_commit':BASELINE,
   'repository_comparison':{'from':BASELINE,'through_pr_head':PR_BASE,'code_paths_changed':0,'basis':'The pinned Graphify inventory is tied to the active-code baseline; GitHub comparison confirms this PR changes Stage 1–4 artifacts and no active application-code paths.'},
   'method':'Full deterministic search and per-record disposition using exact canonical/short IDs, Plan task labels, and discriminative terms over the full immutable 347-file code inventory. Manual mapping links require Plan ownership plus direct active-code evidence.',
   'inventory_count':len(inventory),'inventory_sha256':inventory_sha,'corpus_blob_inventory':inventory,'search_scope_refs':[r['task_or_package_ref'] for r in results],
   'record_count':len(results),'status_counts':dict(counts),'records':results,
   'decision_summary':{'initial_scope_count':657,'search_completed':len(results),'status_counts':dict(counts),'SEARCH_INCONCLUSIVE':counts.get('SEARCH_INCONCLUSIVE',0),'CODE_FOUND_NOT_IN_GRAPHIFY':counts.get('CODE_FOUND_NOT_IN_GRAPHIFY',0)},
   'limitations':['NO_CODE_EVIDENCE_FOUND means no direct counterpart evidence in the pinned baseline corpus; it does not prove future reuse is impossible.','Lexical co-occurrence is not accepted as mapping evidence.','No Graphify source graph node was added or modified.']})
  m['validation']['stage4_high_finding_followup']['AUD-07']={'status':'COMPLETED_NO_INCONCLUSIVE_RECORDS','initial_scope_count':657,'search_completed':len(results),'status_counts':dict(counts),'code_source_commit':BASELINE,'inventory_count':len(inventory),'inventory_sha256':inventory_sha}
  digest=projection_digest(m)
  m['validation']['semantic_replay_projection_sha256']=digest
  m['validation']['semantic_mapping_reproducibility']='PASS_DETERMINISTIC_SEMANTIC_VALIDATION_REPLAY'
  writej(FILES['mapping'],m)
  print(json.dumps({'write':'PASS','scope':len(results),'status_counts':dict(counts),'inventory_count':len(inventory),'inventory_sha256':inventory_sha,'projection_sha256':digest},ensure_ascii=False,indent=2))
  return 0
 if results!=audit.get('records'):errors.append('AUD-07 full semantic search replay differs from stored records')
 digest=projection_digest(m)
 if m.get('validation',{}).get('semantic_replay_projection_sha256')!=digest:errors.append('semantic mapping/relations/code-search projection changed since recorded replay')
 print(json.dumps({'result':'PASS' if not errors else 'FAIL','graph_counts':dict(counts),'mapping_count':len(maps),'mapping_status_counts':dict(Counter(r['mapping_status'] for r in maps)),'open_decisions':len(decisions),'open_decision_scope_counts':dict(Counter(r['mapping_status'] for r in decisions)),'special_references':len(special),'relations':len(rels),'unresolved_relations':0,'code_search_records':len(results),'code_search_status_counts':dict(counts),'inventory_files':len(inventory),'topological_task_order_count':len(order),'semantic_projection_sha256':digest,'immutable_graphs':'PASS'},ensure_ascii=False,indent=2))
 return fail(errors) if errors else 0
if __name__=='__main__':
 try:
  raise SystemExit(main())
 except (ValueError,OSError) as exc:
  raise SystemExit(f'FAIL: {exc}') from None
