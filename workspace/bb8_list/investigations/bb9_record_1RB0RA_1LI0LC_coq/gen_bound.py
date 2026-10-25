"""Generate proofs/BB9_record_bound.v: exact score and lower bounds for the BB(9) record candidate.
  python gen_bound.py OUT.v"""
import sys
from pathlib import Path
from common import *
import mexp, gen_d2
from planner8 import is_run

TM_ROWS = TM.split('_')


def tm_table():
    lines = []
    for qi, row in enumerate(TM_ROWS):
        q = 'ABCDEFGHI'[qi]
        for s in (0, 1):
            e = row[3 * s:3 * s + 3]
            rhs = 'None' if e == '---' else 'Some (%s, %s, %s)' % (e[0], e[1], e[2])
            lines.append('tm (%s, %d) = %s' % (q, s, rhs))
    return '  ' + ' /\\\n  '.join(lines) + '.'


def list_expr(side):
    """Coq list (of Sym) for a side ending in BLANK (the part before const 0)."""
    parts, cur = [], []
    for t in side:
        if isinstance(t, int):
            cur.append(str(t))
        elif is_run(t):
            if cur:
                parts.append('[' + ';'.join(cur) + ']')
                cur = []
            for v, c in t[2]:
                e = v if c == 1 else '(%d * %s)' % (c, v)
                parts.append('[%s]^^%s' % (';'.join(map(str, t[1])), e))
        else:
            assert t == BLANK, t
            break
    if cur:
        parts.append('[' + ';'.join(cur) + ']')
    return ' ++ '.join(parts) if parts else '[]'


def ones_of(side):
    c, lin = 0, {}
    for t in side:
        if isinstance(t, int):
            c += t
        elif is_run(t):
            for v, a in t[2]:
                lin[v] = lin.get(v, 0) + sum(t[1]) * a
    return c, lin


def main(out):
    pl.LEMMAS.clear()
    tree = mexp.explore(gen_d2.TARGET, None, splits=0)
    assert tree.get('halt') and len(tree['items']) == 1 and not pl.LEMMAS
    _, ops, a, end = tree['items'][0]
    q, L, R, mode = end
    assert mode == '<' and isinstance(L[0], int)
    head, Ltail = L[0], L[1:]
    c1, l1 = ones_of(Ltail)
    c2, l2 = ones_of(R)
    lin = dict(l1)
    for k, v in l2.items():
        lin[k] = lin.get(k, 0) + v
    const = c1 + c2 + head
    count = ' + '.join(['%d * %s' % (v, k) for k, v in sorted(lin.items())] + [str(const)])
    print('ones at the halt:', count, file=sys.stderr)
    assert lin == {'q': 9, 'r': 2} and const == 106, (lin, const)
    halt_lemma = coqgen.stage_lemma('HALTFULL0', a, ops, end)
    text = Path('bound.v.in').read_text()
    text = text.replace('@TM@', TM).replace('@TABLE@', tm_table())
    text = text.replace('@CEND@', coqgen.cfg_coq(end)).replace('@HALTFULL@', halt_lemma)
    text = text.replace('@LLIST@', list_expr(Ltail)).replace('@RLIST@', list_expr(R)).replace('@HEAD@', 'S%d' % head)
    text = text.replace('@STATE@', q)
    Path(out).write_text(text, newline='\n')
    print('wrote', out, file=sys.stderr)


if __name__ == '__main__':
    main(sys.argv[1])
