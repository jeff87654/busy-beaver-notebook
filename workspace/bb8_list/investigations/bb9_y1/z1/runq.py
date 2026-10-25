# runq.py OUT PAR cmd1 ;; cmd2 ;; ... : run command lines (exe + args, ';;'-separated), PAR at a time at Idle priority,
# real PIDs -> ../pids.txt, output appended to OUT with '== cmd' headers.
import subprocess, sys, os, time
HERE = os.path.dirname(os.path.abspath(__file__))
out, par = sys.argv[1], int(sys.argv[2])
cmds = [c.split() for c in ' '.join(sys.argv[3:]).split(';;') if c.strip()]
IDLE = 0x00000040
live = []; f = open(out, 'a')
while cmds or live:
    while cmds and len(live) < par:
        c = cmds.pop(0); tmp = open(out + '.tmp%d' % len(cmds), 'w+')
        p = subprocess.Popen(c, stdout=tmp, stderr=subprocess.STDOUT, text=True, creationflags=IDLE, cwd=HERE)
        open(os.path.join(os.path.dirname(HERE), 'pids.txt'), 'a').write('%s %d z1 %s\n' % (time.strftime('%m-%d %H:%M:%S'), p.pid, ' '.join(c)[-120:]))
        live.append((p, c, tmp))
    for x in live[:]:
        p, c, tmp = x
        if p.poll() is None: continue
        live.remove(x); tmp.seek(0); f.write('== %s\n%s\n' % (' '.join(c), tmp.read())); f.flush(); tmp.close(); os.remove(tmp.name)
    time.sleep(0.5)
