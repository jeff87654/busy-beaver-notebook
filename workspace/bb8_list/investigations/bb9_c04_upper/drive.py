# drive.py: run pkf5.exe on a list of (label, kt, Rlist, R, jumps) jobs, at most 2 at a time; record child PIDs in pids.txt.
# Output: runs/<out>.txt with "== label" headers, all J lines (kind, t, k, R | view) and the HALT/END/STOP line.
import subprocess, sys, os, json, time
M = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_0RG1LD_0LH1LH_1RI---_0RI0RF'
HERE = os.path.dirname(os.path.abspath(__file__))
def cmd(kt, rlist, R, jumps, view=900):
    return [os.path.join(HERE, 'pkf5.exe'), M, '--kt', kt, '--Rlist', rlist, '--R', str(R), '--rmod', '36', '--exactcap', '1000',
            '--jumps', str(jumps), '--view', str(view), '--maxs', '5e11', '--maxt', '5e12']
def fmt(line):
    if line.startswith('J'):
        head, _, view = line.partition('|'); a = head.split()
        rin = a[8] if len(a) > 8 and a[8].startswith('rin') else ''
        return '%s %s %s %s %s %s %s |%s' % (a[0], a[1], a[4], a[5], a[6], a[7], rin, view.rstrip('\n'))
    return line.rstrip('\n')
def run(jobs, out, par=2):
    f = open(os.path.join(HERE, 'runs', out), 'a'); pending = list(jobs); live = []
    while pending or live:
        while pending and len(live) < par:
            lab, kt, rl, R, J = pending.pop(0)
            tmp = open(os.path.join(HERE, 'runs', 'tmp_%d.out' % len(pending)), 'w+'); p = subprocess.Popen(cmd(kt, rl, R, J), stdout=tmp, text=True); p.tmp = tmp
            open(os.path.join(HERE, 'pids.txt'), 'a').write('%d pkf4 %s %s\n' % (p.pid, out, lab))
            live.append((lab, p))
        for lab, p in list(live):
            if p.poll() is not None:
                p.tmp.seek(0); lines = [fmt(l) for l in p.tmp if l.startswith('J') or l.split()[:1] in (['HALT'], ['STOP'], ['END'])]
                f.write('== %s\n' % lab + '\n'.join(lines) + '\n'); f.flush(); live.remove((lab, p))
        time.sleep(0.2)
if __name__ == '__main__':
    spec = json.load(open(sys.argv[1])); run([tuple(j) for j in spec['jobs']], spec['out'])
