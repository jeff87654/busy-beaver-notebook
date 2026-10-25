"""Boot search 2: 5-state boot tables within Hamming distance <= D of Wade's (transitions changed),
one transition is the exit (w,d,X) into a framework state the program needs anyway (no 6.continue.4).
Accept iff the run reaches main().0 with: marker, P=[] (only zeros up to registers), clean register file
(runs separated by single 0), last 11 runs '1', nothing left of the marker. Reports gap."""
import sys, itertools, time, re
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\zf\framework\fwmin')
import lowprio_local
from common import *
from tmfast import *
D = int(sys.argv[1]) if len(sys.argv) > 1 else 2
z = zf2.ZF2(); z.AXIOMORDER = AXIOMORDER; z.build_machine()
start, base = from_tm(z.tm)
for s in '01': del base[('6.continue.4', s)]
BOOT = ['0.boot.A','0.boot.B','0.boot.C','0.boot.D','0.boot.E']
fw = {k: v for k, v in base.items() if not k[0].startswith('0.boot')}
targets = sorted({s for s, _ in fw if s[0] in '123456'})
wade = {k: v for k, v in base.items() if k[0].startswith('0.boot')}
wade[('0.boot.D', '1')] = ('0', 'L', 'EXIT')
keys = [(s, r) for s in BOOT for r in '01']
opts = [(w, d, n) for w in '01' for d in 'LR' for n in BOOT + ['EXIT']]
MAXB = 200000

def runboot(bt):
    """Run boot table bt (EXIT = exit transition). Returns (tape,pos,exit_w,exit_d) or None."""
    tape = {}; pos = 0; st = '0.boot.A'; steps = 0
    while steps < MAXB:
        r = tape.get(pos, '0')
        w, d, n = bt[(st, r)]
        if n == 'EXIT': return tape, pos, r, st
        tape[pos] = w; pos += 1 if d == 'R' else -1; st = n; steps += 1
    return None

found = []; tried = 0; t0 = time.time()
for nchg in range(0, D + 1):
    for ks in itertools.combinations(keys, nchg):
        for vals in itertools.product(opts, repeat=nchg):
            bt = dict(wade)
            for k, v in zip(ks, vals): bt[k] = v
            if sum(1 for v in bt.values() if v[2] == 'EXIT') != 1: continue
            if any(bt[k] == wade[k] for k in ks): continue
            tried += 1
            r = runboot(bt)
            if r is None: continue
            tape0, pos0, rd, st = r
            # quick filter: need >= 11 isolated ones to the right somewhere
            hi = max(tape0); lo = min(tape0)
            tail = ''.join(tape0.get(i, '0') for i in range(max(lo, hi - 60), hi + 1)).rstrip('0')
            if not re.search(r'(?:^|0)(?:10){10}1$', tail): continue
            for w in '01':
                for d in 'LR':
                    for X in targets:
                        tape = dict(tape0); tape[pos0] = w; pos = pos0 + (1 if d == 'R' else -1)
                        rr = run_until(fw, X, 'main().0', 3000, tape, pos)
                        if rr is None: continue
                        ok, g, nr, why = boot_check(*rr[:2])
                        if ok:
                            found.append((g, nr, ks, vals, (st, rd), (w, d, X)))
                            print('FOUND gap', g, 'runs', nr, 'changes', list(zip(ks, vals)), 'exit from', (st, rd), '->', (w, d, X), flush=True)
    print('done nchg', nchg, 'tried', tried, 'found', len(found), 'time', round(time.time() - t0), flush=True)
