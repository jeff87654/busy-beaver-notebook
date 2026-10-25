"""Framework state roles for a Wade-format machine (TM object or .tm file)."""
import re
from collections import Counter
def role(s):
    if s.startswith('0'): return 'boot'
    if s.startswith('1.q'): return '1.q gadget'
    if s.startswith('1.decnz'): return '1.decnz*'
    if s.startswith('1.inc'): return '1.inc*'
    if s.startswith('1.sel'): return '1.sel*'
    if s.startswith('2.'): return '2.ret*'
    if s.startswith('1.'): return '1.other: '+s
    m = re.match(r'3\.(.*)\.(\w+)$', s)
    if m: return '3.<reg>.' + m.group(2)
    if s in ('4.dispatch.1', '5.root'): return 'dispatch.1+5.root'
    if s.startswith('4.dispatch'): return '4.dispatch.2..Z'
    if s.startswith('6.break'): return '6.break.k'
    if s.startswith('6.continue'): return '6.continue.k'
    return 'other: ' + s
def roles(names):
    return Counter(role(s) for s in names if s[0].isdigit())
if __name__ == '__main__':
    import sys
    sys.path.insert(0, '.')
    from tmsim import load
    st, tbl = load(sys.argv[1])
    for k, v in sorted(roles({s for s, _ in tbl}).items()): print(f'{v:4d} {k}')
