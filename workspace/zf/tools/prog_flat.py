"""Parse coq/ZF2Dag.v and print the flattening of main()'s cons chain into subroutine elements.
Usage: python tools/prog_flat.py [--coq]"""
import re, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent.parent
txt = (HERE / 'coq' / 'ZF2Dag.v').read_text()
nodes, names = {}, {}
for m in re.finditer(r'\| (\d+) => \((.*?), (E\w+(?: \d+)?)\)\s+\(\* (.*?) \*\)', txt):
    n = int(m.group(1))
    nodes[n] = (m.group(2), m.group(3)); names[n] = m.group(4)

def is_chain(n):
    nm = names[n]
    return nm.startswith('main().') and n != 58 and not nm.startswith('main().124')

def expand(e):
    m = re.match(r'ENode (\d+)', e)
    if m and is_chain(int(m.group(1))):
        n = int(m.group(1)); a, b = nodes[n]
        return expand(a) + expand(b)
    return [e]

if __name__ == '__main__':
    flat = expand('ENode 0')
    if '--coq' in sys.argv:
        print('[' + '; '.join(flat) + ']')
    else:
        for e in flat:
            m = re.match(r'ENode (\d+)', e)
            print(e, names[int(m.group(1))] if m else '')
        print(len(flat), 'elements; chain nodes:', sorted(n for n in nodes if is_chain(n)).__len__())
