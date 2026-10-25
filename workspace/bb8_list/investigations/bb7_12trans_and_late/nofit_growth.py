# nofit_growth.py: span / ones growth of the top NOFIT classes from the clean sweep12 run.
# If span grows like t^alpha with alpha <= ~0.5-0.7 (polynomial), the machine is not record class
# (an f_omega-type machine's tape stays tiny for astronomically long; its list length is bounded, digits explode).
import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle  # IDLE_PRIORITY_CLASS
import math

MACHINES = [
    ('nd1199', '1RB1RE_1LC1RG_1LD1LC_1LA0LE_0LE1RF_0RA1RA_---0RB'),
    ('nd1197', '1RB1RE_1LC1RG_1LD1LC_1RE0LE_0RA1RF_0RA1RA_---0RB'),
    ('nd800',  '1RB0LF_1RC1RF_1LD0RA_0LA1LD_---1RA_0LC1RG_0RA0LE'),
    ('nd798a', '1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_0RA1LG_---0LF'),
    ('nd798b', '1RB1RE_1LC1RG_1LD1LC_0RE0LE_0LG1RF_0RA1RA_---0RB'),
    ('nd667',  '1RB0RD_0LC1LC_1LE1LD_0RF1LB_1RG1LF_---0LE_1RA1RG'),
    ('nd567',  '1RB0LE_1RC---_1RD1RB_0LA0LE_0RF1LD_1RG1RC_1RB1RE'),
    ('nd533',  '1RB0LF_1RC1RF_1LD1RE_0LA1LD_---0RB_0LE1RG_0RA1RB'),
    ('nd402',  '1RB1RE_1LC1RG_1LD1LC_1RF0LE_1RA1RF_0RA1RA_---0RB'),
    ('nd401',  '1RB1RA_0LC0LF_0RD1LC_1RA1RE_1RF1RG_1LB1LF_---0RE'),
    ('nd322',  '1RB1LD_1LC0LE_1RD0RA_1RE1RC_1LF0RE_0LB1LG_---1LF'),
    ('nd267',  '1RB1RE_1LC1LB_0RE0LD_1LA1RG_0RD1RF_0RE1RA_0RA---'),
    ('nd91',   '1RB1RF_1LC1RE_0LD1LC_1RA0LF_---1RD_0RA1RG_0RD1RA'),
    ('nd26',   '1RB1LE_1RC0LG_1RD1RC_0LA0RA_0LF1LF_0LA1LA_---1LB'),
]

def parse(s):
    tr = []
    for g in s.split('_'):
        row = []
        for i in (0, 3):
            t = g[i:i + 3]
            if t[2] in '-Z' or t == '---':
                row.append(None)
            else:
                row.append((int(t[0]), 1 if t[1] == 'R' else -1, ord(t[2]) - 65))
        tr.append(row)
    return tr

def run(s, checkpoints):
    tr = parse(s)
    SZ = 1 << 23
    tape = bytearray(SZ)
    pos = SZ // 2
    lo = hi = pos
    q = 0
    step = 0
    out = []
    ci = 0
    while ci < len(checkpoints):
        target = checkpoints[ci]
        while step < target:
            a = tr[q][tape[pos]]
            if a is None:
                out.append(('HALT', step + 1, hi - lo + 1, sum(tape[lo:hi + 1])))
                return out
            tape[pos] = a[0]
            pos += a[1]
            q = a[2]
            step += 1
            if pos < lo:
                lo = pos
                if lo <= 0:
                    out.append(('EDGE', step, hi - lo + 1, -1)); return out
            elif pos > hi:
                hi = pos
                if hi >= SZ - 1:
                    out.append(('EDGE', step, hi - lo + 1, -1)); return out
        out.append(('RUN', step, hi - lo + 1, sum(tape[lo:hi + 1])))
        ci += 1
    return out

def main():
    cps = [1 << k for k in range(18, 25)]  # 262k .. 16.8M
    for name, m in MACHINES:
        res = run(m, cps)
        pts = [(r[1], r[2]) for r in res if r[0] == 'RUN' and r[2] > 1]
        alpha = None
        if len(pts) >= 3:
            (t1, s1), (t2, s2) = pts[-3], pts[-1]
            alpha = math.log(s2 / s1) / math.log(t2 / t1)
        print(f"{name:7s} {m}  alpha(span~t^a, last 4x)={alpha if alpha is None else round(alpha, 3)}")
        for r in res:
            print(f"    {r[0]:4s} t={r[1]:>9d} span={r[2]:>7d} ones={r[3]}")
        sys.stdout.flush()

if __name__ == '__main__':
    main()
