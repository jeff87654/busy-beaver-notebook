"""Generate the busycoq HALTING proof for 1RB1RH_0LC0LF_1LE1LD_0RE1LF_1RA1RD_0LG0LE_1LB1LF_1RF---
from planner8 runs (planner8.py copied unchanged from ../bb8_076450_1RB1LG1RC0RE).

Usage: python gen_halt.py out.v [--verbose]
Fixed parts: halt_header.v.in and halt_tail.v.in (Python %-templates).
"""
import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive

TMS = "1RB1RH_0LC0LF_1LE1LD_0RE1LF_1RA1RD_0LG0LE_1LB1LF_1RF---"
P = (0, 1)
l = [V('l')]
PHASES = [
    ('Trule', 'forall b l, [0;1]^^b *> 1 >> 0 >> 1 >> l {{E}}> const 0 -->* '
              '[0;1]^^(S (S (S b))) *> 1 >> l {{E}}> const 0',
     ('E', mkrun(P, {'b': 1}) + [1, 0, 1] + l, [BLANK], '>'),
     ('E', mkrun(P, {'b': 1}, 3) + [1] + l, [BLANK], '>')),
    ('Rrule', 'forall n l, [0;1]^^(S n) *> 1 >> 1 >> l {{E}}> const 0 -->* '
              '[0;1]^^4 *> 1 >> [0;1]^^n *> l {{E}}> const 0',
     ('E', mkrun(P, {'n': 1}, 1) + [1, 1] + l, [BLANK], '>'),
     ('E', mkrun(P, {}, 4) + [1] + mkrun(P, {'n': 1}) + l, [BLANK], '>')),
    ('L1', 'forall b, [0;1]^^b *> 1 >> const 0 {{E}}> const 0 -->* '
           '[0;1]^^(S (S (S b))) *> const 0 {{E}}> const 0',
     ('E', mkrun(P, {'b': 1}) + [1, BLANK], [BLANK], '>'),
     ('E', mkrun(P, {'b': 1}, 3) + [BLANK], [BLANK], '>')),
    ('ROraw', 'forall j, [0;1;0;1]^^j *> 0 >> 1 >> const 0 {{E}}> const 0 -->* '
              '[0;1]^^2 *> 1 >> 1 >> [0;1;1;1]^^(S j) *> const 0 {{E}}> const 0',
     ('E', mkrun((0, 1, 0, 1), {'j': 1}) + [0, 1, BLANK], [BLANK], '>'),
     ('E', mkrun(P, {}, 2) + [1, 1] + mkrun((0, 1, 1, 1), {'j': 1}, 1) + [BLANK], [BLANK], '>')),
    ('REraw', 'forall j, [0;1;0;1]^^(S j) *> const 0 {{E}}> const 0 -->* '
              '1 >> 1 >> [0;1;1;1]^^(S (S j)) *> const 0 {{H}}> 1 >> const 0',
     ('E', mkrun((0, 1, 0, 1), {'j': 1}, 1) + [BLANK], [BLANK], '>'),
     ('H', [1, 1] + mkrun((0, 1, 1, 1), {'j': 1}, 2) + [BLANK], [1, BLANK], '>')),
]


def cl(t):
    return '[' + ';'.join(map(str, t)) + ']'


def script_to_coq(script):
    out = []
    i = 0
    while i < len(script):
        op = script[i]
        if op[0] == 'steps':
            nxt = script[i + 1]
            if op[1]:
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
    """steps from the blank tape to Zc 1 2 = 0^inf 1110 11 1010 E> 0^inf (literal simulation)."""
    from lit import Sim
    s = Sim(tms, size=4096)
    for _ in range(1000):
        s.step()
        if s.state == 4 and s.tape[s.pos] == 0 and not any(s.tape[s.pos:]):
            w = ''.join(map(str, s.tape[:s.pos])).lstrip('0')
            if w == '1110111010':
                return s.steps
    raise RuntimeError('init config not reached')


def main():
    outp = sys.argv[1]
    verbose = '--verbose' in sys.argv
    pl.set_tm(TMS)
    pl.LEMMAS.clear()
    bodies = []
    for name, stmt, start, target in PHASES:
        script, _ = drive(name, start, target, maxev=400, verbose=verbose)
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
    subst = dict(tm=TMS, table=table(TMS), init=init_steps(TMS))
    text = open('halt_header.v.in').read() % subst
    for nm in sorted(pl.LEMMAS):
        text += crossing_lemma(nm, pl.LEMMAS[nm]) + '\n'
    text += '(** ** Phase lemmas (scripts generated by the planner) *)\n\n'
    text += '\n'.join(bodies)
    text += open('halt_tail.v.in').read() % subst
    open(outp, 'w', newline='\n').write(text)
    print('wrote', outp, 'with', len(pl.LEMMAS), 'crossing lemmas', file=sys.stderr)


if __name__ == '__main__':
    main()
