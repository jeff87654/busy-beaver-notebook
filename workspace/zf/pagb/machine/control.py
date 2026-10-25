"""Positive control: the machine with NG replaced by CTL := "a = 0 ∧ a = σb" (open, i.e. ∀x∀y(x = 0 ∧
x = σy), refuted by zero_succ in one MP) halts on the hand-built proof program.

The program  START ++ Build(mp(QZS-leaf, CTL-leaf, F)) ++ DROP NIP NIP  is
  1. run through spec_pa.enum_step from random arbitrary states (must halt), and
  2. run on the compiled register-machine DAG of pa_ctl_wade.tm (rmsim, accelerated helpers),
     starting from the same states loaded as candidate N = encode(program) (must halt);
  3. the same program on the NG machine (pa_wade.tm) must NOT halt (the CTL slot holds NG there).
Usage: python control.py        (sets PA_VARIANT itself; run from this directory)
"""
import os, sys, random, itertools, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools'))

def program(compiler_pa, spec, design):
    """D = mp(minor, major, F): either CTL = ¬Y (find a row = Y, then MP with CTL as major), or CTL is
    an atom X (find a row = X → F, i.e. the matching zero_succ instance, MP with CTL as minor)."""
    jC = design.NG_INDEX + 1
    a0, b0 = 5, 6
    ctl = spec.ev(design.CTL, {'a': a0, 'b': b0, 'c': 0, 'u': 0})
    q, t = divmod(ctl, 4); y, f = spec.unP(q)
    if t == 0 and f == 1:
        target, ctl_is_major = y, True
    else:
        target, ctl_is_major = spec.wim(ctl, 1), False
    hit = None
    for j, r in enumerate(design.ROWS):
        if j == design.NG_INDEX: continue
        for a, b, c, u in itertools.product(range(0, 9), repeat=4):
            if spec.ev(r, {'a': a, 'b': b, 'c': c, 'u': u}) == target:
                hit = (j + 1, a, b, c, u); break
        if hit: break
    assert hit, 'no row gives the refuting instance'
    leaf_ctl = ('row', jC, a0, b0, 0, 0)
    D = ('mp', leaf_ctl, ('row',) + hit, 1) if not ctl_is_major else ('mp', ('row',) + hit, leaf_ctl, 1)
    assert compiler_pa.conclusion(D) == 1
    return compiler_pa.START + compiler_pa.build(D) + compiler_pa.HALT_SUFFIX, D

def run_rm(dagpath, state, cmds, compiler_pa):
    import dag, rmsim
    start, tbl, nodes, regidx = dag.extract(dagpath)
    accel, kinds = rmsim.build_accel(nodes)
    t, S, d, h = state
    N = compiler_pa.encode(cmds)
    R = {'prooflist': 0, 'nextproof': N, 'topwff': t, 'wffstack': S, 'axiomcode': 0,
         'param1': d, 'param2': h, 'scratch1': 0, 'scratch2': 0, 'param4': 0}
    for i in range(len(cmds)):
        ex = rmsim.run(nodes, 'main().0', R, accel=accel)
        if ex == ('halt',):
            return ('halt', i)
    return ('no halt', R['topwff'])

def main(variant):
    os.environ['PA_VARIANT'] = variant
    import design, spec_pa as spec, compiler_pa
    import frozen_pa; frozen_pa.machine_path(design.SUFFIX)          # frozen: read + hash check; ctl: build
    import json
    pj = os.path.join(HERE, 'runs', 'control_program.json')
    if variant == 'ctl':
        cmds, D = program(compiler_pa, spec, design)
        json.dump([list(c) for c in cmds], open(pj, 'w'))
        print(f'[{variant}] program: {len(cmds)} commands; derivation {D}')
    else:
        cmds = [tuple(c) for c in json.load(open(pj))]
        print(f'[{variant}] same {len(cmds)}-command program on the NG machine')
    rnd = random.Random(3)
    res = []
    for k in range(5):
        st = compiler_pa.rand_state(rnd) if k else (0, 0, 0, 0)    # small cache under the occurs-check gate
        out_spec = compiler_pa.run_cmds(st, cmds)
        out_rm = run_rm(os.path.join(HERE, f'pa{design.SUFFIX}_wade.tm'), st, cmds, compiler_pa)
        res.append((out_spec[0], out_rm[0]))
        print(f'  state {k}: spec {out_spec[0]} {out_spec[1] if out_spec[0] == "halt" else ""} | RM {out_rm}')
    return res

if __name__ == '__main__':
    if len(sys.argv) > 1:
        res = main(sys.argv[1])
        want = 'halt' if sys.argv[1] == 'ctl' else 'no halt'
        ok = all((a == 'halt') == (want == 'halt') and (b == 'halt') == (want == 'halt') for a, b in res)
        print('OK' if ok else 'FAIL'); raise SystemExit(0 if ok else 1)
    # each variant in a fresh process (design is chosen at import)
    rc = 0
    for v in ('ctl', 'ng'):
        rc |= subprocess.call([sys.executable, os.path.abspath(__file__), v])
    print('CONTROL ALL OK' if rc == 0 else 'CONTROL FAIL')
