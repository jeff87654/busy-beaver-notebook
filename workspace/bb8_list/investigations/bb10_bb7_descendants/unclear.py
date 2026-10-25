"""For every UNCLEAR result: last champion phase / event config and the failure message (shortened)."""
import sys, re
from pathlib import Path
for fn in sys.argv[1:]:
    for l in open(fn):
        f = l.rstrip('\n').split('\t')
        if len(f) < 3 or 'HALT' in f[2].split()[1]:
            continue
        lg = Path('logs') / f'{f[0]}.log'
        L = lg.read_text().splitlines() if lg.exists() else []
        ph = [x for x in L if 'champion phase' in x or 'event config' in x]
        last = ph[-1].strip()[:150] if ph else '-'
        msg = f[2][7:80]
        fc = re.search(r'full_cycles=(\d+)', f[2])
        print(f'{f[0][28:]} | {f[1]} | fc={fc.group(1) if fc else "?"} | {msg}\n      {last}')
