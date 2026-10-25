import idle
"""For each verify_f3 file with a same-named file in verify_c04: is it exactly the mechanical port? else diff size."""
import re, difflib
from pathlib import Path
C = Path(r'C:\Users\jeffr\Downloads\bb9f3_wt\BB9\verify_c04'); F = Path(r'C:\Users\jeffr\Downloads\bb9f3_wt\BB9\verify_f3')
def port(s):
    s = s.replace('\r\n', '\n')
    s = s.replace('From BB8 Require Import Individual92.', 'From XL Require Import Individual112.')
    s = s.replace('<{{H}}', '<{{J}}')
    return re.sub(r'From (Dev|K31|Score|Fgh) Require', lambda m: 'From X' + m.group(1) + ' Require', s)
for d in ['dev', 'k31', 'score']:
    for f in sorted((F / d).glob('*.v')):
        c = C / d / f.name
        if not c.exists(): print('NEW      ', d + '/' + f.name); continue
        a = port(c.read_text(encoding='utf-8')).splitlines(); b = f.read_text(encoding='utf-8').splitlines()
        if a == b: print('PORT     ', d + '/' + f.name)
        else:
            n = sum(1 for l in difflib.unified_diff(a, b, lineterm='', n=0) if l[:1] in '+-' and l[:3] not in ('+++', '---'))
            print('EDITED   ', d + '/' + f.name, n, 'changed lines (of %d)' % len(a))
