"""Generate the busycoq NON-HALTING proof for 1RB1LE_1RC1LE_0RD1RE_1LA---_1LG1RF_0LH0LG_1RH1LB_0RA0RG
from planner8 runs (phases IN, S5, S4, Z0).

Usage: python gen_coq.py out.v
Fixed parts: coq_head.v.in and coq_tail.v.in (Python %-templates).
Adapted from ../bb8_076450_1RB1LE0LC1RE/gen_coq.py (script_to_coq, crossing_lemma, table unchanged).
"""
import sys
import planner8 as pl
from planner8 import drive, mkrun, V, BLANK

TM = "1RB1LE_1RC1LE_0RD1RE_1LA---_1LG1RF_0LH0LG_1RH1LB_0RA0RG"
T4 = (1, 0, 1, 0)
K = {'k': 1}
B = {'b': 1}
R = [V('r')]


def E(side):
    return ('E', [BLANK], side, '>')


# planner configurations (must match the Coq statements in PHASES token for token)
PH = {
    'IN': (E([0, 1, 1, 0] + mkrun(T4, K) + [0, 1] + mkrun((0, 1), B) + R),
           E([0, 1, 1, 0, 1, 0, 1, 0] + mkrun(T4, K) + mkrun((0, 1), B) + R)),
    'S5': (E([0, 1, 1, 0] + mkrun(T4, K) + [1] * 5 + R),
           E([0, 1] + [1, 0] * 5 + [0, 1, 0, 1] + mkrun((0, 1, 0, 1), K) + R)),
    'S4': (E([0, 1, 1, 0] + mkrun(T4, K) + [1] * 4 + [BLANK]),
           E([0, 1] + [1, 0] * 5 + [0, 1] + mkrun((0, 1, 0, 1), K) + [BLANK])),
    'Z0': (E([0, 1, 1, 0] + mkrun(T4, K) + [BLANK]),
           E([0, 1] + [1, 0] * 3 + [1] * 5 + mkrun((1, 1, 1, 1), K) + [BLANK])),
}


def ones(k):
    return '1 >> ' * k


PRE = 'const 0 {{E}}> 0 >> 1 >> 1 >> 0 >> [1;0;1;0]^^k *> '
PHASES = [
    ('IN', True, 'forall k b r, ' + PRE + '0 >> 1 >> [0;1]^^b *> r -->+ '
     'const 0 {{E}}> 0 >> 1 >> 1 >> 0 >> 1 >> 0 >> 1 >> 0 >> [1;0;1;0]^^k *> [0;1]^^b *> r'),
    ('S5', True, 'forall k r, ' + PRE + ones(5) + 'r -->+ '
     'const 0 {{E}}> 0 >> 1 >> ' + '1 >> 0 >> ' * 5 + '0 >> 1 >> 0 >> 1 >> [0;1;0;1]^^k *> r'),
    ('S4', True, 'forall k, ' + PRE + ones(4) + 'const 0 -->+ '
     'const 0 {{E}}> 0 >> 1 >> ' + '1 >> 0 >> ' * 5 + '0 >> 1 >> [0;1;0;1]^^k *> const 0'),
    ('Z0', True, 'forall k, ' + PRE + 'const 0 -->+ '
     'const 0 {{E}}> 0 >> 1 >> ' + '1 >> 0 >> ' * 3 + ones(5) + '[1;1;1;1]^^k *> const 0'),
]


def cl(t):
    return '[' + ';'.join(map(str, t)) + ']'


def script_to_coq(script, progress):
    out = []
    i = 0
    first = True
    while i < len(script):
        op = script[i]
        if op[0] == 'steps':
            nxt = script[i + 1]
            exact = nxt[0] == 'lemma'
            if first and progress:
                if op[1] == 0:
                    raise RuntimeError('progress phase must start with a literal step')
                out.append('eapply progress_intro; [prove_step | simpl_tape].' if exact else 'start_progress.')
                if exact and op[1] > 1:
                    out.append('do %d step.' % (op[1] - 1))
            else:
                out.append(('do %d step.' % op[1]) if exact else 'execute.')
            first = False
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
            if first and progress:
                out.append('start_progress.')
                first = False
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
    """steps from the blank tape to Fa 0 1 (1111) = 0^inf E>0 1 1 0 1 0 1 0 1^9 0^inf (literal simulation)."""
    from lit import Sim
    s = Sim(tms, size=4096)
    want = [1, 1, 0, 1, 0, 1, 0] + [1] * 9
    for _ in range(10000):
        if not s.step():
            raise RuntimeError('halted')
        if s.state == 4 and s.tape[s.pos] == 0 and not any(s.tape[:s.pos]) and \
                list(s.tape[s.pos + 1:s.pos + 1 + len(want)]) == want and not any(s.tape[s.pos + 1 + len(want):]):
            return s.steps
    raise RuntimeError('init config not reached')


def main():
    outp = sys.argv[1]
    pl.set_tm(TM)
    pl.LEMMAS.clear()
    bodies = []
    for name, progress, stmt in PHASES:
        start, target = PH[name]
        script, _ = drive(name, start, target, matchers=(), maxev=400, verbose=False)
        tac = script_to_coq(script, progress)
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
        print('%-4s literal steps %4d, ops %d' % (name, nsteps, len(script)), file=sys.stderr)
    subst = dict(tm=TM, table=table(TM), init=init_steps(TM))
    text = open('coq_head.v.in').read() % subst
    for nm in sorted(pl.LEMMAS):
        text += crossing_lemma(nm, pl.LEMMAS[nm]) + '\n'
    text += '(** ** Phase lemmas (scripts generated by the planner) *)\n\n'
    text += '\n'.join(bodies)
    text += open('coq_tail.v.in').read() % subst
    open(outp, 'w', newline='\n').write(text)
    print('wrote', outp, 'with', len(pl.LEMMAS), 'crossing lemmas', file=sys.stderr)


if __name__ == '__main__':
    main()
