import idle
"""tops.py DIR...: count top rebuild views ('0*2 7 1*K', '0 7 1*K', '0*2 1 7 z2 X 1*K', K >= 1000) per run file."""
import sys, glob, re, os
pat = re.compile(r'^(0\*\d+|0) (1 )?7 (z2 \d+ )?1\*(\d+)$')
res = []
for d in sys.argv[1:]:
    for f in glob.glob(os.path.join(d, '*.txt')):
        ks = []; out = ''
        for l in open(f, errors='replace'):
            if l.startswith('J') and '|' in l:
                v = l.split('|', 1)[1].strip(); mm = pat.match(v)
                if mm and int(mm.group(4)) >= 1000: ks.append(int(mm.group(4)))
            elif l.startswith(('HALT', 'STOP', 'END')): out = ' '.join(l.split()[:2])
        if len(ks) >= 2: res.append((len(set(ks)), f, out, ks))
for n, f, out, ks in sorted(res, key=lambda x: -x[0]): print(n, f, out or 'KILLED', ks[:12])
