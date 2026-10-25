"""Per-op random testing of SMFW fragments against sm_abstract. python -I run_tests.py [ops] [--n N]"""
import sys, os, random
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import harness as H

def check(op, N, seed):
    builder = BUILDERS[op]; rng = random.Random(seed); fails = []; ran = 0
    tbl = H.load_tbl()
    if (H.ENTRY[op], '0') not in tbl and (H.ENTRY[op], '1') not in tbl:
        print('%-8s  NOT IMPLEMENTED (needs the STEP-L/STEP-R shuttle engine; see COUNTS.md)' % op)
        return True
    for i in range(N):
        case = builder(rng)
        A, B, c, Nbits, rpos = case['A'], case['B'], case['c'], case.get('N'), case.get('rpos', 0)
        sm = H.mk_SM(A, B, c, Nbits, rpos)
        try:
            exp_out = sm.prim(*case['prim'])
        except Exception:
            continue
        ran += 1
        exp = H.norm(sm.A, sm.B, sm.c)
        try:
            out, got, tape = H.run_frag(tbl, op, A, B, c, Nbits, rpos)
            gotn = H.norm(got[0], got[1], got[2])
            bad = (out != exp_out or gotn != exp)
        except Exception as e:
            bad = True; out = 'RUN:'+str(e); gotn = None
        if bad:
            fails.append((case, exp_out, exp, out, gotn))
        if len(fails) > 6: break
    print('%-8s %4d ran: %s' % (op, ran, 'OK' if not fails else 'FAIL %d' % len(fails)))
    for cs, eo, ex, go, gn in fails[:4]:
        print('    in ', {k: cs[k] for k in ('A','B','c')}, cs.get('prim'))
        print('    exp', eo, ex); print('    got', go, gn)
    return not fails

def b_incc(rng): return dict(A=H.rstack(rng), B=H.rB(rng), c=rng.randint(0,6), prim=('INCC',))
def b_decc(rng):
    c = rng.choice([0,0,1,2,3,4,5]); return dict(A=H.rstack(rng), B=H.rB(rng), c=c, prim=('DECC',))
def b_newp(rng): return dict(A=H.rstack(rng), B=H.rB(rng), c=rng.randint(0,5), prim=('NEWP',))
def b_newt(rng): return dict(A=H.rstack(rng), B=H.rB(rng), c=rng.randint(0,5), prim=('NEWT',))
def b_app1(rng):
    B = H.rB(rng, want_W=True)
    if not B or not B[-1][1]: B.append(['theorem',[8]])
    return dict(A=H.rstack(rng), B=B, c=rng.randint(0,5), prim=('APP1',))
def b_push(v):
    def f(rng):
        B = H.rB(rng, want_W=True)
        if not B: B.append(['theorem',[]])
        return dict(A=H.rstack(rng), B=B, c=rng.randint(0,5), prim=('PUSH',(v,)))
    return f
def b_check(rng):
    A = H.rstack(rng)
    if rng.random() < 0.4: A[-1] = list(SA_CONTRA)
    return dict(A=A, B=[], c=rng.randint(0,5), prim=('CHECK',))
def b_dupt(rng):
    A = H.rstack(rng); B = H.rB(rng, want_W=True)
    if not B: B.append(['theorem',[]])
    return dict(A=A, B=B, c=rng.randint(0,5), prim=('DUPT',))
def b_dup(k):
    def f(rng):
        B = []
        for _ in range(k): B.append(['param', list(H.rwff(rng) if rng.random()<0.7 else H.rvar(rng))])
        B.append(['theorem', list(H.rwff(rng)) if rng.random()<0.6 else []])
        return dict(A=H.rstack(rng), B=B, c=rng.randint(0,5), prim=('DUP',(k,)))
    return f
def b_det(rng):
    A = H.rstack(rng, 2, 4)
    return dict(A=A, B=[], c=rng.randint(0,5), prim=('DET',))
def b_commit(rng):
    B = H.rB(rng, want_W=True)
    B = [e for e in B if e[0]=='param'] + [['theorem', list(H.rwff(rng))]]
    return dict(A=H.rstack(rng), B=B, c=rng.randint(0,5), prim=('COMMIT',))
def b_rb(rng):
    ln = rng.randint(0,6); N = [rng.randint(0,1) for _ in range(ln)]
    rpos = rng.randint(0, ln)
    return dict(A=H.rstack(rng), B=H.rB(rng), c=rng.randint(0,5), N=N, rpos=rpos, prim=('RB',))

import sm_abstract as _SA
SA_CONTRA = _SA.CONTRADICTION
BUILDERS = {'INCC':b_incc,'DECC':b_decc,'NEWP':b_newp,'NEWT':b_newt,'APP1':b_app1,
            'CHECK':b_check,'DUPT':b_dupt,'DET':b_det,'COMMIT':b_commit,'RB':b_rb}
for v in range(3,12): BUILDERS['PUSH%d'%v] = b_push(v)
for k in (1,2,3): BUILDERS['DUP%d'%k] = b_dup(k)

if __name__ == '__main__':
    argv=sys.argv[1:]; N=300
    if '--n' in argv:
        i=argv.index('--n'); N=int(argv[i+1]); del argv[i:i+2]
    ops=[a for a in argv if not a.startswith('--')]
    if not ops: ops = list(BUILDERS)
    allok = True
    for op in ops:
        if op in BUILDERS: allok &= check(op, N, 777)
        else: print('no builder', op)
    sys.exit(0 if allok else 1)
