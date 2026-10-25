# ctlscan.py: run ngcps2 / ngann over window pairs for the base machines, 2 Idle workers, timeouts; log to ctlscan.tsv
import subprocess, sys, os, time, itertools, threading, queue
D = os.path.dirname(os.path.abspath(__file__))
M = dict(l.split() for l in open(os.path.join(D, 'machines.txt')) if l.strip())
def mirror(m):
    out = []
    for r in m.split('_'):
        s = ''
        for c in range(2):
            t = r[3*c:3*c+3]
            s += t if t[0] == '-' else t[0] + ('L' if t[1] == 'R' else 'R') + t[2]
        out.append(s)
    return '_'.join(out)
jobs = []
names = sys.argv[1].split(',')
for name in names:
    m = M[name]
    for s in range(6, 31):
        for nL in range(2, 17):
            nR = s - nL
            if 2 <= nR <= 16: jobs.append((s, name, 'ng', m, nL, nR))
    for kL in range(3, 11):
        for kR in range(3, 11):
            jobs.append((kL + kR + 3, name, 'ann', m, kL, kR))
            jobs.append((kL + kR + 3, name, 'annM', mirror(m), kL, kR))
jobs.sort()
TO = int(sys.argv[2]) if len(sys.argv) > 2 else 240
q = queue.Queue()
for j in jobs: q.put(j)
done = set(); lock = threading.Lock()
out = open(os.path.join(D, 'ctlscan.tsv'), 'a')
def worker():
    while True:
        try: s, name, kind, m, a, b = q.get_nowait()
        except queue.Empty: return
        with lock:
            if name in done: continue
        if kind == 'ng': cmd = [os.path.join(D, 'ngcps2.exe'), m, str(a), str(b)]
        else: cmd = [os.path.join(D, 'ngann.exe'), m, str(a), str(b), '2', '1']
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=0x40, text=True)
        with lock: open(os.path.join(D, 'pids.txt'), 'a').write(f"{p.pid} {' '.join(cmd[:1])} {name} {kind} {a} {b}\n")
        try: o, _ = p.communicate(timeout=TO); res = o.strip().splitlines()[-1] if o.strip() else 'EMPTY'
        except subprocess.TimeoutExpired: p.kill(); p.communicate(); res = 'TIMEOUT'
        with lock:
            out.write(f"{name}\t{kind}\t{a}\t{b}\t{res}\n"); out.flush()
            if 'NONHALT' in res: done.add(name)
ts = [threading.Thread(target=worker) for _ in range(2)]
for t in ts: t.start()
for t in ts: t.join()
