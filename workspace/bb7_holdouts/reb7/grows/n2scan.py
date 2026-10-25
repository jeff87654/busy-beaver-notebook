import idle, sys, subprocess, itertools
M = '1RB0RC_1RC0RA_1LD0LB_1LE0LA_0LF---_1RC0LG_1LF1LA'
MS = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\grows\ms.exe'
MAXM = sys.argv[1]
vals = [int(v) for v in sys.argv[2].split(',')]
ys = [int(v) for v in sys.argv[3].split(',')]
lefts = ['', '10^1 11^1', '10^3 11^1', '10^5 11^1']
nh = 0; tot = 0
for L in range(0, 3):
    for segs in itertools.product(itertools.product(vals, vals), repeat=L):
        for left in lefts:
            for x in (1, 3):
                for y in ys:
                    toks = [left] if left else []
                    for p, q in segs: toks += ['01^%d' % p, '10^%d' % q, '11^1']
                    toks += ['01^%d' % x, '10^%d' % y]
                    init = 'A 0 | ' + ' '.join(toks) + ' [01]\n'
                    r = subprocess.run([MS, M, '2', MAXM, 'p0', 'i'], input=init, capture_output=True, text=True, creationflags=0x40).stdout.strip().splitlines()[-1]
                    tot += 1
                    if r.startswith('H') or r.startswith('IN'):
                        nh += 1; print(init.strip(), '->', r, flush=True)
print('total', tot, 'halts', nh)
