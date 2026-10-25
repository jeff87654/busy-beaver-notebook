# micro-benchmark: time of step' on TL1-like goal with big numerals
import subprocess, time, sys
head = open('../coq_head.v.in').read()
def mk(k, nsteps):
    return head + '''
Lemma bench : forall x l, ([0;0;1]^^(27 * x + kN %d) *> [1;1;1]^^(x + 1) *> l) {{E}}> (1 >> 0 >> 0 >> 1 >> 1 >> const 0) -->+ ([0;0;1]^^(27 * x + kN %d) *> l) {{E}}> (1 >> 0 >> 0 >> 1 >> 1 >> const 0).
Proof.
  intros. step1'. do %d step'.
Abort.
''' % (k, k + 7, nsteps)
for k, n in ((5, 18), (4083, 18), (40, 18)):
    open('B.v', 'w').write(mk(k, n))
    t = time.time()
    r = subprocess.run([sys.executable, 'coqc_scratch.py', 'B.v'], capture_output=True, text=True)
    print(k, n, r.stdout.strip()[-60:])
