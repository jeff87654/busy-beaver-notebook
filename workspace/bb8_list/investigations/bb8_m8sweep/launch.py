"""launch.py: run commands in parallel (max N), Idle priority, PIDs appended to pids.txt (also its own).
usage: python launch.py JOBFILE N   (JOBFILE lines: outfile<TAB>command line)"""
import subprocess, sys, time, os
HERE = os.path.dirname(os.path.abspath(__file__))
jobs = [l.rstrip('\n').split('\t', 1) for l in open(sys.argv[1]) if l.strip() and not l.startswith('#')]
N = int(sys.argv[2]); run = []
pf = open(os.path.join(HERE, 'pids.txt'), 'a')
pf.write('%d\t%s\tlaunch.py %s\n' % (os.getpid(), time.strftime('%Y-%m-%d %H:%M:%S'), sys.argv[1])); pf.flush()
while jobs or run:
    while jobs and len(run) < N:
        out, cmd = jobs.pop(0)
        f = open(out, 'w')
        p = subprocess.Popen(cmd, shell=False, stdout=f, stderr=subprocess.STDOUT, creationflags=0x40 | 0x08000000, cwd=HERE)
        pf.write('%d\t%s\t%s\n' % (p.pid, time.strftime('%Y-%m-%d %H:%M:%S'), cmd[:200])); pf.flush()
        run.append((p, f))
    time.sleep(0.5)
    for p, f in run[:]:
        if p.poll() is not None:
            f.close(); run.remove((p, f))
