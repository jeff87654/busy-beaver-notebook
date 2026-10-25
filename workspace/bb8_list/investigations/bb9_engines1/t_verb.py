import sys, threading
sys.setrecursionlimit(30000); threading.stack_size(64*1024*1024)
import fam, mfx
BASES = {l.split()[0]: l.split()[1:] for l in open('bases.txt') if l.strip() and not l.startswith('#')}
lbl, m, b0, st, M, LB = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])
base, t, n = BASES[lbl]; fam.register(lbl, base, t, int(n)); fam.start(lbl, b0)
m10 = m + '_------' * (9 - m.count('_'))
def main():
    k, h = mfx.follow(lbl, m10, st, 30_000_000, b0, M, LB, verbose=True)
    print('RESULT', k, h[-1])
th = threading.Thread(target=main); th.start(); th.join()
