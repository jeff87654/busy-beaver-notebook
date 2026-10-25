import idle, subprocess, sys
"""mprobe: run K(A; 0^j) + marker blocks + tail and print the first few generalized events."""
def run(M, A, j, mk, tail, maxs=200000000, maxev=6, mode='chg'):
    blocks = [2 * A] + [0] * j + mk + tail
    r = subprocess.run(['./gfollow.exe', M, str(maxs), str(maxev), mode], input=' '.join(map(str, blocks)), capture_output=True, text=True)
    return r.stdout.strip().split('\n')
G = {
 '0LH/1RC': ('1RB0RG_1RC1RB_0RD0LH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---1RC', [5, 0]),
 '0LH/0LF': ('1RB0RG_1RC1RB_0RD0LH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---0LF', [1, 0, 0, 0]),
 '0LH/0RC': ('1RB0RG_1RC1RB_0RD0LH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---0RC', [3, 5, 1, 0, 0]),
 '0LH/0RE': ('1RB0RG_1RC1RB_0RD0LH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---0RE', [9, 0]),
 '1LH/0RA': ('1RB0RG_1RC1RB_0RD1LH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---0RA', [23, 0]),
}
if __name__ == '__main__':
    for name, (M, mk) in G.items():
        print('=====', name, M)
        for A in (6, 7, 8, 9):
            for j in (1, 2, 5):
                ev = run(M, A, j, mk, [2] * 12)
                print('  A=%d j=%d:' % (A, j), ' | '.join(e[:130] for e in ev[1:4]))
