# val_halters.py: all m9s halting leaves (enum1, pass2, pass2I, mut2): symsim must HALT with m9s's exact sigma
import sys, subprocess, os, collections
D = os.path.dirname(os.path.abspath(__file__))
SYM = os.path.join(D, sys.argv[1] if len(sys.argv) > 1 else 'symsim.exe')
ref = [l.split() for l in open(os.path.join(D, 'val', 'halters_all.txt'))]
inp = ''.join(f'{r[0]} {r[1]}\n' for r in ref)
out = [l.split() for l in subprocess.run([SYM, 'run', '--budget', '200000'], input=inp, capture_output=True, text=True).stdout.split('\n') if l.startswith('R ')]
assert len(out) == len(ref)
C = collections.Counter(); bad = []
for r, o in zip(ref, out):
    sig = [x for x in o if x.startswith('sigma=')][0][6:]
    if o[3] != 'HALT': C['NOT-HALT ' + o[3]] += 1; bad.append((r, o[3:5])); continue
    if r[3] == '0': C['exact sigma ' + ('match' if sig == r[2] else 'MISMATCH') + (' (jumps)' if r[4] != '0' else '')] += 1
    else: C['m9s-representative halter, symbolic sigma'] += 1; print('  rep', r[0], r[1], 'm9s', r[2], 'symsim', sig)
    if r[3] == '0' and sig != r[2]: bad.append((r, sig))
for k, v in sorted(C.items()): print(f'{v:8d} {k}')
print('BAD', len(bad)); [print(' ', b) for b in bad[:20]]
