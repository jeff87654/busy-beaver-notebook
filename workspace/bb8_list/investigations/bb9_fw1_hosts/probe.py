"""probe.py POOL OUT [WORKERS=2] [NSTATES=7,8,9]: base host-probe chains (hpc.exe MODE 1: keep O + first digit, a=0, b=b1)
from the blank tape, b1 = 3 and 4, 6 rounds, 2e7 steps per round. Appends one JSON line per machine to OUT
(resumable: machines already in OUT are skipped). PIDs -> pids.txt."""
import idle, subprocess, sys, json, re, os, threading
from concurrent.futures import ThreadPoolExecutor
H = os.path.dirname(os.path.abspath(__file__))
EXE = os.path.join(H, 'hpcw.exe'); ENV = dict(os.environ, HPC_WMAX=os.environ.get('HPC_WMAX', '20000'))
lock = threading.Lock()
def tmpl(t):
    o, q, rest = t.split(',', 2)
    d = dict(x.split('=', 1) for x in rest.split(','))
    al, be = map(int, re.fullmatch(r'(\d+)d\+(-?\d+)', d['d']).groups()); alB, beB = map(int, re.fullmatch(r'(\d+)b\+(-?\d+)', d['b']).groups())
    return dict(o=o, q=q, P=d['P'], u=d['u'], s=d['s'], al=al, be=be, alB=alB, beB=beB, S=d['S'])
def hpc(m, T, b1, word='-', pos=0, state='A', rounds=6, maxs=20000000, stab=6, minnd=2, mode=1, prw=1):
    cmd = [EXE, m, T['o'], T['q'], T['u'], T['s'], T['S'], str(T['be']), str(T['alB']), str(T['beB']), word, str(pos), state,
           str(b1), str(rounds), str(maxs), str(stab), str(minnd), str(mode), str(prw)]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True, creationflags=0x40, env=ENV)
    with lock:
        with open(os.path.join(H, 'pids.txt'), 'a') as f: f.write(f'{p.pid} hpc {m} b1={b1}\n')
    o = p.communicate()[0]
    return parse(o)
def parse(o):
    rs = []; ws = {}
    for l in o.splitlines():
        mm = re.match(r'R(\d+) (\d+) (-?\d+) (-?\d+) (-?\d+) \| n=(-?\d+) a=(-?\d+) b=(-?\d+) \|O\|=(\d+) O=\[(.*)\] d=(.*)$', l)
        if mm: rs.append(dict(r=int(mm[1]), st=int(mm[2]), lo=int(mm[3]), vis=int(mm[4]), hi=int(mm[5]), n=int(mm[6]), a=int(mm[7]), b=int(mm[8]), Ol=int(mm[9]), O=mm[10], d=mm[11])); continue
        mm = re.match(r'W(\d+) (-?\d+) (\S*)', l)
        if mm: ws[int(mm[1])] = (int(mm[2]), mm[3]); continue
        mm = re.match(r'R(\d+) HALT (\d+) state (\w) read (\d) lo (-?\d+) vis (-?\d+)', l)
        if mm: rs.append(dict(r=int(mm[1]), halt=mm[3] + mm[4], st=int(mm[2]), lo=int(mm[5]), vis=int(mm[6]))); continue
        mm = re.match(r'R(\d+) TIMEOUT lo (-?\d+) vis (-?\d+)', l)
        if mm: rs.append(dict(r=int(mm[1]), timeout=1, lo=int(mm[2]), vis=int(mm[3]))); continue
        mm = re.match(r'R(\d+) WIDE (\d+)', l)
        if mm: rs.append(dict(r=int(mm[1]), timeout=1, wide=int(mm[2]), lo=0, vis=0)); continue
    return rs, ws
def job(row, out):
    m, ns, src, grade, t = row
    try: T = tmpl(t)
    except Exception as e: res = dict(m=m, err=str(e))
    else:
        res = dict(m=m, ns=int(ns), src=src, grade=grade, t=t, ch={})
        for b1 in (3, 4):
            rs, ws = hpc(m, T, b1)
            res['ch'][b1] = rs
            if b1 == 3 and 0 in ws: res['w0'] = ws[0]
    with lock:
        with open(out, 'a') as f: f.write(json.dumps(res) + '\n')
if __name__ == '__main__':
    pool, out = sys.argv[1], sys.argv[2]; W = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    NS = set(sys.argv[4].split(',')) if len(sys.argv) > 4 else {'7', '8', '9'}
    done = set()
    if os.path.exists(out):
        for l in open(out): done.add(json.loads(l)['m'])
    rows = [l.rstrip('\n').split('\t') for l in open(pool)]
    rows = [r for r in rows if r[0] not in done and r[1] in NS]
    print(len(rows), 'to do', flush=True)
    with ThreadPoolExecutor(W) as ex:
        for r in rows: ex.submit(job, r, out)
