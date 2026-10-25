"""Test of the occurs-check gate (option a) through one AX run of main() on the compiled DAG, against
spec_pa.enum_step. The AX command AX(c; x=a, y=0, u) runs from d = 0, h = b, so param1 = a and
param2 = b are the chosen term codes. Every code a, b < maxcode (every code is decoded as a term) and
c ≤ maxc, plus random structured term codes containing / not containing v_c.
Checks: full post-state equality with the spec (current = bundle or ⊤, stack, registers) and that the
gate actually closes exactly when c ∈ tvars(a) ∪ tvars(b).
Usage: python test_occ.py [maxcode] [maxc] [nrand]"""
import os, sys, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools')); sys.path.insert(0, HERE)
os.environ.setdefault('PA_DESIGN', 'A')
import design, spec_pa as spec, rmsim, dag
from validate_pa import to_regs, from_regs

def main(maxcode=120, maxc=4, nrand=300):
    assert design.GATE == 'occ', 'design is not option (a)'
    import frozen_pa; frozen_pa.machine_path(design.SUFFIX)
    start, tbl, nodes, regidx = dag.extract(os.path.join(HERE, f'pa{design.SUFFIX}_wade.tm'))
    accel, kinds = rmsim.build_accel(nodes)
    def run(a, b, c, u=0):
        cell = spec.P(3 + c, spec.P(a, spec.P(0, spec.P(u, 0))))
        s = (cell + 1, 9, 5, 77, 0, b)                 # pl, np, tw, ws, d, h
        want = spec.enum_step(s)
        R = to_regs(s)
        ex = rmsim.run(nodes, 'main().0', R, accel=accel, maxsteps=10**9)
        got = from_regs(R)
        closed = (c in spec.tvars(a)) or (c in spec.tvars(b))
        okgate = (want[2] == 0) == closed or spec.bundle(a, b, c, u) == 0
        return ex == ('normal',) and got == want and okgate and R['scratch1'] == R['scratch2'] == R['axiomcode'] == 0, closed
    n = bad = hits = 0
    for c in range(maxc + 1):
        for a in range(maxcode):
            for b in (0, 3, 7, a // 2, maxcode - 1 - a):
                ok, z = run(a, b, c); n += 1; hits += z
                if not ok:
                    bad += 1
                    if bad < 6: print('MISMATCH', a, b, c, flush=True)
        print(f'  c={c}: {n} runs so far, mismatches {bad}', flush=True)
    rnd = random.Random(1)
    def rt(dep, c):
        k = rnd.random()
        if dep == 0 or k < 0.35: return spec.weq(rnd.choice([0, 1, 2, c]), 0)
        if k < 0.45: return 0
        if k < 0.65: return spec.wim(rt(dep - 1, c), 1)
        return rnd.choice([spec.wel, spec.wal])(rt(dep - 1, c), rt(dep - 1, c))
    def rtc(c, cap=3 * 10**5):          # the gate's mod-4 loop is linear in the code: keep codes small
        while True:
            t = rt(2, c)
            if t < cap: return t
    for _ in range(nrand):
        c = rnd.randint(0, 3); a, b = rtc(c), rtc(c)
        ok, z = run(a, b, c); n += 1; hits += z
        if not ok:
            bad += 1
            if bad < 6: print('MISMATCH structured', a, b, c, flush=True)
        if n % 25 == 0: print(f'  structured: {n} runs so far, mismatches {bad}', flush=True)
    print(f'AX runs through the occurs-check gate: {n} ({hits} with c occurring -> gate closed), mismatches {bad}')
    return bad

if __name__ == '__main__':
    raise SystemExit(1 if main(*[int(x) for x in sys.argv[1:]]) else 0)
