import sys, threading
sys.setrecursionlimit(30000); threading.stack_size(64*1024*1024)
import fam, mfx
BASES = {l.split()[0]: l.split()[1:] for l in open('bases.txt') if l.strip() and not l.startswith('#')}
lbl = sys.argv[1]; m = sys.argv[2]; b0s = [int(x) for x in sys.argv[3].split(',')]; st = int(sys.argv[4]) if len(sys.argv)>4 else 40
base, t, n = BASES[lbl]
fam.register(lbl, base, t, int(n))
def main():
    for b in b0s:
        fam.start(lbl, b)
        r = mfx.screen(lbl, m, st, 3_000_000, b0=b)
        print(f"b0={b} A={r['kind']} B={r['kindB']} stages={r['stages']} cycles={r['cycles']} grow={r['grow']}")
        for x, y in zip(r['histA'], r['histB'] + [''] * 99): print('   A:', x, ' | B:', y)
th = threading.Thread(target=main); th.start(); th.join()
