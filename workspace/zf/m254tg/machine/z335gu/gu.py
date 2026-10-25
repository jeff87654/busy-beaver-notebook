"""z335gu: Grothendieck-universe variants of R3Y1_335 (comparison counts only).
Adds v_5 (fresh variable) and the UREP tree; everything else is the axtext/search tooling (copied)."""
import json, time, sys
import lowprio, zf2, zfp, forms
from forms import EQ, EL, IM, N, AL, EX, A, BI, PH, SUB, OR
from TMBuilder import subroutine

# fresh variable v_5 (same pattern as zf2's v_4 = v_2 + 2)
zf2.ZF2.v_5 = subroutine(lambda self: [self.v_3(), [self.topwff.inc, self.topwff.inc]])
zf2.ZF2.v_5.__name__ = 'v_5'

# forms.variant pads vmap only to 5 variables; pad to 8
_orig_variant = forms.variant
def variant(t, vmap=(0, 1, 2, 3), flips=0):
    vmap = tuple(vmap) + tuple(range(len(vmap), 8))
    return _orig_variant(t, vmap, flips)
forms.variant = variant

R = AL(1, PH)                                   # REP's relation R(v3, v2) := A. v1 ph
BND = OR(SUB(2, 1, 0), EL(2, 1))                # v2 C_ v1 \/ v2 e. v1   (REPsb0's fiber bound)
HYP = AL(3, EX(1, AL(2, IM(R, BND))))           # REPsb0 hypothesis
IMG = AL(2, BI(EL(2, 1), EX(3, A(EL(3, 0), R))))  # v1 = image of v0 under R
HYPW = AL(3, EX(1, A(EL(1, 4), AL(2, IM(R, BND)))))  # same, bound v1 taken in w = v4
TRANS = AL(3, IM(EL(3, 4), AL(2, IM(EL(2, 3), EL(2, 4)))))   # w transitive
INNER = AL(5, AL(0, IM(EL(0, 4), IM(HYPW, EX(1, A(EL(1, 4), IMG))))))  # A. v5 A. v0 e. w: REP inside w
forms.TREES['UREP'] = IM(HYP, EX(1, A(IMG, EX(4, A(EL(1, 4), A(TRANS, INNER))))))
# UREP2: no outer image; collection of bounds into w (R with v4 neutralised there), REP derived from INNER
R4 = AL(4, R)
COLL = AL(3, IM(EL(3, 0), EX(1, A(EL(1, 4), AL(2, IM(R4, BND))))))
forms.TREES['UREP2'] = IM(HYP, EX(4, A(EL(0, 4), A(TRANS, A(COLL, INNER)))))
for _n in ('UREP', 'UREP2'):
    forms.REPLIKE.add(_n); zfp.REPLIKE.add(_n)

assert forms.TREES['REPsb0'] == IM(HYP, EX(1, IMG))

def ntok(name, flips=0):
    return len(forms.postfix(forms.variant(forms.TREES[name], (0, 1, 2, 3), flips)))

def build(cfg):
    perm = {k: tuple(v) for k, v in cfg['perm'].items()}
    z = zfp.build(zfp.make(cfg['clauses'], perm, cfg['opt'], cfg['vmap'], cfg['flips']), cfg['order'])
    return z

def variant_cfg(base, rep='UREP', drop_inf=False, flips=0):
    cfg = json.loads(json.dumps(base))
    cl = cfg['clauses']; i = cl.index('REPsb0'); cl[i] = rep
    cfg['flips'].pop('REPsb0', None)
    cfg['perm'][rep] = cfg['perm'].pop('REPsb0')
    if flips: cfg['flips'][rep] = flips
    if drop_inf:
        j = cl.index('INF'); del cl[j]
        cfg['order'] = [k - (k > j) for k in cfg['order'] if k != j]
        cfg['vmap'].pop('INF', None); cfg['flips'].pop('INF', None)
    return cfg

if __name__ == '__main__':
    base = json.load(open('R3Y1_335.json'))
    t = time.time(); print('baseline', zfp.count(build(base)), '%.1fs' % (time.time() - t))
    print('tokens REPsb0', ntok('REPsb0'), 'UREP', ntok('UREP'), 'INF', ntok('INF'), 'nflip UREP', forms.nflip(forms.TREES['UREP']))
    print(forms.show(forms.TREES['UREP']))
    for rep in ('UREP', 'UREP2'):
        print(rep, 'tokens', ntok(rep), forms.show(forms.TREES[rep]))
        for drop in (False, True):
            c = variant_cfg(base, rep, drop_inf=drop)
            print(rep + (' -INF' if drop else ''), zfp.count(build(c)))

# UREP with the transitivity conjunct's bound variables (p, q) chosen freely (alpha-variants)
def TRANSpq(p, q): return AL(p, IM(EL(p, 4), AL(q, IM(EL(q, p), EL(q, 4)))))
TPQ = [(p, q) for p in (0, 1, 2, 3, 5) for q in (0, 1, 2, 3, 5) if p != q]
for p, q in TPQ:
    nm = 'UREP_%d%d' % (p, q)
    forms.TREES[nm] = IM(HYP, EX(1, A(IMG, EX(4, A(EL(1, 4), A(TRANSpq(p, q), INNER))))))
    forms.REPLIKE.add(nm); zfp.REPLIKE.add(nm)
