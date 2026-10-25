import idle
"""Dependency-aware compile scheduler for bb9_h003_coq (x/ and h/).  python sched.py CAP [file.v ...]
Builds every .v under x/ and h/ (or only the listed ones and what they need) whose .vo is missing or older than
the .v or than a dependency's .vo; at most CAP of MY coqc processes (pids.txt) alive at once; longest first.
A failed file stops its dependents.  Log: logs/sched.txt.  Each compile goes through cq.py (Idle priority)."""
import subprocess, sys, time, os, re
from pathlib import Path
W = Path(__file__).resolve().parents[1]
LOG = open(W / 'logs' / 'sched.txt', 'a')
def log(m):
    LOG.write('%s %s\n' % (time.strftime('%H:%M:%S'), m)); LOG.flush()
with open(W / 'pids.txt', 'a') as f:
    f.write('%d sched %s\n' % (os.getpid(), time.strftime('%Y-%m-%d %H:%M:%S')))
LOGI = {'XL': W / 'x' / 'lib', 'XDev': W / 'x' / 'dev', 'XK31': W / 'x' / 'k31', 'XScore': W / 'x' / 'score',
        'XFgh': W / 'x' / 'fgh', 'H3': W / 'h'}
EST = {'K_e1': 7100, 'G_sub2': 3600, 'K_e2': 2200, 'G_entry': 2000, 'G_sub4': 1900, 'G_sub5': 1700, 'G_sub3': 1600,
       'G_stop': 760, 'G_xtop': 700, 'G_p20_5': 700, 'G_p20_4': 700, 'G_p20_3': 600, 'G_p20_2': 550, 'G_p20_1': 500,
       'G_p20_0': 480, 'G_p14_5': 400, 'G_p14_4': 380, 'G_p14_3': 360, 'G_p14_2': 355, 'G_p14_1': 335, 'G_p14_0': 320,
       'G_xreb2': 300, 'G_xreb1': 250, 'K_x': 300, 'G_rules': 150, 'G_end': 100, 'K_rf': 90, 'Abs': 110}
PRIO = {'HFinal', 'HScore', 'HGoal', 'Final', 'Statement', 'probe', 'G_xt1', 'G_t1_T1a1', 'G_t1_T1a2a', 'G_t1_YR', 'G_t1_YE', 'G_t1_T1b', 'Res', 'KStep', 'HArith', 'HPhB', 'HTop', 'Ones', 'Defs', 'Sim', 'Orbit', 'G_rules', 'Abs', 'Lift', 'G_tops_P4b', 'G_tops_P3', 'G_tops_P4', 'G_tops_TXa', 'G_t1', 'G_top1', 'G_pbab', 'G_pbc', 'Score'}   # short, needed early
def deps(v):
    s = v.read_text(encoding='utf-8')
    out = []
    for m in re.finditer(r'From\s+(\w+)\s+Require\s+(?:Import\s+|Export\s+)?([^.]*)\.', s):
        d = LOGI.get(m.group(1))
        if d is None: continue
        for name in m.group(2).split():
            p = d / (name + '.v')
            if p.exists(): out.append(p)
    return out
allv = sorted((W / 'x').glob('*/*.v')) + sorted((W / 'h').glob('*.v'))
want = set(allv) if len(sys.argv) <= 2 else set()
if len(sys.argv) > 2:
    todo = [Path(a).resolve() for a in sys.argv[2:]]
    while todo:
        v = todo.pop()
        if v in want: continue
        want.add(v); todo += deps(v)
D = {v: deps(v) for v in want}
def vo(v): return v.with_suffix('.vo')
def stale(v, memo={}):
    if v in memo: return memo[v]
    r = (not vo(v).exists()) or vo(v).stat().st_mtime < v.stat().st_mtime or \
        any(stale(d) or vo(d).stat().st_mtime > vo(v).stat().st_mtime for d in D.get(v, []) if d in D)
    memo[v] = r; return r
pending = {v for v in want if stale(v)}
done_ok = {v for v in want if v not in pending}
failed = set(); running = {}
def live_pids():
    tl = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq coqc.exe', '/FO', 'CSV', '/NH'], capture_output=True, text=True).stdout
    return {int(x.split('","')[1]) for x in tl.strip().splitlines() if x.startswith('"coqc')}
class Ext:                                          # a compile of mine already running (started by an earlier run)
    def __init__(self, pid): self.pid = pid
    def poll(self): return None if self.pid in live_pids() else 0
LP = live_pids()
for l in open(W / 'pids.txt'):
    f = l.split()
    if len(f) > 2 and f[1] == 'coqc' and int(f[0]) in LP:
        v = Path(f[2])
        if v in pending:
            pending.discard(v); running[v] = Ext(int(f[0])); log('adopted running %s (pid %s)' % (v.stem, f[0]))
log('START %d to build: %s' % (len(pending), ' '.join(v.stem for v in sorted(pending))))
def alive():
    pids = [int(l.split()[0]) for l in open(W / 'pids.txt') if ' coqc ' in l]
    tl = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq coqc.exe', '/FO', 'CSV', '/NH'], capture_output=True, text=True).stdout
    live = {int(x.split('","')[1]) for x in tl.strip().splitlines() if x.startswith('"coqc')}
    return len([p for p in pids if p in live])
CAP = int(sys.argv[1])
while pending or running:
    for v, p in list(running.items()):
        if p.poll() is not None:
            dn = W / 'logs' / (v.parent.name + '_' + v.stem + '.done')
            for _ in range(30):
                if dn.exists(): break
                time.sleep(2)
            res = dn.read_text().strip() if dn.exists() else 'exit ? (no .done)'
            log('%s %s' % (v.stem, res))
            del running[v]
            (done_ok if res.startswith('exit 0') else failed).add(v)
    blocked = {v for v in pending if any(d in failed for d in D[v])}
    for v in blocked:
        log('BLOCKED %s' % v.stem); failed.add(v)
    pending -= blocked
    ready = sorted([v for v in pending if all(d in done_ok or d not in D for d in D[v])], key=lambda v: (v.stem not in PRIO, -EST.get(v.stem, 60)))
    if ready and alive() < CAP:
        v = ready[0]; pending.discard(v)
        running[v] = subprocess.Popen([sys.executable, str(W / 'tools' / 'cq.py'), str(v)], stdout=subprocess.DEVNULL)
        log('start %s' % v.stem); time.sleep(5); continue
    if not running and not ready and pending:
        log('STUCK: %s' % ' '.join(v.stem for v in pending)); break
    time.sleep(15)
log('DONE ok=%d failed=%s' % (len(done_ok), ' '.join(v.stem for v in failed)))
