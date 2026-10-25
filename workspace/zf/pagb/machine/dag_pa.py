"""DAG export of the FROZEN pagb machine, for the prog (L2) and tm layers.  Read-only: never rebuilds.

python dag_pa.py            check hashes, export, reproduce, print stats
Outputs (written to runs/, NOT frozen; regenerate any time):
  runs/pa_dag.json     {"start", "regidx", "nodes": {name: [car, cdr]}, "sha256_tm"}: the program DAG of
                       pa_wade.tm as extracted by zf/tools/dag.py (edges: ["node", n] | ["op", reg,
                       "inc"|"decnz"] | ["break", k] | ["continue", k] | ["halt"]). Same format as the
                       m254 / m254tg prog layers consumed.
  runs/pa_flat.json    the flat goto-free op graph of one run of main() (flatten.flatten_dag): node ->
                       ["inc", reg, next] | ["decnz", reg, next_nonzero, next_zero] | ["goto", next] |
                       ["halt"] | ["end"]; paths are the keys.
Checks:
  1. the frozen files have the recorded sha256 (frozen_pa.FROZEN);
  2. REPRODUCTION: source_pa.py, compiled again with Wade's TMBuilder in a scratch copy, gives a .tm that
     is byte-identical to pa_wade.tm (LF);
  3. DAG stats: TM states, DAG nodes, framework states, registers, the occurs-check gate's nodes (occ*).
"""
import os, sys, json, shutil, tempfile, hashlib, importlib, collections
HERE = os.path.dirname(os.path.abspath(__file__))
ZF = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ZF, 'tools')); sys.path.insert(0, os.path.join(ZF, 'ext', 'turing_machine_explorer'))
sys.path.insert(0, HERE)
import frozen_pa

TM = os.path.join(HERE, 'pa_wade.tm')

def reproduce():
    """recompile the frozen source in a scratch dir; return sha256 of the LF-normalized result."""
    tmp = tempfile.mkdtemp(prefix='pagb_repro_')
    try:
        shutil.copy(os.path.join(HERE, 'source_pa.py'), os.path.join(tmp, 'source_pa_repro.py'))
        sys.path.insert(0, tmp)
        mod = importlib.import_module('source_pa_repro')
        z = mod.ZF2(); z.debug = False; z.build_machine()
        out = os.path.join(tmp, 'repro.tm'); z.tm.save(out)
        raw = open(out, 'rb').read().replace(b'\r\n', b'\n')
        nstates = len(set(s[0] for s in z.tm.states))
        return hashlib.sha256(raw).hexdigest(), nstates
    finally:
        sys.path.remove(tmp); shutil.rmtree(tmp, ignore_errors=True)

def main():
    frozen_pa.check_frozen()
    print('1. frozen hashes OK')
    h, ns = reproduce()
    ok = h == frozen_pa.FROZEN['pa_wade.tm']
    print(f'2. reproduction: compile(source_pa.py) sha256 {h} -> {"IDENTICAL to" if ok else "DIFFERS from"} pa_wade.tm; {ns} states')
    assert ok
    import dag
    start, tbl, nodes, regidx = dag.extract(TM)
    json.dump({'start': start, 'regidx': regidx, 'nodes': {k: list(v) for k, v in nodes.items()},
               'sha256_tm': frozen_pa.FROZEN['pa_wade.tm']},
              open(os.path.join(HERE, 'runs', 'pa_dag.json'), 'w', newline='\n'), indent=0)
    states = {s for (s, _) in tbl}
    fw = {s for s in states if s[0].isdigit()}
    ops = collections.Counter(e[0] if e[0] != 'op' else 'op.' + e[2] for v in nodes.values() for e in v)
    occ = sorted(n for n in nodes if n.startswith('occ'))
    print(f'3. TM states {len(states)} (framework {len(fw)}, DAG {len(states) - len(fw)}); DAG nodes {len(nodes)}; '
          f'registers {len(regidx)} {sorted(regidx, key=regidx.get)}')
    print(f'   edge kinds {dict(ops)}')
    print(f'   occurs-check gate nodes: {len(occ)} ({", ".join(sorted({n.split("(")[0] for n in occ}))})')
    import flatten
    flat, entry = flatten.flatten_dag(nodes)
    ser = {('/'.join(map(str, k)) if isinstance(k, tuple) else k):
           [x if not isinstance(x, tuple) else '/'.join(map(str, x)) for x in v] for k, v in flat.items()}
    json.dump(ser, open(os.path.join(HERE, 'runs', 'pa_flat.json'), 'w', newline='\n'))
    kinds = collections.Counter(v[0] for v in flat.values())
    print(f'4. flat op graph of main(): {len(flat)} sites {dict(kinds)}')
    print('wrote runs/pa_dag.json, runs/pa_flat.json')

if __name__ == '__main__':
    main()
