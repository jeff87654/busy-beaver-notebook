"""Generate the busycoq NON-HALTING proof for 1RB1LF_1RC1RE_1RD0LG_0RE1LD_1LA0LC_0RG1LA_---0LH_1RA1LC
from planner8 runs (phases P6, C6, R6 defined in explore.py).

Usage: python gen_coq.py out.v
Fixed parts: coq_head.v.in and coq_tail.v.in (Python %-templates).
"""
import sys
import planner8 as pl
from planner8 import drive
import explore as ex

TM = "1RB1RD_1LC1LF_1RH1RA_1LE1LG_0RB1LE_1RC0LG_1RA0LB_---1RF"
CC = 'const 0 {{C}}> '
PHASES = [
    # name, progress (-->+)?, statement
    ('P1', False, 'forall a b r, ' + CC + '0 >> D^^a *> 1 >> 0 >> 1 >> 0 >> 0 >> D^^b *> 1 >> r -->* '
                  + CC + '0 >> 1 >> 0 >> 0 >> 1 >> 0 >> 0 >> D^^a *> 1 >> 0 >> D^^b *> 1 >> r'),
    ('P2', True, 'forall a k r, ' + CC + '0 >> D^^a *> 1 >> 0 >> 1 >> 1 >> 1 >> [1]^^k *> r -->+ '
                 + CC + '0 >> 1 >> 0 >> 0 >> 1 >> 0 >> D^^a *> 1 >> 0 >> 1 >> [1]^^k *> r'),
    ('Q1', False, 'forall a b r, ' + CC + '0 >> D^^a *> 1 >> 0 >> 1 >> 0 >> 0 >> D^^b *> 1 >> 0 >> 1 >> r -->* '
                  + CC + '0 >> 1 >> 0 >> 0 >> 1 >> 0 >> 0 >> D^^a *> 1 >> 0 >> D^^b *> 1 >> 0 >> 1 >> r'),
    ('Q2', False, 'forall a k r, ' + CC + '0 >> D^^a *> 1 >> 0 >> 1 >> 0 >> 1 >> [1]^^k *> r -->* '
                  + CC + '0 >> 1 >> 0 >> 0 >> 1 >> 0 >> 0 >> D^^a *> 1 >> [1]^^k *> r'),
    ('X1', False, 'forall a m r, ' + CC + '0 >> D^^a *> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> [1]^^m *> r -->* '
                  + CC + '0 >> 1 >> 0 >> 0 >> 1 >> 0 >> D^^a *> 1 >> 1 >> 1 >> 1 >> [1]^^m *> r'),
    ('X0', False, 'forall a, ' + CC + '0 >> 1 >> 0 >> 0 >> D^^a *> 1 >> 1 >> const 0 -->* '
                  + CC + '0 >> 1 >> 0 >> 0 >> 1 >> 0 >> 1 >> 0 >> 0 >> D^^a *> const 0'),
    ('P0', False, 'forall a b, ' + CC + '0 >> D^^a *> 1 >> 0 >> 1 >> 0 >> 0 >> 1 >> 0 >> 0 >> D^^b *> const 0 -->* '
                  + CC + '0 >> 1 >> 0 >> 0 >> 1 >> 0 >> 0 >> D^^a *> 1 >> 0 >> 1 >> 0 >> 0 >> D^^b *> const 0'),
    ('R0', False, 'forall a, ' + CC + '0 >> 1 >> 0 >> 0 >> D^^a *> 1 >> 0 >> 1 >> 0 >> 0 >> const 0 -->* '
                  + CC + '0 >> 1 >> 0 >> 0 >> 1 >> 0 >> 1 >> 1 >> [1;1;1]^^a *> 1 >> 1 >> 1 >> 1 >> 1 >> 1 >> const 0'),
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
            # before a hand-written sweep ('lemma') the head is not stuck yet, so step exactly op[1] times
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
    return 58


def main():
    outp = sys.argv[1]
    pl.set_tm(TM)
    pl.LEMMAS.clear()
    bodies = []
    for name, progress, stmt in PHASES:
        start, target = ex.PH[name]
        script, _ = drive(name, start, target, matchers=(), maxev=400, verbose=False)
        tac = script_to_coq(script, progress)
        body = 'Lemma %s : %s.\nProof.\n  intros.\n' % (name, stmt.replace('D^^', '[1;0;0]^^'))
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
