"""Generate a busycoq non-halting proof for an F-shape (A0:0RF-type) relative of the digit-list counter:

    Kf(ds; a; b) = 0^inf 1^d1 0 ... 0 1^dn 0 1^a 0 1^b 0 F> 0^inf          (kfam shape ('F', '0'))
    R1 b -> b + 3;  R2 a = b + 1, b = 2;  R3 refill b + 1 - k, a = 1, b = 2;  halt at k = b + 1;
    R4 K(; 0; b) -> K(1^b; 1; 2).

    python gen_kcoq_F0.py TM OUT.v [--title T] [--report R]

The script checks these rules with kfit (shape F,0), runs the planner on ADD, ENTRY, LOOP, FINAL1, END4
(kphases_F0.py), finds the first K configuration from the blank tape and fills kcoq_template_F0.v.in.
A machine whose rules differ in any constant (b2, a3, b3, R4 tail, ...) needs a template change: EX's start
(a, b) = (1, 2), the refill b + 1 - k and Top b = Kf (1^b) 1 2 are written into the template.

WALK variant (added in neighbors_final6.md): the A0:0RF neighbors that change D0 and keep F1 = 0RD have
R3 refill b + 2 - k, and after a reset their A0 walks right through the (10) pairs (hand-written lemma WALK)
instead of moving a block through them (SHIFT).  If the fit matches one of the two WALK kinds below, the
phases of kphases_F0w.py (FIN1, E4A, FEND) and kcoq_template_F0w.v.in are used; the constants a2, a3, b3 are
taken from the fit.  A fit equal to EXPECT still takes the original path unchanged.
  'A1' : R2 a = b + 2, b = b3;  R3 refill b + 2 - k, (1, b3);  R4 (1^(b+1)); 1; b3     (b3 in {0, 1, ...})
  'A0' : R2 a = b + 1, b = 3;   R3 refill b + 2 - k, (0, 3);   R4 (1^(b+1)); 0; 3
"""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import planner8 as pl
from planner8 import drive
from coqgen_util import script_to_coq, crossing_lemma, table
from kphases_F0 import phases, COQ
import kfam
from kfit import fit
from tmlit import Sim

EXPECT = dict(m1=1, c1=3, m2=1, c2=1, b2=2, m3=1, c3=1, a3=1, b3=2, mh=1, ch=1, P=(), m4=1, c4=0, a4=1, b4=2)


def coq_list(ds_top_first):
    return '[' + '; '.join('%d%%nat' % d for d in reversed(ds_top_first)) + ']'


WALK_COMMON = dict(m1=1, c1=3, m2=1, m3=1, c3=2, mh=1, ch=1, P=(), m4=1, c4=1)


def walk_kind(P):
    """('A1', b3) / ('A0', 3) if the fitted rules are one of the WALK kinds, else None."""
    if any(P.get(k) != v for k, v in WALK_COMMON.items()):
        return None
    if P.get('c2') == 2 and P.get('a3') == 1 and P.get('a4') == 1 and P.get('b2') == P.get('b3') == P.get('b4'):
        return ('A1', P['b3'])
    if P.get('c2') == 1 and P.get('a3') == 0 and P.get('a4') == 0 and P.get('b2') == P.get('b3') == P.get('b4') == 3:
        return ('A0', 3)
    return None


def gen(tm, outp, title=None, report=None):
    kfam.set_shape('F', '0')
    P, raw = fit(tm)
    bad = [(k, P.get(k), v) for k, v in EXPECT.items() if P.get(k) != v]
    if bad:
        wk = walk_kind(P)
        if wk is None:
            raise SystemExit('rules differ from the F0 template and from the WALK kinds: %r' % bad)
        return gen_walk(tm, outp, wk, title, report)
    s = Sim(tm)
    r = kfam.run_from(s, 10 ** 6)
    if r[0] != 'K':
        raise SystemExit('no K configuration from the blank tape')
    nsteps, (ds0, a0, b0) = r[1], r[2]
    if any(d == 0 for d in ds0):
        raise SystemExit('first K configuration has a zero digit: %r' % (r[2],))
    print('init: K(%s; %d; %d) after %d steps' % (ds0, a0, b0, nsteps), file=sys.stderr)
    pl.set_tm(tm)
    pl.LEMMAS.clear()
    ph = phases()
    bodies = []
    for pname in ['ADD', 'ENTRY', 'LOOP', 'FINAL1', 'END4']:
        start, target = ph[pname]
        script, _ = drive(pname, start, target, matchers=(), maxev=400, verbose=False)
        if script[-1][0] != 'end':
            raise SystemExit('planner did not reach the target of %s: %r' % (pname, script[-3:]))
        if len(script) == 1 and script[0][0] == 'end':
            tac = ['eapply progress_intro; [prove_step | simpl_tape].',
                   'do %d step. finish_norm.' % (script[0][1] - 1)]
        else:
            tac = script_to_coq(script, True)
        body = 'Lemma %s : %s.\nProof.\n  intros.\n' % (pname, COQ[pname])
        line = '  '
        for t in tac:
            if len(line) + len(t) > 100:
                body += line.rstrip() + '\n'
                line = '  '
            line += t + ' '
        body += line.rstrip() + '\nQed.\n'
        bodies.append(body)
        nst = sum(o[1] for o in script if o[0] in ('steps', 'end'))
        print('  %-6s literal steps %4d, ops %d' % (pname, nst, len(script)), file=sys.stderr)
    crossings = ''.join(crossing_lemma(nm, pl.LEMMAS[nm]) + '\n' for nm in sorted(pl.LEMMAS))
    subst = dict(title=title or 'BB(8) neighbor', report=report or 'see the investigation report', tm=tm,
                 table=table(tm), crossings=crossings, phases='\n'.join(bodies),
                 init_comment='Kf %s %d %d after %d steps' % (coq_list(ds0), a0, b0, nsteps),
                 ds0=coq_list(ds0), a0=a0, b0=b0, nsteps=nsteps)
    text = open(os.path.join(HERE, 'kcoq_template_F0.v.in')).read() % subst
    open(outp, 'w', newline='\n').write(text)
    print('wrote', outp, file=sys.stderr)


def phase_bodies(names, ph, coq):
    bodies = []
    for pname in names:
        start, target = ph[pname]
        script, _ = drive(pname, start, target, matchers=(), maxev=400, verbose=False)
        if script[-1][0] != 'end':
            raise SystemExit('planner did not reach the target of %s: %r' % (pname, script[-3:]))
        if len(script) == 1 and script[0][0] == 'end':
            tac = ['eapply progress_intro; [prove_step | simpl_tape].',
                   'do %d step. finish_norm.' % (script[0][1] - 1)]
        else:
            tac = script_to_coq(script, True)
        body = 'Lemma %s : %s.\nProof.\n  intros.\n' % (pname, coq[pname])
        line = '  '
        for t in tac:
            if len(line) + len(t) > 100:
                body += line.rstrip() + '\n'
                line = '  '
            line += t + ' '
        body += line.rstrip() + '\nQed.\n'
        bodies.append(body)
        nst = sum(o[1] for o in script if o[0] in ('steps', 'end'))
        print('  %-6s literal steps %4d, ops %d' % (pname, nst, len(script)), file=sys.stderr)
    return bodies


def gen_walk(tm, outp, wk, title=None, report=None):
    import kphases_F0w
    kind, b3 = wk
    print('WALK kind %s, b3 = %d' % (kind, b3), file=sys.stderr)
    s = Sim(tm)
    r = kfam.run_from(s, 10 ** 6)
    if r[0] != 'K':
        raise SystemExit('no K configuration from the blank tape')
    nsteps, (ds0, a0, b0) = r[1], r[2]
    if any(d == 0 for d in ds0):
        raise SystemExit('first K configuration has a zero digit: %r' % (r[2],))
    print('init: K(%s; %d; %d) after %d steps' % (ds0, a0, b0, nsteps), file=sys.stderr)
    pl.set_tm(tm)
    pl.LEMMAS.clear()
    bodies = phase_bodies(kphases_F0w.NAMES, kphases_F0w.phases(kind, b3), kphases_F0w.coq(kind, b3))
    crossings = ''.join(crossing_lemma(nm, pl.LEMMAS[nm]) + '\n' for nm in sorted(pl.LEMMAS))
    if kind == 'A1':
        ones = ''.join('1 >> ' for _ in range(b3))
        v = dict(a2='(S (S b))', a3=1, res_pre='', r4_pre='',
                 res_concl='(0 >> %s0 >> [1;0]^^k *> 1 >> [1]^^r *> 1 >> 0 >> [1]^^y *> lft t) {{F}}> const 0'
                 % ones,
                 fend_comment='L A> 0 1 0 0^inf -->+ L 0 1^%d 0 F> 0^inf' % b3)
    else:
        v = dict(a2='(S b)', a3=0,
                 res_pre='rewrite (align_lpow 1 [0] _ (k + 0)). simpl app.\n  ',
                 r4_pre='rewrite (align_lpow 1 [0] _ (S b + 0)). simpl app.\n  ',
                 res_concl='(0 >> 1 >> 1 >> 1 >> 0 >> [0;1]^^k *> [1]^^r *> 1 >> 0 >> [1]^^y *> lft t) {{F}}> const 0',
                 fend_comment='L 1 A> 0 1 0 0^inf -->+ L 0 1 1 1 0 F> 0^inf')
    subst = dict(title=title or 'BB(8) neighbor', report=report or 'see the investigation report', tm=tm,
                 table=table(tm), crossings=crossings, phases='\n'.join(bodies), kind=kind, b3=b3,
                 init_comment='Kf %s %d %d after %d steps' % (coq_list(ds0), a0, b0, nsteps),
                 ds0=coq_list(ds0), a0=a0, b0=b0, nsteps=nsteps, **v)
    text = open(os.path.join(HERE, 'kcoq_template_F0w.v.in')).read() % subst
    open(outp, 'w', newline='\n').write(text)
    print('wrote', outp, file=sys.stderr)


def main():
    a = sys.argv
    title = a[a.index('--title') + 1] if '--title' in a else None
    report = a[a.index('--report') + 1] if '--report' in a else None
    gen(a[1], a[2], title, report)


if __name__ == '__main__':
    main()
