"""Cross-check the TM layer's frozen ../tm/coq/DagTG.v (imported here as M254TGT.DagTG): regenerate the
decision DAG of the frozen machine/m254tg_wade.tm (Wade TMBuilder compile of machine/source_tg.py),
numbered as zf/tools/gen_coq_dag.py does (names sorted, main().0 = node 0, registers = dag.extract's
regidx = declaration order), and require its node table (every `| k => (..)` line) to equal the file's.

Usage: python -I tools/gen_coq.py      (from anywhere; exit status 1 on a mismatch)
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ZF = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
TM = os.path.join(ZF, 'm254tg', 'machine', 'm254tg_wade.tm')
DAG = os.path.join(ZF, 'm254tg', 'tm', 'coq', 'DagTG.v')
sys.path.insert(0, os.path.join(ZF, 'tools'))
from dag import extract

REGS = ['nextproof', 'topwff', 'wffstack', 'axiomcode', 'param1', 'param2', 'scratch1', 'scratch2', 'prooflist']


def coq_edge(e, idx, regidx):
    k = e[0]
    if k == 'node':
        return f'ENode {idx[e[1]]}'
    if k == 'op':
        return f"{'EInc' if e[2] == 'inc' else 'EDecnz'} {regidx[e[1]]}"
    if k == 'break':
        return f'EBreak {e[1]}'
    if k == 'continue':
        return f'EContinue {e[1]}'
    if k == 'halt':
        return 'EHalt'
    raise ValueError(e)


def main():
    start, tbl, nodes, regidx = extract(TM)
    assert regidx == {r: i for i, r in enumerate(REGS)}, regidx
    names = sorted(nodes)
    names.remove('main().0')
    names = ['main().0'] + names
    idx = {n: i for i, n in enumerate(names)}
    mine = [f'  | {idx[n]} => ({coq_edge(nodes[n][0], idx, regidx)}, {coq_edge(nodes[n][1], idx, regidx)})   (* {n} *)'
            for n in names] + ['  | _ => (EHalt, EHalt)']
    with open(DAG, encoding='utf-8') as f:
        text = f.read()
    theirs = [l for l in text.splitlines() if l.startswith('  | ')]
    if mine != theirs or f'Definition dagtg : prog := mkProg dagtg_nodes 0 {len(names)}.' not in text:
        sys.exit('MISMATCH: tm/coq/DagTG.v differs from the regenerated DAG')
    print('tm/coq/DagTG.v = regenerated DAG of m254tg_wade.tm;', len(names), 'nodes; start', start)


if __name__ == '__main__':
    main()
