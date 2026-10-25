"""sm.py MACHINE_FILE K MACRO1,MACRO2,...: dump tape at those macro steps; print with period-p repeats (p<=12) compressed."""
import sys, subprocess
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\nonlist'); import idle
D = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\nonlist'
f, K, ts = sys.argv[1], sys.argv[2], sys.argv[3].split(',')
W = int(sys.argv[4]) if len(sys.argv) > 4 else 400
def comp(t):
    out = []; i = 0; n = len(t)
    while i < n:
        best = (1, 1)
        for p in range(1, 13):
            r = 1
            while i + (r + 1) * p <= n and t[i + r * p:i + (r + 1) * p] == t[i:i + p]: r += 1
            if r >= 3 and r * p > best[0] * best[1]: best = (p, r)
        p, r = best
        if r >= 3: out.append('(' + ' '.join(t[i:i + p]) + ')x%d' % r); i += p * r
        else: out.append(t[i]); i += 1
    return ' '.join(out)
for T in ts:
    p = subprocess.run([D + r'\nlp7v.exe', f, 'NUL', str(int(T) * 2 + 10**7), '--life', '--K=' + K, '--dumpat=' + T], capture_output=True, text=True, creationflags=0x40)
    L = p.stdout.splitlines()
    if len(L) < 2: print(T, 'no dump'); continue
    h, t = L[1].split('|', 1); t = [x.replace('^1', '') if x.endswith('^1') else x for x in t.split()]
    print(L[0].split()[1], L[0].split()[2], h.strip(), '|', comp(t)[:W])
