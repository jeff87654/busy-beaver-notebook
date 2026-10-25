"""Generate the busycoq proof for 1RB0RC_1LA1RF_0RE0LD_1LE0LH_1LA0LG_1RA0LF_0LC1LE_---1LF.
Usage: python gen.py out.v"""
import sys, os, threading
threading.Timer(100, lambda: os._exit(3)).start()
import planner8 as pl
from planner8 import drive, mkrun, V, BLANK, is_run
from gen_base import script_to_coq, crossing_lemma, table, cl

TM = "1RB0RC_1LA1RF_0RE0LD_1LE0LH_1LA0LG_1RA0LF_0LC1LE_---1LF"
U = [1, 0, 0, 0, 0, 1, 0, 1]
B6 = (0, 1, 0, 1, 0, 1)
Z6B = (0, 0, 0, 0, 0, 0)
R = [V('r')]
NIL = [BLANK]
none = {}
m = {'m': 1}
a = {'a': 1}
k = {'k': 1}


def W(mcnt, extra01, acnt, r, mconst=0):
    return ('A', [BLANK], [0, 1, 1] + mkrun(B6, mcnt, mconst) + [0, 1] * extra01 + mkrun((0,), acnt[0], acnt[1]) + U + r, '>')


def digit(dcnt):
    return mkrun((0,), dcnt[0], dcnt[1]) + U + [BLANK]


def cnt_coq(c):
    return ' + '.join(('%s' % v_) if co == 1 else ('%d * %s' % (co, v_)) for v_, co in c)


def tok_coq(t):
    if isinstance(t, int):
        return '%d >> ' % t
    if t == BLANK:
        return 'const 0'
    if t[0] == 'VAR':
        return t[1]
    return '%s^^%s *> ' % (cl(t[1]), '(' + cnt_coq(t[2]) + ')' if '+' in cnt_coq(t[2]) or '*' in cnt_coq(t[2]) else cnt_coq(t[2]))


def side_coq(side):
    return ''.join(tok_coq(t) for t in side)


def cfg_coq(cfg):
    q, L, Rr, mode = cfg
    return '%s {{%s}}> %s' % (side_coq(L), q, side_coq(Rr))


PH = {}
FZ = {}
# N1: normal step  X(m, a+2, r) -> X(m+1, a+1, r)
PH['N1'] = ('m a r', W(m, 2, (a, 2), R), W(m, 5, (a, 1), R))
# Z6: 1111 A> 0^(k+2) r -> A> 0 11 01 01 0^(k+1) r
PH['Z6'] = ('k r', ('A', [1, 1, 1, 1, BLANK], mkrun((0,), k, 2) + R, '>'),
            ('A', [BLANK], [0, 1, 1, 0, 1, 0, 1] + mkrun((0,), k, 1) + R, '>'))
# N2: X(m,1,0^(a+5) U) -> Y(m+7, a+1)
PH['N2'] = ('m a', W(m, 2, (none, 1), digit((a, 5))), W(m, 22, (a, 1), NIL))


ZL = {(1, 1, 1, 1): ('Z6', [0, 1, 1, 0, 1, 0, 1]), (1, 1): ('Z2', [0, 1, 1, 0, 1])}


def fuse_matcher(cfg):
    q, L, Rr, mode = cfg
    if q != 'A' or mode != '>' or L[-1] != BLANK or tuple(L[:-1]) not in ZL:
        return None
    zname, zpre = ZL[tuple(L[:-1])]
    i = 0
    while i < len(Rr) and Rr[i] == 0:
        i += 1
    c1 = i
    if i >= len(Rr) or not is_run(Rr[i]) or Rr[i][1] != Z6B:
        return None
    run = Rr[i]
    i += 1
    j = i
    while j < len(Rr) and Rr[j] == 0:
        j += 1
    c2 = j - i
    rest = Rr[j:]
    if not (rest and rest[0] == 1) or c1 + c2 < 2:
        return None
    cnt = tuple((v_, 6 * co) for v_, co in run[2])
    rest_c = side_coq(rest)
    cfg2 = ('A', [BLANK], zpre + mkrun((0,), dict(cnt), c1 + c2 - 1) + rest, '>')
    K = c1 + c2 - 2
    fzn = 'FZ_%s_%d_%d' % (zname, c1, c2)
    ctx = side_coq(L)
    zcells = ''.join('%d >> ' % t_ for t_ in zpre) + '0 >> '
    FZ[fzn] = ('Lemma %s : forall m (r : side), %s {{A}}> [0]^^%d *> [0;0;0;0;0;0]^^m *> [0]^^%d *> r\n'
               '  -->+ const 0 {{A}}> %s[0]^^(%d + 6 * m) *> r.\n'
               'Proof.\n  intros m r. rewrite zf.\n'
               '  replace (%d + 6 * m + %d) with (S (S (%d + 6 * m))) by lia.\n'
               '  apply (%s (%d + 6 * m) r).\nQed.\n' % (fzn, ctx, c1, c2, zcells, K, c1, c2, K, zname, K))
    frag = 'eapply evstep_trans; [apply progress_evstep, %s |].' % fzn
    return cfg2, frag, 'fuse zeros (%d, %d) + %s' % (c1, c2, zname)


fuse_matcher.anytime = True
PH['Z2'] = ('k r', ('A', [1, 1, BLANK], mkrun((0,), k, 2) + R, '>'),
            ('A', [BLANK], [0, 1, 1, 0, 1] + mkrun((0,), k, 1) + R, '>'))
PH['N2p'] = ('m', W(m, 2, (none, 1), digit((none, 4))), W({}, 1, ({'m': 6}, 53), NIL))
PH['C1'] = ('m', W(m, 2, (none, 1), digit((none, 1))), W({}, 2, ({'m': 6}, 53), NIL))
PH['N2s'] = ('m', W(m, 2, (none, 1), NIL), W({}, 2, ({'m': 6}, 41), NIL))
PH['N3p'] = ('a', W({}, 1, (a, 13), NIL), W({}, 2, (none, 14), digit((a, 1))))
PH['N3a'] = ('m a', W(m, 1, (a, 5), NIL), ('A', [1, 1, 1, 1, BLANK], [('run', Z6B, (('m', 1),))] + U + mkrun((0,), a, 1) + U + [BLANK], '>'))
MATCH = {'N2p': (fuse_matcher,), 'C1': (fuse_matcher,), 'N2s': (fuse_matcher,)}


def main():
    outp = sys.argv[1]
    only = sys.argv[2:]
    pl.set_tm(TM)
    pl.LEMMAS.clear()
    bodies = []
    names_done = []
    for name in ['N1', 'Z6', 'Z2', 'N2', 'N3a', 'N2p', 'C1', 'N2s', 'N3p']:
        if only and name not in only:
            continue
        vars_, start, target = PH[name]
        FZ.clear()
        script, _ = drive(name, start, target, matchers=MATCH.get(name, ()), maxev=400, verbose=('-v' in sys.argv))
        tac = script_to_coq(script, True)
        if FZ and tac[-1].endswith('finish_norm.'):
            tac[-1] = tac[-1][:-len('finish_norm.')] + "apply evstep_refl'. rewrite rep6. try (norm_nat; try reflexivity; lia_refl)."
        binders = ' '.join(vars_.replace('r', '').split())
        stmt = 'forall %s%s, %s -->+ %s' % (binders and (binders + ' '), '(r : side)' if 'r' in vars_.split() else '', cfg_coq(start), cfg_coq(target))
        stmt = stmt.replace('forall  ', 'forall ')
        body = ''.join(v_ + chr(10) for v_ in FZ.values()) + 'Lemma %s : %s.\nProof.\n  intros.\n' % (name, stmt)
        line = '  '
        for t in tac:
            if len(line) + len(t) > 100:
                body += line.rstrip() + '\n'
                line = '  '
            line += t + ' '
        body += line.rstrip() + '\nQed.\n'
        bodies.append(body)
        names_done.append(name)
    text = ''
    for nm in sorted(pl.LEMMAS):
        text += crossing_lemma(nm, pl.LEMMAS[nm]) + chr(10)
    open('lib_cross.txt', 'w', newline=chr(10)).write(text)
    for nm_, body in zip(names_done, bodies):
        open('ph_%s.txt' % nm_, 'w', newline=chr(10)).write(body)
    print('wrote lib_cross.txt and', len(bodies), 'phase files', file=sys.stderr)


if __name__ == '__main__':
    main()
