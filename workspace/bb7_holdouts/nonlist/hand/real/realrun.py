"""realrun.py [SLIMLOG] [TIMEOUT] [Klist]: real blank-tape run of every member machine (members.tsv) with ms2.exe
(exact macro sim, stops at 10^SLIMLOG base steps / halt / macro cap / timeout). Idle priority, one process at a time.
Writes realrun.tsv: idx machine K result steps lastsnapshot(compressed, 300 chars)."""
import subprocess, sys, os, re, time
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'pids.txt'), 'a').write(str(os.getpid()) + chr(9) + time.strftime('%Y-%m-%d %H:%M:%S') + chr(9) + 'python realrun.py (tier1-real agent)' + chr(10))
H = os.path.dirname(os.path.abspath(__file__))
SL = sys.argv[1] if len(sys.argv) > 1 else '15'; TO = float(sys.argv[2]) if len(sys.argv) > 2 else 120
KS = sys.argv[3].split(',') if len(sys.argv) > 3 else None
MS = os.path.join(H, 'ms2.exe')
def comp(ts):
    out = []; i = 0
    while i < len(ts):
        if i + 3 < len(ts) and ts[i] == ts[i + 2] and ts[i + 1] == ts[i + 3]:
            j = i
            while j + 3 < len(ts) and ts[j] == ts[j + 2] and ts[j + 1] == ts[j + 3]: j += 2
            out.append(f'({ts[i]} {ts[i+1]})x{(j - i) // 2 + 1}'); i = j + 2
        else: out.append(ts[i]); i += 1
    return ' '.join(out).replace('^1 ', ' ')
out = open(os.path.join(H, f'realrun_{SL}.tsv'), 'a')
done = set()
try:
    for l in open(os.path.join(H, f'realrun_{SL}.tsv')): done.add((l.split('\t')[1], l.split('\t')[2]))
except Exception: pass
for l in open(os.path.join(H, 'members.tsv')):
    f = l.rstrip('\n').split('\t'); m = f[2]
    for K in (KS or [f[3]]):
        if (m, K) in done: continue
        t0 = time.time()
        p = subprocess.Popen([MS, m, K, '400000000000', 'g0', 'x', SL, '0.5'], stdout=subprocess.PIPE, text=True, creationflags=0x40)
        last = ''; res = 'END'; st = ''
        try:
            o, _ = p.communicate(timeout=TO)
        except subprocess.TimeoutExpired:
            p.kill(); o, _ = p.communicate(); res = 'TIMEOUT'
        lines = o.splitlines()
        for x in lines:
            if x.startswith('H '): res = 'HALT'; st = x
            elif x.startswith('SLIM'): res = 'SLIM'
            elif x.startswith('INBLOCK'): res = 'INBLOCK'; st = x
        tl = [x for x in lines if 'T ' in x[:7] and '|' in x]
        if tl:
            a, b = tl[-1].split('|', 1); last = a.replace('SLIM ', '').split()[2] + ' ' + a.split()[-2] + ' | ' + comp(b.split())
        if res == 'HALT': last = st
        out.write(f'{f[0]}\t{m}\t{K}\t{res}\t{time.time()-t0:.1f}\t{last[:400]}\n'); out.flush()
