"""C7 from a D0f moment with r = L mod 5 = 2: outcome.  python r2d0.py"""
import idle, subprocess, sys, re
C7 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_1RG1LD_0RG0RF_0LI---_1LC0RA'
EXE = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_c7_coq\tools\c7m.exe'
def word(t, L, P, s, y, l='11'):
    return l + '1' + '10' * s + '101' + '10' * y + '011' + '100' * P + '1' * L + '11' + '11111100' * t + '1001'
def run(t, L, P, s, y, l='11', maxs='2e7'):
    out = subprocess.run([EXE, C7, 'w:' + word(t, L, P, s, y, l), maxs, 'noh', 'kt', 'far=200'], capture_output=True, text=True, creationflags=0x40).stdout
    return out
if __name__ == '__main__':
    for L in range(int(sys.argv[1]), int(sys.argv[2]), 5):
        for (s, y) in [(2, 17), (5, 30), (24, 9)]:
            out = run(7, L, 196, s, y)
            fate = 'HALT' if 'HALT' in out else 'MAX'
            m = re.search(r'^KT .*? 7 1\*(\d+) 2 0\*(\d+)$', out, re.M)
            first = [l for l in out.splitlines() if l.startswith('D0')][:1]
            print(L, (L - 2) // 5, ((L - 2) // 5) % 5, s, y, fate, m.groups() if m else None, first, flush=True)
