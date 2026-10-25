"""zscreen.py LIST OUTTSV NPAR TEMPLATE "WORLD" : run zfg6 on each machine of LIST ('name machine'), one summary line each:
name machine outcome(H slot / T / ...) jumps zeros-seq(compressed) ones.  PIDs -> ../pids.txt."""
import subprocess, sys, os, re, time
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
lst, outp, npar, tmpl, world = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4], sys.argv[5].split()
EXTRA = os.environ.get('Z_EXTRA', '--jumps 300 --maxs 2e9 --maxtotal 1e10 --quiet').split()
jobs = [l.split()[:2] for l in open(lst) if l.strip()]
done = set(l.split('\t')[0] for l in open(outp)) if os.path.exists(outp) else set()
jobs = [j for j in jobs if j[0] not in done]
fo = open(outp, 'a'); pidf = open(os.path.join(BASE, 'pids.txt'), 'a'); running = []
def comp(z):
    c = []
    for k in z:
        if c and c[-1][0] == k: c[-1][1] += 1
        else: c.append([k, 1])
    s = ' '.join(k if n == 1 else '%sx%d' % (k, n) for k, n in c)
    return s if len(s) < 300 else s[:100] + ' ... ' + s[-180:]
while jobs or running:
    while jobs and len(running) < npar:
        name, m = jobs.pop(0); tmp = outp + '.tmp_' + name
        p = subprocess.Popen([os.path.join(BASE, os.environ.get('Z_EXE', 'zfg6.exe')), m, tmpl] + world + EXTRA, stdout=open(tmp, 'w'), stderr=subprocess.STDOUT)
        pidf.write('%d zscreen %s\n' % (p.pid, name)); pidf.flush(); running.append((p, name, m, tmp))
    time.sleep(0.5)
    for r in running[:]:
        if r[0].poll() is None: continue
        running.remove(r); txt = open(r[3], errors='replace').read(); os.remove(r[3])
        leaf = [l for l in txt.splitlines() if l.startswith('LEAF')]
        if leaf:
            L = leaf[-1]; f = L.split(); outc = ' '.join(f[2:4]) if f[2] == 'H' else f[2]
            zm = re.search(r'zeros=\[([^\]]*)\]', L); z = zm.group(1).split(',') if zm and zm.group(1) else []
            om = re.search(r'ones=(\d+)', L); ones = om.group(1) if om else ''
        else: outc, z, ones = 'NOLEAF:' + (txt.strip().splitlines() or ['?'])[-1][:60], [], ''
        fo.write('\t'.join([r[1], r[2], outc, str(len(z)), comp(z), ones]) + '\n'); fo.flush()
print('done', flush=True)
