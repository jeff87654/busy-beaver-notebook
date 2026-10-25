"""hcheck.py: (1) static check: which transitions enter E and H; (2) literal sim from small Kt configs, counting H reads by symbol."""
import sys
MS = """1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RH0LC_1RG1LD_0RG0RF_---0LC
1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RH0LC_1RG1LD_0RG0RF_---1LF
1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RH0LC_1RG1LD_0RG0RF_---1RD
1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RH0LC_1RG1LD_0RG0RF_---0RF
1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RH0LC_1RG1LD_0RG0RF_---1RA""".split()
def parse(m):
    T = {}
    for s, blk in enumerate(m.split('_')):
        for c in range(2):
            x = blk[3*c:3*c+3]
            T[(s, c)] = None if x[0] == '-' else (int(x[0]), 1 if x[1] == 'R' else -1, ord(x[2]) - 65)
    return T
def kt(ds, mm, r, t):
    w = '11'
    for d in ds: w += '10' * d + '1'
    w += '10' * mm + '1' + '10' * r + '11' + '11111100' * t + '1001'
    return w
for m in MS:
    T = parse(m)
    into = {s: [(chr(65+a), c) for (a, c), v in T.items() if v and v[2] == s] for s in range(8)}
    print(m, ' into E:', into[4], ' into H:', into[7], ' undefined:', [(chr(65+a), c) for (a, c), v in T.items() if v is None])
    # literal sims
    hr = [0, 0]; Ecnt = [0, 0]
    for (ds, mm, r, tt) in [([], 0, 0, 0), ([1]*11, 1, 2, 0), ([1]*11, 1, 5, 0), ([1]*3, 1, 8, 0), ([4, 1, 1], 1, 2, 1)]:
        tape = {}; 
        if ds or mm or r or tt:
            w = kt(ds, mm, r, tt); 
            for i, ch in enumerate(w): tape[i] = int(ch)
            pos, st = len(w), 1
        else: pos, st = 0, 0
        for step in range(3_000_000):
            c = tape.get(pos, 0)
            if st == 4: Ecnt[c] += 1
            if st == 7: hr[c] += 1
            tr = T[(st, c)]
            if tr is None: print('  HALT', step); break
            tape[pos] = tr[0]; pos += tr[1]; st = tr[2]
    print('  E reads (0,1):', Ecnt, ' H reads (0,1):', hr)
