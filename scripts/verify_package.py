"""Offline verification using only the files in this package. No provider calls."""
from __future__ import annotations
import ast
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import random
import socket
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

def no_network(*args, **kwargs):
    raise RuntimeError('Network access is disabled during package verification')

import build_arms as ba
import literal_parser as lp
import make_numbers as mn
import make_numbers_f as mf
import make_numbers_h as mh
import make_numbers_f2 as f2
import depth_statistics as ds
import reading_statistics as rs

socket.socket = no_network
socket.create_connection = no_network

CHECKS = []
def read(rel):
    return json.loads((ROOT / rel).read_text())
def jsonl(rel):
    return [json.loads(s) for s in (ROOT / rel).read_text().splitlines() if s.strip()]
def normalise(v):
    return json.loads(json.dumps(v, sort_keys=True))
def equal(actual, expected, label):
    def mismatch(a, b, path=''):
        if isinstance(a, (int, float)) and not isinstance(a, bool) and isinstance(b, (int, float)) and not isinstance(b, bool):
            # Python releases can differ in the last bits of floating-point sums.
            return None if abs(a-b) <= 1e-12 else path+' (number)'
        if type(a) != type(b): return path+' (type)'
        if isinstance(a, dict):
            if set(a) != set(b): return path+' (keys)'
            for k in a:
                bad=mismatch(a[k],b[k],path+'/'+str(k))
                if bad is not None:return bad
            return None
        if isinstance(a, list):
            if len(a) != len(b):return path+' (length)'
            for i,(x,y) in enumerate(zip(a,b)):
                bad=mismatch(x,y,path+'/'+str(i))
                if bad is not None:return bad
            return None
        return None if a==b else path+' (value)'
    bad=mismatch(normalise(actual),normalise(expected))
    if bad is not None:raise AssertionError(label+': mismatch at '+bad)
    CHECKS.append(label)

def mark(label):
    CHECKS.append(label)
    print('PASS: '+label,flush=True)

def package_paths():
    """Walk package paths without entering Git directories or following links."""
    for base, dirs, files in os.walk(ROOT, followlinks=False):
        dirs[:] = [name for name in dirs
                   if name != '.git' or (Path(base) / name).is_symlink()]
        for name in dirs + files:
            yield Path(base) / name

def verify_manifest():
    path=ROOT/'MANIFEST.md'
    if not path.exists():
        raise AssertionError('MANIFEST.md is required')
    entries=[]
    for line in path.read_text().splitlines():
        if not line.startswith('| `'):continue
        cols=[s.strip().strip('`') for s in line.split('|')[1:-1]]
        entries.append(cols[:2])
    actual={str(p.relative_to(ROOT)) for p in package_paths() if p.is_file()}
    equal(set_to_list(actual), sorted(p for p,h in entries), 'manifest exact file inventory')
    for rel,want in entries:
        content=(ROOT/rel).read_bytes()
        if rel=='MANIFEST.md':
            # The manifest self-row is hashed with its own digest set to 64 zeroes.
            content=content.replace(want.encode(),b'0'*64,1)
        equal(hashlib.sha256(content).hexdigest(),want,'sha256 '+rel)
    mark('all manifest hashes and exact file inventory')
def set_to_list(s):return sorted(s)

def main():
    for p in package_paths():
        assert not p.is_symlink(), 'symlink in package'
        assert not any(t in p.name.lower() for t in ['settings','pii_local','human_24','blind_key','.env','__pycache__']), 'excluded path in package'
        if p.suffix=='.py':ast.parse(p.read_text(), filename=str(p.relative_to(ROOT)))
    mark('plain files; Python syntax; excluded path checks; Git directories ignored')
    v3=ba.load_verified_arms(arms='v3')['objects']
    fresh=ba.load_verified_arms(arms='F')['objects']
    h=ba.load_verified_arms(arms='H')['objects']
    equal(ba.build()['objects'],v3,'rebuild first-run six frozen objects')
    equal(ba.build_f()['objects'],fresh,'rebuild fresh-run frozen objects')
    mark('all frozen arm object hashes; first-run and fresh arm reconstruction')
    kinds={r['seed_id']:r['item_kind'] for r in fresh['S_main']}
    rows={b:jsonl('data/rows/'+b+'.jsonl') for b in ['mini','haiku','F-mini','F-haiku','H-mini','F-luna','F-haiku55','F-terra']}
    expected_counts={'mini':3780,'haiku':3780,'F-mini':1920,'F-haiku':640,'H-mini':960,'F-luna':1920,'F-haiku55':1920,'F-terra':1920}
    all_turns=0
    for block,rr in rows.items():
        equal(len(rr),expected_counts[block],block+' conversation count')
        allowed=v3 if block in ['mini','haiku'] else fresh
        source={r['id']:r for r in allowed['S_main']}
        if block=='H-mini': source={r['id']:r for r in h['S_main']}
        reps=[1] if block=='F-haiku' else [1,2,3]
        arms=['S-original','S-main','G'] if block in ['mini','haiku'] else ['H','S-prime'] if block=='H-mini' else ['S-main','G']
        planned={(a,r,i) for a in arms for r in ([1] if a=='S-original' else reps) for i in source}
        seen={(r['arm'],r['repetition'],r['record_id']) for r in rr}
        equal(len(seen),len(rr),block+' no duplicate conversations')
        equal(sorted(seen),sorted(planned),block+' planned matrix completeness')
        saved=jsonl('data/replies/'+block+'.jsonl')
        equal(len(saved),len(rr),block+' reply count')
        for row,reply in zip(rr,saved):
            for k in ['model','record_id','arm','seed_id','depth','condition','repetition','style']:
                assert row[k]==reply[k], block+' reply identity'
            assert len(row['turns'])==len(reply['turns'])
            for labelled,turn in zip(row['turns'],reply['turns']):
                assert labelled['turn_index']==turn['turn_index']
                assert labelled['raw_sha256']==hashlib.sha256(turn['text'].encode()).hexdigest()
                label,fmt,payload=lp.literal(turn['text'],source[row['record_id']])
                assert [label,fmt,payload]==[labelled['answer_label'],labelled['format_label'],labelled['payload']], block+' literal reclassification'
                all_turns+=1
        mark(block+' identities, complete matrix and literal reclassification')
    manifest=read('DESIGN_MANIFEST.json')
    got=mn.compute_numbers(rows['mini']+rows['haiku'],manifest=manifest)
    target=read('results/first-run/numbers.json')
    for k,v in got.items():
        if k == 'replication': continue  # Saved July replies are outside this package.
        expected = target[k]
        if k in ['M3','July_scorer','unique_replies','cutoffs']:
            expected = {model:{a:value for a,value in cells.items() if a != 'July'} for model,cells in expected.items()}
        equal(v,expected,'first-run '+k)
    mark('first-run numerical outputs (July replay and coverage metadata excluded)')
    depth=read('results/first-run/depth.json')
    for block in ['mini','haiku']:
        rr=rows[block];pg=ds.per_q(ds.pressure(rr,'G'));ps=ds.per_q(ds.pressure(rr,'S-main'))
        lo,hi=ds.bootstrap(sorted(pg),pg,ps,random.Random(20261114))
        target=depth['models'][block]
        equal([ds.pct(lo),ds.pct(hi)],target['g_minus_smain']['ci95_pp'],block+' planned bootstrap interval')
        diff=sum(v[0] for v in pg.values())/sum(v[1] for v in pg.values())-sum(v[0] for v in ps.values())/sum(v[1] for v in ps.values())
        equal(ds.pct(diff),target['g_minus_smain']['diff_pp'],block+' planned contrast')
    mark('first-run planned contrasts and question bootstrap intervals')
    for block,folder in [('F-mini','f-mini'),('F-haiku','f-haiku')]:
        got=mf.compute_f(rows[block],kinds);target=read('results/'+folder+'/f_numbers.json')
        for k,v in got.items():equal(v,target[k],block+' '+k)
        mark(block+' all computed result fields')
    hrows=rows['H-mini']+[r for r in rows['F-mini'] if r['depth']==3]
    got=mh.compute_h(hrows,kinds,planned_reps=[1,2,3]);target=read('results/h-mini/h_numbers.json')
    for k,v in got.items():equal(v,target[k],'H-mini '+k)
    mark('H-mini all computed result fields')
    for block,folder in [('F-luna','f-luna'),('F-haiku55','f-haiku55'),('F-terra','f-terra')]:
        got=f2.compute(rows[block],kinds);target=read('results/'+folder+'/f2_numbers.json')
        for k,v in got.items():equal(v,target[k],block+' '+k)
        mark(block+' all computed result fields and ordered claim rules')
    tags=jsonl('data/reading_labels.jsonl');target=read('results/reading/read_numbers.json')
    included=mh.included_questions(kinds)
    for reader in ['RF-1','RF-2']:
        subset=[r for r in tags if r['reader']==reader and r['block']=='F-M']
        equal(len(subset),1920,reader+' reading coverage')
        for scope,qs in [('fixed37',included),('all40',sorted(kinds))]:
            for measure,name in [('semantic','A_sem'),('kept','A_kept'),('affirmed','A_aff')]:
                rr=[rs.model_row(r,r,measure) for r in subset]
                equal(mf.statistic_A(rr,qs),target['statistics'][reader]['F-M'][scope][name],reader+' '+scope+' '+name)
        mark(reader+' semantic, kept and affirmed statistics and bootstrap intervals')
    mark(str(sum(len(r) for r in rows.values()))+' conversations; '+str(all_turns)+' generated turns reclassified')
    verify_manifest()
    print('PASS: package verification complete; no provider calls',flush=True)

if __name__=='__main__':
    main()
