# f1screen.py OUT : run all 288 F1 variants (M8 + H1 = xDI + one halting slot in I) in the 9 C04 route worlds
# (key31 rho 0..4, keys 37/43/49/55) for 2e6 steps past M8's halt; per world: IMM (halt <= 64 steps after M8's halt
# step), LATE s (halt later, s = steps after), RUN (no halt in budget).  Real PIDs -> ../pids.txt.  3 at a time.
import subprocess, sys, os, time, itertools
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(HERE)
EXE = os.path.join(HERE, 'pkf7.exe')
M8P = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_1RG1LD_0RG0RF_1RG'
W = '0,0,1077,4,645,6,385,6,229,19749,2,77,1*%d,0,2,z2,1*%d;1;902;18'
WORLDS = [('k31r0', 300, 12, 38837261), ('k31r1', 301, 12, 48166103), ('k31r2', 302, 12, 38985764), ('k31r3', 303, 12, 57717407),
          ('k31r4', 304, 12, 57710665), ('k49', 803, 18, 56512247), ('k37', 803, 42, 57220409), ('k55', 803, 192, 81398506),
          ('k43', 803, 732, 75334907)]
trans = [w + d + s for w in '01' for d in 'LR' for s in 'ABCDEFGHI']
variants = []
for h1 in [w + d + 'I' for w in '01' for d in 'LR']:
    for t in trans:
        variants.append(M8P + h1 + '_---' + t); variants.append(M8P + h1 + '_' + t + '---')
out = open(sys.argv[1], 'a'); pidf = open(os.path.join(BASE, 'pids.txt'), 'a')
jobs = [(m, w) for m in variants for w in WORLDS]; live = []; res = {}
def classify(txt, base):
    for l in txt.splitlines():
        if l.startswith('HALT'):
            a = l.split(); st = int(a[3]); dd = st - base
            return ('IMM' if dd <= 64 else 'LATE%d' % dd) + ':' + a[1] + ':' + a[a.index('ones') + 1]
    return 'RUN'
while jobs or live:
    while jobs and len(live) < 3:
        m, w = jobs.pop(0); name, P, k, st = w
        p = subprocess.Popen([EXE, m, '--kt', W % (P, k), '--R', '366', '--rmod', '3600', '--exactcap', '1000', '--jumps', '100000',
                              '--view', '50', '--maxs', '5e10', '--maxt', str(st + 2000000), '--cnt', '--quiet'], stdout=subprocess.PIPE, text=True)
        pidf.write('%s %d f1screen %s %s\n' % (time.strftime('%m-%d %H:%M:%S'), p.pid, m[-12:], name)); pidf.flush()
        live.append((p, m, w))
    for x in live[:]:
        p, m, w = x
        if p.poll() is None: continue
        live.remove(x); res.setdefault(m, {})[w[0]] = classify(p.stdout.read(), w[3])
        if len(res[m]) == len(WORLDS):
            r = res.pop(m); out.write(m + '\t' + '\t'.join('%s=%s' % (n[0], r[n[0]]) for n in WORLDS) + '\n'); out.flush()
    time.sleep(0.05)
