"""Post-process bootenum output: for each exiting boot, try exit (w,d,X) into every framework state the
zf2 program needs anyway (no 6.continue.4); run until main().0; check the dispatch tape."""
import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\zf\framework\fwmin')
from common import *
from tmfast import *
z = zf2.ZF2(); z.AXIOMORDER = AXIOMORDER; z.build_machine()
start, base = from_tm(z.tm)
for s in '01': del base[('6.continue.4', s)]
fw = {k: v for k, v in base.items() if not k[0].startswith('0.boot')}
targets = sorted({s for s, _ in fw if s[0] in '123456'} | {'main().0'})
seen = set(); found = []
for line in open(sys.argv[1]):
    code, es, er, p, t = line.split()
    es, er, p = int(es), int(er), int(p)
    if t in seen and False: continue
    tape0 = {i: c for i, c in enumerate(t) if c == '1'}
    for w in '01':
        for d in 'LR':
            for X in targets:
                tape = dict(tape0); tape[p] = w; pos = p + (1 if d == 'R' else -1)
                if X == 'main().0': rr = (tape, pos, 0)
                else: rr = run_until(fw, X, 'main().0', 5000, tape, pos)
                if rr is None: continue
                if not rr[0]: continue
                ok, g, nr, why = boot_check(rr[0], rr[1])
                if ok:
                    found.append((g, nr, code, es, er, w, d, X))
for f in sorted(found, reverse=True): print(f)
print('found', len(found), file=sys.stderr)
