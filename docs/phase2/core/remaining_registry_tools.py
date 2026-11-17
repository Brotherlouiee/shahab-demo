"""Validate/render the remaining Core planning registry without product execution."""
from __future__ import annotations

import argparse
import collections
import copy
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DIRECTORY = ROOT / 'docs/phase2/core'
REGISTRY = DIRECTORY / 'CORE_REGISTRY.jsonl'
BASE = '3030623ddb669c9d6cd311d2e032bb911d0cc612'
C02_CASE_BASELINE = 'b141778eb8c2eb41d73afd3a9cea79892c89f032'  # Provenance retained in checkpoint; CI does not require this local-only commit object.


def need(condition, message):
    if not condition:
        raise ValueError(message)


def epic_status_ok(by):
    e=by.get('TE:CORE:C02:001', {})
    return e.get('planning_status') == 'PLANNING_ACCEPTED' and 'BLOCKED' in e.get('implementation_status','')


def assess_global_triage(inventory, triage):
    """Return completion only when each inventoried unit has a sourced semantic disposition."""
    ids=[x.get('source_unit_id') for x in triage]
    if len(ids)!=len(set(ids)) or set(ids)!=set(inventory): return False
    for item in triage:
        d=item.get('global_disposition',{})
        if d.get('evidence_refs')!=item.get('evidence_refs'): return False
        if item.get('screening_status') not in ('REUSED_PRIOR_REVIEW','SEMANTICALLY_SCREENED'): return False
        if not d.get('classification') or not d.get('owner_domain') or not d.get('rationale') or not d.get('evidence_refs'): return False
        if not isinstance(d.get('package_relations'),list) or not isinstance(d.get('risk_tier'),str): return False
    return True


def assess_scope_view(view, inventory):
    """Allow honest INITIAL views; COMPLETE requires exact, reasoned one-to-one coverage."""
    status=view.get('scope_status')
    if status=='INITIAL':
        digest=view.get('unresolved_unit_ids_sha256','')
        backed=view.get('evidence_backed_unit_ids')
        if not isinstance(backed,list) or len(backed)!=len(set(backed)) or not set(backed)<=set(inventory): return False
        unresolved=sorted(set(inventory)-set(backed))
        expected=hashlib.sha256('\n'.join(unresolved).encode()).hexdigest()
        return (isinstance(view.get('unresolved_unit_count'),int) and view['unresolved_unit_count']==len(unresolved)
                and bool(re.fullmatch(r'[0-9a-f]{64}',digest)) and digest==expected)
    if status!='COMPLETE': return False
    assignments=view.get('scope_assignments',[])
    ids=[x.get('unit_id') for x in assignments]
    valid={'OWNED','SHARED_CONTRACT','CROSS_REFERENCE','UNCERTAIN','EXCLUDED_WITH_REASON'}
    return (len(ids)==len(set(ids)) and set(ids)==set(inventory)
            and all(x.get('category') in valid and x.get('reason') and x.get('evidence_refs') for x in assignments))


def assess_evidence_gate(status, required_ids, evidenced_ids, blockers):
    """PASS requires a nonempty exact evidence set and zero recorded blockers."""
    return status=='PASS' and bool(required_ids) and set(required_ids)==set(evidenced_ids) and blockers==0


def normalized_case_fingerprint(case):
    fields=('actor_fixture','initial_state_and_authority','action','input','observable_expectation','side_effect_invariant','boundary_or_race')
    value=' '.join(str(case.get(k,'')).casefold() for k in fields)
    value=re.sub(r'\b(?:req|test|ac)[:._-]?core[:._-]?c02[:._-]?\d+\b','ID',value)
    value=re.sub(r'\b(?:p|e|a|o|i|n)-?\d+\b','FIX',value)
    return ' '.join(value.split())


def transition_checks():
    """Exercise incomplete rejection, genuine completion, and both scope states."""
    inventory={'SU-X-1','SU-X-2'}
    complete=[{'source_unit_id':u,'screening_status':'SEMANTICALLY_SCREENED','evidence_refs':['E:'+u],'global_disposition':{'classification':'CONTEXT','owner_domain':'Core','rationale':'Fixture-specific contextual classification from source text.','evidence_refs':['E:'+u],'package_relations':[],'risk_tier':'LOW'}} for u in sorted(inventory)]
    incomplete=copy.deepcopy(complete); incomplete[1]['screening_status']='UNCERTAIN_NOT_SEMANTICALLY_REVIEWED'
    need(not assess_global_triage(inventory,incomplete),'G1 transition accepted incomplete evidence')
    need(assess_global_triage(inventory,complete),'G1 transition rejected fully sourced evidence')
    initial={'scope_status':'INITIAL','evidence_backed_unit_ids':['SU-X-1'],'unresolved_unit_count':1,'unresolved_unit_ids_sha256':hashlib.sha256(b'SU-X-2').hexdigest()}
    scope_complete={'scope_status':'COMPLETE','scope_assignments':[{'unit_id':u,'category':'EXCLUDED_WITH_REASON','reason':'Fixture source reviewed and outside this package domain.','evidence_refs':['E:'+u]} for u in sorted(inventory)]}
    false_complete=copy.deepcopy(scope_complete); false_complete['scope_assignments'].pop()
    need(not assess_scope_view(false_complete,inventory),'Scope View transition accepted incomplete assignment')
    need(assess_scope_view(scope_complete,inventory),'Scope View transition rejected complete assignment')
    need(assess_scope_view(initial,inventory),'Scope View transition rejected permitted initial state')
    expected={'REQ-X-1','REQ-X-2'}
    ra_complete={'status':'PASS','evidence':expected,'blockers':0}
    ra_incomplete={'status':'PASS','evidence':{'REQ-X-1'},'blockers':0}
    ipa_complete={'status':'PASS','evidence':expected,'blockers':0}
    ipa_incomplete={'status':'PASS','evidence':expected-{'REQ-X-2'},'blockers':0}
    need(not assess_evidence_gate(ra_incomplete['status'],expected,ra_incomplete['evidence'],ra_incomplete['blockers']),'RA transition accepted incomplete evidence')
    need(assess_evidence_gate(ra_complete['status'],expected,ra_complete['evidence'],ra_complete['blockers']),'RA transition rejected complete evidence')
    need(not assess_evidence_gate(ipa_incomplete['status'],expected,ipa_incomplete['evidence'],ipa_incomplete['blockers']),'IPA transition accepted incomplete evidence')
    need(assess_evidence_gate(ipa_complete['status'],expected,ipa_complete['evidence'],ipa_complete['blockers']),'IPA transition rejected complete evidence')
    return {'g1_incomplete_rejected':True,'g1_complete_accepted':True,'scope_incomplete_rejected':True,'scope_complete_accepted':True,'scope_initial_accepted':True,'ra_incomplete_rejected':True,'ra_complete_accepted':True,'ipa_incomplete_rejected':True,'ipa_complete_accepted':True}


def validate(rows):
    ids = [x['id'] for x in rows if 'id' in x]
    need(len(ids) == len(set(ids)), 'duplicate id')
    by = {x['id']: x for x in rows if 'id' in x}
    validation_evidence=by.get('EVIDENCE:C02:V4:FINAL_VALIDATION',{})
    expected_transition_names={'g1_incomplete_rejected','g1_complete_accepted','scope_incomplete_rejected','scope_complete_accepted','scope_initial_accepted','ra_incomplete_rejected','ra_complete_accepted','ipa_incomplete_rejected','ipa_complete_accepted'}
    need(validation_evidence.get('command')=='python docs/phase2/core/remaining_registry_tools.py --check --mutations' and validation_evidence.get('metrics',{}).get('registry_records')==len(rows), 'final validation evidence is missing or stale')
    need(validation_evidence.get('mutation_tests_total')==43 and validation_evidence.get('mutation_tests_rejected')==43 and validation_evidence.get('mutation_tests_accepted')==0 and all(v=='REJECTED' for v in validation_evidence.get('mutation_results',{}).values()) and len(validation_evidence.get('mutation_results',{}))==43, 'final mutation evidence incomplete')
    need(validation_evidence.get('state_transition_tests_total')==9 and validation_evidence.get('state_transition_tests_passed')==9 and set(validation_evidence.get('state_transitions',{}))==expected_transition_names and all(validation_evidence.get('state_transitions',{}).values()), 'final state-transition evidence incomplete')
    need(validation_evidence.get('metrics',{}).get('c01_prefix_records')==2554 and validation_evidence.get('metrics',{}).get('product_tests_executed')==0, 'final validation evidence overclaims or omits C01/product-test controls')
    checkpoint = by['CHECKPOINT:CORE:REMAINING:001']
    old_bytes = subprocess.check_output(['git', 'show', f'{BASE}:docs/phase2/core/CORE_REGISTRY.jsonl'], cwd=ROOT)
    original = [json.loads(x) for x in old_bytes.splitlines()]
    need(hashlib.sha256(old_bytes).hexdigest() == checkpoint['preserved_prefix_sha256'], 'wrong original registry')
    need(rows[:len(original)] == original and REGISTRY.read_bytes().startswith(old_bytes), 'C01 or original source inventory modified')
    namespace = {'__name__': 'preserved_c01_validator'}
    exec(by['VALIDATE:C01:RECOVERY']['code'], namespace)
    with tempfile.NamedTemporaryFile() as frozen:
        frozen.write(old_bytes); frozen.flush(); namespace['F'] = Path(frozen.name); namespace['validate'](original)
    need(by['BATCH:C02:001']['source_blobs'] == {k: v['blob'] for k, v in rows[0]['sources'].items()}, 'batch source version drift')

    units = [x for x in rows if x['t'] == 'u']
    unit_by = {x['id']: x for x in units}
    source_lines = {k: Path(v['p']).read_text(encoding='utf-8').splitlines() for k, v in rows[0]['sources'].items()}
    # V4 reusable G1 ledger: complete inventory coverage is distinct from
    # completed semantic triage. A disposition can record uncertainty; missing
    # evidence cannot be relabeled complete.
    g1 = [x for x in rows if x.get('t') == 'global_triage']
    g1_by_unit = {x.get('source_unit_id'): x for x in g1}
    g1_protocol = by.get('AUDIT:V4:G1', {})
    scope_views = [x for x in rows if x.get('t') == 'package_scope_view']
    need(len(g1) == len(units) == 2230 and set(g1_by_unit) == set(unit_by), 'G1 does not cover every source unit exactly once')
    need(g1_protocol.get('version') == 'SHAHAB_V4_G1_2026-11-17' and g1_protocol.get('triage_records') == len(g1), 'G1 protocol/inventory version mismatch')
    expected_packages={'C01','C02','C03','C04','C05a','C05b','C06','C07','C08','C09','C10','C11a','C11b','C12a','C12b','C13a','C13b','C14'}|{f'R{i:02}' for i in range(1,11)}|{f'A{i:02}' for i in range(1,9)}
    need(len(scope_views) == 36 and {x.get('package') for x in scope_views} == expected_packages, 'V4 package view inventory contains missing or fabricated package IDs')
    need(all(assess_scope_view(x,set(unit_by)) for x in scope_views), 'Scope View is neither valid INITIAL nor evidence-complete COMPLETE')
    for item in g1:
        u = unit_by.get(item.get('source_unit_id'))
        need(u and item.get('id') == 'G1:V4:' + u['id'], 'G1 source unit/id mismatch')
        need(item.get('source_blob_sha') == rows[0]['sources'][u['s']]['blob'] and item.get('position') == [u['a'],u['z']], 'G1 source version/position mismatch')
        source_text = ' '.join(source_lines[u['s']][u['a']-1:u['z']]).strip()
        need(item.get('source_text_sha256') == hashlib.sha256(source_text.encode()).hexdigest(), 'G1 source text hash drift')
        need(bool(item.get('source_text_sha256')) and bool(item.get('evidence_refs')), 'G1 row lacks source hash or semantic evidence')
        d=item.get('global_disposition',{})
        need(d.get('evidence_refs')==item.get('evidence_refs'), 'G1 disposition/evidence reference mismatch')
        need(all(x.get('basis') for x in d.get('package_relations',[])), 'G1 relation lacks a source-specific basis')
        if any(x.get('relation')=='UNCERTAIN' for x in d.get('package_relations',[])):
            need(bool(d.get('uncertainty')), f"G1 ownership uncertainty not recorded: {item['id']}")
        valid_packages={x.get('package') for x in scope_views}
        need({x.get('package') for x in d.get('package_relations',[]) if x.get('package')} <= valid_packages, f"G1 references unknown package: {item['id']}")
        for ref in item['evidence_refs']:
            evidence=by.get(ref)
            if ref==u['id']:
                need(bool(u.get('semantic_review')) or u.get('review_status')=='SEMANTICALLY_VERIFIED_C01_ONLY' or item.get('screening_status')=='SEMANTICALLY_SCREENED', f"invalid source-unit evidence reference: {item['id']}")
                if item.get('screening_status')=='REUSED_PRIOR_REVIEW':
                    exact_source='\n'.join(source_lines[u['s']][u['a']-1:u['z']])
                    need(u.get('content_sha256')==hashlib.sha256(exact_source.encode()).hexdigest(), f"reused source-unit evidence fingerprint mismatch: {item['id']}")
            else:
                need(evidence and evidence.get('source_unit_id')==u['id'], f"reused evidence missing or points to another source unit: {item['id']}:{ref}")
                need(evidence.get('t')=='semantic_unit_review' and evidence.get('source_text_sha256')==item['source_text_sha256'], f"reused semantic review evidence fingerprint mismatch: {item['id']}:{ref}")
    g1_complete=assess_global_triage(set(unit_by),g1)
    need(g1_protocol.get('fresh_global_semantic_triage_complete') is g1_complete and g1_protocol.get('status') == ('COMPLETE' if g1_complete else 'INCOMPLETE'), 'G1 status does not match evidence')
    scope_complete=all(x.get('scope_status')=='COMPLETE' for x in scope_views)
    need(g1_protocol.get('scope_views_complete') is scope_complete, 'scope-view status summary drift')
    expected_initial=sorted(x['package'] for x in scope_views if x.get('scope_status')=='INITIAL')
    expected_complete=sorted(x['package'] for x in scope_views if x.get('scope_status')=='COMPLETE')
    need(g1_protocol.get('scope_views_initial')==expected_initial and sorted(g1_protocol.get('scope_views_complete_packages',[]))==expected_complete, 'G1 package scope state inventory drift')
    need(g1_protocol.get('uncertain_source_units_count')==0 and g1_protocol.get('uncertain_source_units_sha256')==hashlib.sha256(b'').hexdigest(), 'G1 screened units mislabeled as unresolved')
    need(not any('867 source units have no prior semantic review' in x or 'All package scope views remain incomplete' in x or 'C02 test oracles need' in x for x in g1_protocol.get('blockers',[])), 'stale G1 blocker contradicts current evidence')
    uncertain_g1 = sorted(x['source_unit_id'] for x in g1 if x.get('screening_status') == 'UNCERTAIN_NOT_SEMANTICALLY_REVIEWED')
    need(checkpoint.get('v4_g1', {}).get('uncertain_source_unit_ids') == uncertain_g1 and checkpoint['v4_g1'].get('uncertain_unreviewed_count') == len(uncertain_g1), 'checkpoint G1 unresolved-unit ledger drift')
    need(checkpoint['v4_g1'].get('triage_record_count') == len(g1) and checkpoint['v4_g1'].get('scope_view_count') == len(scope_views), 'checkpoint G1 count drift')
    c02_scope=next(x for x in scope_views if x.get('package')=='C02')
    c02_categories=collections.Counter(x.get('category') for x in c02_scope.get('scope_assignments',[]))
    need(c02_categories=={'OWNED':41,'CROSS_REFERENCE':21,'EXCLUDED_WITH_REASON':2168}, 'C02 scope category counts drift')
    expected_scope_digest=hashlib.sha256('\n'.join(f"{x['unit_id']}:{x['category']}:{x['global_disposition_id']}" for x in c02_scope.get('scope_assignments',[])).encode()).hexdigest()
    need(c02_scope.get('scope_digest')==expected_scope_digest, 'C02 scope digest mismatch')
    g1_digest=hashlib.sha256('\n'.join(f"{x['source_unit_id']}:{x['source_blob_sha']}:{x['position'][0]}:{x['position'][1]}:{x['source_text_sha256']}:{x['global_disposition']['classification']}" for x in sorted(g1,key=lambda z:z['source_unit_id'])).encode()).hexdigest()
    need(g1_protocol.get('g1_digest')==g1_digest and checkpoint['v4_g1'].get('global_triage_digest')==g1_digest, 'G1/checkpoint digest mismatch')
    need(checkpoint['v4_g1'].get('c02_scope_digest')==expected_scope_digest, 'checkpoint C02 scope digest mismatch')
    c02_owned={x['unit_id'] for x in c02_scope.get('scope_assignments',[]) if x.get('category')=='OWNED'}
    c02_candidate_source={uid for c in rows if c.get('t')=='candidate' and c.get('pkg')=='C02' and c.get('status')=='RA_ACCEPTED' for uid in c.get('source_units',[])}
    need(c02_candidate_source <= c02_owned, 'C02 accepted candidate source absent from C02 owned scope')
    need(not any(x['category']=='UNCERTAIN' for x in c02_scope.get('scope_assignments',[])), 'C02 scope contains an unresolved package assignment')
    first_units = [x for x in units if x['s'] == 'W' and 126 <= x['a'] <= 368]
    source_reviews = [x for x in rows if x['t'] == 'source_review' and x.get('pkg') == 'C02']
    sem_reviews = [x for x in rows if x['t'] == 'semantic_unit_review' and x.get('pkg') == 'C02']
    need(len(first_units) == 123 and by['BATCH:C02:001']['reviewed_units'] == 123, 'first-pass scope mismatch')
    need(len(source_reviews) == len({x['source_unit_id'] for x in source_reviews}), 'duplicate first-pass review')
    need({u['id'] for u in first_units} <= {x['source_unit_id'] for x in source_reviews}, 'missing first-pass review')
    candidates = [x for x in rows if x['t'] == 'candidate' and x.get('pkg') == 'C02']
    base_candidates = [x for x in candidates if len(x['id'].split(':')) == 3 and x['id'].split(':')[-1].isdigit()]
    atom_children = [x for x in candidates if x.get('atomic_behavior')]
    first_batch = by.get('BATCH:C02:001', {})
    need(len([c for c in base_candidates if not c.get('batch')]) == first_batch.get('candidate_count'), 'first batch candidate inventory mismatch')
    for batch in (x for x in rows if x.get('t') == 'batch' and x.get('pkg') == 'C02' and x['id'] != 'BATCH:C02:001'):
        if 'candidate_count' in batch:
            need(sum(c.get('batch') == batch['id'] for c in base_candidates) == batch['candidate_count'], f"candidate inventory mismatch for {batch['id']}")
    need(len(base_candidates) == sum(1 for c in candidates if len(c['id'].split(':')) == 3 and c['id'].split(':')[-1].isdigit()), 'candidate inventory is not internally consistent')
    valid_classes = {'APPROVED_EXPLICIT', 'DERIVED_NECESSARY', 'OPEN_DECISION', 'PROPOSAL', 'EXAMPLE', 'CONTEXT', 'SUPERSEDED'}
    for review in source_reviews:
        need(review['review_status'] == 'FIRST_PASS_ONLY' and review['classification'] in valid_classes, 'unearned first-pass acceptance')
        expected = {c['id'] for c in base_candidates if review['source_unit_id'] in c['source_units']}
        need(set(review['candidate_ids']) == expected, 'first-pass reverse trace mismatch')
    sem_by_unit = {x['source_unit_id']: x for x in sem_reviews}
    c02_owned_units={x['unit_id'] for x in c02_scope.get('scope_assignments',[]) if x.get('category')=='OWNED'}
    need(c02_owned_units<=set(sem_by_unit), 'C02-owned source unit lacks the required deep semantic review')
    full_search = by.get('REVIEW:C02:FULL_DOCUMENT_SEARCH', {})
    need(len(sem_reviews) == len(sem_by_unit) == full_search.get('unique_source_units', len(sem_reviews)), 'second-pass unique-unit coverage mismatch')
    for review in sem_reviews:
        unit = unit_by.get(review['source_unit_id'])
        need(unit and review['source_span'] == [unit['s'], unit['a'], unit['z']], 'semantic source span mismatch')
        txt = ' '.join(source_lines[unit['s']][unit['a']-1:unit['z']]).strip()
        need(hashlib.sha256(txt.encode()).hexdigest() == review['source_text_sha256'], 'semantic source text drift')
        handoff = review.get('handoff')
        if handoff:
            known_packages = {x['pkg'] for x in rows if x['t'] == 'package'}
            need(set(handoff.get('consulted_packages', [])) <= known_packages, f"unknown handoff package in {review['id']}")
            consulted_basis = handoff.get('consulted_package_basis', {})
            need(set(consulted_basis) == set(handoff.get('consulted_packages', [])), f"handoff has unjustified consulted package in {review['id']}")
            for package_id, basis in consulted_basis.items():
                need(basis == {'semantic_review_id':review['id'],'source_unit_id':review['source_unit_id'],'source_text_sha256':review['source_text_sha256'],'rationale':review.get('reason','')} and len(basis['rationale']) >= 40, f"handoff consulted-package basis drift in {review['id']}:{package_id}")
            primary = handoff.get('primary_package')
            need(primary is None or primary in known_packages, f"unknown primary handoff package in {review['id']}")
            primary_owner = handoff.get('primary_owner')
            need(primary_owner is None or primary_owner in known_packages, f"untyped primary handoff owner in {review['id']}")
            if handoff.get('pending_package_allocation'):
                need(bool(handoff.get('owner_domain')) and handoff.get('receiving_acceptance') == 'NOT_RECORDED', f"unjustified pending handoff in {review['id']}")
                basis = handoff.get('allocation_basis', {})
                need(basis == {'semantic_review_id':review['id'],'source_unit_id':review['source_unit_id'],'disposition':review['disposition'],'source_text_sha256':review['source_text_sha256']}, f"handoff lacks source-specific allocation basis in {review['id']}")
                need(not review.get('candidate_ids') and review.get('reason'), f"handoff is not justified as non-C02 behavior in {review['id']}")
            else:
                need(primary in known_packages or handoff.get('primary_owner') in known_packages, f"handoff has no registered owner or explicit pending allocation in {review['id']}")
    for candidate in base_candidates:
        need(candidate['normative_status'] in valid_classes and candidate['text'], 'invalid or empty candidate')
        need(candidate['owner_package'] in {x['pkg'] for x in rows if x['t'] == 'package'}, 'unknown candidate owner')
        source, start, end = candidate['span']
        mapped = {u['id'] for u in units if u['s'] == source and u['a'] <= end and u['z'] >= start}
        need(mapped == set(candidate['source_units']), 'candidate source span mismatch')
        if candidate['normative_status'] == 'DERIVED_NECESSARY': need(candidate.get('derivation'), 'unexplained derived candidate')
        if candidate['status'] == 'ATOMIZED_PARENT':
            need(candidate.get('atomized_children') and candidate.get('atomized_requirement') and not candidate.get('accepted_requirement'), 'invalid atomized parent')
            old = by[candidate['atomized_requirement']]
            need(old['status'] == 'SUPERSEDED_ATOMIZED' and set(old['superseded_by_atomic_requirements']), 'parent requirement not superseded')
        elif candidate['owner_package'] == 'C02':
            need(candidate['status'] == 'RA_ACCEPTED' and candidate.get('accepted_requirement') in by, 'accepted C02 candidate lacks requirement')
            req = by[candidate['accepted_requirement']]
            need(req['status'] == 'RA_ACCEPTED' and candidate['id'] in req['source_candidates'], 'candidate/requirement reverse trace mismatch')
            for uid in candidate['source_units']:
                need(uid in sem_by_unit and candidate['id'] in sem_by_unit[uid]['candidate_ids'], 'accepted candidate lacks semantic reverse trace')
        else:
            need(candidate['status'] == 'HANDOFF_ONLY' and not candidate.get('accepted_requirement'), 'handoff promoted to C02')
    for c in atom_children:
        parent = by[c['derived_from_candidate']]
        need(parent['status'] == 'ATOMIZED_PARENT' and parent['span'] == c['span'], 'atomic child parent/span mismatch')
        if c.get('atomic_behavior'):
            if c['status'] == 'HANDOFF_ONLY':
                need(c.get('handoff_target') and not c.get('accepted_requirement'), 'atomic handoff missing destination or incorrectly accepted')
            else:
                need(c['status'] == 'RA_ACCEPTED' and c.get('accepted_requirement') in by, 'atomic behavior lacks accepted requirement')
                req = by[c['accepted_requirement']]
                need(req['source_candidates'] == [c['id']] and req.get('atomized_from_requirement') == parent['atomized_requirement'], 'atomic behavior trace mismatch')
    accepted = [x for x in rows if x['t'] == 'req' and x.get('pkg') == 'C02' and x.get('status') == 'RA_ACCEPTED']
    accepted_ids = {r['id'] for r in accepted}
    need(accepted, 'no accepted C02 requirements')
    task_by = {x['id']: x for x in rows if x['t'] == 'task' and x.get('pkg') == 'C02'}
    decisions = [x for x in rows if x['t'] == 'decision' and x.get('pkg') == 'C02' and x.get('status') == 'OPEN_DECISION']
    for req in accepted:
        need(req['semantic_status'] in ('SECOND_PASS_REVIEWED', 'SECOND_PASS_ATOMIC_CHILD'), 'missing semantic review')
        need(len(req['source_candidates']) == 1 and req['source_units'], 'requirement source trace missing')
        need(len(req['behaviours']) == len(req['acceptance_criteria']) == len(req['tests']) == len(req['tasks']) == 1, 'requirement not atomic/one-to-one')
        ac, test, task = by[req['acceptance_criteria'][0]], by[req['tests'][0]], task_by[req['tasks'][0]]
        need(ac['requirements'] == [req['id']] and test['requirements'] == [req['id']], 'requirement/AC/test trace mismatch')
        need(test['acceptance_criteria'] == [ac['id']] and test['task'] == task['id'] and ac['task'] == task['id'], 'test/AC/task linkage mismatch')
        need(ac['id'] in task['acceptance_criteria'] and test['id'] in task['tests'] and req['id'] in task['requirements'], 'task reverse trace mismatch')
        cases = {c['kind']:c for c in test['cases']}
        need({'POSITIVE','NEGATIVE','BOUNDARY_OR_CONCURRENCY'} <= set(cases) and test['execution_status'] == 'NOT_EXECUTED', 'invalid/claimed test execution')
        required_case_fields = {'actor_fixture','initial_state_and_authority','action','input','observable_expectation','side_effect_invariant','boundary_or_race'}
        boilerplate = ('provide the exact authorized preconditions', 'declared allowed effect occurs', 'exercise this concrete violation', 'test immediately before/after its stated lifecycle', 'as applicable')
        case_fingerprints = []
        for case in cases.values():
            need(required_case_fields <= set(case), f"test case lacks falsifiable scenario fields: {test['id']}:{case['kind']}")
            joined = ' '.join(str(case[k]) for k in required_case_fields).casefold()
            need(not any(token in joined for token in boilerplate), f"generic boilerplate test case: {test['id']}:{case['kind']}")
            need(len(case['input'].split()) >= 8 and len(case['observable_expectation'].split()) >= 12, f"missing concrete input/observable oracle: {test['id']}:{case['kind']}")
            need(len({str(case.get(k, '')).strip().casefold() for k in ('action','input','observable_expectation')}) == 3, f"action/input/oracle are not independently specified: {test['id']}:{case['kind']}")
            case_fingerprints.append(' '.join(re.sub(r'\b(?:REQ|requirement)[: ]*(?:CORE:)?C02[:.]?\d+\b', 'REQ', joined).split()))
        need(len(case_fingerprints) == len(set(case_fingerprints)), f"duplicate normalized case scenarios: {test['id']}")
        need(test.get('scenario_review', {}).get('requirement') == req['id'], f"test lacks requirement-specific review linkage: {test['id']}")
        review = test['scenario_review']
        need(review.get('review_status') in ('FINAL_REQUIREMENT_TO_ORACLE_READBACK','V4_REQUIREMENT_SPECIFIC_ACTION_INPUT_ORACLE_REVIEW') and review.get('manual_semantic_acceptance') == 'AUTHOR_SECOND_READ_COMPLETE', f"test lacks final requirement/oracle readback: {test['id']}")
        need(review.get('requirement_text_sha256') == hashlib.sha256(req.get('text','').encode()).hexdigest(), f"test readback requirement text hash drift: {test['id']}")
        need(review.get('source_units') == req.get('source_units') and review.get('source_span') == req.get('sources'), f"test readback source trace drift: {test['id']}")
        known_contract_ids = {x['id'] for x in rows if x.get('t') == 'contract' and x.get('pkg') == 'C02'}
        need(review.get('task') == test['task'] and review.get('acceptance_criteria') == test['acceptance_criteria'] and set(review.get('contracts', [])) <= known_contract_ids, f"test readback task/AC/contract trace drift: {test['id']}")
        need(review.get('reviewer_independence') == 'SAME_AUTHOR_SECOND_READ_NOT_INDEPENDENT_REVIEW' and review.get('review_evidence'), f"test reviewer provenance missing: {test['id']}")
        if package_status := next(x for x in rows if x['t'] == 'package' and x['pkg'] == 'C02'):
            if package_status['IPA'] == 'PASS':
                need(test['scenario_review'].get('manual_semantic_acceptance') == 'AUTHOR_SECOND_READ_COMPLETE', f"IPA PASS without semantic acceptance evidence: {test['id']}")
        need(ac.get('negative') == cases['NEGATIVE']['stimulus_and_expected'] and ac.get('boundary_or_concurrency') == cases['BOUNDARY_OR_CONCURRENCY']['stimulus_and_expected'], 'AC/Test adversarial cases drift')
        need(ac.get('positive') == cases['POSITIVE']['stimulus_and_expected'], 'AC/Test positive case drift')
    for task in task_by.values():
        need(task.get('subtasks') and task.get('entry_condition') and task.get('deliverable'), 'task decomposition incomplete')
        need(task.get('planning_status') == 'PLANNING_ACCEPTED', f"C02 retained task has invalid planning status: {task['id']}")
        need(set(task['requirements']) <= accepted_ids, 'task references nonaccepted requirement')
        for sub in task['subtasks']:
            need(set(sub.get('requirements',[])) <= set(task['requirements']) and set(sub.get('acceptance_criteria',[])) <= set(task['acceptance_criteria']) and set(sub.get('tests',[])) <= set(task['tests']), 'subtask leaks a non-owned requirement/AC/Test')
        task_decisions={d['id'] for d in decisions if task['id'] in d.get('affected_tasks',[])}
        need(set(task.get('decision_gates',[])) <= task_decisions, 'task carries an unrelated decision gate')
    contracts = [x for x in rows if x['t'] == 'contract' and x.get('pkg') == 'C02']
    dependencies = [x for x in rows if x['t'] == 'dependency' and x.get('id','').startswith('DEP:C02:')]
    decisions = [x for x in rows if x['t'] == 'decision' and x.get('pkg') == 'C02' and x.get('status') == 'OPEN_DECISION']
    need(contracts and dependencies and decisions, 'missing C02 contracts, dependencies, or decision records')
    for contract in contracts:
        need(contract.get('planning_status') == 'PLANNING_ACCEPTED_IMPLEMENTATION_BLOCKED_BY_GATES' and contract.get('implementation_status') == 'NOT_IMPLEMENTED', 'contract acceptance/implementation states are inconsistent')
        need(contract.get('api_contract') and contract.get('tasks') and contract.get('requirements') and contract.get('acceptance_criteria') and contract.get('tests'), 'contract lacks scoped request/response or trace details')
        need(set(contract['requirements']) <= accepted_ids and set(contract['tasks']) <= set(task_by), 'contract references nonaccepted C02 artifacts')
        need(all(contract['id'] in task_by[tid].get('contract_refs',[]) for tid in contract['tasks']), 'contract/task reverse trace mismatch')
    for task in task_by.values(): need(set(task.get('contract_refs',[])) <= {c['id'] for c in contracts} and all(task['id'] in by[cid]['tasks'] for cid in task.get('contract_refs',[])), 'task references an unrelated contract')
    for req in accepted:
        need('conditions' in req and 'exceptions' in req and 'decision_refs' in req and 'decision_gate' in req, 'requirement semantic qualifiers absent')
        need(req['conditions'] and req['exceptions'], 'requirement conditions/exceptions have no explicit disposition')
        need(set(req['decision_refs']) <= {d['id'] for d in decisions} and req['decision_gate'] == req['decision_refs'], 'requirement references unknown or inconsistent decision gate')
        decision_map={d['id']:set(d.get('affected_requirements',[])) for d in decisions}
        need(all(req['id'] in decision_map[d] for d in req['decision_refs']), 'requirement carries a decision unrelated to its source behavior')
    task_components = {t['components'] for t in task_by.values()}
    task_deliverables = {t['deliverable'] for t in task_by.values()}
    task_entries = {t['entry_condition'] for t in task_by.values()}
    subtask_actions = {s['action'] for t in task_by.values() for s in t['subtasks']}
    need(len(task_components)==len(task_by) and len(task_deliverables)==len(task_by) and len(task_entries)==len(task_by) and len(subtask_actions)==sum(len(t['subtasks']) for t in task_by.values()), 'task decomposition is templated')
    package = next(x for x in rows if x['t'] == 'package' and x['pkg'] == 'C02')
    gates = {x.get('gate'): x for x in rows if x['t'] == 'gate' and x.get('pkg') == 'C02'}
    need(by['REVIEW:C02:FULL_DOCUMENT_SEARCH']['result'] in ('CLOSED_MANUAL_RECONCILIATION','INCOMPLETE_NO_PROOF_OF_NO_KEYWORD_MISSES','CLOSED_BY_V4_G1_AND_C02_SCOPED_VIEW'), 'invalid whole-document reconciliation state')
    if package['RA'] == 'PASS':
        ra_review=by['REVIEW:C02:V4:RA_FINAL']
        need(assess_evidence_gate(gates['RA']['status'],accepted_ids,ra_review.get('accepted_requirements',[]),gates['RA']['remaining_blockers']), 'RA gate state is not justified by complete evidence')
        inventory=sorted({x['source_unit_id'] for x in sem_reviews})
        digest=hashlib.sha256(('\n'.join(inventory)).encode()).hexdigest()
        need(by['REVIEW:C02:FULL_DOCUMENT_SEARCH']['result'] == 'CLOSED_BY_V4_G1_AND_C02_SCOPED_VIEW' and by['REVIEW:C02:FULL_DOCUMENT_SEARCH'].get('semantic_inventory_sha256') == digest and by['REVIEW:C02:FULL_DOCUMENT_SEARCH'].get('semantic_inventory') == inventory, 'RA PASS without V4 global triage, C02 scope, and preserved deep-review inventory')
        need(g1_complete and c02_scope.get('scope_status')=='COMPLETE' and not checkpoint['v4_g1'].get('c02_deep_review_required_units'), 'C02 RA PASS without closed shared triage and C02-specific scope')
    need(by['REVIEW:C02:GUIDE_READ']['result'] == 'COMPLETE' and by['REVIEW:C02:GOVERNANCE_READ']['result'] == 'COMPLETE', 'mandatory governance reading incomplete')
    unique_semantic_units = {x['source_unit_id'] for x in sem_reviews}
    need(checkpoint.get('reviewed_unique_source_units') == len(unique_semantic_units), 'checkpoint semantic source-unit count drift')
    need(checkpoint.get('next_source_unit') is None, 'C02/C03 checkpoint must use null until a C03 source unit is selected')
    need(checkpoint.get('last_source_unit') in unique_semantic_units, 'checkpoint last source unit is not a reviewed C02 source unit')
    need(not any('249 unique reviewed' in str(note).lower() for note in checkpoint.get('notes', [])), 'stale checkpoint note')
    risk_audit = by.get('REVIEW:C02:RISK_REMAINDER_001', {})
    need(risk_audit.get('reviewed_unique_units') == len(unique_semantic_units), 'risk audit/checkpoint review count drift')
    need(risk_audit.get('unreviewed_units') == len(units) - len(unique_semantic_units), 'risk audit remainder count drift')
    if package['RA'] == 'PASS':
        need(gates['RA']['status'] == 'PASS' and gates['RA']['accepted_requirements'] == len(accepted) and gates['RA']['remaining_blockers'] == 0, 'unearned RA')
        need(all(c['status'] in ('RA_ACCEPTED','HANDOFF_ONLY','ATOMIZED_PARENT') for c in base_candidates), 'unresolved candidate')
        need(not any(x['category']=='UNCERTAIN' for x in c02_scope['scope_assignments']), 'C02 RA PASS with unresolved owned/uncertain unit')
    ipa_evidence = by['REVIEW:C02:IPA:DESIGN']
    if package['IPA'] == 'PASS':
        need(ipa_evidence['result'] == 'PASS_DESIGN_SUFFICIENCY_IMPLEMENTATION_BLOCKED_BY_OPEN_DECISIONS' and set(ipa_evidence['source_requirements']) == accepted_ids, 'IPA semantic evidence is stale/incomplete')
    need(set(ipa_evidence['tasks']) == set(task_by) and set(ipa_evidence['contracts']) == {x['id'] for x in rows if x['t']=='contract' and x.get('pkg')=='C02'}, 'IPA task/contract trace incomplete')
    if package['IPA'] == 'PASS':
        need(assess_evidence_gate(gates['IPA']['status'],accepted_ids,by['REVIEW:C02:V4:IPA_FINAL'].get('source_requirements',[]),gates['IPA']['remaining_blockers']), 'IPA gate state is not justified by complete evidence')
        need(gates['IPA']['status'] == 'PASS' and gates['IPA']['requirements'] == len(accepted) and len(task_by) > 0 and ipa_evidence['implementation_status'] == 'BLOCKED_PENDING_DECISION_GATES', 'unearned IPA')
        need(all(t.get('planning_status') == 'PLANNING_ACCEPTED' for t in task_by.values()), 'IPA PASS contradicts task planning status')
        need(all(d.get('planning_status') == 'PLANNING_ACCEPTED' for d in dependencies), 'IPA PASS contradicts dependency planning status')
        need(all(a.get('planning_status') == 'PLANNING_ACCEPTED_IMPLEMENTATION_BLOCKED_BY_GATES' for a in rows if a.get('t')=='ac' and a.get('pkg')=='C02' and a.get('planning_status')!='NOT_A_C02_ACCEPTANCE_ARTIFACT'), 'IPA PASS contradicts AC planning status')
        need(gates['IPA'].get('ac') == sum(x.get('t')=='ac' and x.get('pkg')=='C02' and x.get('planning_status')!='NOT_A_C02_ACCEPTANCE_ARTIFACT' and x.get('status') not in ('HANDOFF_ONLY','SUPERSEDED_ATOMIZED') for x in rows) and gates['IPA'].get('tests') == sum(x.get('t')=='test' and x.get('pkg')=='C02' and x.get('status') not in ('HANDOFF_ONLY','SUPERSEDED_ATOMIZED') for x in rows), 'IPA gate counts diverge from active design artifacts')
        need(epic_status_ok(by), 'IPA PASS contradicts technical enabler status')
    packages = [x for x in rows if x['t'] == 'package']
    need(len(packages) == 17, 'package inventory mismatch')
    for other in packages:
        if other['pkg'] != 'C02': need(other['RA'] == 'NOT_STARTED' and other['IPA'] == 'NOT_STARTED', 'unearned other-package gate')
        need(checkpoint['status'] == 'PARTIAL' and checkpoint['last_complete_package'] == ('C02' if package['RA']=='PASS' and package['IPA']=='PASS' else 'C01') and not checkpoint['ready_for_final_audit'], 'unearned whole-program completion')
    for inspection in (x for x in rows if x['t'] == 'code_inspection'):
        need(inspection['runtime_verified'] is False and inspection['tests_executed'] == 0, 'unproved runtime claim')
        for item in inspection['paths']:
            blob = subprocess.check_output(['git','hash-object',item['path']],cwd=ROOT,text=True).strip()
            need(blob == item['blob'], 'code inspection version drift')
    repeated = [(t['id'], c['kind']) for t in rows if t.get('t')=='test' and t.get('pkg')=='C02' and t.get('status') not in ('SUPERSEDED_ATOMIZED','HANDOFF_ONLY') for c in t.get('cases',[]) if len({str(c.get(k,'' )).strip().casefold() for k in ('action','input','observable_expectation')}) < 3]
    global_cases=collections.defaultdict(list)
    for t in rows:
        if t.get('t')=='test' and t.get('pkg')=='C02' and t.get('status') not in ('SUPERSEDED_ATOMIZED','HANDOFF_ONLY'):
            for c in t.get('cases',[]):global_cases[normalized_case_fingerprint(c)].append((t['id'],c['id'],t['requirements'][0]))
    cross_test_duplicates=[v for v in global_cases.values() if len(v)>1]
    need(not cross_test_duplicates, f"normalized C02 test scenario duplicated across requirements: {cross_test_duplicates[:3]}")
    need(checkpoint.get('c02_test_oracle_findings') == [{'test_id':t['id'],'case_id':c['id'],'requirement':t.get('requirements',[None])[0]} for t in rows if t.get('t')=='test' and t.get('pkg')=='C02' and t.get('status') not in ('SUPERSEDED_ATOMIZED','HANDOFF_ONLY') for c in t.get('cases',[]) if len({str(c.get(k,'')).strip().casefold() for k in ('action','input','observable_expectation')}) < 3], 'checkpoint C02 oracle finding list drift')
    correction=checkpoint.get('c02_test_oracle_correction',{})
    baseline_inventory=validation_evidence.get('metrics',{}).get('c02_baseline_case_inventory',[])
    need(checkpoint.get('c02_test_oracle_correction',{}).get('baseline_commit_sha')==C02_CASE_BASELINE, 'C02 test-case baseline provenance drift')
    need(len(baseline_inventory)==243 and len({x.get('case_id') for x in baseline_inventory})==243, 'C02 test-case baseline inventory incomplete')
    baseline_case_ids=[]; baseline_duplicates=[]; baseline_active_duplicates=[]; baseline_inactive_duplicates=[]; baseline_triples=baseline_double_only=baseline_active_equal_pairs=baseline_all_equal_pairs=0
    current_case_by_id={case['id']:(test,case) for test in rows if test.get('t')=='test' and test.get('pkg')=='C02' for case in test.get('cases',[])}
    need(set(current_case_by_id)=={x.get('case_id') for x in baseline_inventory}, 'C02 Test Case ID set differs from the enumerated baseline')
    for item in baseline_inventory:
        case_id=item['case_id'];test,case=current_case_by_id[case_id]
        need(item.get('test_id')==test['id'] and item.get('baseline_test_status')==test.get('status'), f"C02 baseline Test Case parent/status mismatch: {case_id}")
        equal_pairs=item.get('baseline_equal_pair_comparisons')
        need(equal_pairs in (0,3), f"unsupported baseline Action/Input/Oracle pair count: {case_id}")
        baseline_case_ids.append(case_id)
        if equal_pairs:
            baseline_duplicates.append(case_id)
            (baseline_inactive_duplicates if test.get('status') in ('SUPERSEDED_ATOMIZED','HANDOFF_ONLY') else baseline_active_duplicates).append(case_id)
            baseline_all_equal_pairs+=equal_pairs
            if test.get('status') not in ('SUPERSEDED_ATOMIZED','HANDOFF_ONLY'): baseline_active_equal_pairs+=equal_pairs
            if equal_pairs==3:baseline_triples+=1
            else:baseline_double_only+=1
    need(validation_evidence.get('metrics',{}).get('c02_baseline_case_count')==len(baseline_inventory), 'C02 case baseline count evidence drift')
    need(sorted(correction.get('baseline_all_duplicate_case_ids',[]))==sorted(baseline_duplicates), 'C02 all-status duplicate case-ID inventory does not match baseline')
    need(sorted(correction.get('baseline_duplicate_case_ids',[]))==sorted(baseline_active_duplicates)==sorted(correction.get('corrected_case_ids',[])), 'C02 active correction case-ID inventory does not match exact baseline defects')
    need(sorted(correction.get('inactive_legacy_duplicate_case_ids',[]))==sorted(baseline_inactive_duplicates), 'C02 inactive historical duplicate case-ID inventory drift')
    need((correction.get('baseline_all_triple_duplicate_case_count'),correction.get('baseline_active_triple_duplicate_case_count'),correction.get('baseline_inactive_triple_duplicate_case_count'),correction.get('baseline_double_only_case_count'),correction.get('baseline_active_equal_pair_comparison_count'),correction.get('baseline_all_equal_pair_comparison_count'))==(baseline_triples,len(baseline_active_duplicates),len(baseline_inactive_duplicates),baseline_double_only,baseline_active_equal_pairs,baseline_all_equal_pairs)==(60,24,36,0,72,180), 'C02 baseline 24/60 discrepancy was not resolved from all case IDs and active status')
    need(validation_evidence.get('metrics',{}).get('c02_baseline_all_triple_duplicate_cases')==baseline_triples and validation_evidence.get('metrics',{}).get('c02_baseline_active_triple_duplicate_cases')==len(baseline_active_duplicates) and validation_evidence.get('metrics',{}).get('c02_baseline_inactive_triple_duplicate_cases')==len(baseline_inactive_duplicates) and validation_evidence.get('metrics',{}).get('c02_baseline_double_only_cases')==baseline_double_only and sorted(validation_evidence.get('metrics',{}).get('c02_corrected_case_ids',[]))==sorted(baseline_active_duplicates), 'validation evidence does not reconcile the C02 case-ID baseline')
    return {'registry_records':len(rows),'first_pass_units':len(source_reviews),'second_pass_source_units':len(sem_reviews),'candidate_records':len(candidates),'accepted_c02_requirements':len(accepted),'new_tasks':len(task_by),'new_test_definitions':len([x for x in rows if x['t']=='test' and x.get('pkg')=='C02' and x.get('status') not in ('SUPERSEDED_ATOMIZED','HANDOFF_ONLY')]),'product_tests_executed':0,'g1_source_units':len(g1),'g1_reused_prior_reviews':sum(x.get('screening_status')=='REUSED_PRIOR_REVIEW' for x in g1),'g1_unreviewed_uncertain':len(uncertain_g1),'g1_scope_views':len(scope_views),'g1_scope_views_complete':scope_complete,'g1_semantic_triage_complete':g1_complete,'c02_action_input_oracle_identical_cases':len(repeated),'c02_scope_owned_units':len(c02_owned),'c02_scope_cross_references':sum(x['category']=='CROSS_REFERENCE' for x in c02_scope['scope_assignments']),'c02_scope_excluded_with_reason':sum(x['category']=='EXCLUDED_WITH_REASON' for x in c02_scope['scope_assignments']),'c02_ra_ipa':f"{package['RA']}/{package['IPA']}"}


def mutation_checks(rows):
    def duplicate_test_case(r):
        src=next(x for x in r if x.get('id')=='TEST:CORE:C02:001')['cases'][0]
        dst_test=next(x for x in r if x.get('id')=='TEST:CORE:C02:004')
        dst=next(x for x in dst_test['cases'] if x['kind']=='POSITIVE')
        for key in ('actor_fixture','initial_state_and_authority','action','input','observable_expectation','side_effect_invariant','boundary_or_race'):
            dst[key]=src[key]
        dst['stimulus_and_expected']=src['stimulus_and_expected']
        next(x for x in r if x.get('id')=='AC:CORE:C02:004')['positive']=src['stimulus_and_expected']
    mutations = {
        'duplicate_id':lambda r:r.append(copy.deepcopy(next(x for x in r if x.get('id')=='PKG:C02'))),
        'original_record_changed':lambda r:r[0].update(base='wrong'),
        'missing_source_review':lambda r:r.remove(next(x for x in r if x['t']=='source_review' and x.get('pkg')=='C02')),
        'candidate_reverse_trace':lambda r:next(x for x in r if x['t']=='source_review' and x.get('candidate_ids')).update(candidate_ids=[]),
        'candidate_source_span':lambda r:next(x for x in r if x.get('id')=='CAND:C02:004').update(span=['W',1,1]),
        'unearned_requirement_acceptance':lambda r:next(x for x in r if x.get('id')=='CAND:C02:004').update(status='HANDOFF_ONLY'),
        'unearned_package_acceptance':lambda r:next(x for x in r if x.get('pkg')=='C03' and x['t']=='package').update(RA='PASS'),
        'unproved_runtime_execution':lambda r:next(x for x in r if x['t']=='code_inspection').update(runtime_verified=True),
        'unearned_completion':lambda r:next(x for x in r if x.get('id')=='CHECKPOINT:CORE:REMAINING:001').update(ready_for_final_audit=True),
        'missing_semantic_review':lambda r:next(x for x in r if x.get('id')=='SEMREVIEW:C02:SU-W-00091').update(candidate_ids=[]),
        'missing_deep_review_for_owned_c02_unit':lambda r:r.remove(next(x for x in r if x.get('t')=='semantic_unit_review' and x.get('pkg')=='C02' and x.get('source_unit_id') in {a['unit_id'] for a in next(y for y in r if y.get('id')=='SCOPE:V4:C02')['scope_assignments'] if a['category']=='OWNED'})),
        'orphan_atomic_requirement':lambda r:next(x for x in r if x.get('id')=='REQ:CORE:104').update(source_candidates=[]),
        'broken_task_trace':lambda r:next(x for x in r if x.get('id')=='TASK:CORE:C02:003')['requirements'].remove('REQ:CORE:103'),
        'ipa_task_status_contradiction':lambda r:next(x for x in r if x.get('id')=='TASK:CORE:C02:001').update(planning_status='DRAFT_NOT_ACCEPTED'),
        'generic_negative_test':lambda r:next(x for x in r if x.get('id')=='TEST:CORE:C02:001')['cases'][1].update(stimulus_and_expected='wrong organization/actor, stale or revoked authority, unknown identity result ... as applicable'),
        'long_generic_scenario':lambda r:next(x for x in r if x.get('id')=='TEST:CORE:C02:001')['cases'][0].update(actor_fixture='authorized actor and fixture, synthetic isolated scope with exact permissions',initial_state_and_authority='all exact authorized preconditions are satisfied for this requirement and clause',action='perform the declared allowed effect for the requirement using its exact authorized preconditions',input='submit the valid input for the concrete protected path under the exact authorized preconditions of the requirement',observable_expectation='the declared allowed effect occurs for the requirement as expected and no unrelated effect occurs',side_effect_invariant='no unintended effect occurs',boundary_or_race='test immediately before and after its stated lifecycle with authorization as applicable'),
        'unknown_handoff_package':lambda r:next(x for x in r if x.get('t')=='semantic_unit_review' and x.get('handoff'))['handoff'].update(consulted_packages=['C15']),
        'unjustified_registered_handoff':lambda r:next(x for x in r if x.get('t')=='semantic_unit_review' and x.get('handoff') and 'C14' not in x['handoff'].get('consulted_packages',[]))['handoff']['consulted_packages'].append('C14'),
        'stale_checkpoint_source':lambda r:next(x for x in r if x.get('id')=='CHECKPOINT:CORE:REMAINING:001').update(next_source_unit='REVIEW:C02:F01_F05'),
        'templated_task_components':lambda r:next(x for x in r if x.get('id')=='TASK:CORE:C02:002').update(components=next(x for x in r if x.get('id')=='TASK:CORE:C02:001')['components']),
        'missing_requirement_condition':lambda r:next(x for x in r if x.get('id')=='REQ:CORE:050').update(conditions=[]),
        'unrelated_decision_gate':lambda r:next(x for x in r if x.get('id')=='REQ:CORE:050').update(decision_refs=['DECISION:C02:03'],decision_gate=['DECISION:C02:03']),
        'unscoped_contract':lambda r:next(x for x in r if x.get('id')=='TASK:CORE:C02:001').update(contract_refs=['CONTRACT:C02:03']),
        'dropped_g1_source_unit':lambda r:r.remove(next(x for x in r if x.get('t')=='global_triage')),
        'corrupt_g1_source_hash':lambda r:next(x for x in r if x.get('t')=='global_triage').update(source_blob_sha='corrupt'),
        'corrupt_g1_digest':lambda r:next(x for x in r if x.get('id')=='AUDIT:V4:G1').update(g1_digest='0'*64),
        'corrupt_checkpoint_g1_digest':lambda r:next(x for x in r if x.get('id')=='CHECKPOINT:CORE:REMAINING:001')['v4_g1'].update(global_triage_digest='0'*64),
        'corrupt_c02_scope_digest':lambda r:next(x for x in r if x.get('id')=='SCOPE:V4:C02').update(scope_digest='0'*64),
        'unearned_g1_completion':lambda r:next(x for x in r if x.get('id')=='AUDIT:V4:G1').update(status='INCOMPLETE',fresh_global_semantic_triage_complete=False),
        'missing_package_scope_view':lambda r:r.remove(next(x for x in r if x.get('id')=='SCOPE:V4:A01')),
        'copied_action_input_oracle':lambda r:(lambda c:c.update(input=c['action'],observable_expectation=c['action']))(next(x for x in r if x.get('id')=='TEST:CORE:C02:004')['cases'][0]),
        'copied_action_input_only':lambda r:(lambda c:c.update(input=c['action']))(next(x for x in r if x.get('id')=='TEST:CORE:C02:004')['cases'][0]),
        'copied_action_oracle_only':lambda r:(lambda c:c.update(observable_expectation=c['action']))(next(x for x in r if x.get('id')=='TEST:CORE:C02:005')['cases'][0]),
        'copied_input_oracle_only':lambda r:(lambda c:c.update(observable_expectation=c['input']))(next(x for x in r if x.get('id')=='TEST:CORE:C02:010')['cases'][0]),
        'false_scope_complete':lambda r:next(x for x in r if x.get('id')=='SCOPE:V4:A01').update(scope_status='COMPLETE'),
        'corrupt_initial_scope_digest':lambda r:next(x for x in r if x.get('id')=='SCOPE:V4:C03').update(unresolved_unit_ids_sha256='0'*64),
        'corrupt_reused_evidence_ref':lambda r:next(x for x in r if x.get('id')=='G1:V4:SU-B-00001')['global_disposition'].update(evidence_refs=['MISSING:EVIDENCE']),
        'corrupt_reused_semantic_evidence_hash':lambda r:next(x for x in r if x.get('id')=='SEMREVIEW:C02:SU-B-00003').update(source_text_sha256='0'*64),
        'missing_global_disposition':lambda r:next(x for x in r if x.get('id')=='G1:V4:SU-B-00001').pop('global_disposition'),
        'unearned_c02_ra':lambda r:next(x for x in r if x.get('t')=='gate' and x.get('pkg')=='C02' and x.get('gate')=='RA').update(remaining_blockers=1),
        'unearned_c02_ipa':lambda r:next(x for x in r if x.get('t')=='gate' and x.get('pkg')=='C02' and x.get('gate')=='IPA').update(status='PARTIAL'),
        'open_decision_marked_resolved':lambda r:next(x for x in r if x.get('id')=='DECISION:C02:01').update(status='RESOLVED'),
        'duplicate_normalized_case_across_requirements':lambda r:duplicate_test_case(r),
    }
    results={}
    for name,mutate in mutations.items():
        altered=copy.deepcopy(rows); mutate(altered)
        try: validate(altered)
        except (ValueError,KeyError,IndexError): results[name]='REJECTED'
        else: raise ValueError(f'mutation accepted: {name}')
    return results


def table(headers, items):
    def safe(value): return str(value).replace('|',' / ').replace('\n',' ')
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(map(safe,row))+' |' for row in items])


def render(rows):
    by={x['id']:x for x in rows if 'id' in x}; cp=by['CHECKPOINT:CORE:REMAINING:001']
    packages=[x for x in rows if x['t']=='package']; candidates=[x for x in rows if x['t']=='candidate']; reviews=[x for x in rows if x['t']=='source_review']
    c02=next(x for x in packages if x['pkg']=='C02')
    cands=[x for x in candidates if x.get('pkg')=='C02']; reqs=[x for x in rows if x.get('t')=='req' and x.get('pkg')=='C02' and x.get('status')=='RA_ACCEPTED']
    tasks=[x for x in rows if x.get('t')=='task' and x.get('pkg')=='C02']; ac=[x for x in rows if x.get('t')=='ac' and x.get('pkg')=='C02' and x.get('status') not in ('SUPERSEDED_ATOMIZED','HANDOFF_ONLY')]; tests=[x for x in rows if x.get('t')=='test' and x.get('pkg')=='C02' and x.get('status') not in ('SUPERSEDED_ATOMIZED','HANDOFF_ONLY')]
    sem=[x for x in rows if x.get('t')=='semantic_unit_review' and x.get('pkg')=='C02']; gates={x['gate']:x['status'] for x in rows if x['t']=='gate' and x.get('pkg')=='C02'}
    publication=cp.get('publication',{})
    if publication.get('status')=='AUTHORIZED_PENDING_PUBLICATION':
        publication_line='انتشار این شاخه برای ایجاد PR به `main` با دستور صریح مالک مجاز شده است؛ Push/PR هنوز انجام نشده و Merge مجاز یا انجام‌شده نیست.'
    elif publication.get('status')=='PR_OPEN_NO_MERGE':
        publication_line=f"PR شمارهٔ {publication.get('pr_number')} باز و بدون Merge است: {publication.get('pr_url')}"
    else:
        publication_line='درخواست انتشار قبلی مسدود بود؛ وضعیت فعلی در Checkpoint ثبت شده است.'
    common=[
        f"# ادامه برنامه Core/Wallet — وضعیت اصلاح C02: RA={c02['RA']} / IPA={c02['IPA']}",
        '**نمای مشتق از [CORE_REGISTRY.jsonl](CORE_REGISTRY.jsonl). وضعیت کل: PARTIAL؛ آمادگی ممیزی نهایی: خیر.**',
        f"C01 با RA=PASS و IPA=PASS در سطح تعریف برنامه حفظ شده است. C02 اکنون RA={c02['RA']} و IPA={c02['IPA']} است؛ پذیرش تعریف برنامه مجوز پیاده‌سازی نیست.",
        f"شاخه `{cp['branch']}`؛ مبنای معتبر `{BASE}`. SHA حامل Checkpoint از Git خوانده شود.",
        f"Blob رجیستری مبنا `{cp['base_registry_blob']}`؛ hash پیشوند تغییرناپذیر `{cp['preserved_prefix_sha256']}`؛ ۲۵۵۴ رکورد قبلی حفظ شده‌اند.",
        '## وضعیت ۱۷ بسته',
        table(['بسته','عنوان','واحدهای مرورشده','نامزد/اتمی','نیازمندی فعال / TE / Task / AC-Test','RA','IPA'],[(p['pkg'],p['title'],len({x['source_unit_id'] for x in sem}) if p['pkg']=='C02' else 0,len(cands) if p['pkg']=='C02' else 0,f"{len(reqs)} / 1 / {len(tasks)} / {len(ac)}-{len(tests)}" if p['pkg']=='C02' else '۰ / ۰ / ۰ / ۰',p['RA'],p['IPA']) for p in packages]),
        '## پوشش دو سند و ممیزی معنایی',
        f"فهرست G1 نسخه V4 برای هر ۲٬۲۳۰ واحد شناسه، سند، موقعیت و hash دارد. {sum(x.get('screening_status')=='REUSED_PRIOR_REVIEW' for x in rows if x.get('t')=='global_triage')} بازبینی معتبر قبلی استفاده شد و ۸۶۷ واحد تازه در سطح غربال‌گری مشترک تعیین تکلیف شدند؛ ابهام‌های مالکیت با رابطه UNCERTAIN و دلیل ثبت شده‌اند. G1={by['AUDIT:V4:G1']['status']}. از ۳۶ Scope View، یک نما (C02) کامل و ۳۵ نمای بسته‌های آینده INITIAL هستند. C02: {len({x['source_unit_id'] for x in sem})} بازبینی عمیق ثبت‌شده، {len(cands)} نامزد/رد اتمی، {len(reqs)} الزام پذیرفته‌شده. شمارش از Commit پایه: ۶۰ Case تکرار سه‌گانه در کل ۲۴۳ مورد (۲۴ فعال و ۳۶ منسوخ/Handoff) و صفر موردِ تکرار فقط دوتایی؛ ۲۴ مورد فعال اصلاح شدند. از ۲۰۷ Case فعال فعلی، {sum(1 for t in tests for c in t.get('cases',[]) if len({str(c.get(k,'')).strip().casefold() for k in ('action','input','observable_expectation')})<3)} مورد با فیلدهای برابر باقی است. RA/IPA={c02['RA']}/{c02['IPA']}.",
        'تخصیص بستهٔ دقیق برای حوزه‌های RAG/Assistant در این شاخه قابل اثبات نبود؛ موارد مربوط با owner_domain و pending_package_allocation ثبت شده‌اند. هیچ alias نامعتبر به شناسهٔ بسته تبدیل نشده است. تصمیم‌های باز، اجرای محصول و مستقل‌بودن بازبین ادعا نشده‌اند.',
        '## استفادهٔ مجدد از کد',by['INSPECT:C02:002']['finding'],
        '## تعریف برنامه و آزمون',
        'Validator ساختاری و آزمون‌های جهش مستقل اجرا شدند؛ محصول یا رفتار runtime آزموده نشده است. Testهای C02 تعریف دقیق برنامه‌اند و در وضعیت NOT_EXECUTED مانده‌اند.',
        table(['مترک','مقدار'],[('registry records',len(rows)),('C02 candidates and atomic traces',len(cands)),('C02 semantic reviews',len(sem)),('accepted atomic requirements',len(reqs)),('tasks',len(tasks)),('AC/Test',f'{len(ac)}/{len(tests)}'),('product tests executed',0),('RA/IPA',f"{gates.get('RA')}/{gates.get('IPA')}")]),
        '## وضعیت ادامه',
        f"آخرین بستهٔ برنامه‌ریزی‌شدهٔ کامل {cp['last_complete_package']} است؛ C03 شروع نشده است. {cp['next_action']}",
        'کل برنامه ۱۷ بسته هنوز PARTIAL است؛ `CORE_REMAINING_17_PLANNING_COMPLETE` و آمادگی ممیزی نهایی Core اعلام نمی‌شود.',
        '## انتشار',publication_line,
        '## اعتبارسنجی', '```text\npython docs/phase2/core/remaining_registry_tools.py --render\npython docs/phase2/core/remaining_registry_tools.py --check --mutations\n```',
    ]
    candidate_view=[
        '# C02 — الزامات اتمی، والدهای مرکب و Handoff',f"**RA={c02['RA']}؛ IPA={c02['IPA']}؛ منبع داده CORE_REGISTRY.jsonl.**",
        table(['ID','Source','Owner','Normative status','Disposition','Clause'],[(c['id'],':'.join(map(str,c['span'])),c['owner_package'],c['normative_status'],c.get('status'),c['text']) for c in cands]),
        table(['Requirement','Source candidate','Task','AC','Test','Code state'],[(r['id'],','.join(r['source_candidates']),','.join(r['tasks']),','.join(r['acceptance_criteria']),','.join(r['tests']),r['code_state']) for r in reqs]),
        'تصمیم‌های باز با گیت اجرای implementation باقی‌اند؛ این پذیرش برنامه مجوز اجرا یا ادعای انطباق نیست.',
        table(['Source unit','Class','Candidates','Disposition'],[(x['source_unit_id'],x['classification'],','.join(x.get('candidate_ids',[])),x['disposition']) for x in sem]),
    ]
    return {'CHECKPOINT.md':'\n\n'.join(common)+'\n','C02_RA_CANDIDATES.md':'\n\n'.join(candidate_view)+'\n'}


def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--render',action='store_true'); parser.add_argument('--check',action='store_true'); parser.add_argument('--mutations',action='store_true'); args=parser.parse_args()
    rows=[json.loads(x) for x in REGISTRY.read_text().splitlines()]; metrics=validate(rows); mutations=mutation_checks(rows) if args.mutations else {}; views=render(rows)
    if args.render:
        for name,content in views.items(): (DIRECTORY/name).write_text(content)
    if args.check:
        for name,content in views.items(): need((DIRECTORY/name).read_text()==content,f'stale derived view: {name}')
        namespace={'__name__':'preserved_c01_renderer'}; exec(next(x['code'] for x in rows if x.get('id')=='RENDER:C01:RECOVERY'),namespace); c01_rows=rows[:next(x for x in rows if x.get('id')=='CHECKPOINT:CORE:REMAINING:001')['preserved_prefix_records']]; c01,_=namespace['render'](c01_rows)
        need((DIRECTORY/'C01_RA_CANDIDATES.md').read_text()==c01,'C01 view changed or stale')
    transitions=transition_checks()
    print(json.dumps({'metrics':metrics,'mutations':mutations,'transitions':transitions},ensure_ascii=False,sort_keys=True))


if __name__=='__main__': main()
