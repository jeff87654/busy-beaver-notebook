"""Exhaustive one-entry neighborhood of the existing local BB(8) record.

Changes E0 or any entry in F/G/H, holding the remaining core fixed.
Every replacement among 36 binary-write/direction/destination entries is
included. Machines without any halt transition are rejected syntactically.
"""
import json
import multiprocessing as mp
import time
from sim import parse, fmt
from search3 import prefix, run
from macro import simulate_macro

SNAPSHOT = None
DEADLINE = None


def initialize(deadline):
    global SNAPSHOT, DEADLINE
    SNAPSHOT = prefix()
    DEADLINE = deadline


def evaluate(task):
    index, position, entry, machine = task
    table = parse(machine)
    if not any(e[2] == -1 for row in table for e in row):
        result = ('no_halt_transition', None, None, 0)
    elif time.monotonic() >= DEADLINE:
        result = ('not_evaluated_deadline', None, None, 0)
    else:
        result = run(table, 300000, SNAPSHOT)[:4]
    return {'index':index, 'position':position, 'entry':entry,
            'machine':machine, 'status':result[0], 'steps':result[1],
            'ones':result[2], 'ops':result[3]}


if __name__ == '__main__':
    start = time.monotonic()
    with open('run2_merged.json') as f:
        old = json.load(f)['best'][0]
    base = parse(old[2])
    tasks = []
    for state, symbol in [(4,0)] + [(i,j) for i in range(5,8) for j in range(2)]:
        for write in range(2):
            for direction in (-1,1):
                for destination in range(-1,8):
                    entry = (write,direction,destination)
                    if entry == base[state][symbol]:
                        continue
                    table = [row[:] for row in base]
                    table[state][symbol] = entry
                    tasks.append((len(tasks), chr(65+state)+str(symbol),
                                  entry, fmt(table)))
    assert len(tasks) == 245
    results = []
    with mp.Pool(2, initialize, (start+160,)) as pool:
        for result in pool.imap_unordered(evaluate, tasks):
            results.append(result)
            if result['status'] == 'halt' and result['steps'] > old[0]:
                print('NEW RECORD ' + json.dumps(result), flush=True)
    best = sorted((r for r in results if r['status']=='halt'
                   and r['steps'] > old[0]), key=lambda r:r['steps'], reverse=True)
    for record in best:
        if time.monotonic() > start + 170:
            record['verification_pending_deadline'] = True
            continue
        checks = []
        for k in (2,3,4):
            status, steps, ones, ops = simulate_macro(parse(record['machine']), k, 1000000)
            checks.append({'k':k,'status':status,'steps':steps,'ones':ones,'ops':ops})
            if status=='halt':
                assert (steps,ones)==(record['steps'],record['ones'])
                break
        record['macro_checks'] = checks
    counts = {}
    for r in results:
        counts[r['status']] = counts.get(r['status'],0)+1
    output = {'base_record':old, 'configuration':{'workers':2,'ops':300000,
               'positions':['E0','F0','F1','G0','G1','H0','H1'],
               'neighbor_count':245}, 'elapsed_seconds':time.monotonic()-start,
              'counts':counts,'best':best,'results':sorted(results,key=lambda r:r['index'])}
    with open('audit_neighbors.json','w') as f:
        json.dump(output,f,indent=2)
    print(json.dumps({k:v for k,v in output.items() if k!='results'},indent=2),flush=True)
