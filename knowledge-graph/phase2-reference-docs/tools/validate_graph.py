#!/usr/bin/env python3
"""Audit a Graphify JSON and its extraction chunks without mutation or external APIs.

This is a mechanical validation: successful literal provenance/coverage checks do
not prove that a quote entails a semantic claim or that extraction is exhaustive.
Reviewers must independently assess each assertion and record their decision.
"""
from __future__ import annotations
import argparse
import collections
import hashlib
import json
import re
from pathlib import Path

SOURCES = {
    'docs/SHAHAB_PHASE_2_DEVELOPMENT_BLUEPRINT.md': ('0709c84fe9e47e1d9218c6d0f93a82c89a62d6b234565e9b0ca2d4158759f266', 2550),
    'docs/SHAHAB_DIGITAL_WALLET.md': ('8b8d139b64f25f8f9592f936c070ece37b3e97df55d4e6b1d0cf305933960b74', 1780),
}
INFERRED = {0.95, 0.85, 0.75, 0.65, 0.55}
RELATIONS = {'calls', 'implements', 'references', 'cites', 'conceptually_related_to', 'shares_data_with', 'semantically_similar_to', 'rationale_for'}
STRUCTURAL_SHA256 = '80d6db4684d9c7f7971d36c714c3f5fe012d2b1893f293f5a754b44d8d4a72c5'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canon(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def attr(obj, key):
    if key in obj:
        return obj[key]
    return (obj.get('attributes') or {}).get(key)


def has_attr(obj, key):
    return key in obj or key in (obj.get('attributes') or {})


def loc_lines(locator, fallback, lo, hi):
    """Parse explicit line references; never treat section numbers as line numbers."""
    value = str(locator or '')
    candidates = []
    for m in re.finditer(r'\bL(\d+)(?:\s*[-–]\s*L?(\d+))?', value):
        a, b = int(m.group(1)), int(m.group(2) or m.group(1))
        if b >= a and b - a <= 5000:
            candidates.extend(range(a, b + 1))
    if not candidates:
        m = re.search(r'\blines?\s+(.+?)(?=;|$)', value, re.I)
        if m:
            candidates.extend(int(x) for x in re.findall(r'\d+', m.group(1)))
    if not candidates:
        m = re.search(r':([\d,\s&andL–-]+)$', value)
        if m:
            value = m.group(1)
        elif re.fullmatch(r'[\d,\s&L–-]+', value):
            pass
        else:
            value = str(fallback or '')
        for part in re.split(r',|\band\b|&', value):
            nums = [int(x) for x in re.findall(r'\d+', part)]
            if len(nums) >= 2 and re.search(r'\d+\s*[-–]\s*L?\d+', part):
                if nums[1] >= nums[0] and nums[1] - nums[0] <= 5000:
                    candidates.extend(range(nums[0], nums[1] + 1))
            else:
                candidates.extend(nums)
    return sorted(set(x for x in candidates if lo <= x <= hi))


def source_span_valid(quote, lines, numbers):
    if not isinstance(quote, str) or not quote.strip() or not numbers:
        return False
    # Search one or more consecutive selected lines without removing markup or ZWNJ.
    # Nonconsecutive citations are not glued into a fictional quote.
    groups = []
    for number in numbers:
        if not groups or number != groups[-1][-1] + 1:
            groups.append([number])
        else:
            groups[-1].append(number)
    return any(quote in '\n'.join(lines[n-1] for n in group) for group in groups)


def confidence_valid(kind, score):
    if isinstance(score, bool) or not isinstance(score, (int, float)):
        return False
    if kind == 'EXTRACTED':
        return score == 1.0
    if kind == 'INFERRED':
        return score in INFERRED
    if kind == 'AMBIGUOUS':
        return 0.1 <= score <= 0.3
    return False


def valid_known_kb_witness(typ, obj, source, numbers):
    """Regression: Blueprint L246 is DRS output, never KB evidence."""
    is_kb=(typ=='node' and obj.get('id')=='docs_shahab_phase_2_development_blueprint_knowledge_base' and source=='docs/SHAHAB_PHASE_2_DEVELOPMENT_BLUEPRINT.md')
    return not (is_kb and 246 in numbers)


def quarantine_evidence_matches_edge(edge, evidence, sources):
    """Require correction citations to be among the quarantined edge's witnesses."""
    if not isinstance(evidence,list) or not evidence:
        return False
    cited=[]
    embedded=edge.get('evidence')
    if isinstance(embedded,list):
        cited=[(item.get('source_file'),item.get('line'),item.get('quote')) for item in embedded if isinstance(item,dict)]
    else:
        source=edge.get('source_file')
        quote=attr(edge,'evidence_quote')
        locator=attr(edge,'evidence_locator') or edge.get('source_location')
        numbers=loc_lines(locator,edge.get('source_location'),1,len(sources.get(source,[])))
        cited=[(source,n,quote) for n in numbers]
    cited_set=set(cited)
    return all(isinstance(item,dict) and (item.get('source_file'),item.get('line'),item.get('quote')) in cited_set for item in evidence)


def manifest_items(manifest):
    if isinstance(manifest, list):
        return [x for x in manifest if isinstance(x, dict)]
    if isinstance(manifest, dict):
        return [x for values in manifest.values() if isinstance(values, list) for x in values if isinstance(x, dict)]
    return []


def actual_tables(src, lo, hi):
    tables, start = [], None
    for n in range(lo, hi+2):
        line = src[n-1] if n <= hi else ''
        if '|' in line:
            start = n if start is None else start
        elif start is not None:
            end = n - 1
            if end > start and any(re.match(r'\s*\|?\s*:?-{3,}', src[k-1]) for k in range(start,end+1)):
                tables.append((start,end))
            start = None
    return tables


def manifest_table_spans(manifest):
    if isinstance(manifest, dict):
        entries = manifest.get('tables', [])
    elif isinstance(manifest, list):
        entries = [e for e in manifest if isinstance(e,dict) and (str(e.get('type') or e.get('kind','')).lower() == 'table' or ('header_line' in e and 'rows' in e) or ('line_start' in e and 'line_end' in e))]
    else:
        return []
    spans=[]
    for entry in entries:
        if not isinstance(entry,dict):
            continue
        nums=[]
        for key in ('location','lines'):
            nums.extend(int(x) for x in re.findall(r'\d+',str(entry.get(key,''))))
        for key in ('line','line_number','header_line','line_start','line_end','start_line','end_line'):
            if isinstance(entry.get(key),int):
                nums.append(entry[key])
        for key in ('rows','witness_lines'):
            if isinstance(entry.get(key),list):
                nums.extend(x for x in entry[key] if isinstance(x,int))
        if nums:
            spans.append((min(nums),max(nums)))
    return spans


class Audit:
    def __init__(self):
        self.errors=[]
        self.metrics=collections.Counter()
        self.warnings=[]

    def check(self, condition, issue):
        if not condition:
            self.errors.append(issue)
        return bool(condition)


def audit(args):
    a=Audit()
    sources={}
    for rel,(expected,length) in SOURCES.items():
        p=args.repo/rel
        if not a.check(p.is_file(),f'source missing: {rel}'):
            continue
        a.check(sha(p)==expected, f'source sha256 mismatch: {rel}')
        lines=p.read_text(encoding='utf-8').splitlines()
        a.check(len(lines)==length,f'source line count mismatch: {rel}')
        sources[rel]=lines
    if len(sources)!=len(SOURCES):
        return a
    progress=json.loads(args.progress.read_text(encoding='utf-8'))
    entries=progress.get('chunks',[])
    a.check(len(entries)==22,'expected exactly 22 checkpoint chunk entries')
    a.check(len({e.get('id') for e in entries})==len(entries),'duplicate checkpoint chunk id')
    ranges=collections.defaultdict(list)
    chunks=[]
    for item in entries:
        cid=item.get('id'); name=item.get('source_file'); lo=item.get('start_line'); hi=item.get('end_line')
        if not a.check(name in sources and isinstance(lo,int) and isinstance(hi,int) and 1<=lo<=hi<=len(sources.get(name,[])), f'{cid}: invalid source/range'):
            continue
        ranges[name].append((lo,hi,cid))
        cp=args.chunks/(str(cid)+'.json')
        if not a.check(cp.is_file(),f'{cid}: missing chunk'):
            continue
        a.check(bool(item.get('output_sha256')),f'{cid}: checkpoint chunk hash missing')
        if item.get('output_sha256'):
            a.check(sha(cp)==item['output_sha256'],f'{cid}: chunk hash differs from checkpoint')
        a.check(item.get('status')=='PASS' and item.get('validation')=='PASS',f'{cid}: checkpoint status not PASS')
        data=json.loads(cp.read_text(encoding='utf-8')); chunks.append((cid,data))
        src=sources[name]
        coverage=data.get('coverage_range',{}); coverage=coverage.get(name,coverage) if isinstance(coverage,dict) else {}
        a.check(coverage.get('start_line')==lo and coverage.get('end_line')==hi,f'{cid}: coverage range mismatch')
        a.check(data.get('coverage',{}).get(name)==hi-lo+1,f'{cid}: coverage count mismatch')
        nodes=data.get('nodes',[]); edges=data.get('edges',[]); ids={n.get('id') for n in nodes}
        a.check(len(ids)==len(nodes),f'{cid}: duplicate node ID')
        items=manifest_items(data.get('coverage_manifest'))
        headings=[n for n in range(lo,hi+1) if re.match(r'^\s{0,3}#{1,6}\s+',src[n-1])]
        for n in headings:
            covered=any(e.get('line')==n or n in e.get('witness_lines',[]) or e.get('start_line',10**9)<=n<=e.get('end_line',-1) for e in items)
            a.check(covered or any(src[n-1].strip() in str(e) for e in items),f'{cid}: heading L{n} missing from manifest')
        tables=actual_tables(src,lo,hi); spans=manifest_table_spans(data.get('coverage_manifest'))
        for start,end in tables:
            a.check(any(x<=start and y>=end for x,y in spans),f'{cid}: table L{start}-L{end} missing from manifest')
        a.metrics['headings']+=len(headings); a.metrics['table_blocks']+=len(tables)
        for typ, records in [('node',nodes),('edge',edges)]:
            for ix,obj in enumerate(records):
                key=f'{cid}:{typ}[{ix}]'
                a.check(obj.get('source_file')==name,f'{key}: incorrect source_file')
                quote=attr(obj,'evidence_quote'); loc=attr(obj,'evidence_locator') or obj.get('source_location')
                # Citations must resolve to exact lines in the pinned full source; a corrected node may cite its defining section outside this extraction chunk.
                nums=loc_lines(loc,obj.get('source_location'),1,len(src))
                a.check(source_span_valid(quote,src,nums),f'{key}: quote absent at exact cited lines')
                # L246 is preceding DRS output, not Knowledge Base evidence.
                a.check(valid_known_kb_witness(typ,obj,name,nums),f'{key}: known wrong Knowledge Base witness is DRS L246')
                for field in ('decision_status','owner'):
                    a.check(has_attr(obj,field),f'{key}: missing {field} field')
                st=attr(obj,'decision_status')
                a.check(isinstance(st,str) and bool(st.strip()),f'{key}: empty decision_status; record unknown explicitly')
                owner=attr(obj,'owner'); owner_status=attr(obj,'owner_status')
                if owner is None or (isinstance(owner,str) and not owner.strip()):
                    a.check(isinstance(owner_status,str) and bool(owner_status.strip()),f'{key}: unknown owner needs explicit owner_status')
                if typ=='edge':
                    a.check(obj.get('source') in ids and obj.get('target') in ids,f'{key}: endpoint not in chunk')
                    a.check(confidence_valid(obj.get('confidence'),obj.get('confidence_score')),f'{key}: confidence rubric invalid')
                    a.check(obj.get('relation') in RELATIONS,f'{key}: invalid relationship type')
                a.metrics['chunk_'+typ+'s']+=1
    for name,src in sources.items():
        ordered=sorted(ranges[name]); cursor=1
        for lo,hi,cid in ordered:
            a.check(lo==cursor,f'{cid}: gap/overlap before L{lo}; expected L{cursor}')
            cursor=hi+1
        a.check(cursor==len(src)+1,f'{name}: checkpoint ranges do not cover final line')
    a.check(sha(args.structural)==STRUCTURAL_SHA256,'structural baseline sha256 mismatch')
    graph=json.loads(args.graph.read_text(encoding='utf-8')); base=json.loads(args.structural.read_text(encoding='utf-8'))
    nodes=graph.get('nodes',[]); edges=graph.get('links',[]); ids=[n.get('id') for n in nodes]; idset=set(ids)
    a.check(graph.get('directed') is True,'graph not directed')
    a.check(graph.get('multigraph') is True,'graph must preserve parallel edges')
    a.check(len(ids)==len(idset),'graph has duplicate node IDs')
    for ix,e in enumerate(edges):
        a.check(e.get('source') in idset and e.get('target') in idset, f'graph edge[{ix}] dangling endpoint')
    # Exact original structural records, including multiplicity and metadata, survive.
    available=collections.Counter(canon(n) for n in nodes)
    variants=graph.get('lossless_merge',{}).get('node_variants',[])
    # The ordinary case has structural nodes as the first and unmodified record.
    for n in base.get('nodes',[]):
        a.check(available[canon(n)]>0,f'structural node missing or mutated: {n.get("id")}')
        if available[canon(n)]>0: available[canon(n)]-=1
    # Duplicate semantic IDs are recorded as complete node variants.  Count
    # exact input records, including repeated identical records, rather than
    # just checking that an ID exists somewhere in the output graph.
    available.update(canon(v.get('node')) for v in variants if isinstance(v,dict) and isinstance(v.get('node'),dict))
    for cid, data in chunks:
        for ix, node in enumerate(data.get('nodes', [])):
            key=canon(node)
            a.check(available[key]>0, f'{cid}: node[{ix}] missing or changed in controlled union')
            if available[key]>0: available[key]-=1
    for key,count in available.items():
        a.check(count==0,f'graph contains {count} unconsumed node record(s) absent from structural/chunk inputs: {key[:160]}')
    available=collections.Counter(canon(e) for e in edges)
    for ix,e in enumerate(base.get('links',[])):
        a.check(available[canon(e)]>0,f'structural link[{ix}] missing or mutated')
        if available[canon(e)]>0: available[canon(e)]-=1
    quarantined=graph.get('lossless_merge',{}).get('quarantined_edges',[])
    corrections_exists=bool(args.corrections and args.corrections.is_file())
    a.check(corrections_exists,'reviewed corrections file missing')
    corrections_data=json.loads(args.corrections.read_text(encoding='utf-8')) if corrections_exists else {}
    corrections=corrections_data.get('quarantine',[])
    a.check(isinstance(corrections,list),'corrections file must contain a quarantine array')
    correction_by_hash={}
    for ix,c in enumerate(corrections if isinstance(corrections,list) else []):
        digest=c.get('record_sha256') if isinstance(c,dict) else None
        a.check(isinstance(digest,str) and len(digest)==64,f'corrections quarantine[{ix}]: invalid record hash')
        if isinstance(digest,str):
            a.check(digest not in correction_by_hash,f'corrections quarantine[{ix}]: duplicate record hash')
            correction_by_hash[digest]=c
        a.check(isinstance(c,dict) and isinstance(c.get('reason'),str) and bool(c['reason'].strip()),f'corrections quarantine[{ix}]: reason missing')
        evidence=c.get('evidence',[]) if isinstance(c,dict) else []
        a.check(isinstance(evidence,list) and bool(evidence),f'corrections quarantine[{ix}]: evidence missing')
        for j,ev in enumerate(evidence if isinstance(evidence,list) else []):
            name=ev.get('source_file') if isinstance(ev,dict) else None
            number=ev.get('line') if isinstance(ev,dict) else None
            quote=ev.get('quote') if isinstance(ev,dict) else None
            valid=name in sources and isinstance(number,int) and 1<=number<=len(sources[name]) and isinstance(quote,str) and bool(quote) and quote in sources[name][number-1]
            a.check(valid,f'corrections quarantine[{ix}]: evidence[{j}] is not exact source line')
    # Quarantine can account only for an authentic semantic input edge. Build
    # that inventory before considering quarantine metadata, so fabricated
    # `original_edge` values cannot conceal missing chunk/review records.
    expected_semantic_edges=collections.Counter()
    for _,data in chunks:
        expected_semantic_edges.update(canon(e) for e in data.get('edges',[]))
    review_paths=sorted(args.reviews.glob('*.json')) if args.reviews else []
    for path in review_paths:
        reviewed=json.loads(path.read_text(encoding='utf-8'))
        expected_semantic_edges.update(canon(e) for e in reviewed.get('edges',[]))
    structural_edges=collections.Counter(canon(e) for e in base.get('links',[]))
    for ix,q in enumerate(quarantined):
        original=q.get('original_edge')
        a.check(isinstance(original,dict),f'quarantined edge[{ix}]: original record missing')
        a.check(isinstance(q.get('reason'),str) and bool(q['reason'].strip()),f'quarantined edge[{ix}]: reason missing')
        a.check(bool(q.get('evidence')),f'quarantined edge[{ix}]: source-based evidence missing')
        a.check(q.get('action')=='quarantined_from_active_graph',f'quarantined edge[{ix}]: invalid action')
        if isinstance(original,dict):
            key=canon(original)
            digest=hashlib.sha256(key.encode('utf-8')).hexdigest()
            a.check(q.get('record_sha256')==digest,f'quarantined edge[{ix}]: record hash does not match original')
            correction=correction_by_hash.get(digest)
            a.check(correction is not None,f'quarantined edge[{ix}]: no matching reviewed correction record')
            if correction is not None:
                a.check(q.get('reason')==correction.get('reason'),f'quarantined edge[{ix}]: reason differs from reviewed correction')
                a.check(q.get('evidence')==correction.get('evidence'),f'quarantined edge[{ix}]: evidence differs from reviewed correction')
                a.check(quarantine_evidence_matches_edge(original,correction.get('evidence'),sources),f'quarantined edge[{ix}]: correction evidence does not match original edge witness')
                a.check(q.get('allowed_replacement_sha256',[])==correction.get('allowed_replacement_sha256',[]),f'quarantined edge[{ix}]: replacement hashes differ from reviewed correction')
                correction_by_hash.pop(digest)
            a.check(structural_edges[key]==0,f'quarantined edge[{ix}]: protected structural record cannot be quarantined')
            a.check(expected_semantic_edges[key]>0,f'quarantined edge[{ix}]: original record is absent from controlled inputs')
            if expected_semantic_edges[key]>0: expected_semantic_edges[key]-=1
    a.check(not correction_by_hash,f'{len(correction_by_hash)} reviewed correction record(s) missing from graph quarantine')
    available_hyper=collections.Counter(canon(h) for h in graph.get('hyperedges',[]))
    for h in base.get('hyperedges',[]):
        a.check(available_hyper[canon(h)]>0,'structural hyperedge missing or mutated')
        if available_hyper[canon(h)]>0: available_hyper[canon(h)]-=1
    for cid,data in chunks:
        for ix,h in enumerate(data.get('hyperedges',[])):
            a.check(available_hyper[canon(h)]>0,f'{cid}: hyperedge[{ix}] missing or mutated')
            if available_hyper[canon(h)]>0: available_hyper[canon(h)]-=1
    if args.reviews:
        a.check(len(review_paths)==3,'expected three independent relation-review files')
        for path in review_paths:
            reviewed=json.loads(path.read_text(encoding='utf-8'))
            for ix,e in enumerate(reviewed.get('edges',[])):
                key=f'{path.name}:edge[{ix}]'
                a.check(e.get('source') in idset and e.get('target') in idset,f'{key}: endpoint missing')
                a.check(confidence_valid(e.get('confidence'),e.get('confidence_score')),f'{key}: confidence rubric invalid')
                a.check(e.get('relation') in RELATIONS,f'{key}: invalid relationship type')
                for field in ('decision_status','owner'):
                    a.check(has_attr(e,field),f'{key}: missing {field} field')
                a.check(isinstance(attr(e,'decision_status'),str) and bool(attr(e,'decision_status').strip()),f'{key}: empty decision_status')
                if attr(e,'owner') is None:
                    a.check(isinstance(attr(e,'owner_status'),str) and bool(attr(e,'owner_status').strip()),f'{key}: unknown owner needs explicit owner_status')
                evidence=e.get('evidence',[])
                a.check(isinstance(evidence,list) and bool(evidence),f'{key}: evidence missing')
                for j,ev in enumerate(evidence):
                    name=ev.get('source_file'); n=ev.get('line'); quote=ev.get('quote')
                    valid=name in sources and isinstance(n,int) and 1<=n<=len(sources[name]) and isinstance(quote,str) and bool(quote) and quote in sources[name][n-1]
                    a.check(valid,f'{key}: evidence[{j}] is not exact source line')
                a.metrics['review_edges']+=1
    # Every non-structural active edge must be accounted for exactly once by
    # the chunk/review inputs, and every expected edge must be active or
    # validly quarantined. Reject unreviewed extras as well as omissions.
    active_semantic_edges=collections.Counter(canon(e) for e in edges)
    for edge,count in structural_edges.items():
        if active_semantic_edges[edge]>=count: active_semantic_edges[edge]-=count
        else: active_semantic_edges[edge]=0
    for key,count in expected_semantic_edges.items():
        a.check(active_semantic_edges[key]>=count,f'controlled semantic edge missing or changed: {key[:160]}')
        if active_semantic_edges[key]>=count: active_semantic_edges[key]-=count
    for key,count in active_semantic_edges.items():
        a.check(count==0,f'graph contains {count} unconsumed link record(s) absent from structural/chunk/review inputs: {key[:160]}')
    for key,count in available_hyper.items():
        a.check(count==0,f'graph contains {count} unconsumed hyperedge record(s): {key[:160]}')
    a.metrics.update({'graph_nodes':len(nodes),'graph_edges':len(edges),'graph_hyperedges':len(graph.get('hyperedges',[])),'structural_nodes':len(base.get('nodes',[])),'structural_edges':len(base.get('links',[])),'node_variants':len(variants),'quarantined_edges':len(quarantined),'chunks':len(chunks)})
    a.warnings.append('PASS means mechanical checks passed only; semantic entailment, ownership classification and atomic completeness require independently recorded source-based review.')
    return a


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo',type=Path,required=True,help='checkout containing the two pinned docs')
    p.add_argument('--graph',type=Path,required=True)
    p.add_argument('--structural',type=Path,required=True)
    p.add_argument('--progress',type=Path,required=True)
    p.add_argument('--chunks',type=Path,required=True)
    p.add_argument('--reviews',type=Path,required=True,help='directory containing exactly three reviewed relation JSON files')
    p.add_argument('--corrections',type=Path,required=True,help='reviewed exact quarantine corrections JSON')
    p.add_argument('--output',type=Path)
    args=p.parse_args()
    a=audit(args)
    result={'result':'PASS' if not a.errors else 'FAIL','metrics':dict(a.metrics),'issue_count':len(a.errors),'issues':a.errors,'warnings':a.warnings}
    data=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if args.output:
        args.output.write_text(data,encoding='utf-8')
    else:
        print(data,end='')
    raise SystemExit(1 if a.errors else 0)


if __name__=='__main__':
    main()
