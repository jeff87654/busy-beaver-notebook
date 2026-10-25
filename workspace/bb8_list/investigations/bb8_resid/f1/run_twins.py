import subprocess, os, sys
D = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(D)
env = dict(os.environ, CTX_FARS='c04', CTX_P='60,61,62', CTX_K='18,24,12,42,6')
tw = {'t_0LH_0RC': '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LH0LC_1RG1LD_0RG0RF_0RC---', 't_0LH_1RD': '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LH0LC_1RG1LD_0RG0RF_1RD---',
      't_1LH_0RB': '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_1RG1LD_0RG0RF_0RB---', 't_1LH_0RE': '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_1RG1LD_0RG0RF_0RE---'}
for name, m in tw.items():
    p = subprocess.Popen([sys.executable, os.path.join(D, 'ctx.py'), m, os.path.join(D, 'ctx_%s.tsv' % name), '1'], env=env)
    open(os.path.join(BASE, 'pids.txt'), 'a').write('%d run_twins ctx.py %s\n' % (p.pid, name)); p.wait()
