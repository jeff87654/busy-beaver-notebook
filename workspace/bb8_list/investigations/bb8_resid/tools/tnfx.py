"""tnfx.py: TNF-style branching of a parent machine's free slots under pkf6 (jump-accelerated follower).
usage: python tnfx.py OUTDIR NPAR "WORLD ARGS" PARENT [PARENT...]
A machine is run with pkf6; if it halts by reading an undefined slot listed in BRANCH (env, default all undefined slots of
states >= FIRSTNEW, env FIRSTNEW=I) and some other undefined slot remains, the slot is set to each of the 2*2*n values and
the children are queued (the halting run itself is recorded as a leaf too).  One line per run -> OUTDIR/tree.tsv:
name machine outcome jumps esc ones depths last.  pkf6 PIDs -> ../pids.txt (real Windows PIDs from Popen)."""
import subprocess, sys, os, re, time
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
outdir, npar, wargs = sys.argv[1], int(sys.argv[2]), sys.argv[3].split()
parents = sys.argv[4:]
EXTRA = os.environ.get('TNF_EXTRA', '--jumps 400 --maxt 1e10 --maxs 2e9 --rcap 1000000 --view 300').split()
FIRSTNEW = ord(os.environ.get('FIRSTNEW', 'I')) - 65
os.makedirs(outdir, exist_ok=True)
tree = open(os.path.join(outdir, 'tree.tsv'), 'a'); pidf = open(os.path.join(BASE, 'pids.txt'), 'a')
def slots(m):
    rows = m.split('_'); return [(q, c) for q in range(len(rows)) for c in range(2) if rows[q][3*c] == '-']
def setslot(m, q, c, v):
    rows = m.split('_'); rows[q] = rows[q][:3*c] + v + rows[q][3*c+3:]; return '_'.join(rows)
def summarize(path):
    ks, Rs, esc, out, ones, last, nj, maxR = [], [], 0, 'RUNNING', '', '', 0, 0
    for l in open(path, errors='replace'):
        if l.startswith('J'):
            nj += 1
            mk = re.search(r' k=(\d+) (?:m=\d+ )?R=(\d+)', l)
            if mk:
                k, R = int(mk.group(1)), int(mk.group(2))
                if Rs and k > max(ks) and k >= 0.9 * maxR: esc += 1
                ks.append(k); Rs.append(R); maxR = max(maxR, R)
            last = l.split('|', 1)[1].strip()[:150] if '|' in l else ''
        elif l.startswith('HALT'): out = 'HALT ' + l.split()[1]; mo = re.search(r'ones (\d+)', l); ones = mo.group(1) if mo else ''
        elif l.startswith('STOP'): out = 'STOP'
        elif l.startswith('END'): out = 'END'
        elif l.startswith('RCAP'): out = 'RCAP'
        elif 'bad_alloc' in l: out = 'BADALLOC'
    comp = []
    for k in ks:
        if comp and comp[-1][0] == k: comp[-1][1] += 1
        else: comp.append([k, 1])
    ds = ' '.join('%d' % k if c == 1 else '%dx%d' % (k, c) for k, c in comp)
    if len(ds) > 200: ds = ds[:80] + ' ... ' + ds[-110:]
    return out, nj, esc, ones, ds, last
queue = [('P%d' % i, p) for i, p in enumerate(parents)]
done = set(l.split('\t')[1] for l in open(os.path.join(outdir, 'tree.tsv')) if '\t' in l) if os.path.exists(os.path.join(outdir, 'tree.tsv')) else set()
running = []
while queue or running:
    while queue and len(running) < npar:
        name, m = queue.pop(0)
        if m in done: continue
        done.add(m)
        path = os.path.join(outdir, re.sub(r'[^A-Za-z0-9_]', '', name) + '.txt')
        fo = open(path, 'w')
        p = subprocess.Popen([os.path.join(BASE, os.environ.get('SCR_EXE', 'pkf6.exe')), m] + wargs + EXTRA, stdout=fo, stderr=subprocess.STDOUT)
        pidf.write('%d tnfx %s %s %s\n' % (p.pid, outdir, name, time.strftime('%H:%M:%S'))); pidf.flush()
        running.append((p, fo, name, m, path))
    time.sleep(0.5)
    for r in running[:]:
        if r[0].poll() is None: continue
        r[1].close(); running.remove(r)
        p, fo, name, m, path = r
        out, nj, esc, ones, ds, last = summarize(path)
        tree.write('\t'.join([name, m, out, str(nj), str(esc), ones, ds, last]) + '\n'); tree.flush()
        if out.startswith('HALT'):
            q, c = ord(out[5]) - 65, int(out[6])
            und = slots(m)
            if q >= FIRSTNEW and (q, c) in und and len(und) >= 2:
                n = len(m.split('_'))
                for v in [w + d + chr(65 + s) for w in '01' for d in 'LR' for s in range(n)]:
                    queue.append((name + '.' + chr(65 + q) + str(c) + v, setslot(m, q, c, v)))
print('done', flush=True)
