"""Filter tr9 output: print a snapshot only when its shape (tape with run counts replaced by #) changes.
  tr9 ... | python shapes.py [STRIP_PREFIX] [MAXCHARS]"""
import re
import sys

strip = sys.argv[1] if len(sys.argv) > 1 else ''
maxc = int(sys.argv[2]) if len(sys.argv) > 2 else 300
prev = None
hdr = None
cnt = 0
for line in sys.stdin:
    if not line.startswith('  '):
        hdr = line.strip()
        continue
    t = line.strip()
    if strip and t.startswith(strip):
        t = 'L ' + t[len(strip):]
    sh = re.sub(r'\^\d+', '^#', t)
    if sh != prev:
        if cnt:
            print(f'    ... {cnt} similar')
        print(hdr.split(':')[0], '|', t[:maxc])
        prev = sh
        cnt = 0
    else:
        cnt += 1
        last = (hdr, t)
