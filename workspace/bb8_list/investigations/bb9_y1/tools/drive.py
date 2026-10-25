# drive.py SPEC.json : run pkf6.exe jobs (at most PAR at a time, Idle priority is set by pkf6 itself), record real PIDs.
# spec = {"out": "name.txt", "par": 3, "machine": "...", "jobs": [[label, [extra pkf6 args...]], ...]}
# Output: runs/<out> with "== label" headers, compacted J lines and the HALT/END/STOP lines (+ tape line).
import subprocess, sys, os, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(HERE)
Y1 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_1RG1LD_0RG0RF_1RG0LI_0RA---'
def fmt(line):
    if line.startswith('J'):
        head, _, view = line.partition('|'); a = head.split()
        keep = [x for x in a if not x.startswith(('step=', 'seg=', 'used='))]
        return ' '.join(keep) + ' |' + view.rstrip('\n')
    return line.rstrip('\n')
def run(spec):
    out = os.path.join(BASE, 'runs', spec['out']); par = spec.get('par', 3); M = spec.get('machine', Y1)
    exe = os.path.join(HERE, spec.get('exe', 'pkf6.exe'))
    f = open(out, 'a'); pending = list(spec['jobs']); live = []; n = 0
    while pending or live:
        while pending and len(live) < par:
            lab, args = pending.pop(0); n += 1
            tmpn = out + '.tmp%d' % n; tmp = open(tmpn, 'w+')
            p = subprocess.Popen([exe, M] + [str(a) for a in args], stdout=tmp, stderr=subprocess.STDOUT, text=True)
            p.tmp = tmp; p.tmpn = tmpn
            open(os.path.join(BASE, 'pids.txt'), 'a').write('%s %d pkf6 %s %s\n' % (time.strftime('%m-%d %H:%M:%S'), p.pid, spec['out'], lab))
            live.append((lab, p))
        for lab, p in list(live):
            if p.poll() is not None:
                p.tmp.seek(0); lines = []
                for l in p.tmp:
                    if l.startswith('J') or l.split()[:1] in (['HALT'], ['STOP'], ['END'], ['RCAP'], ['zeros:']) or l.startswith('  tape') or l.startswith('DUMP') or l.startswith('POST') or l.startswith("  SNAP") or l.startswith("H1EV") or l.startswith("FG"):
                        lines.append(fmt(l))
                f.write('== %s\n' % lab + '\n'.join(lines) + '\n'); f.flush(); p.tmp.close(); os.remove(p.tmpn); live.remove((lab, p))
        time.sleep(0.2)
if __name__ == '__main__':
    run(json.load(open(sys.argv[1])))
