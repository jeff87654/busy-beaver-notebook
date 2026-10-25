import sys, threading
sys.setrecursionlimit(30000); threading.stack_size(64*1024*1024)
import fam, mfx
BASES = {l.split()[0]: l.split()[1:] for l in open('bases.txt') if l.strip() and not l.startswith('#')}
lbl, m, b0, st, M = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
maxs = int(float(sys.argv[6])) if len(sys.argv) > 6 else 1_000_000_000
base, t, n = BASES[lbl]; fam.register(lbl, base, t, int(n)); fam.start(lbl, b0)
m10 = m + '_------' * (9 - m.count('_'))
def main():
    k, h = mfx.follow(lbl, m10, st, maxs, b0, M, 19, ordered=True, verbose=True)
    print('RESULT', k); print('\n'.join(h))
th = threading.Thread(target=main); th.start(); th.join()
