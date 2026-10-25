import subprocess, os, sys, time
D = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(D)
env = dict(os.environ, CTX_FARS='c04,sm')
items = [('M8', '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_1RG1LD_0RG0RF_1RG---')] + [tuple(l.split()) for l in open(os.path.join(D, 'halters.txt')) if l.strip()]
for name, m in items:
    p = subprocess.Popen([sys.executable, os.path.join(D, 'ctx.py'), m, os.path.join(D, 'ctx_%s.tsv' % name), '2'], env=env)
    open(os.path.join(BASE, 'pids.txt'), 'a').write('%d run_halters ctx.py %s\n' % (p.pid, name)); p.wait()
