"""parked.py: a counter parked at the MSD end behind a gap of zero digits is just the list's leading digit.
Construct K(ds=[c,0^g,x]; a; b) for one base per family and print the K-trace (literal, kview)."""
import idle, sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import kl
BASES = {'r': ('1RB0LG_1RC1RB_0RD0RB_0LE1RD_0LD1LF_---1LA_1LC1LG', 'R,E,P=-,u=1,s=0,d=1d+0,b=1b+0,S=-', 6),
         'i': ('1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_0LA0LG_---0LE', None, None),
         'd': ('1RB1RA_0LC0LF_1RD1LC_0RF1RE_1LB0RG_1LE1LF_---0RA', None, None)}
for tag, (M, t, B) in BASES.items():
    T = kl.tmpl(M, t)
    for ds, a in [([3, 0, 0, 1], 1), ([2, 0, 0, 0, 0, 1], 1)]:
        b = B if B is not None else (T['beB'] and 0)
        ev = kl.run(M, ds, a, b if B is not None else 0, steps=3 * 10**7, nchg=8, maxl=30, T=T)
        print(tag, M, 'start', ds, a)
        for e in ev[:12]: print('   ', e if e[0] != 'K' else ('K', e[1], e[2][:8] + (['..%d' % len(e[2])] if len(e[2]) > 8 else []), e[3], e[4]))
