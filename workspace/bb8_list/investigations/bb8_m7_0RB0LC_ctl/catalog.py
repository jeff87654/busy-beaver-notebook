"""catalog.py DUMPFILE [DUMPFILE...]: run rounds.exe on every dumped literal-run start, collect round shapes"""
import sys, subprocess, collections, os
from shapes_lib import comp
HERE = os.path.dirname(os.path.abspath(__file__))
M = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RB0LC_1RG1LD_0RH0RF_---0RE'
cnt = collections.Counter(); ex = {}
for fn in sys.argv[1:]:
    for line in open(fn):
        st, spec = line.rstrip('\n').split('\t', 1)
        st = int(st)
        if st < 0: continue
        p = subprocess.run([os.path.join(HERE, 'rounds.exe'), M, spec, str(st + 10)], capture_output=True, text=True)
        for l in p.stdout.splitlines():
            if '=>' not in l: continue
            body = l.split(' | ', 1)[1]
            a, b = body.split('=>')
            key = comp(a) + '  =>  ' + comp(b)
            cnt[key] += 1
            if key not in ex: ex[key] = l[:300]
for k, v in cnt.most_common():
    print(f'{v:8d}  {k}')
print('distinct', len(cnt))
