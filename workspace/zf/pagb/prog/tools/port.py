"""One-time port of zf/m254tg/prog/coq/{ProgLibTG,L2RootTG}.v to the pagb DAG (../tm/coq/DagPA.v).

Nodes of the TG DAG (m254tg_wade.tm) are matched to nodes of the PA DAG (pa_wade.tm) by structural
hash (unique match, else same name); main()/axioms() nodes are matched by name.  Unmatched old nodes
are reported (their lemmas must be rewritten by hand).  Node numbers are renumbered in `ENode k`,
`dagtg_nodes k`, lemma names with a node-number suffix and "node k" comments.
Usage: python -I tools/port.py [--dry]"""
import hashlib, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ZF = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
OLD = os.path.join(ZF, 'm254tg', 'prog', 'coq')
NEW = os.path.normpath(os.path.join(HERE, '..', 'coq'))
sys.path.insert(0, os.path.join(ZF, 'tools'))
from dag import extract


def numbered(tm):
    _, _, nodes, _ = extract(tm)
    names = sorted(nodes)
    names.remove('main().0')
    return nodes, ['main().0'] + names


def hashes(nodes):
    memo = {}

    def h(n):
        if n not in memo:
            a, b = nodes[n]
            memo[n] = hashlib.sha1((e(a) + '|' + e(b)).encode()).hexdigest()
        return memo[n]

    def e(x):
        return 'N' + h(x[1]) if x[0] == 'node' else repr(x)
    return {n: h(n) for n in nodes}


def mapping():
    n1, names1 = numbered(os.path.join(ZF, 'm254tg', 'machine', 'm254tg_wade.tm'))
    n2, names2 = numbered(os.path.join(ZF, 'pagb', 'machine', 'pa_wade.tm'))
    h1, h2 = hashes(n1), hashes(n2)
    by_hash = {}
    for n in names2:
        by_hash.setdefault(h2[n], []).append(n)
    idx2 = {n: i for i, n in enumerate(names2)}
    M, miss = {}, []
    for i, n in enumerate(names1):
        if n.startswith(('main()', 'axioms()')):
            if n in idx2 and (not n.startswith('axioms().') or n == 'axioms().0'):
                M[i] = idx2[n]
            continue
        c = by_hash.get(h1[n], [])
        if len(c) == 1:
            M[i] = idx2[c[0]]
        elif n in c:
            M[i] = idx2[n]
        else:
            miss.append((i, n, c))
    return M, miss, names1, names2


def port(src, M, exact):
    def num(k):
        k = int(k)
        return str(M[k]) if k in M else f'XX{k}'
    src = re.sub(r'\b(ENode|dagtg_nodes|node|nodes) (\d+)\b', lambda m: f'{m.group(1)} {num(m.group(2))}', src)
    src = re.sub(r'\b([a-z]+)(\d+)(?=\b|_)',
                 lambda m: m.group(1) + num(m.group(2)) if (m.group(1), m.group(2)) in exact else m.group(0), src)
    src = src.replace('dagtg_nodes', 'dagpa_nodes').replace('dagtg', 'dagpa').replace('DagTG', 'DagPA')
    src = src.replace('ProgLibTG', 'ProgLibPA').replace('L2RootTG', 'L2RootPA').replace('M254TGP', 'PAGBP')
    src = src.replace('M254TGT', 'PAGBT')
    return src


if __name__ == '__main__':
    M, miss, names1, names2 = mapping()
    print(len(M), 'mapped;', len(miss), 'unmatched old nodes')
    for i, n, c in miss:
        print('  unmatched', i, n, c[:3])
    if '--dry' in sys.argv:
        sys.exit(0)
    srcs = {f: open(os.path.join(OLD, f), encoding='utf-8').read() for f in ['ProgLibTG.v', 'L2RootTG.v']}
    exact = {(p, k) for s in srcs.values()
             for p, k in re.findall(r'\b(?:Lemma|Theorem)\s+([a-z]+)(\d+)(?:_\w+)?\b', s)}
    for old, new in [('ProgLibTG.v', 'ProgLibPA.v'), ('L2RootTG.v', 'L2RootPA.v')]:
        out = port(srcs[old], M, exact)
        with open(os.path.join(NEW, new), 'w', encoding='utf-8', newline='\n') as f:
            f.write(out)
        print('wrote', new, 'unmapped refs:', sorted(set(re.findall(r'XX\d+', out))))
