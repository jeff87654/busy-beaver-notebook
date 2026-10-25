"""verify_all.py : re-run every symbolic check of the F89 odd-mode rule set (msim lemmas + small-K + symsim) and print PASS/FAIL."""
import subprocess, sys, os
H = os.path.dirname(os.path.abspath(__file__))
def run(args, env=None):
    e = dict(os.environ); e.update(env or {})
    p = subprocess.run([sys.executable] + args, cwd=H, capture_output=True, text=True, env=e)
    return p.stdout + p.stderr
ok = True
out = run(['lemS.py']); print(out.strip())
ok &= 'S1 (True' in out and 'S2 (True' in out and 'S3 [1, 1^{x-1}, 1, 1]' in out
out = run(['lemB0.py']); print(out.strip())
ok &= all(('%s (True' % n) in out for n in ('B1', 'B2', 'B2r2', 'B2r1')) and 'B3 [1^{k+2}, 1, 1, 2*a+5, 2*d+1] rnew 0' in out and 'D [2*a+5, 2*b+1] rnew 0' in out
ok &= out.count('rnew=0') == 4
out = run(['lemB.py']); print(out.strip())
ok &= all(('%s (True' % n) in out for n in ('B1', 'B2', 'B2r2', 'B2r1')) and out.count('B3 rest') == 3
out = run(['lemT.py']); print(out.strip())
ok &= all(('%s (True' % n) in out for n in ('T1', 'T2', 'T2r2', 'T2r1')) and 'T3 2*a+4 [1^{k+2}, 1, 2*a+5]' in out
out = run(['msmall.py']); print(out.strip().splitlines()[-1])
ok &= 'bad 1' in out and out.count('FAIL') == 1 and 'FAIL [2*a+1]' in out   # the one FAIL = S, which needs lemS
out = run(['symtest.py'], {'HLB': '5'}); print(out.strip().splitlines()[-1])
ok &= 'fail 18' in out   # the 18 = symbolic-k / S cases symsim cannot do (covered by msim lemmas)
out = run(['symtest2.py'], {'HLB': '5'}); print(out.strip().splitlines()[-1])
ok &= 'fail 0' in out
print('VERIFY_ALL', 'PASS' if ok else 'FAIL')
