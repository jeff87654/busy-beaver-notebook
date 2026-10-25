"""cyc.py: exact cycle check (the configuration repeats exactly) from the champion's halting configuration.
  python cyc.py MACHINES.txt STARTS.txt STEPS     Prints CYCLE(period) / HALT / UNKNOWN per start."""
import sys
sys.path.insert(0, '.')
from kcls import parse
def check(M, word, head, q, N):
    t = parse(M); L = 1 << 20; off = L // 2
    tape = bytearray(L); tape[off:off+len(word)] = bytes(int(c) for c in word)
    h = off + head; seen = {}
    lo, hi = off - 2, off + len(word) + 2
    for n in range(N):
        lo = min(lo, h); hi = max(hi, h)
        key = (q, h, bytes(tape[lo:hi + 1]))
        if key in seen: return 'CYCLE(period %d from %d)' % (n - seen[key], seen[key])
        seen[key] = n
        c = tape[h]; tr = t[2*q + c]
        if tr is None: return 'HALT@%d' % n
        tape[h] = tr[0]; h += tr[1]; q = tr[2]
    return 'UNKNOWN'
if __name__ == '__main__':
    ms = [l.split()[0] for l in open(sys.argv[1]) if l.strip()]
    starts = [l.split() for l in open(sys.argv[2]) if l.strip()]
    for M in ms:
        print(M + '\t' + '\t'.join('%s:%s' % (s[0], check(M, s[1], int(s[2]), ord(s[3]) - 65, int(sys.argv[3]))) for s in starts))
