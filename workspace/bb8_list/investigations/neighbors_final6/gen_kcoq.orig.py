"""Generate a busycoq non-halting proof for a K-family neighbor of the digit-list counter
    1RB1RA_0RC0RA_0LD1RC_1RE1LE_1LF0LG_1LB0RD_0LH1LF_1RF---   (m = 4)
whose rules are the parent's with a general transfer factor m >= 2:
    R1 b -> m b + m;  R2 a = m b + m - 1;  R3 refill m b + m - 1 - k;  halt at k = m b + m - 3;
    R4 K(;0;b) -> K(P, 1^(m b + c4); a4; b4).

    python gen_kcoq.py TM OUT.v [--title T] [--report R]

Steps (all automatic; the script stops with an error if the machine does not fit):
 1. kfit.fit(TM): fits the rules from literal probes and checks that they are the m-template above.
 2. END4b: literal probe of 0^inf 1 1 C> 0 (10)^i, fitted to  u (01)^(i+s) B>  (s >= 0).
 3. planner8.drive on TR1, TR2, ENTRY, LOOP, FINAL (kphases.py statements with m) and END4b -> Coq scripts.
 4. init: literal run from the blank tape to the first K configuration K(ds0; a0; b0) (digits nonzero, b0 >= 1).
 5. Fills kcoq_template.v.in.
Compile and check with ..\\..\\proofs\\check.py (copy OUT.v there first).
"""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import planner8 as pl
from planner8 import drive, BLANK
from coqgen_util import script_to_coq, crossing_lemma, table
from kphases import phases, coq_stmt, T10
from kfit import fit
from kfam import parse_at, run_from
from tmlit import Sim, ST


def fit_end4(tm):
    res = {}
    for i in range(3, 9):
        w = '11' + '0' + '10' * i
        s = Sim.from_word(tm, '0000' + w, 6, 'C')
        while s.steps < 200000:
            if not s.step():
                raise SystemExit('END4b probe halts at i=%d' % i)
            if parse_at(s) is not None:
                lo, hi = s.bounds()
                res[i] = ''.join(map(str, s.tape[lo:s.pos]))
                break
        else:
            raise SystemExit('END4b probe: no K configuration at i=%d' % i)
    fits = set()
    for i, word in res.items():
        n = 0
        while word.endswith('01' * (n + 1)):
            n += 1
        fits.add((word[:len(word) - 2 * n], n - i))
    if len(fits) != 1:
        raise SystemExit('END4b does not fit u (01)^(i+s): %r' % res)
    u, s = fits.pop()
    if s < 0:
        raise SystemExit('END4b fit has s = %d < 0 (template needs s >= 0): u=%s' % (s, u))
    return u, s


def init_config(tm, N=10 ** 6):
    s = Sim(tm)
    r = run_from(s, N)
    if r[0] != 'K':
        raise SystemExit('no K configuration from the blank tape within %d steps: %r' % (N, r[:3]))
    return r[1], r[2]


def coq_list(ds_top_first):
    return '[' + '; '.join('%d%%nat' % d for d in reversed(ds_top_first)) + ']'


def gen(tm, outp, title=None, report=None):
    P, raw = fit(tm)
    need = ['m1', 'c1', 'm2', 'c2', 'b2', 'm3', 'c3', 'a3', 'b3', 'mh', 'ch', 'm4', 'c4', 'P', 'a4', 'b4']
    miss = [k for k in need if k not in P]
    if miss:
        raise SystemExit('rules do not fit (missing %s)' % miss)
    m = P['m1']
    tmpl = dict(m1=m, c1=m, m2=m, c2=m - 1, b2=1, m3=m, c3=m - 1, a3=1, b3=1, mh=m, ch=m - 3, m4=m)
    bad = [(k, P[k], v) for k, v in tmpl.items() if P[k] != v]
    if bad or m < 2 or P['b4'] < 1 or any(d == 0 for d in P['P']):
        raise SystemExit('not the m-template: %r (m=%d, R4 %r)' % (bad, m, (P['P'], P['a4'], P['b4'])))
    u, s = fit_end4(tm)
    print('m = %d; R4 -> (%s, 1^(%db%+d)); %d; %d; END4b -> %s (01)^(i+%d)' % (
        m, P['P'], m, P['c4'], P['a4'], P['b4'], u, s), file=sys.stderr)
    nsteps, (ds0, a0, b0) = init_config(tm)
    if b0 < 1 or any(d == 0 for d in ds0):
        raise SystemExit('first K configuration %r not usable' % ((ds0, a0, b0),))
    print('init: K(%s; %d; %d) after %d steps' % (ds0, a0, b0, nsteps), file=sys.stderr)

    pl.set_tm(tm)
    pl.LEMMAS.clear()
    ph = phases(m)
    left_end4 = [1, 0] * s + T10 + [int(c) for c in reversed(u)] + [BLANK]
    ph['END4b'] = (('C', [1, 1, 0, BLANK], [0] + T10 + [BLANK], '>'), ('B', left_end4, [BLANK], '>'))
    end4_coq = '1 >> 0 >> ' * s + '[1;0]^^i *> ' + ''.join('%s >> ' % c for c in reversed(u)) + 'const 0'
    bodies = []
    for pname in ['TR1', 'TR2', 'ENTRY', 'LOOP', 'FINAL', 'END4b']:
        if pname == 'END4b':
            stmt = ('forall i, (1 >> 1 >> 0 >> const 0) {{C}}> 0 >> [1;0]^^i *> const 0 -->+ '
                    '(%s) {{B}}> const 0' % end4_coq)
        else:
            stmt = coq_stmt(pname, m)
        start, target = ph[pname]
        script, _ = drive(pname, start, target, matchers=(), maxev=400, verbose=False)
        if script[-1][0] != 'end':
            raise SystemExit('planner did not reach the target of %s: %r' % (pname, script[-3:]))
        if len(script) == 1 and script[0][0] == 'end':
            tac = ['eapply progress_intro; [prove_step | simpl_tape].',
                   'do %d step. finish_norm.' % (script[0][1] - 1)]
        else:
            tac = script_to_coq(script, True)
        body = 'Lemma %s : %s.\nProof.\n  intros.\n' % (pname, stmt)
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
    tail = coq_list(P['P'])
    ctop = m + P['c4']
    if ctop < 0:
        raise SystemExit('Top needs b*m + %d ones' % ctop)
    top_digits = ','.join(str(d) for d in P['P'])
    subst = dict(
        title=title or 'BB(8) neighbor', report=report or 'see the investigation report', tm=tm, m=m,
        table=table(tm), crossings=crossings, phases='\n'.join(bodies),
        ones_m=''.join('1 >> ' for _ in range(m)),
        c2m=2 * m, c2m1=2 * m - 1, c2m2=2 * m - 2, c2m3=2 * m - 3, c2m4=2 * m - 4,
        ctop=ctop, tail=tail, a4=P['a4'], b4=P['b4'],
        top_comment='Kc (1^(%d b0 + %d) ++ %s) %d %d (digits %s,1,...,1)' % (m, ctop, tail, P['a4'], P['b4'], top_digits),
        end4_comment='0^inf %s (01)^(i+%d)' % (' '.join(u), s),
        init_comment='Kc %s %d %d after %d steps' % (coq_list(ds0), a0, b0, nsteps),
        ds0=coq_list(ds0), a0=a0, b0=b0, b0m1=b0 - 1, nsteps=nsteps)
    text = open(os.path.join(HERE, 'kcoq_template.v.in')).read() % subst
    open(outp, 'w', newline='\n').write(text)
    print('wrote', outp, file=sys.stderr)


def main():
    a = sys.argv
    title = a[a.index('--title') + 1] if '--title' in a else None
    report = a[a.index('--report') + 1] if '--report' in a else None
    gen(a[1], a[2], title, report)


if __name__ == '__main__':
    main()
