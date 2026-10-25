import idle
"""check_tg.py FILES..: check every topgrid row against the exact branch rules (intermediate views included).
b1: Top(K) -R_a-> Top(12R_a+(9K+36)/5)
b3: Top(K) -R_a-> '0 1 (6R_a+1) (Kb+8) 1*Kb' -R_b-> '0 1 (6R_a+1) 1*(Kb+1)' -R_c-> Top(12R_c+(3K+16)/5),  Kb=(3K-14)/5
b4: Top(K) -R_a-> '0 1 (6R_a+5) 2 z2 (Ka+7) 1*Ka' -R_b-> '0 1 (6R_a+4) (6R_b+10) 1*(Ka-1)' -R_c-> '0 1 (6R_a+4) 1*Ka' -R_d->
    Top(12R_d+(3K-2)/5),  Ka=(3K-27)/5
exit (K=0,2 mod 5): first CL view starts '0*2 y0 ' with y0 = (L0+d)/5, L0 = 3K-2, d = 7 (L0=3 mod 5), 11 (L0=4)."""
import sys, re
bad = ok = 0
for fn in sys.argv[1:]:
    for line in open(fn):
        m = re.match(r'K=(\d+) .* t=(\d+) R=([\d,]+) -> (.*?) \| inter: ?(.*)$', line.strip())
        if not m: continue
        K, t, Rs = int(m.group(1)), int(m.group(2)), [int(x) for x in m.group(3).split(',')]
        res, inter = m.group(4), [x.strip() for x in m.group(5).split('||')] if m.group(5) else []
        r = K % 5; Ra = Rs[0]
        if r == 1:
            exp_inter = []; Kp = 12 * Ra + (9 * K + 36) // 5
        elif r == 3:
            Kb = (3 * K - 14) // 5; Rb, Rc = Rs[1], Rs[2]
            exp_inter = ['0 1 %d %d 1*%d' % (6 * Ra + 1, Kb + 8, Kb), '0 1 %d 1*%d' % (6 * Ra + 1, Kb + 1)]
            Kp = 12 * Rc + (3 * K + 16) // 5
        elif r == 4:
            Ka = (3 * K - 27) // 5; Rb, Rd = Rs[1], Rs[3]
            exp_inter = ['0 1 %d 2 z2 %d 1*%d' % (6 * Ra + 5, Ka + 7, Ka), '0 1 %d %d 1*%d' % (6 * Ra + 4, 6 * Rb + 10, Ka - 1),
                         '0 1 %d 1*%d' % (6 * Ra + 4, Ka)]
            Kp = 12 * Rd + (3 * K - 2) // 5
        else:
            L0 = 3 * K - 2; d = {3: 7, 4: 11}[L0 % 5]
            good = res.startswith('EXIT') and len(inter) == 1 and (inter[0].startswith('0*2 %d ' % ((L0 + d) // 5)) or inter[0].startswith('0*2 %d 1*' % ((L0 + d) // 5 + 3)))
            ok += good; bad += not good
            if not good: print('MISMATCH exit', line.strip()[:300])
            continue
        good = res.startswith('TOP %d t=%d' % (Kp, t + 3)) and [x[:120] for x in inter] == [x[:120] for x in exp_inter]
        ok += good; bad += not good
        if not good: print('MISMATCH', line.strip()[:300], '| expected', Kp, exp_inter)
print('ok', ok, 'bad', bad)
