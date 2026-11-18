import copy
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

P=Path(__file__).with_name('validate_graph.py')
spec=importlib.util.spec_from_file_location('validate_graph',P)
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)

def dump(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False),encoding='utf-8')

def digest(obj):
    return hashlib.sha256(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest()

def init(tmp):
    root=Path(tmp); sources=['docs/b.md','docs/w.md']; chunks=root/'chunks';reviews=root/'review'; entries=[]; nodes=[];edges=[]
    for source in sources:
        p=root/source;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('\n'.join(f'line {i}' for i in range(1,12))+'\n')
    v.SOURCES={source:(hashlib.sha256((root/source).read_bytes()).hexdigest(),11) for source in sources}
    for idx in range(1,23):
        source=sources[(idx-1)//11]; line=(idx-1)%11+1; cid=f'GSEM-{idx:03}'
        node={'id':cid,'label':cid,'source_file':source,'source_location':str(line),'evidence_quote':f'line {line}','decision_status':'UNSPECIFIED','owner':None,'owner_status':'UNSPECIFIED'}
        edge={'source':cid,'target':cid,'relation':'references','confidence':'EXTRACTED','confidence_score':1.0,'source_file':source,'source_location':str(line),'evidence_quote':f'line {line}','decision_status':'UNSPECIFIED','owner':None,'owner_status':'UNSPECIFIED'}
        data={'nodes':[node],'edges':[edge],'coverage':{source:1},'coverage_range':{'start_line':line,'end_line':line},'coverage_manifest':[]}
        cp=chunks/(cid+'.json');dump(cp,data);nodes.append(copy.deepcopy(node));edges.append(copy.deepcopy(edge));entries.append({'id':cid,'source_file':source,'start_line':line,'end_line':line,'status':'PASS','validation':'PASS','output_sha256':hashlib.sha256(cp.read_bytes()).hexdigest()})
    base={'nodes':[{'id':'base-a'},{'id':'base-b'}],'links':[{'source':'base-a','target':'base-b','relation':'contains_section'}]}
    nodes=copy.deepcopy(base['nodes'])+nodes; edges=copy.deepcopy(base['links'])+edges
    for i in range(3):
        e={'source':'GSEM-001','target':'GSEM-012','relation':'references','confidence':'INFERRED','confidence_score':0.75,'decision_status':'UNSPECIFIED','owner':None,'owner_status':'UNSPECIFIED','evidence':[{'source_file':sources[0],'line':1,'quote':'line 1'}], 'serial':i}
        dump(reviews/f'review-{i}.json',{'edges':[e]});edges.append(copy.deepcopy(e))
    graph={'directed':True,'multigraph':True,'nodes':nodes,'links':edges,'hyperedges':[],'lossless_merge':{'node_variants':[]}}
    dump(root/'progress.json',{'chunks':entries});dump(root/'base.json',base);dump(root/'graph.json',graph)
    v.STRUCTURAL_SHA256=hashlib.sha256((root/'base.json').read_bytes()).hexdigest()
    corrections=root/'corrections.json';dump(corrections,{'quarantine':[]})
    return SimpleNamespace(repo=root,graph=root/'graph.json',structural=root/'base.json',progress=root/'progress.json',chunks=chunks,reviews=reviews,corrections=corrections,output=None)

class TestValidation(unittest.TestCase):
    def setUp(self): self.tmp=tempfile.TemporaryDirectory();self.args=init(self.tmp.name)
    def tearDown(self): self.tmp.cleanup()
    def issues(self): return v.audit(self.args).errors
    def test_fixture_passes(self): self.assertEqual(self.issues(),[])
    def test_lost_parallel_edge_detected(self):
        g=json.loads(self.args.graph.read_text());g['links'].pop();dump(self.args.graph,g)
        self.assertTrue(any('controlled semantic edge missing or changed' in x for x in self.issues()))
    def test_quarantine_preserves_original_evidence(self):
        g=json.loads(self.args.graph.read_text());edge=g['links'].pop()
        correction={'record_sha256':digest(edge),'reason':'misattributed witness','evidence':edge['evidence']}
        dump(self.args.corrections,{'quarantine':[correction]})
        g['lossless_merge']['quarantined_edges']=[{**correction,'original_edge':edge,'allowed_replacement_sha256':[],'action':'quarantined_from_active_graph'}];dump(self.args.graph,g)
        self.assertEqual(self.issues(),[])
        wrong_evidence=[{'source_file':'docs/w.md','line':11,'quote':'line 11'}]
        bad_correction={**correction,'evidence':wrong_evidence};dump(self.args.corrections,{'quarantine':[bad_correction]})
        g['lossless_merge']['quarantined_edges'][0]['evidence']=wrong_evidence;dump(self.args.graph,g)
        self.assertTrue(any('does not match original edge witness' in x for x in self.issues()))
        dump(self.args.corrections,{'quarantine':[correction]})
        g['lossless_merge']['quarantined_edges'][0]['evidence']=correction['evidence']
        del g['lossless_merge']['quarantined_edges'][0]['reason'];dump(self.args.graph,g)
        self.assertTrue(any('reason missing' in x for x in self.issues()))
    def test_fabricated_quarantine_cannot_hide_missing_input_edge(self):
        g=json.loads(self.args.graph.read_text());edge=g['links'].pop(3)
        g['lossless_merge']['quarantined_edges']=[{'original_edge':edge,'record_sha256':digest(edge),'reason':'invented','evidence':[{'source_file':'docs/w.md','line':11,'quote':'line 11'}],'allowed_replacement_sha256':[],'action':'quarantined_from_active_graph'}]
        dump(self.args.graph,g)
        self.assertTrue(any('no matching reviewed correction record' in x for x in self.issues()))
    def test_unexpected_node_is_rejected(self):
        g=json.loads(self.args.graph.read_text());g['nodes'].append({'id':'unreviewed-node'});dump(self.args.graph,g)
        self.assertTrue(any('unconsumed node record' in x for x in self.issues()))
    def test_unexpected_link_is_rejected(self):
        g=json.loads(self.args.graph.read_text());g['links'].append({'source':'GSEM-001','target':'GSEM-002','relation':'references'});dump(self.args.graph,g)
        self.assertTrue(any('unconsumed link record' in x for x in self.issues()))
    def test_missing_correction_ledger_is_rejected(self):
        self.args.corrections.unlink()
        self.assertTrue(any('reviewed corrections file missing' in x for x in self.issues()))
    def test_missing_owner_detected(self):
        p=self.args.chunks/'GSEM-001.json';d=json.loads(p.read_text());del d['edges'][0]['owner'];dump(p,d)
        self.assertTrue(any('missing owner field' in x for x in self.issues()))
    def test_literal_witness_must_match_location(self):
        p=self.args.chunks/'GSEM-001.json';d=json.loads(p.read_text());d['edges'][0]['evidence_quote']='line 2';dump(p,d)
        self.assertTrue(any('quote absent at exact cited lines' in x for x in self.issues()))
    def test_bad_inference_score_detected(self):
        p=self.args.reviews/'review-0.json';d=json.loads(p.read_text());d['edges'][0]['confidence_score']=0.87;dump(p,d)
        self.assertTrue(any('confidence rubric invalid' in x for x in self.issues()))
    def test_source_hash_checked(self):
        (self.args.repo/'docs/b.md').write_text('edited\n');self.assertTrue(any('source sha256 mismatch' in x for x in self.issues()))
    def test_known_drs_quote_cannot_support_knowledge_base(self):
        source='docs/SHAHAB_PHASE_2_DEVELOPMENT_BLUEPRINT.md'
        node={'id':'docs_shahab_phase_2_development_blueprint_knowledge_base'}
        self.assertFalse(v.valid_known_kb_witness('node',node,source,[246]))
        self.assertTrue(v.valid_known_kb_witness('node',node,source,[252]))
        self.assertTrue(v.valid_known_kb_witness('node',node,source,[532]))
        self.assertTrue(v.valid_known_kb_witness('edge',node,source,[246]))
    def test_structural_mutation_detected(self):
        g=json.loads(self.args.graph.read_text());g['links'][0]['relation']='changed';dump(self.args.graph,g)
        self.assertTrue(any('structural link[0] missing or mutated' in x for x in self.issues()))
    def test_duplicate_variant_required(self):
        # A duplicated input node that shares an ID is only accepted if the full
        # duplicate record is preserved in lossless_merge.node_variants.
        cp=self.args.chunks/'GSEM-002.json';d=json.loads(cp.read_text());node=copy.deepcopy(d['nodes'][0]);node['id']='GSEM-001';d['nodes'].append(node);dump(cp,d)
        self.assertTrue(any('node[1] missing or changed' in x for x in self.issues()))
        g=json.loads(self.args.graph.read_text());g['lossless_merge']['node_variants'].append({'node':node,'input':'GSEM-002.json'});dump(self.args.graph,g)
        self.assertFalse(any('node[1] missing or changed' in x for x in self.issues()))
    def test_gap_detected(self):
        p=self.args.progress;d=json.loads(p.read_text());d['chunks'][2]['start_line']=4;dump(p,d)
        self.assertTrue(any('gap/overlap' in x for x in self.issues()))

if __name__=='__main__':unittest.main()
