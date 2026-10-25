"""show.py MACHINE [nfol args]: follower run printing the WHOLE tape at every K-moment as tokens
(D-tokens; 'z' = an extra 0 between tokens, i.e. '1001' -> 0 z 0)."""
import sys, threading, re
from nfol import follow, FAR_TAIL, expand, rle
def toks_of_bits(b):
    out = []; i = 0; n = len(b)
    b = b.lstrip('0')
    while i < len(b):
        if b[i] == '0':
            out.append('z'); i += 1; continue
        j = i + 1; m = 0
        while j + 1 < len(b) and b[j] == '0' and b[j+1] == '1':
            m += 1; j += 2
        out.append(m); i = j
    return out
def rl(v):
    out = []; i = 0
    while i < len(v):
        j = i
        while j < len(v) and v[j] == v[i]: j += 1
        out.append(f'{v[i]}^{j-i}' if j - i > 1 else str(v[i])); i = j
    return ' '.join(out)
if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument('machine'); ap.add_argument('--start'); ap.add_argument('--fark', type=int)
    ap.add_argument('--stages', type=int, default=60); ap.add_argument('--b0', type=int, default=6); ap.add_argument('--policy', default='std')
    ap.add_argument('--from', dest='frm', type=int, default=0)
    a = ap.parse_args()
    far = '10101' * a.fark + FAR_TAIL if a.fark is not None else ''
    def log(s):
        f = s.split(' ', 2)
        if len(f) > 1 and f[1] == 'K:' and int(f[0]) >= a.frm:
            body = f[2]
            m = re.search(r' far=(\S+)', body)
            fb = m.group(1) if m else ''
            toks = body.split('|')[0].strip()
            print(f[0], 'K:', rl(toks_of_bits(fb)), '||', toks, '|', body.split('|')[1].split(' far=')[0].split(' U=')[0].strip(), flush=True)
        elif len(f) > 1 and f[1] in ('HALT', 'T', 'W', 'JUMPFAIL', 'FAIL'):
            print(s, flush=True)
    sys.setrecursionlimit(30000); threading.stack_size(64 * 1024 * 1024)
    res = []
    t = threading.Thread(target=lambda: res.append(follow(a.machine, a.b0, a.policy, a.stages, 2 * 10**8, 1, log, expand(a.start) if a.start else None, far)))
    t.start(); t.join(); print('RESULT', res[0][0])
