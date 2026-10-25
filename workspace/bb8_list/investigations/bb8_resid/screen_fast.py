"""screen.py LIST WORLD [NPAR] : run pkf6 on every machine of LIST (lines "name machine ...") in an order-faithful world.
WORLD = name:args, e.g.  w1:"--B 126 --rk 1 --rc 20"   (written to runs/scr_<name>/<machine-name>.txt)
Summary -> runs/scr_<name>/summary.tsv : name, outcome, jumps, #esc, depth list (compressed), halt ones, last view.
Escalation = a CL whose depth k is a new record and >= 0.9 * max(R of all earlier CLs) (a list built from an accumulator).
PIDs of the pkf6 children are appended to pids.txt (pkf6 sets Idle priority itself)."""
import subprocess, sys, os, time, re
LIST, WORLD = sys.argv[1], sys.argv[2]
NPAR = int(sys.argv[3]) if len(sys.argv) > 3 else 2
wname, wargs = WORLD.split(':', 1)
BASE = os.path.dirname(os.path.abspath(__file__))
odir = os.path.join(BASE, 'runs', 'scr_' + wname); os.makedirs(odir, exist_ok=True)
EXTRA = os.environ.get('SCR_EXTRA', '--jumps 400 --maxt 2e10 --maxs 1e10 --rcap 60000 --view 300')
jobs = []
for ln in (open(LIST) if LIST != '--resum' else []):
    f = ln.split()
    if len(f) >= 2 and not ln.startswith('#'): jobs.append((f[0], f[1], f[2] if len(f) > 2 else ''))

def summarize(name, m, path):
    ks, Rs, esc, out, ones, last, nj = [], [], 0, 'RUNNING', '', '', 0
    maxR = 0
    for l in open(path, errors='replace'):
        if l.startswith('  J'): l = l[2:]
        if l.startswith('LEAF') and ' H ' in l: out = 'HALT ' + l.split(' H ')[1].split()[0]; mo = re.search(r'ones=(\d+)', l); ones = mo.group(1) if mo else ''; continue
        if l.startswith('LEAF') and ' T @' in l: out = 'STOP'; continue
        if l.startswith('LEAF') and ' RCAP' in l: continue
        if l.startswith('  TAPE'): last = l.split('|', 1)[1].strip()[:150]; continue
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
        elif l.startswith('RCAP'): out = 'RCAP'; esc += 1; last = l.split('|', 1)[1].strip()[:150]
        elif l.startswith('  tape:') and out.startswith(('HALT', 'STOP')): last = l.split(':', 1)[1].strip()[:150]
    # compress depth list
    comp = []
    for k in ks:
        if comp and comp[-1][0] == k: comp[-1][1] += 1
        else: comp.append([k, 1])
    ds = ' '.join('%d' % k if c == 1 else '%dx%d' % (k, c) for k, c in comp)
    if len(ds) > 200: ds = ds[:80] + ' ... ' + ds[-110:]
    return '\t'.join([name, out, str(nj), str(esc), ones, ds, last, m])

if LIST == '--resum':
    for fn in sorted(os.listdir(odir)):
        if fn.endswith('.txt'): print(summarize(fn[:-4], '', os.path.join(odir, fn)))
    sys.exit()
running = []; done = []; t0 = {}
summ = open(os.path.join(odir, 'summary.tsv'), 'a')
pidf = open(os.path.join(BASE, 'pids.txt'), 'a')
i = 0
while i < len(jobs) or running:
    while i < len(jobs) and len(running) < NPAR:
        name, m, tmpl = jobs[i]; i += 1
        path = os.path.join(odir, name + '.txt')
        fo = open(path, 'w')
        cmd = [os.path.join(BASE, os.environ.get('SCR_EXE', 'pkf6.exe')), m] if not tmpl else [os.path.join(BASE, 'zfg6.exe'), m, tmpl, '--alljumps']
        p = subprocess.Popen(cmd + wargs.split() + EXTRA.split(), stdout=fo, stderr=subprocess.STDOUT)
        pidf.write('%d screen.py %s %s %s\n' % (p.pid, wname, name, time.strftime('%H:%M:%S'))); pidf.flush()
        running.append((p, fo, name, m, path)); t0[p.pid] = time.time()
    time.sleep(0.03)
    for r in running[:]:
        if r[0].poll() is None and time.time() - t0.get(r[0].pid, time.time()) > float(os.environ.get('SCR_WALL', '1e9')):
            r[0].kill(); r[0].wait()
        if r[0].poll() is not None:
            r[1].close(); running.remove(r)
            summ.write(summarize(r[2], r[3], r[4]) + '\n'); summ.flush()
print('done', len(jobs))
