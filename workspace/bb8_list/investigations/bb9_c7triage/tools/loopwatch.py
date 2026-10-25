import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); import idle
"""loopwatch.py: kills qrun jobs (own PIDs from pids.txt, image pkf8.exe only) whose last 6 jumps are CL rounds of an
exact rebuild loop: same kind, same t, same view after masking numbers >= 1000, and the masked numbers growing as an
arithmetic progression with nonzero step.  Logged to loopkill.txt (id, reason).  Stops when qstop2 exists."""
import re, time, subprocess
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda f: os.path.join(BASE, f)
open(P('pids.txt'), 'a').write('%d driver loopwatch.py %s\n' % (os.getpid(), time.strftime('%m-%d %H:%M:%S')))
NUM = re.compile(r'\d+')
def outmap():
    d = {}
    for f in ('prio.txt', 'queue.txt'):
        if os.path.exists(P(f)):
            for l in open(P(f)):
                p = l.rstrip('\n').split('\t')
                if len(p) >= 5: d[p[0]] = P(p[1])
    return d
def is_loop(path):
    """exact rebuild loop: for some period p <= 6, the last 3p jumps have identical masked views/kinds/t with period p,
    and every number >= 1000 grows by a constant nonzero step per period."""
    try: L = [l for l in open(path, errors='replace') if l.startswith('J')]
    except OSError: return None
    for per in range(1, 7):
        n = 3 * per
        if len(L) < n + 4: continue
        last = L[-n:]; shapes = []; bigs = []
        for l in last:
            f = l.split()
            t = [x for x in f if x.startswith('t=')][0]
            view = l.split('|', 1)[1].strip() if '|' in l else ''
            bigs.append(tuple(int(x) for x in NUM.findall(view) if int(x) >= 1000))
            shapes.append((f[1], t, NUM.sub(lambda m: 'X' if int(m.group()) >= 1000 else m.group(), view)))
        if any(shapes[i] != shapes[i + per] for i in range(n - per)): continue
        if not any(bigs): continue
        ok = True; grow = False
        for i in range(per):
            for c in range(len(bigs[i])):
                d1 = bigs[i + per][c] - bigs[i][c]; d2 = bigs[i + 2 * per][c] - bigs[i + per][c]
                if d1 != d2 or d1 < 0: ok = False
                if d1 > 0: grow = True
        if ok and grow: return 'rebuild loop per=%d %s last %s' % (per, shapes[-1][1], bigs[-1])
    return None
killed = set(l.split()[0] for l in open(P('loopkill.txt'))) if os.path.exists(P('loopkill.txt')) else set()
while not os.path.exists(P('qstop2')):
    om = outmap(); latest = {}
    for l in open(P('pids.txt')):
        f = l.split()
        if len(f) >= 3 and f[1] == 'qrun': latest[f[2]] = int(f[0])
    dn = set(l.split()[0] for l in open(P('qdone.txt'))) if os.path.exists(P('qdone.txt')) else set()
    for jid, pid in latest.items():
        if jid in killed or jid not in om or jid in dn: continue
        o = subprocess.run(['tasklist', '/FI', 'PID eq %d' % pid, '/FO', 'CSV', '/NH'], capture_output=True, text=True).stdout
        if 'pkf8.exe' not in o.lower(): continue
        why = is_loop(om[jid])
        if why:
            subprocess.call(['taskkill', '/PID', str(pid), '/F'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            open(P('loopkill.txt'), 'a').write('%s\t%s\t%s\n' % (jid, time.strftime('%m-%d %H:%M:%S'), why)); killed.add(jid)
    time.sleep(10)
