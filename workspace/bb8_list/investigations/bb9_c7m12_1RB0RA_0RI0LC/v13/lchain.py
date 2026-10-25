"""Check the champion rules R1-R3 on a token list with an arbitrary prefix, in the tail context.
Canonical configuration: PREFIX + digits D(3d+1) + D(3a+1) + D(3b+2) + tail starting with '0*6 <1 00>' or '0*7'.
  python v13/lchain.py MACHINE "PREFIX" "d1,d2,..." a b MAXSTEPS [NPRINT]
Runs literally, extracts every canonical configuration and checks each consecutive pair against
R1 (a>0: a-1, 2b+2), R2 (a=0, last digit>0: d-1, a=2b+2, b=0), R3 (a=0, last nonzero d followed by zeros:
d-1, 2b+2 at the next position, a=0, b=0). Reports the first violation or the configuration where the prefix changes."""
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
from tok2word import tok2word  # noqa: E402

M, prefix = sys.argv[1], sys.argv[2]
ds = [int(x) for x in sys.argv[3].split(',') if x != '']
a, b, mx = int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])
nprint = int(sys.argv[7]) if len(sys.argv) > 7 else 0
TAIL = '0*6 <1 00> 0*5 <1 00> 0*5 <1 00> 0*5 <1 00> 0*5 <1 00> 0*5 <1 00 1 00> 0'
toks = prefix + ' ' + ' '.join(str(3 * d + 1) for d in ds) + f' {3 * a + 1} {3 * b + 2} ' + TAIL
w = tok2word(toks)
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
out = subprocess.run([str(HERE / 'tr9f.exe'), M, w, str(len(w)), 'B', str(mx), 'dall', '10000000'],
                     capture_output=True, text=True, creationflags=LOW).stdout.splitlines()
pre = prefix.split()


def expand(tt):
    r = []
    for t in tt:
        if '*' in t and not t.startswith('<'):
            v, k = t.split('*')
            r += [v] * int(k)
        else:
            r.append(t)
    return r


def parse(line):
    body = line.split(' | ', 1)[1]
    m = re.match(r'(.*?) (0\*[67] <1 00>.*)$', body)
    if not m:
        return None
    tt = expand(m.group(1).split())
    p = expand(pre)
    if tt[:len(p)] != p:
        return 'PREFIX'
    rest = tt[len(p):]
    if len(rest) < 2 or any(not x.isdigit() for x in rest):
        return None
    vals = [int(x) for x in rest]
    if vals[-1] % 3 != 2 or any(v % 3 != 1 for v in vals[:-1]):
        return None
    return tuple((v - 1) // 3 for v in vals[:-2]), (vals[-2] - 1) // 3, (vals[-1] - 2) // 3


def step(st):
    d, a, b = st
    if a > 0:
        return d, a - 1, 2 * b + 2
    nz = [i for i, x in enumerate(d) if x > 0]
    if not nz:
        return None
    j = nz[-1]
    if j == len(d) - 1:
        return d[:-1] + (d[-1] - 1,), 2 * b + 2, 0
    return d[:j] + (d[j] - 1, 2 * b + 2) + d[j + 2:], 0, 0


states = []
for line in out:
    if not line.startswith('S '):
        continue
    p = parse(line)
    if p == 'PREFIX':
        print('prefix changed at', line[:160])
        break
    if p and (not states or states[-1][1] != p):
        states.append((line.split(' | ')[0], p))
ok = True
for i in range(1, len(states)):
    exp = step(states[i - 1][1])
    if exp != states[i][1]:
        print('VIOLATION', states[i - 1], '->', states[i], 'expected', exp)
        ok = False
        break
print(f'{len(states)} canonical configurations, rules {"OK" if ok else "FAIL"}; last {states[-1] if states else None}')
end = [l for l in out if l.startswith('HALT') or l.startswith('END')]
for s in states[:nprint]:
    print('  ', s)
