"""Members of behaviour classes whose representative has a result: MACHINE<TAB>tag<TAB><TAB><TAB>REF lines.
   python members.py SIGS.tsv RESULTS... > members.tsv  (tags from set_r1/set_r2)"""
import sys
from collections import OrderedDict
sigf, resf = sys.argv[1], sys.argv[2:]
cls = OrderedDict()
for l in open(sigf):
    m, s = l.rstrip('\n').split('\t'); cls.setdefault(s, []).append(m)
res = {}
for fn in resf:
    for l in open(fn):
        f = l.rstrip('\n').split('\t')
        if len(f) >= 3: res[f[0]] = f[2]
tag = {}
for fn in ('set_r1.tsv', 'set_r2.tsv'):
    for l in open(fn):
        f = l.rstrip('\n').split('\t'); tag.setdefault(f[0], f[1])
for s, ms in cls.items():
    done = [m for m in ms if m in res]
    if not done: continue
    import os
    withpkl = [m for m in done if os.path.exists(f'logs/{m}.stages.pkl')]
    ref = withpkl[0] if withpkl else done[0]
    for m in ms:
        if m not in res:
            print(f'{m}\t{tag.get(m, "")}\t\t\t{ref}')
