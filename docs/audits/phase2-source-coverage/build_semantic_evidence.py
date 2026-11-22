#!/usr/bin/env python3
"""Export package-authored source dispositions as an auditable evidence register.

This importer preserves source locators and the package plan's own disposition;
its output is not a fresh semantic approval and never upgrades coverage to VERIFIED.
"""
from __future__ import annotations
import csv, json, re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PLAN = ROOT / 'docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md'
REGISTRY = ROOT / 'docs/phase2/core/CORE_REGISTRY.jsonl'
COVERAGE = Path(__file__).resolve().parent
PKG_HEADING = re.compile(r'^###\s+((?:C\d{2}[ab]?|R\d{2}|A\d{2}))\s+[—–-]\s+(.+)$')
CAND_ID = re.compile(r'\b(?:CAN|CAND|CANDIDATE):[A-Z0-9]+(?::[A-Z0-9]+)*\b')
SRC_REF = re.compile(r'\b([BW]):\s*(\d+)(?:\s*[-–—]\s*(\d+))?')
SOURCE_UNIT = re.compile(r'\bSU-([BW])-(\d{5})\b')
SOURCE_UNIT_RANGE = re.compile(r'\bSU-([BW])-(\d{5})(?:\.\.(?:SU-[BW]-)?(\d{5}))?\b')
BLUEPRINT_SECTION_LOCATOR = re.compile(r'(?:ADR-RAG-\d+|§\d+(?:\.\d+)+)\s*:\s*(\d+)(?:\s*[-–—]\s*(\d+))?')
ID_RE = re.compile(r'\b(?:REQ|TASK|AC|TEST|TD|TC|EN|TE|STORY|HANDOFF|CONTRACT|OPEN|DECISION):[A-Z0-9]+(?::[A-Z0-9]+){0,3}(?:\.S\d+)?\b')
NUMBER_RANGE = re.compile(r'(\d+)(?:\s*[-–—]\s*(\d+))?')

def source_refs_in_line(line):
    refs=[parse_ref(m) for m in SRC_REF.finditer(line)]
    if re.search(r'\bBlueprint\b|\bADR-RAG-\d+\b',line,re.I):
        for marker in re.finditer(r'\b(?:lines?|line|خطوط)\s*([^;|]+)',line,re.I):
            fragment=marker.group(1)
            for loc in NUMBER_RANGE.finditer(fragment):
                a=int(loc.group(1)); b=int(loc.group(2) or loc.group(1))
                if a<=2550 and b<=2550:
                    refs.append({'document':'docs/SHAHAB_PHASE_2_DEVELOPMENT_BLUEPRINT.md','start':a,'end':b,'literal':f'B:{a}–{b}'})
    for loc in BLUEPRINT_SECTION_LOCATOR.finditer(line):
        a=int(loc.group(1)); b=int(loc.group(2) or loc.group(1))
        if a<=2550 and b<=2550:
            refs.append({'document':'docs/SHAHAB_PHASE_2_DEVELOPMENT_BLUEPRINT.md','start':a,'end':b,'literal':f'B:{a}–{b}'})
    return refs


def parse_ref(m):
    return {'document': 'docs/SHAHAB_PHASE_2_DEVELOPMENT_BLUEPRINT.md' if m.group(1)=='B' else 'docs/SHAHAB_DIGITAL_WALLET.md', 'start':int(m.group(2)), 'end':int(m.group(3) or m.group(2)), 'literal':m.group(0)}

def main():
    plan_lines=PLAN.read_text(encoding='utf-8').splitlines()
    sources={k:(ROOT/v).read_text(encoding='utf-8').splitlines() for k,v in {'B':'docs/SHAHAB_PHASE_2_DEVELOPMENT_BLUEPRINT.md','W':'docs/SHAHAB_DIGITAL_WALLET.md'}.items()}
    source_units={}
    if REGISTRY.exists():
        for raw in REGISTRY.read_text(encoding='utf-8').splitlines():
            obj=json.loads(raw)
            if obj.get('t')=='u': source_units[obj['id']]=obj
    heads=defaultdict(list)
    for i,line in enumerate(plan_lines):
        m=PKG_HEADING.match(line)
        if m: heads[m.group(1)].append((i,m.group(2)))
    rows=[]
    seen=set()
    # Import package candidate rows from their final package sections. Shared
    # candidate registers are retained under the owning package named in ID.
    for pkg,positions in heads.items():
        start,title=positions[-1]
        end=next((i for i in range(start+1,len(plan_lines)) if PKG_HEADING.match(plan_lines[i])),len(plan_lines))
        for offset,line in enumerate(plan_lines[start:end],start+1):
            if not line.strip().startswith('|'): continue
            ids=CAND_ID.findall(line)
            refs=source_refs_in_line(line)
            su_literals=[]
            for match in SOURCE_UNIT_RANGE.finditer(line):
                doc,a,b=match.group(1),int(match.group(2)),int(match.group(3) or match.group(2))
                for number in range(a,b+1):
                    unit=source_units.get(f'SU-{doc}-{number:05d}')
                    if unit:
                        refs.append({'document':'docs/SHAHAB_PHASE_2_DEVELOPMENT_BLUEPRINT.md' if doc=='B' else 'docs/SHAHAB_DIGITAL_WALLET.md','start':unit['a'],'end':unit['z'],'literal':f'SU-{doc}-{number:05d}'})
                su_literals.append(match.group(0))
            if not ids: continue
            for doc,number in SOURCE_UNIT.findall(line):
                unit=source_units.get(f'SU-{doc}-{number}')
                if unit:
                    refs.append({'document':'docs/SHAHAB_PHASE_2_DEVELOPMENT_BLUEPRINT.md' if doc=='B' else 'docs/SHAHAB_DIGITAL_WALLET.md','start':unit['a'],'end':unit['z'],'literal':f'SU-{doc}-{number}'})
            tokens=sorted(set(ID_RE.findall(line)))
            cells=[c.strip() for c in line.strip().strip('|').split('|')]
            for candidate in ids:
                # Avoid counting a referenced candidate as a new row unless it
                # is a first-column identifier in the table row.
                if not cells or candidate.strip('`') not in cells[0]: continue
                owner=pkg
                match=re.search(r'(?:CAN|CAND|CANDIDATE):(?:RAG:|ASSISTANT:)?(C\d{2}[AB]?|R\d{2}|A\d{2})\b',candidate)
                if match:
                    owner=match.group(1).replace('C05A','C05a').replace('C05B','C05b').replace('C11A','C11a').replace('C12A','C12a').replace('C12B','C12b').replace('C13A','C13a').replace('C13B','C13b')
                key=(owner,candidate,offset)
                if key in seen: continue
                seen.add(key)
                excerpts=[]
                for ref in refs:
                    snippet=' '.join(sources['B' if ref['document'].endswith('BLUEPRINT.md') else 'W'][ref['start']-1:ref['end']])
                    excerpts.append(f"{ref['literal']} :: {snippet[:900]}")
                rows.append({'package_id':owner,'candidate_id':candidate,'plan_locator':f'{PLAN.relative_to(ROOT)}:{offset}','source_locators':';'.join(r['literal'] for r in refs),'source_text_excerpts':' || '.join(excerpts),'linked_requirement_ids':';'.join(x for x in tokens if x.startswith('REQ:')),'linked_task_ids':';'.join(x for x in tokens if x.startswith('TASK:')),'linked_ac_test_ids':';'.join(x for x in tokens if x.startswith(('AC:','TEST:','TD:','TC:'))),'package_disposition_text':' | '.join(cells[1:]),'evidence_status':'PACKAGE_RA_EVIDENCE_RECORDED_NOT_INDEPENDENTLY_REVERIFIED'})
        # Preserve package source references outside Candidate tables too.
        # These are locators or dispositions, never silently treated as requirements.
        for offset,line in enumerate(plan_lines[start:end],start+1):
            if CAND_ID.search(line): continue
            refs=source_refs_in_line(line)
            for match in SOURCE_UNIT_RANGE.finditer(line):
                doc,a,b=match.group(1),int(match.group(2)),int(match.group(3) or match.group(2))
                for number in range(a,b+1):
                    unit=source_units.get(f'SU-{doc}-{number:05d}')
                    if unit: refs.append({'document':'docs/SHAHAB_PHASE_2_DEVELOPMENT_BLUEPRINT.md' if doc=='B' else 'docs/SHAHAB_DIGITAL_WALLET.md','start':unit['a'],'end':unit['z'],'literal':f'SU-{doc}-{number:05d}'})
            if not refs: continue
            tokens=sorted(set(ID_RE.findall(line)))
            cells=[c.strip() for c in line.strip().strip('|').split('|')]
            excerpts=[]
            for ref in refs:
                key='B' if ref['document'].endswith('BLUEPRINT.md') else 'W'
                snippet=' '.join(sources[key][ref['start']-1:ref['end']])
                excerpts.append(f"{ref['literal']} :: {snippet[:700]}")
            rows.append({'package_id':pkg,'candidate_id':'','plan_locator':f'{PLAN.relative_to(ROOT)}:{offset}','source_locators':';'.join(r['literal'] for r in refs),'source_text_excerpts':' || '.join(excerpts),'linked_requirement_ids':';'.join(x for x in tokens if x.startswith('REQ:')),'linked_task_ids':';'.join(x for x in tokens if x.startswith('TASK:')),'linked_ac_test_ids':';'.join(x for x in tokens if x.startswith(('AC:','TEST:','TD:','TC:'))),'package_disposition_text':line.strip(),'evidence_status':'PACKAGE_SCOPE_LOCATOR_RECORDED_NOT_INDEPENDENTLY_REVERIFIED'})
    # C01/C02 candidate evidence is maintained in the source-locked registry.
    if REGISTRY.exists():
        for lineno,line in enumerate(REGISTRY.read_text(encoding='utf-8').splitlines(),1):
            obj=json.loads(line)
            if obj.get('t')=='u':
                pkg=obj.get('p') or ''
                if pkg!='C01' or obj.get('st')!='RA': continue
                doc=obj.get('s'); a=obj.get('a'); b=obj.get('z')
                excerpt=' '.join(sources[doc][a-1:b])
                clauses=(obj.get('semantic_review') or {}).get('clauses') or [{}]
                rows.append({'package_id':pkg,'candidate_id':'','plan_locator':f'docs/phase2/core/CORE_REGISTRY.jsonl:{lineno}','source_locators':f'{doc}:{a}–{b}','source_text_excerpts':f'{doc}:{a}–{b} :: {excerpt[:900]}','linked_requirement_ids':';'.join(obj.get('r',[]) or []),'linked_task_ids':'','linked_ac_test_ids':'','package_disposition_text':f"source_unit={obj.get('id','')}; classification={obj.get('classification','')}; disposition={obj.get('disposition','')}; review={obj.get('review_status','')}; {clauses[0].get('reason','')}",'evidence_status':'C01_SOURCE_UNIT_REVIEW_RECORDED_NOT_INDEPENDENTLY_REVERIFIED'})
                continue
            if obj.get('t')=='semantic_unit_review':
                if obj.get('pkg')!='C02': continue
                span=obj.get('source_span') or []
                if len(span)<3: continue
                doc=span[0]; a=int(span[1]); b=int(span[2]); excerpt=' '.join(sources[doc][a-1:b])
                rows.append({'package_id':'C02','candidate_id':'','plan_locator':f'docs/phase2/core/CORE_REGISTRY.jsonl:{lineno}','source_locators':f'{doc}:{a}–{b}','source_text_excerpts':f'{doc}:{a}–{b} :: {excerpt[:900]}','linked_requirement_ids':';'.join(obj.get('candidate_ids',[]) or []),'linked_task_ids':'','linked_ac_test_ids':'','package_disposition_text':f"source_unit={obj.get('source_unit_id','')}; classification={obj.get('classification','')}; disposition={obj.get('disposition','')}; {obj.get('reason','')}",'evidence_status':'C02_SOURCE_CONTEXT_REVIEW_RECORDED_NOT_INDEPENDENTLY_REVERIFIED'})
                continue
            if obj.get('t')!='candidate': continue
            pkg=obj.get('pkg','')
            spans=obj.get('span') or []
            locators=[]
            if len(spans)>=3 and spans[0] in {'B','W'}:
                locators=[f"{spans[0]}:{spans[1]}–{spans[2]}"]
            if pkg not in {'C01','C02'}: continue
            src_excerpts=[]
            for loc in locators:
                m=re.match(r'([BW]):(\d+)–(\d+)',loc)
                if m:
                    doc=m.group(1); a=int(m.group(2)); b=int(m.group(3))
                    snippet=' '.join(sources[doc][a-1:b])
                    src_excerpts.append(f'{loc} :: {snippet[:900]}')
            rows.append({'package_id':pkg,'candidate_id':obj.get('id',''),'plan_locator':f'docs/phase2/core/CORE_REGISTRY.jsonl:{lineno}','source_locators':';'.join(locators),'source_text_excerpts':' || '.join(src_excerpts),'linked_requirement_ids':';'.join(obj.get('requirements',[]) or []),'linked_task_ids':'','linked_ac_test_ids':'','package_disposition_text':f"owner={obj.get('owner_package','')}; status={obj.get('status','')}; normative_status={obj.get('normative_status','')}; {obj.get('text','')}",'evidence_status':'SOURCE_LOCKED_REGISTRY_EVIDENCE_RECORDED_NOT_INDEPENDENTLY_REVERIFIED'})
    fields=['package_id','candidate_id','plan_locator','source_locators','source_text_excerpts','linked_requirement_ids','linked_task_ids','linked_ac_test_ids','package_disposition_text','evidence_status']
    out=COVERAGE/'package-semantic-evidence.csv'
    with out.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(sorted(rows,key=lambda r:(r['package_id'],r['candidate_id'],r['plan_locator'])))
    # Quantify explicit evidence only; do not imply whole-source coverage.
    by=defaultdict(list)
    for r in rows: by[r['package_id']].append(r)
    index=list(csv.DictReader((COVERAGE/'package-execution-index.csv').open(encoding='utf-8-sig',newline='')))
    outrows=[]
    for item in index:
        pkg=item['package_id']; rs=by[pkg]
        allrefs=set(); reqmapped=0; candidate_ids=set(); unit_rows=0
        for r in rs:
            allrefs.update(re.findall(r'\b[WB]:\d+(?:[–-]\d+)?',r['source_locators']))
            if r['candidate_id']: candidate_ids.add(r['candidate_id'])
            unit_rows+=bool('SU-' in r['source_locators'])
            reqmapped+=bool(r['linked_requirement_ids'])
        outrows.append({'package_id':pkg,'package_name':item['package_name'],'planning_status':item['planning_status'],'reported_ra':item['declared_ra'],'reported_ipa':item['declared_ipa'],'package_evidence_rows':len(rs),'distinct_candidate_ids':len(candidate_ids),'source_unit_linked_rows':unit_rows,'requirement_linked_evidence_rows':reqmapped,'distinct_direct_source_locators':len(allrefs),'package_evidence_status':'EVIDENCE_PRESENT' if rs else 'NO_PACKAGE_EVIDENCE_IMPORTED','independent_semantic_revalidation':'NOT_CLAIMED','notes':'Counts describe imported locators/dispositions and prior package evidence; they do not assert fresh semantic approval or whole-program coverage.'})
    fields2=list(outrows[0])
    with (COVERAGE/'package-semantic-audit.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields2,lineterminator='\n');w.writeheader();w.writerows(outrows)
    print(json.dumps({'package_evidence_rows':len(rows),'packages_with_imported_evidence':len(by),'packages_without_imported_evidence':[x['package_id'] for x in index if not by[x['package_id']]],'package_summary':[{k:v for k,v in r.items() if k in ('package_id','package_evidence_rows','distinct_candidate_ids','source_unit_linked_rows','requirement_linked_evidence_rows')} for r in outrows]},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
