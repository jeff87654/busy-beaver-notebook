# an_scan.py runs/<file>: per run, ESC line (first CL whose view ends "... 2 7 1*P'"), the post-ESC form (J after ESC), counter C, z; checks
#   P'=0: "2 1 C 7 1*z"  C = 6R_E + (3P'+45)/5     P'=2: "2 4 (6R_E+1) C 7"  C = (3P'+9)/5   P'=3: "2 3 (6R_E+6) 2 z2 C 7"  C = (3P'-9)/5
#   P'=4: "2 2 (6R_E+7) z2 0 2 z2 C 7"  C = (3P'-12)/5    P'=1: "2 3 (6R_E+8) 2 z2 X" X = z+7 ;  z_view = (3P'-c')/5, c' = (30,33,21,34,37)
import sys, re
def ex(v):
    o = []
    for i, x in enumerate(v):
        if '*' in x and i < len(v) - 1: a, b = x.split('*'); o += [a] * int(b)
        else: o.append(x)
    return o
recs = open(sys.argv[1]).read().split('== ')[1:]
cp = {0: 30, 1: 33, 2: 21, 3: 34, 4: 37}
bad = 0; cnt = {}
for r in recs:
    lines = r.strip().split('\n'); lab = lines[0]; J = [l for l in lines[1:] if l.startswith('J')]; end = lines[-1]
    vw = [ex(l.split('|', 1)[1].split()) for l in J]; Rs = [int(re.search(r'R=(\d+)', l).group(1)) for l in J]
    ie = next(i for i, v in enumerate(vw) if v[-2] == '7' and v[-3] == '2')     # ESC: "... 2 7 1*P'"
    Pp = int(vw[ie][-1].split('*')[1]); RE = Rs[ie]; v = vw[ie + 1]; z = int(v[-1].split('*')[1]); res = Pp % 5
    # locate the post-ESC part: tokens after the ESC prefix (ESC view minus its last 4 tokens "6 2 7 1*P'" -> keep common prefix)
    pre = len(vw[ie]) - 5; tail = v[pre:]
    ok = z == (3 * Pp - cp[res]) // 5 and (3 * Pp - cp[res]) % 5 == 0
    if res == 0: C = int(tail[2]); ok &= tail[:2] == ['2', '1'] and C == 6 * RE + (3 * Pp + 45) // 5 and tail[3] == '7'
    elif res == 2: C = int(tail[3]); ok &= tail[:3] == ['2', '4', str(6 * RE + 1)] and C == (3 * Pp + 9) // 5 and tail[4] == '7'
    elif res == 3: C = int(tail[5]); ok &= tail[:5] == ['2', '3', str(6 * RE + 6), '2', 'z2'] and C == (3 * Pp - 9) // 5 and tail[6] == '7'
    elif res == 4: C = int(tail[7]); ok &= tail[:7] == ['2', '2', str(6 * RE + 7), 'z2', '0', '2', 'z2'] and C == (3 * Pp - 12) // 5 and tail[8] == '7'
    else: C = None; ok &= tail[:5] == ['2', '3', str(6 * RE + 8), '2', 'z2'] and int(tail[5]) == z + 7
    ok &= end.startswith('HALT')
    if C is not None: ok &= C % 3 == 0
    cnt[res] = cnt.get(res, 0) + 1
    if not ok: bad += 1; print('MISMATCH', lab, 'Pp', Pp, 'RE', RE, 'tail', tail[:9], end[:60])
print('runs', len(recs), 'by P\' mod 5', cnt, 'mismatches', bad)
