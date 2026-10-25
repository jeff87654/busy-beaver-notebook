"""Generate the busycoq proof for 1RB0RF_1RC0LF_0RD0RB_1LE1LG_0LA0LC_0LD1RH_1RA1LC_1RF---.

usage: python gen_coq.py out.v [phases-only]

The phase lemmas (T1, P0raw ... Y1raw) are proved by scripts that planner8.py (symbolic execution mirroring
busycoq's [execute], extended by pext.py with sweeps whose small context travels with the head) writes.
Hand-written parts: coq_head.v.in, coq_tloop.v.in (transfer loop), coq_tail.v.in (rules, levels, arithmetic,
non-halting)."""
import sys
import planner8 as P
import pext
import phases as PHS

TM = PHS.TM


def cl(t):
    return '[' + ';'.join(map(str, t)) + ']'


def cnt_coq(c):
    assert len(c) == 1 and c[0][1] == 1, c
    return c[0][0]


def side_coq(side):
    out = []
    for t in side:
        if isinstance(t, int):
            out.append('%d >> ' % t)
        elif t == P.BLANK:
            out.append('const 0')
        elif t[0] == 'VAR':
            out.append(t[1])
        else:
            out.append('%s^^%s *> ' % (cl(t[1]), cnt_coq(t[2])))
    return ''.join(out)


def paren(s):
    return s if s == 'const 0' or s.isidentifier() else '(' + s + ')'


def cfg_coq(cfg):
    q, L, R, mode = cfg
    if mode == '>':
        return '%s {{%s}}> %s' % (paren(side_coq(L)), q, paren(side_coq(R)))
    return '%s <{{%s}} %s' % (paren(side_coq(L)), q, paren(side_coq(R)))


def vars_of(cfg):
    q, L, R, mode = cfg
    vs = []
    for t in L + R:
        if P.is_run(t):
            v = cnt_coq(t[2])
            if v not in vs:
                vs.append(v)
        elif isinstance(t, tuple) and t[0] == 'VAR' and t[1] not in vs:
            vs.append(t[1])
    return vs


def script_to_coq(script, plus):
    out = []
    first = True
    for op in script:
        if op[0] == 'steps':
            n = op[1]
            if first and plus:
                assert n >= 1
                out.append('step1.')
                n -= 1
            first = False
            if n:
                out.append('do %d step.' % n)
            continue
        elif op[0] == 'cross':
            out.append('follow %s.' % op[1])
        elif op[0] == 'align':
            kind, x0, xs, cnt = op[1]
            c = cnt_coq(cnt)
            if kind == 'ALIGN':
                out.append('rewrite (align_lpow %d %s _ %s). simpl app.' % (x0, cl(xs), c))
            else:
                out.append('rewrite (align_lpow_const %d %s %s). simpl app.' % (x0, cl(xs), c))
        elif op[0] == 'lemma':
            out.append(op[1])
        elif op[0] == 'end':
            assert not first
            if op[1]:
                out.append('do %d step.' % op[1])
            out.append('finish_norm.')
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


ORDER = ['T1', 'P0raw', 'P1raw', 'P2raw', 'Q0raw', 'Q1raw', 'EP0p2raw', 'EQ0p1raw', 'EQ1p1raw', 'EQ5p2raw',
         'Y0raw', 'Y1raw']


def phase_bodies():
    bodies = {}
    for nm in ORDER:
        start, tgt = PHS.PH[nm]
        script, _ = P.drive(nm, start, tgt, matchers=[PHS.m_tloop, pext.m_concrete, pext.m_sweep], maxev=400, verbose=False)
        assert script[-1][0] == 'end', (nm, script[-1])
        vs = vars_of(start)
        for v in vars_of(tgt):
            if v not in vs:
                vs.append(v)
        rel = '-->*' if nm == 'T1' else '-->+'
        stmt = 'forall %s, %s %s %s' % (' '.join(vs), cfg_coq(start), rel, cfg_coq(tgt))
        tac = script_to_coq(script, rel == '-->+')
        body = 'Lemma %s : %s.\nProof.\n  intros.\n' % (nm, stmt)
        line = '  '
        for t in tac:
            if len(line) + len(t) > 110:
                body += line.rstrip() + '\n'
                line = '  '
            line += t + ' '
        body += line.rstrip() + '\nQed.\n'
        nsteps = sum(o[1] for o in script if o[0] in ('steps', 'end'))
        print('%-9s literal steps %5d, ops %d' % (nm, nsteps, len(script)), file=sys.stderr)
        bodies[nm] = body
    return bodies


def main():
    outp = sys.argv[1]
    only = len(sys.argv) > 2
    P.set_tm(TM)
    P.LEMMAS.clear()
    pext.SWEEPS.clear()
    bodies = phase_bodies()
    text = open('coq_head.v.in').read()
    text += ('\n(** ** Crossing a run of blocks (generated; blocks in stream order, nearest the head first;\n'
             '    the literal cells before [l] / [r] are context that is read and restored) *)\n\n')
    for nm in sorted(P.LEMMAS):
        text += crossing_lemma(nm, P.LEMMAS[nm]) + '\n'
    text += '(** ** Sweeps whose small context travels with the head (generated) *)\n\n'
    for nm in sorted(pext.SWEEPS):
        text += pext.sweep_lemma(nm, pext.SWEEPS[nm]) + '\n'
    text += '(** ** One transfer pass and the transfer loop *)\n\n' + bodies['T1'] + '\n'
    text += open('coq_tloop.v.in').read() + '\n'
    text += '(** ** Phase lemmas (scripts generated by the planner) *)\n\n'
    for nm in ORDER[1:]:
        text += bodies[nm] + '\n'
    if not only:
        text += open('coq_tail.v.in').read()
    open(outp, 'w', newline='\n').write(text)
    print('wrote', outp, len(P.LEMMAS), 'crossings', len(pext.SWEEPS), 'sweeps', file=sys.stderr)


if __name__ == '__main__':
    main()
