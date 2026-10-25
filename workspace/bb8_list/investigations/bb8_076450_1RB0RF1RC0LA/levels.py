"""Level map of 1RB0RF_1RC0LA_0RD0RB_1LE1RG_0LA0LC_0LD0LG_1LH1RA_---1LF (event forms, see the report).

Rules: Lv(N odd) -> Lv(4N+6); Lv(N even) -> be(N-3, 10); be(A, n) -> al(A-2, 4n+15) (A odd >= 3, n even);
al(A, n) -> be(A-2, 4n+20) (A odd >= 3, n odd); al(1, n) -> X(4n+20) -> Lv(16n+95) (n odd).
A level starts at be(A, 10) with A = 3 mod 4 and ends at be(3, n): (A-3)/4 double steps n -> 16n+80,
so n_end = (46*16^((A-3)/4) - 16)/3.  Then be(3,n) -> al(1,4n+15) -> Lv(64n+335) -> Lv(256n+1346) -> be(256n+1343, 10).
"""
import math, sys
sys.set_int_max_str_digits(0)
LOG16 = math.log10(16)
A = 7
print('level 1: be(7, 10)')
for lev in range(1, 4):
    j = (A - 3) // 4
    if j < 10**6:
        n = (46 * 16**j - 16) // 3
        assert (46 * 16**j - 16) % 3 == 0
        A2 = 256 * n + 1343
        print('level %d: A = %s (%d digits), %d double steps, ends at be(3, n) with n = %s... (%d digits); next A = 256n+1343 (%d digits), A mod 4 = %d'
              % (lev, str(A)[:30], len(str(A)), j, str(n)[:20], len(str(n)), len(str(A2)), A2 % 4))
        A = A2
    else:
        ld = len(str(j)) - 1 + math.log10(int(str(j)[:15]) / 10**14)   # log10(j)
        print('level %d: A has %d digits; the level ends with n of about 10^(%.4f * 10^%.4f) = 10^10^%.4f (tetration-rate)'
              % (lev, len(str(A)), LOG16, ld, ld + math.log10(LOG16)))
        break
