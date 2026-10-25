"""B-form wrappers of the generated event lemmas: Bf side ts A -->* Bf side' ts' A' (ts = the tokens nearest the head
up to the first gap; side = the rest, written cell by cell as in the generated lemma)."""
import sys
from evs12 import *
from planner8 import is_run

def lin_coq(form, c=0):
    parts = [('%s' % v) if k == 1 else '%d * %s' % (k, v) for v, k in form]
    if c:
        parts = ['%d' % c] + parts
    return ' + '.join(parts) if parts else '0'

def parse_tokens(L):
    """L: stream nearest-first. Returns (list of token items, rest). token item: ('t', const, form) or ('ones', const, form)."""
    toks, i = [], 0
    def ones_run(t):
        return is_run(t) and len(t[1]) % 3 == 0 and t[1] == (1, 0, 1) * (len(t[1]) // 3)
    while i < len(L) and (L[i] == 1 or ones_run(L[i])):
        if is_run(L[i]):
            j = len(L[i][1]) // 3
            toks.append(('ones', 0, tuple((v, j * m) for v, m in L[i][2]))); i += 1; continue
        c, form = 0, {}
        i += 1
        while True:
            if L[i:i + 2] == [0, 1] and not (i + 2 < len(L) and L[i + 2] == 0 and False):
                c += 1; i += 2
            elif i < len(L) and is_run(L[i]) and set(L[i][1]) <= {0, 1} and L[i][1] == (0, 1) * (len(L[i][1]) // 2):
                k = len(L[i][1]) // 2
                for v, m in L[i][2]:
                    form[v] = form.get(v, 0) + k * m
                i += 1
            else:
                break
        toks.append(('t', c, tuple(sorted(form.items()))))
    return toks, L[i:]

def ts_coq(toks):
    """tokens nearest-first -> Coq list expression; each D1 run is one repeat 1 (..), explicit D1s are merged into
    the run they touch (or form a run of their own)"""
    pieces, cur = [], []
    run_c, run_f = 0, None
    def flush():
        nonlocal run_c, run_f
        if run_c or run_f:
            if cur:
                pieces.append('[' + '; '.join(cur) + ']'); cur.clear()
            pieces.append('repeat 1 (%s)' % lin_coq(run_f or (), run_c))
        run_c, run_f = 0, None
    for kind, c, form in toks:
        if kind == 'ones':
            if run_f is not None:
                flush()
            run_f = form
            continue
        if c == 1 and not form:
            run_c += 1
            continue
        flush()
        cur.append(lin_coq(form, c))
    flush()
    if cur:
        pieces.append('[' + '; '.join(cur) + ']')
    return ' ++ '.join(pieces) if pieces else '[]'

def bform_coq(cfg):
    q, L, R, mode = cfg
    assert q == 'H' and mode == '>' and R == [BLANK], cfg
    toks, rest = parse_tokens(L)
    A = toks[0]; Z0 = toks[1]
    assert A[0] == 't' and Z0 == ('t', 0, ()), (A, Z0)
    side = coqgen.side_coq(rest) if rest else None
    return 'Bf (%s)%%sym (%s) (%s)' % (side, ts_coq(toks[2:]), lin_coq(A[2], A[1]))

def wrapper(name):
    S, T = EV[name][:2]
    cn, vs = coqgen.free_vars(S, T)
    args = ' '.join(cn + vs)
    pre, post = [], []
    for t in S[1]:
        if is_run(t) and t[1] == (0, 1) * 3:
            pass
    # tokens c + 3 v in the start are written by the explorer as [0;1]^^c *> [0;1;0;1;0;1]^^v
    toks, _ = parse_tokens(S[1])
    for kind, c, form in toks:
        if kind == 't' and len(form) == 1 and form[0][1] == 3:
            pre.append('rewrite (tok3 %d %s).' % (c, form[0][0]))
    toks, _ = parse_tokens(T[1])
    for kind, c, form in toks:
        if kind == 'ones':
            for v, m in form:
                if m == 2:
                    post.append('rewrite (pow_mul [1;0;1]%%sym 2 %s).' % v)
    NL = chr(10)
    return (('Lemma W_%s : forall %s, %s -->* %s.' + NL + 'Proof. intros. unfold Bf. bnorm. %s follow (EV_%s %s). %s finish_norm. Qed.' + NL)
            %(name, args, bform_coq(S), bform_coq(T), ' '.join(pre), name, args, ' '.join(post)))

if __name__ == '__main__':
    names = sys.argv[1:] or ['R1END', 'E0', 'E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'E10', 'E11', 'E12']
    for n in names:
        print(wrapper(n))
