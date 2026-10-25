"""One-time port of zf/m254/prog/coq/{ProgLib254,L2Root254}.v to the m254tg DAG (coq/DagTG.v).

Every node outside axioms() / main() of the old 219-node DAG (m254/logic/m254_wade.tm) has a
structurally identical node in the new one (machine/m254tg_wade.tm); main()/axioms() nodes are matched
by name.  Node numbers are renumbered simultaneously in `ENode k`, `dag_nodes k`, lemma names with a
node-number suffix (w117, pair162, if123_eq, ...) and "node k" comments.
Usage: python -I tools/port.py   (writes coq/ProgLibTG.v, coq/L2RootTG.v; regions are then regenerated
by tools/gen_prog.py)"""
import hashlib, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ZF = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
OLD = os.path.join(ZF, 'm254', 'prog', 'coq')
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
    n1, names1 = numbered(os.path.join(ZF, 'm254', 'logic', 'm254_wade.tm'))
    n2, names2 = numbered(os.path.join(ZF, 'm254tg', 'machine', 'm254tg_wade.tm'))
    h1, h2 = hashes(n1), hashes(n2)
    by_hash = {}
    for n in names2:
        by_hash.setdefault(h2[n], []).append(n)
    idx2 = {n: i for i, n in enumerate(names2)}
    M = {}
    for i, n in enumerate(names1):
        if n.startswith(('main()', 'axioms()')):
            if n in idx2 and not n.startswith('axioms().') or n == 'axioms().0':
                M[i] = idx2[n]
            continue
        c = by_hash.get(h1[n], [])
        if len(c) == 1:
            M[i] = idx2[c[0]]
        elif n in c:
            M[i] = idx2[n]
        else:
            raise SystemExit(f'no unique match for old node {i} {n}: {c}')
    return M


def port(src, M, exact):
    def num(k):
        k = int(k)
        if k not in M:
            raise SystemExit(f'node {k} referenced but not mapped')
        return str(M[k])
    src = re.sub(r'\b(ENode|dag_nodes|node|nodes) (\d+)\b', lambda m: f'{m.group(1)} {num(m.group(2))}', src)
    src = re.sub(r'\b([a-z]+)(\d+)(?=\b|_)',
                 lambda m: m.group(1) + num(m.group(2)) if (m.group(1), m.group(2)) in exact else m.group(0), src)
    src = src.replace('dag_nodes', 'dagtg_nodes').replace('dag254', 'dagtg').replace('Dag254', 'DagTG')
    src = src.replace('ProgLib254', 'ProgLibTG').replace('L2Root254', 'L2RootTG').replace('M254P', 'M254TGP')
    return src


if __name__ == '__main__':
    M = mapping()
    srcs = {f: open(os.path.join(OLD, f), encoding='utf-8').read() for f in ['ProgLib254.v', 'L2Root254.v']}
    # lemma names ending in a node number (optionally followed by _suffix), across both files
    exact = {(p, k) for s in srcs.values()
             for p, k in re.findall(r'\b(?:Lemma|Theorem)\s+([a-z]+)(\d+)(?:_\w+)?\b', s) if int(k) in M}
    for old, new in [('ProgLib254.v', 'ProgLibTG.v'), ('L2Root254.v', 'L2RootTG.v')]:
        out = port(srcs[old], M, exact)
        with open(os.path.join(NEW, new), 'w', encoding='utf-8', newline='\n') as f:
            f.write(out)
        print('wrote', new)
