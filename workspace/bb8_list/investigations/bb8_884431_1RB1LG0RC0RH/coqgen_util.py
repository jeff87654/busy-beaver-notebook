"""script_to_coq, crossing_lemma and table, copied unchanged from ../bb8_076450_1RB1LE0LC1RE/gen_coq.py."""
import planner8 as pl


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
                out.append('eapply progress_intro; [prove_step | simpl_tape].')
                first = False
                out.append('do %d step. finish_norm.' % (op[1] - 1))
            else:
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

