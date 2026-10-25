"""Generate the busycoq HALTING proof for 1RB0LG_0LC0RH_---1LD_0RD1LE_1RF0LC_1RG1LG_1LA1LF_1RA1RH.
The six rule phases are planned by planner8.py (mirrors busycoq's [execute] on symbolic tapes);
the X/Y-level lemmas, the iteration lemmas and the arithmetic are fixed text (coq_tail.v).

Usage: python gen_halt.py coq/BB8_76450_1RB0LG_0LC0RH_halt.v
"""
import sys
from pathlib import Path
import planner8 as pl
from planner8 import drive
from plan_phases import PHASES, TM

HERE = Path(__file__).resolve().parent


def cl(t):
    return '[' + ';'.join(map(str, t)) + ']'


STMT = {
    'P1': ('+', 'forall i r, const 0 {{A}}> 0 >> 1 >> [1;1]^^i *> 0 >> 1 >> r -->+\n  '
                'const 0 {{A}}> 0 >> 1 >> [1;1]^^(S (S i)) *> 0 >> r'),
    'P2': ('+', 'forall i r, const 0 {{A}}> 0 >> 1 >> [1;1]^^i *> 0 >> 0 >> 1 >> 0 >> 1 >> 1 >> r -->+\n  '
                'const 0 {{A}}> 0 >> 1 >> 0 >> [1;1]^^(S (S i)) *> 1 >> 0 >> 1 >> r'),
    'P3': ('+', 'forall i, const 0 {{A}}> 0 >> 1 >> [1;1]^^i *> 0 >> 0 >> 1 >> const 0 -->+\n  '
                'const 0 {{A}}> 0 >> 1 >> [1;1]^^(S (S (S (S i)))) *> const 0'),
    'P4': ('+', 'forall k, const 0 {{A}}> 0 >> [1;1;1]^^(S k) *> const 0 -->+\n  '
                'const 0 {{A}}> 0 >> 1 >> 0 >> 1 >> 1 >> 1 >> 1 >> 1 >> 0 >> 1 >> [0;1;1]^^k *> const 0'),
    'P5': ('+', 'forall k, const 0 {{A}}> 0 >> 1 >> [1;1;1]^^(S (S (S k))) *> const 0 -->+\n  '
                'const 0 {{A}}> 0 >> 1 >> [1;1]^^8 *> 0 >> 1 >> 1 >> 1 >> 0 >> 1 >> [0;1;1]^^k *> const 0'),
    'P6': ('*', 'forall k, const 0 {{A}}> 0 >> 1 >> 1 >> [1;1;1]^^k *> const 0 -->*\n  '
                '1 >> const 0 {{C}}> 0 >> [0;1;1]^^(S k) *> const 0'),
}


def script_to_coq(script, rel):
    """Same translation as bb8_076450_1RB0LG0RC1RG/gen_coq.py."""
    out = []
    first = True
    i = 0
    while i < len(script):
        op = script[i]
        if op[0] == 'steps':
            n = op[1]
            nxt = script[i + 1]
            if first and rel == '+':
                if n == 0:
                    raise RuntimeError('-->+ lemma starting with a non-step')
                out.append('start_progress.')
            else:
                out.append('execute.')
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
            else:
                raise RuntimeError('unexpected op %r' % (nxt,))
            i += 2
        elif op[0] == 'end':
            n = op[1]
            if first and rel == '+':
                out.append('start_progress.' if n > 0 else 'FAIL')
                first = False
                out.append('finish_norm.')
            else:
                out.append('do %d step. finish_norm.' % n)
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


def main():
    outp = sys.argv[1]
    pl.set_tm(TM)
    pl.LEMMAS.clear()
    bodies = []
    for name, start, target in PHASES:
        rel, stmt = STMT[name]
        script, _ = drive(name, start, target, maxev=400, verbose=False)
        tac = script_to_coq(script, rel)
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
    head = (HERE / 'coq_head.v').read_text(encoding='utf-8')
    tail = (HERE / 'coq_tail.v').read_text(encoding='utf-8')
    text = head.replace('%(tm)s', TM).replace('%(table)s', table(TM))
    for nm in sorted(pl.LEMMAS):
        text += crossing_lemma(nm, pl.LEMMAS[nm]) + '\n'
    text += '(** ** Rule phases (scripts generated by the planner) *)\n\n'
    text += '\n'.join(bodies)
    text += tail
    open(outp, 'w', newline='\n').write(text)
    print('wrote', outp, 'with', len(pl.LEMMAS), 'crossing lemmas', file=sys.stderr)


if __name__ == '__main__':
    main()
