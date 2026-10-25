"""Literal D2-stage map: python d2map.py MACHINE 'LEFT' X k r t [maxsteps]
word = D(0)^2 LEFT D(X) D(2) D(1)^k D(1) D(r) D(0)^6 (100 D(0)^5)^t 100 100, state A at the right end (follower stage input).
Prints the hyb10 stop line (J = champion phase K-moment, canonical state A)."""
import subprocess, sys, tempfile, os
HYB = r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/bb10_bb7_descendants/hyb10r.exe'
LOW = subprocess.IDLE_PRIORITY_CLASS
def D(m): return '10' * m + '1'
def word(left, X, k, r, t, Z=2):
    w = D(0) * 2 + ''.join(D(x) for x in left) + D(X) + D(Z) + D(1) * k + D(1) + D(r) + D(0) * 6
    w += ('100' + D(0) * 5) * t + '100' + '100'
    return w
def run(m, w, steps=300000000, canon='A'):
    fd, p = tempfile.mkstemp(suffix='.txt'); os.write(fd, w.encode()); os.close(fd)
    r = subprocess.run([HYB, m, p, str(len(w)), 'A', str(steps), '-q', canon], capture_output=True, text=True, creationflags=LOW)
    os.unlink(p)
    lines = r.stdout.strip().splitlines()
    return lines[-1] if lines else '?'
if __name__ == '__main__':
    m, left, X, k, r, t = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])
    left = [int(x) for x in left.split(',')] if left else []
    print(run(m, word(left, X, k, r, t), int(sys.argv[7]) if len(sys.argv) > 7 else 300000000)[:400])
