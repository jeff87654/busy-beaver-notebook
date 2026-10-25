import subprocess, os, sys
D = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(D)
env = dict(os.environ, CTX_FARS='c04', CTX_P='60,61', CTX_K='18,24,12')
L = open(os.path.join(D, 'growers.txt')).read().splitlines()
if os.environ.get('REV'): L = L[::-1]
for l in L:
    if not l.strip(): continue
    name, m = l.split()
    if os.path.exists(os.path.join(D, 'g_%s.tsv' % name)): continue
    p = subprocess.Popen([sys.executable, os.path.join(D, 'ctx.py'), m, os.path.join(D, 'g_%s.tsv' % name), '1'], env=env)
    open(os.path.join(BASE, 'pids.txt'), 'a').write('%d run_growers ctx.py %s\n' % (p.pid, name)); p.wait()
