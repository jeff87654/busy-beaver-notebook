"""gk.py: generic run view. tape string (from leftmost 1 to head) -> (runs, trailing zero count)."""
from drv import unr
def gruns(s):
    w = unr(s); z = len(w) - len(w.rstrip('0')); w = w.rstrip('0')
    return [len(x) for x in w.split('0')], z
def vshow(runs):
    s = []; i = 0
    while i < len(runs):
        j = i
        while j < len(runs) and runs[j] == runs[i]: j += 1
        t = str(runs[i]); s.append(t if j - i == 1 else '%s^%d' % (t, j - i)); i = j
    return ' '.join(s)
import subprocess
from drv import SIM
def gword(runs, z):
    return '0'.join('1' * r for r in runs) + '0' * (z - 1)
def gnext(M, Q, z, runs, N=10**8, maxev=1, start_q=None):
    w = gword(runs, z)
    r = subprocess.run([SIM, M, '1', start_q or Q, w, str(len(w)), str(N), Q, str(maxev)], capture_output=True, text=True).stdout.splitlines()
    out = []
    for l in r:
        s = l.split(None, 2)
        if s[0] == 'E' and len(s) == 3: out.append((int(s[1]),) + gruns(s[2]))
        elif s[0] == 'H': out.append(('H', int(s[1])))
        elif s[0] == 'END' and len(s) == 2: out.append(('T', int(s[1])))
        elif s[0] == 'TAPE': out.append(('TAPE', int(s[1])))
    return out
def P(txt):  # parse 'a^k b ...' into run list
    o = []
    for t in txt.split():
        if '^' in t: x, k = t.split('^'); o += [int(x)] * int(k)
        else: o.append(int(t))
    return o
