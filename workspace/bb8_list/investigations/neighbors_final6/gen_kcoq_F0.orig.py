"""Generate a busycoq non-halting proof for an F-shape (A0:0RF-type) relative of the digit-list counter:

    Kf(ds; a; b) = 0^inf 1^d1 0 ... 0 1^dn 0 1^a 0 1^b 0 F> 0^inf          (kfam shape ('F', '0'))
    R1 b -> b + 3;  R2 a = b + 1, b = 2;  R3 refill b + 1 - k, a = 1, b = 2;  halt at k = b + 1;
    R4 K(; 0; b) -> K(1^b; 1; 2).

    python gen_kcoq_F0.py TM OUT.v [--title T] [--report R]

The script checks these rules with kfit (shape F,0), runs the planner on ADD, ENTRY, LOOP, FINAL1, END4
(kphases_F0.py), finds the first K configuration from the blank tape and fills kcoq_template_F0.v.in.
A machine whose rules differ in any constant (b2, a3, b3, R4 tail, ...) needs a template change: EX's start
(a, b) = (1, 2), the refill b + 1 - k and Top b = Kf (1^b) 1 2 are written into the template.
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


def gen(tm, outp, title=None, report=None):
    kfam.set_shape('F', '0')
    P, raw = fit(tm)
    bad = [(k, P.get(k), v) for k, v in EXPECT.items() if P.get(k) != v]
    if bad:
        raise SystemExit('rules differ from the F0 template: %r' % bad)
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


def main():
    a = sys.argv
    title = a[a.index('--title') + 1] if '--title' in a else None
    report = a[a.index('--report') + 1] if '--report' in a else None
    gen(a[1], a[2], title, report)


if __name__ == '__main__':
    main()
