"""Build the SM decision DAG with the configuration in sm_config.py, write sm_dag.json and
sm_dag_cells.txt (exact cell count + attribution).   python -I sm_build.py"""
import sys, json, os, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sm_prog as P
import sm_ref as R
from sm_abstract import SM, BOOT_THEOREM, V0, E, parse_tokens, tokstr


def dag_stats(nodes, root):
    memo = {}

    def depth(n):
        if n in memo:
            return memo[n]
        v = 1 + max((depth(c) if isinstance(c, str) else 0) for c in nodes[n])
        memo[n] = v
        return v

    def czeros(n):
        k = 0
        while isinstance(n, str):
            k += 1
            n = nodes[n][0]
        return k
    leaves = {}
    for n, cc in nodes.items():
        for c in cc:
            if not isinstance(c, str):
                key = c[0] if c[0] != 'op' else c[1]
                leaves[key] = leaves.get(key, 0) + 1
    return depth(root), max(czeros(n) for n in nodes), leaves


def trace_attribution(b, nodes, root):
    """Owner set of every cell = axioms whose step walks through it (one complete step of each
    axiom, from simple and from complex params); readers are attributed statically."""
    seqs = b.sequences
    name = {i: seqs[i].name for i in b.cells}
    # static reader sets
    reader_roots = {k: name[v] for k, v in b.ids.items() if v is not None}
    stop = set(reader_roots.values())
    reader_of = {}
    for k in ('VAR', 'READV', 'READW'):
        if k not in reader_roots:
            continue
        todo = [reader_roots[k]]
        seen = set()
        while todo:
            n = todo.pop()
            if n in seen or (n in stop and n != reader_roots[k]):
                continue
            seen.add(n)
            todo.extend(c for c in nodes[n] if isinstance(c, str))
        for n in seen:
            reader_of.setdefault(n, k)
    owners = {}
    rng = random.Random(5)
    simple = {'V': (V0,), 'W': (E, V0, V0)}
    cplx_w = parse_tokens('-> A v2 ~ = v1 v3 e v0 v0')
    for a in P.AXNAMES:
        for cplx in (False, True):
            if a == 'GEN':
                ps = ((V0 + 2,),) if cplx else ((V0,),)
            elif a == 'DET':
                ps = ()
            else:
                ps = tuple((simple[k] if not cplx else ((V0 + 1,) if k == 'V' else cplx_w))
                           for k in P.param_kinds(a))
            bits = R.encode([(a, ps)], b.code, b.gen_style)
            sm = SM(nodes, root)
            sm.visited = set()
            assert sm.run_candidate(bits) == 'END'
            for n in sm.visited:
                owners.setdefault(n, set()).add(a)
    missing = set(nodes) - set(owners)
    assert not missing, ('unvisited cells', missing)
    table = {}
    shared = {}
    for n in nodes:
        car = nodes[n][0]
        if n == root:
            cat = 'main root (label d; CHECK leaf in its cdr)'
        elif n in reader_of:
            cat = 'reader ' + reader_of[n]
        elif len(owners[n]) == 1:
            cat = 'body ' + next(iter(owners[n]))
        elif car == ['op', 'RB', []] or (isinstance(car, str) and nodes[car][0] == ['op', 'RB', []]):
            cat = 'code tree (decision cells, 2 per internal node)'
        else:
            cat = 'shared ' + '+'.join(sorted(owners[n], key=P.AXNAMES.index))
            shared[cat] = shared.get(cat, 0) + 1
            continue
        table[cat] = table.get(cat, 0) + 1
    return table, shared


def main():
    P.apply_config()
    b, n = P.build()
    nodes, root = b.dag()
    assert len(nodes) == n
    with open(os.path.join(HERE, 'sm_dag.json'), 'w') as f:
        json.dump({'root': root, 'cells': n, 'nodes': nodes,
                   'code': b.code, 'gen_style': b.gen_style,
                   'param_orders': {a: P.AXDICT[a][1] for a in P.AXNAMES},
                   'semantics': 'see sm_abstract.py docstring'}, f, indent=0)
    b0, n0 = P.build(do_breakout=False)
    b1, n1 = P.build(factor=False)
    depth, cz, leaves = dag_stats(nodes, root)
    table, shared = trace_attribution(b, nodes, root)
    # marginal: replace one axiom body by a bare DET leaf (tree unchanged)
    marg = {}
    for a in P.AXNAMES:
        if a == 'DET':
            continue
        _, m = P.build(bodies_override={a: ['DET']})
        marg[a] = n - m
    L = []
    L.append('SM decision DAG (deliverable B1 of SM_SPEC.md) -- exact cell count')
    L.append('=' * 72)
    L.append('CELLS (reachable cons cells = DAG TM states, same count method as Wade 324): %d' % n)
    L.append('  without breakout_common_subsequences (hash-consing only): %d' % n0)
    L.append('  without trie prefix factoring (decide whole code first):   %d' % n1)
    L.append('max root-to-leaf depth %d, max consecutive car edges %d (framework 4.dispatch cap)' % (depth, cz))
    L.append('leaf edges: ' + ', '.join('%s %d' % kv for kv in sorted(leaves.items())))
    L.append('')
    L.append('prefix code (bit 1 = RB nonzero branch) and param reading order:')
    for a in P.AXNAMES:
        L.append('  %-4s %-8s params: %-9s template ops: %s' % (
            a, b.code[a], P.AXDICT[a][1] or '-',
            len(P.template_ops(a)) if P.AXDICT[a][2] else '-'))
    L.append('  wff token code: e=0 ==10 ->=110 ~=1110 A=1111<var>; variables unary 1^i 0')
    L.append('')
    L.append('ATTRIBUTION (trace-based owner sets; a cell walked by exactly one axiom belongs to it)')
    tot = 0
    order = sorted(table.items(), key=lambda kv: (not kv[0].startswith('code'), not kv[0].startswith('main'),
                                                  not kv[0].startswith('reader'), kv[0]))
    for k, v in order:
        L.append('  %-60s %4d' % (k, v)); tot += v
    L.append('  shared cells (prefix/suffix/breakout sharing between axioms):')
    for k, v in sorted(shared.items(), key=lambda kv: -kv[1]):
        L.append('    %-58s %4d' % (k, v)); tot += v
    L.append('  %-60s %4d' % ('TOTAL', tot))
    assert tot == n
    L.append('')
    L.append('summary: code tree %d | readers %d (VAR %d, READV %d, READW %d) | main/DET/GEN/CHECK glue %d |'
             % (table.get('code tree (decision cells, 2 per internal node)', 0),
                sum(v for k, v in table.items() if k.startswith('reader')),
                table.get('reader VAR', 0), table.get('reader READV', 0), table.get('reader READW', 0),
                table.get('main root (label d; CHECK leaf in its cdr)', 0) + table.get('body DET', 0)
                + table.get('body GEN', 0)))
    L.append('         templates exclusive %d + shared %d'
             % (sum(v for k, v in table.items() if k.startswith('body') and k not in ('body DET', 'body GEN')),
                sum(shared.values())))
    L.append('')
    L.append('MARGINAL cost per axiom (cells saved if its body were replaced by a bare DET leaf):')
    L.append('  ' + '  '.join('%s %d' % (a, marg[a]) for a in P.AXNAMES if a in marg))
    txt = '\n'.join(L) + '\n'
    with open(os.path.join(HERE, 'sm_dag_cells.txt'), 'w') as f:
        f.write(txt)
    print(txt)


if __name__ == '__main__':
    main()
