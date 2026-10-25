import sys, itertools
sys.path.insert(0, '.')
import stageu
M = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_---1LJ_0RJ0RF'
def key(out): return stageu.fmt(out).rsplit(' step=', 1)[0]
bad = 0; n = 0
for m, z, R in itertools.product([2, 3, 5, 8], [3, 5, 20, 41], [19, 2539]):
    out, _ = stageu.stage(M, f'6^{m} 0 1^{z} 1 {R}', maxs=2_000_000_000)
    exp = f'K: {"6^"+str(m-2)+" " if m-2 > 1 else ("6 " if m-2 == 1 else "")}4 {2*R-7} 1^{z+11} | a=1 r=1'
    ok = key(out) == exp; n += 1; bad += not ok
    if not ok: print('GROWTH MISMATCH', m, z, R, key(out), '!=', exp)
for m, z, R in itertools.product([1, 2, 5], [3, 20, 41], [19, 2539]):
    out, _ = stageu.stage(M, f'6^{m} 3 1^{z} 1 {R}', maxs=2_000_000_000)
    exp = f'K: {"6^"+str(m)+" " if m > 1 else "6 "}0 {2*R+5} 1^{z-1} | a=1 r=1'
    ok = key(out) == exp; n += 1; bad += not ok
    if not ok: print('PARK MISMATCH', m, z, R, key(out), '!=', exp)
for z, R in itertools.product([3, 20, 41, 200], [19, 2539]):
    out, _ = stageu.stage(M, f'6 0 1^{z} 1 {R}', maxs=2_000_000_000)
    ok = out.startswith('H') and out.split()[2] == 'I' and out.split()[3] == '0'; n += 1; bad += not ok
    if not ok: print('HALT MISMATCH', z, R, key(out))
    else: print('halt ones', z, R, out.split()[4], 'pred', 2*R + 2*z + 23)
print('checks', n, 'bad', bad)
