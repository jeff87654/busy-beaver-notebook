"""Stage 0 of M3 from the record's exhaustion X(b, 35): the first jump K-moment must be
[D6^(4b+2), D2, D2, D0, D5, 0^(8b+49) | a = 0 | r = 0] (tokens far-first); also the step count."""
import mf35, sys
M = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_1LC0RH_1RG1LF_---0LJ_0LD0RA'
bad = 0
for b in list(range(1, 61)) + [126]:
    w, h, s = mf35.xword(b, 35)
    sv = mf35._server()
    sv.stdin.write(f'{M} {s} {h} 3000000000 4000000 600\n{w}\n'); sv.stdin.flush()
    o = sv.stdout.readline().strip().rpartition(' | U=')[0]
    if not o.startswith('J'):
        print(b, 'NOT J', o[:80]); bad += 1; continue
    t = [int(x) for x in o.split('|')[1].split()][::-1]
    exp = [6] * (4 * b + 2) + [2, 2, 0, 5] + [1] * (8 * b + 49) + [1, 1, 2]
    ok = t == exp and o.split('|')[2].strip() == ''
    bad += not ok
    print(b, 'OK' if ok else 'MISMATCH ' + mf35.rle(t)[:120], o.split()[1], flush=True)
print('mismatches', bad)
