"""Port node-number-specific Coq text from another DAG (e.g. v361) to this one: subroutine nodes are matched
by their ZF2Dag.v names (outlined node_XXX and main() names are not stable, they are matched through the
structure), the match is checked to be a structural isomorphism, and node numbers inside [ENode n] and in
lemma names (pushwff221, w278, ...) are renamed.
Usage: python tools/port_nodes.py OLD_DIR FILE.v ..."""
import re, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent.parent


def load(d):
    txt = (Path(d) / 'coq' / 'ZF2Dag.v').read_text()
    nodes, names = {}, {}
    for m in re.finditer(r'\| (\d+) => \((.*?), (E\w+(?: \d+)?)\)\s+\(\* (.*?) \*\)', txt):
        nodes[int(m.group(1))] = (m.group(2), m.group(3)); names[int(m.group(1))] = m.group(4)
    return nodes, names


def checks(nodes, names):
    """the final halt check: main() cells with a decnz car"""
    return [n for n in sorted(nodes) if names[n].startswith('main().') and nodes[n][0].startswith('EDecnz')]


on, onames = load(sys.argv[1]); nn, nnames = load(HERE)
inv = {v: k for k, v in nnames.items()}
M = {}
for n, nm in onames.items():
    if not nm.startswith('main().') and not nm.startswith('node_') and nm in inv:
        M[n] = inv[nm]
for a, b in zip(checks(on, onames), checks(nn, nnames)):
    M[a] = b
changed = True
while changed:                        # propagate along car/cdr edges
    changed = False
    for a, b in list(M.items()):
        for c, e in zip(on[a], nn[b]):
            if c.startswith('ENode') and e.startswith('ENode'):
                x, y = int(c.split()[1]), int(e.split()[1])
                if x not in M:
                    M[x] = y; changed = True
                assert M[x] == y, (a, b, x, y)
missing = [n for n in on if n not in M and not onames[n].startswith('main().')]
assert not missing, missing[:10]


def mapedge(e):
    m = re.fullmatch(r'ENode (\d+)', e)
    return f'ENode {M[int(m.group(1))]}' if m else e


for n in M:
    assert tuple(mapedge(e) for e in on[n]) == nn[M[n]], (n, M[n], on[n], nn[M[n]])
M[0] = 0
PFX = r'(?:pushwff|pair|unpair|ubody|n|select|cparam|loop|if|ifeq|ifnot|check|v|par|weq|wel|wim|wal|wn|wex|wa|w)'
for f in sys.argv[2:]:
    p = Path(f); s = p.read_text(encoding='utf-8')
    s = re.sub(r'\bENode (\d+)\b', lambda m: f'ENode {M.get(int(m.group(1)), int(m.group(1)))}', s)
    s = re.sub(r'\b(' + PFX + r')(\d+)(?=\b|_)', lambda m: m.group(1) + str(M.get(int(m.group(2)), int(m.group(2)))), s)
    p.write_text(s, encoding='utf-8', newline='\n')
print('mapped', len(M), 'nodes;', sum(1 for k, v in M.items() if k != v), 'renumbered')
