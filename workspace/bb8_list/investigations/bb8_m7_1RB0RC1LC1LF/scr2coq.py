import planner8 as pl
from coqgen_util import cl

def script_to_coq2(script):
    out = []
    ops = list(script)
    pre = []
    if ops[0] == ('steps', 0) and ops[1][0] == 'align':
        kind, x0, xs, cnt = ops[1][1]
        c = pl.cnt_str(cnt)
        assert c.isidentifier(), c
        pre.append('rewrite (align_lpow %d %s _ %s). simpl app.' % (x0, cl(xs), c))
        ops = ops[2:]
    first = True
    i = 0
    while i < len(ops):
        op = ops[i]
        if op[0] == 'steps':
            nxt = ops[i + 1]
            exact = nxt[0] == 'lemma'
            if first:
                if op[1] == 0:
                    raise RuntimeError('progress phase must start with a literal step')
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
                    out.append('rewrite (align_lpow %d %s _ _). simpl app.' % (x0, cl(xs)))
                else:
                    out.append('rewrite (align_lpow_const %d %s _). simpl app.' % (x0, cl(xs)))
            else:
                raise RuntimeError('unexpected op %r' % (nxt,))
            i += 2
        elif op[0] == 'end':
            if first:
                out.append('start_progress.')
                first = False
            else:
                out.append('do %d step. finish_norm.' % op[1])
            i += 1
        else:
            raise RuntimeError('stuck: %r' % (op,))
    return pre + out

