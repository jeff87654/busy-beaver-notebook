"""Generate a busycoq HALTING proof for 1RB1LG_1RC0RE_1LD1LC_1LA0LD_1LB1RF_1RC1LG_---0LH_1RA1LF
(and its A1 variants) from planner8 runs.

Usage: python gen_halt.py [main|a1LE|a1RH] out.v
The fixed parts of the file are cal_header.v.in and cal_tail.v.in (Python %-templates).
"""
import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive

MACHINES = {"main": "1RB0LF_1RC0RE_1LD1LC_1LA0LD_1LB1RA_1RG1LG_0LH0RD_---1RF"}
ONE2 = (1, 1)
ONE6 = (1,) * 6
Z6 = (0, 1, 1, 0, 1, 1)
H6 = (1, 1, 0, 1, 1, 0)


def cl(t):
    return '[' + ';'.join(map(str, t)) + ']'


def sweepB(cfg):
    """stuck at B> (blk)^n 1 ... with blk all ones: align, then apply sweepB2/sweepB6."""
    q, L, R, mode = cfg
    if q == 'B' and mode == '>' and pl.is_run(R[0]) and R[0][1] in (ONE2, ONE6) and len(R) > 1 and R[1] == 1:
        blk, cnt = R[0][1], R[0][2]
        c = pl.cnt_str(cnt)
        assert c.isidentifier()
        name = 'sweepB2' if blk == ONE2 else 'sweepB6'
        frag = 'rewrite (align_lpow 1 %s _ %s). simpl app. follow %s.' % (cl(blk[1:]), c, name)
        return (('B', pl.norm_side([R[0]] + L), R[1:], '>'), frag, name)
    return None


R = [V('r')]
A = {'a': 1}
Qv = {'q': 1}
P = {'p': 1}
Q2 = {'q': 2}
ONE6 = (1,) * 6
B6 = (1, 0, 0, 1, 0, 0)


def edgeH(cfg):
    q, L, Rr, mode = cfg
    return q == 'H' and mode == '<' and L == [BLANK]


PHASES = [
    ('O1', 'forall a r, const 0 {{A}}> 0 >> [1;1]^^a *> 1 >> 0 >> r -->* '
           'const 0 {{A}}> 0 >> [1;1]^^(S (S a)) *> 1 >> r',
     ('A', [BLANK], [0] + mkrun(ONE2, A) + [1, 0] + R, '>'),
     ('A', [BLANK], [0] + mkrun(ONE2, A, 2) + [1] + R, '>'), None),
    ('Erule', 'forall a r, const 0 {{A}}> 0 >> [1;1]^^a *> 1 >> 1 >> 0 >> 0 >> 1 >> r -->* '
          'const 0 {{A}}> 0 >> 1 >> 0 >> [0;0]^^a *> 1 >> 1 >> 1 >> 1 >> 1 >> r',
     ('A', [BLANK], [0] + mkrun(ONE2, A) + [1, 1, 0, 0, 1] + R, '>'),
     ('A', [BLANK], [0, 1, 0] + mkrun((0, 0), A) + [1] * 5 + R, '>'), None),
    ('Lrule', 'forall r, const 0 {{A}}> 0 >> 1 >> 0 >> 0 >> 1 >> r -->* '
              'const 0 {{A}}> 0 >> 1 >> 1 >> 1 >> 1 >> 1 >> 0 >> 1 >> r',
     ('A', [BLANK], [0, 1, 0, 0, 1] + R, '>'),
     ('A', [BLANK], [0, 1, 1, 1, 1, 1, 0, 1] + R, '>'), None),
    ('SW', 'forall p r, const 0 {{A}}> 0 >> [1;1]^^p *> 1 >> 1 >> 0 >> 0 >> 0 >> r -->* '
           '[1;1]^^p *> 1 >> const 0 <{{A}} 1 >> 0 >> 0 >> 0 >> 1 >> r',
     ('A', [BLANK], [0] + mkrun(ONE2, P) + [1, 1, 0, 0, 0] + R, '>'),
     ('A', pl.norm_side(mkrun(ONE2, P) + [1, BLANK]), [1, 0, 0, 0, 1] + R, '<'), None),
    ('Z4L', 'forall q r, 1 >> 1 >> %s^^q *> 1 >> const 0 <{{A}} 1 >> 0 >> 0 >> 0 >> 1 >> r -->* '
            'const 0 {{A}}> 0 >> %s^^q *> 1 >> 0 >> 0 >> 1 >> 0 >> 0 >> 0 >> 1 >> r' % (cl(ONE6), cl(B6)),
     ('A', [1, 1] + mkrun(ONE6, Qv) + [1, BLANK], [1, 0, 0, 0, 1] + R, '<'),
     ('A', [BLANK], [0] + mkrun(B6, Qv) + [1, 0, 0, 1, 0, 0, 0, 1] + R, '>'), None),
    ('Z2L', 'forall q r, 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> %s^^q *> 1 >> const 0 <{{A}} 1 >> 0 >> 0 >> 0 >> 1 >> r -->* '
            'const 0 {{A}}> 0 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> %s^^q *> 1 >> 0 >> 0 >> 1 >> 0 >> 0 >> 0 >> 1 >> r' % (cl(ONE6), cl(B6)),
     ('A', [1] * 6 + mkrun(ONE6, Qv) + [1, BLANK], [1, 0, 0, 0, 1] + R, '<'),
     ('A', [BLANK], [0] + [1] * 7 + mkrun(B6, Qv) + [1, 0, 0, 1, 0, 0, 0, 1] + R, '>'), None),
    ('Z0L', 'forall q r, 1 >> 1 >> 1 >> 1 >> %s^^q *> 1 >> const 0 <{{A}} 1 >> 0 >> 0 >> 0 >> 1 >> r -->* '
            'const 0 <{{H}} 0 >> 1 >> [0;1;0;0;1;0]^^q *> 0 >> 1 >> 0 >> 0 >> 1 >> 0 >> 0 >> 0 >> 1 >> r' % cl(ONE6),
     ('A', [1] * 4 + mkrun(ONE6, Qv) + [1, BLANK], [1, 0, 0, 0, 1] + R, '<'),
     ('H', [BLANK], [0, 1] + mkrun((0, 1, 0, 0, 1, 0), Qv) + [0, 1, 0, 0, 1, 0, 0, 0, 1] + R, '<'), edgeH),
]


def script_to_coq(script):
    out = []
    i = 0
    while i < len(script):
        op = script[i]
        if op[0] == 'steps':
            nxt = script[i + 1]
            out.append('execute.')
            if nxt[0] == 'cross':
                out.extend(['follow %s.' % nxt[1]] * nxt[2])
            elif nxt[0] == 'align':
                kind, x0, xs, cnt = nxt[1]
                c = pl.cnt_str(cnt)
                if '+' in c or not c.isidentifier():
                    raise RuntimeError('align on composite count %r' % (cnt,))
                if kind == 'ALIGN':
                    out.append('rewrite (align_lpow %d %s _ %s). simpl app.' % (x0, cl(xs), c))
                else:
                    out.append('rewrite (align_lpow_const %d %s %s). simpl app.' % (x0, cl(xs), c))
            elif nxt[0] == 'lemma':
                out.append(nxt[1])
            else:
                raise RuntimeError('unexpected op %r' % (nxt,))
            i += 2
        elif op[0] == 'end':
            out.append('do %d step. finish_norm.' % op[1])
            i += 1
        else:
            raise RuntimeError('stuck: %r' % (op,))
    return out


def crossing_lemma(name, lm):
    q, d, xs, ys, ctx = lm['q'], lm['dir'], lm['xs'], lm['ys'], lm['ctx']
    ctxs = ''.join('%d >> ' % c for c in ctx)
    if d == '>':
        stmt = 'forall n l r, %sl {{%s}}> %s^^n *> r -->* %s^^n *> %sl {{%s}}> r' % (ctxs, q, cl(xs), cl(ys), ctxs, q)
    else:
        stmt = 'forall n l r, %s^^n *> l <{{%s}} %sr -->* l <{{%s}} %s^^n *> %sr' % (cl(xs), q, ctxs, q, cl(ys), ctxs)
    return ('Lemma %s : %s.\nProof. induction n; intros. - finish. - execute. follow IHn. finish_norm. Qed.\n'
            % (name, stmt))


def table(tms):
    rows = []
    for qi, ch in enumerate(tms.split('_')):
        q = 'ABCDEFGH'[qi]
        ents = []
        for s in (0, 1):
            e = ch[3 * s:3 * s + 3]
            if e == '---':
                ents.append('| %s, %d => None' % (q, s))
            else:
                ents.append('| %s, %d => Some (%s, %s, %s)' % (q, s, e[0], e[1], e[2]))
        rows.append('  ' + '  '.join('%-24s' % x for x in ents).rstrip())
    return '\n'.join(rows)


def init_steps(tms):
    """steps from the blank tape to 0^inf A>0 1^10 0^inf (literal simulation)."""
    from lit import Sim
    s = Sim(tms, size=4096)
    for _ in range(1000):
        s.step()
        if s.state == 0 and s.tape[s.pos] == 0 and not any(s.tape[:s.pos]) and \
                ''.join(map(str, s.tape[s.pos + 1:s.pos + 13])) == '111111111100' and not any(s.tape[s.pos + 13:]):
            return s.steps
    raise RuntimeError('init config not reached')


def main():
    which, outp = sys.argv[1], sys.argv[2]
    tms = MACHINES[which]
    pl.set_tm(tms)
    pl.LEMMAS.clear()
    bodies = []
    for name, stmt, start, target, stop in PHASES:
        pl.STOP_ANY = stop
        script, _ = drive(name, start, target, matchers=(sweepB,), maxev=400, verbose=(len(sys.argv) > 3))
        tac = script_to_coq(script)
        body = 'Lemma %s : %s.\nProof.\n  intros.\n' % (name, stmt)
        line = '  '
        for t in tac:
            if len(line) + len(t) > 100:
                body += line.rstrip() + '\n'
                line = '  '
            line += t + ' '
        body += line.rstrip() + '\nQed.\n'
        bodies.append(body)
        nsteps = sum(o[1] for o in script if o[0] in ('steps', 'end'))
        print('%-6s literal steps %4d, ops %d' % (name, nsteps, len(script)), file=sys.stderr)
    subst = dict(tm=tms, table=table(tms), init=init_steps(tms), which=which)
    text = open('cal_header.v.in').read() % subst
    for nm in sorted(pl.LEMMAS):
        text += crossing_lemma(nm, pl.LEMMAS[nm]) + '\n'
    text += '(** ** Phase lemmas (scripts generated by the planner) *)\n\n'
    text += '\n'.join(bodies)
    text += open('cal_tail.v.in').read() % subst
    open(outp, 'w', newline='\n').write(text)
    print('wrote', outp, 'with', len(pl.LEMMAS), 'crossing lemmas', file=sys.stderr)


if __name__ == '__main__':
    main()
