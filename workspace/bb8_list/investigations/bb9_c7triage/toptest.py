import idle
"""toptest.py MACHINE T K1 K2 ...: start pkf8 at Top(K) = '0*2 7 1*K' (t=T, R=366 class mod 3600), report the next top
'0*2 7 1*K'' (or the first non-top view = exit) and compare with h003's fitted rules."""
import sys, subprocess, re
EXE = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_c7triage\tools\pkf8.exe'
RULE = {1: (9, 36), 4: (3, -2), 3: (3, 16)}
m, T = sys.argv[1], sys.argv[2]
for K in map(int, sys.argv[3:]):
    p = subprocess.run([EXE, m, '--kt', '0,0,7,1*%d;1;1100;%s' % (K - 1, T), '--R', '366', '--cls', '366', '--mod', '3600', '--cnt',
                        '--jumps', '5', '--maxs', '6e9'], capture_output=True, text=True, creationflags=0x40)
    J = [l for l in p.stdout.splitlines() if l.startswith('J')][1:]
    nxt = 'none'
    for l in J:
        v = l.split('|', 1)[1].strip()
        mm = re.fullmatch(r'0\*2 7 1\*(\d+)', v)
        if mm: nxt = int(mm.group(1)); break
        if not v.startswith('0 1 '): nxt = 'exit:' + v[:40]; break
    r = K % 5
    pred = (RULE[r][0] * K + 60 * 366 + RULE[r][1]) // 5 if r in RULE else 'exit'
    ok = (nxt == pred) or (pred == 'exit' and str(nxt).startswith('exit'))
    print(K, K % 25, 'next', nxt, 'pred', pred, 'OK' if ok else 'MISMATCH', flush=True)
