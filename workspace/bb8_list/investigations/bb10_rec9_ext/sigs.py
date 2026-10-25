"""Behaviour signatures from c_end: hash of the first N canonical configurations (hyb10 C lines, state B) and the
stop line, on several (q, r) points.  Usage: python sigs.py MACHFILE OUT.tsv"""
import subprocess, sys, os, hashlib
from cend import c_end
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
HYB = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'bb10_bb7_descendants', 'hyb10.exe')
TMP = os.path.join(os.environ.get('CLAUDE_JOB_DIR', '.'), 'tmp', 'rec9ext')
PTS = [(2, 9), (3, 15), (4, 21)]
files = {}
for q, r in PTS:
    t, h, s = c_end(q, r)
    fn = os.path.join(TMP, f'ce_{q}_{r}.txt'); open(fn, 'w').write(f'{s} {h}\n{t}\n'); files[(q, r)] = fn
out = open(sys.argv[2], 'w')
for m in open(sys.argv[1]).read().split():
    hs = []
    for p in PTS:
        r = subprocess.run([HYB, m, files[p], '0', 'I', '30000000', '-k', '1000000', '-m', '400', '-q', 'B', '-x'],
                           capture_output=True, text=True, creationflags=LOW)
        lines = [l.split(' | ', 1)[-1] if l[0] in 'CHTM' else l for l in r.stdout.splitlines() if l[:1] in 'CHTM']
        last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ''
        hs.append(hashlib.md5('\n'.join(lines).encode()).hexdigest()[:10] + ':' + last[:1])
    out.write(m + '\t' + ' '.join(hs) + '\n'); out.flush()
