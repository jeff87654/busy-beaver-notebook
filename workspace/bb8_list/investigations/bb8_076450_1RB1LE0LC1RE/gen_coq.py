"""Generate the busycoq NON-HALTING proof for 1RB1LE_0LC1RE_0RA0LD_1RA1LC_1LF0RC_1RG1LC_0LH1LG_1LB---
from planner8 runs (phases R1, R3, Y5, Y4, Y3, Y1 defined in explore.py).

Usage: python gen_coq.py out.v
Fixed parts: coq_head.v.in and coq_tail.v.in (Python %-templates).
Adapted from ../bb8_076450_1RB1LF1RC1RE/gen_coq.py (script_to_coq and crossing_lemma unchanged).
"""
import sys
import planner8 as pl
from planner8 import drive
import explore as ex

TM = "1RB1LE_0LC1RE_0RA0LD_1RA1LC_1LF0RC_1RG1LC_0LH1LG_1LB---"
S3 = '[1;1;1]'
S6 = '[1;1;1;1;1;1]'
Z6 = '[0;1;0;1;0;1]'


def ones(k):
    return '1 >> ' * k


PHASES = [
    # name, progress (-->+)?, statement
    ('R1', True, 'forall m r, const 0 {{G}}> 0 >> %s^^m *> %s0 >> 1 >> r -->+ '
                 'const 0 {{G}}> 0 >> %s^^m *> %sr' % (S3, ones(3), S3, ones(9))),
    ('R3', True, 'forall j r, const 0 {{G}}> 0 >> %s^^j *> %s0 >> r -->+ '
                 'const 0 {{G}}> 0 >> 1 >> 1 >> 1 >> %s^^j *> 0 >> 1 >> 0 >> 1 >> 0 >> 1 >> 0 >> 1 >> 1 >> r'
     % (S6, ones(5), Z6)),
    ('Y5', True, 'forall j, const 0 {{G}}> 0 >> %s^^j *> %sconst 0 -->+ '
                 'const 0 {{G}}> 0 >> 1 >> 1 >> 1 >> %s^^j *> 0 >> 1 >> 0 >> 1 >> 0 >> 1 >> 0 >> 1 >> 1 >> const 0'
     % (S6, ones(5), Z6)),
    ('Y4', True, 'forall j, const 0 {{G}}> 0 >> %s^^j *> %sconst 0 -->+ '
                 'const 0 {{G}}> 0 >> 1 >> 1 >> 1 >> %s^^j *> 0 >> 1 >> 0 >> 1 >> 0 >> 1 >> const 0'
     % (S6, ones(4), Z6)),
    ('Y3', True, 'forall j, const 0 {{G}}> 0 >> %s^^j *> %sconst 0 -->+ '
                 'const 0 {{G}}> 0 >> %s%s^^j *> 0 >> 1 >> 1 >> 1 >> const 0'
     % (S6, ones(3), ones(11), Z6)),
    ('Y1', True, 'forall j, const 0 {{G}}> 0 >> %s^^j *> %sconst 0 -->+ '
                 'const 0 {{G}}> 0 >> %s%s^^j *> const 0'
     % (S6, ones(1), ones(11), Z6)),
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
    """steps from the blank tape to Y3 0 = 0^inf G>0 111 0^inf (literal simulation)."""
    from lit import Sim
    s = Sim(tms, size=4096)
    for _ in range(1000):
        s.step()
        if s.state == 6 and s.tape[s.pos] == 0 and not any(s.tape[:s.pos]) and \
                ''.join(map(str, s.tape[s.pos + 1:s.pos + 5])) == '1110' and not any(s.tape[s.pos + 4:]):
            return s.steps
    raise RuntimeError('init config not reached')


def main():
    outp = sys.argv[1]
    pl.set_tm(TM)
    pl.LEMMAS.clear()
    bodies = []
    for name, progress, stmt in PHASES:
        start, target = ex.PH[name]
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
