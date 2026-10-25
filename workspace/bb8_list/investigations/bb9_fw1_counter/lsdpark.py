"""lsdpark.py: a block 1^c parked beyond the LSD end (past the head / accumulator / B), gap g.
Head starts at the normal K-moment position (end of the K word); the block lies g cells further out."""
import idle, sys, subprocess
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import kl
for tag, M, t, B in [('r', '1RB0LG_1RC1RB_0RD0RB_0LE1RD_0LD1LF_---1LA_1LC1LG', 'R,E,P=-,u=1,s=0,d=1d+0,b=1b+0,S=-', 6),
                     ('i', '1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_0LA0LG_---0LE', None, 0),
                     ('d', '1RB1RA_0LC0LF_1RD1LC_0RF1RE_1LB0RG_1LE1LF_---0RA', None, 0)]:
    T = kl.tmpl(M, t)
    for g, c in [(2, 5), (10, 5), (30, 4)]:
        w0 = kl.word(T, [2, 3], 1, B); w = w0 + '0' * g + '1' * c
        cmd = [kl.EXE, M] + kl.args(T) + [str(10**7), '40', '0', w, str(len(w0)), T['q'], '12']
        o = subprocess.run(cmd, creationflags=0x40, capture_output=True, text=True).stdout
        print(tag, T['o'], 'gap', g, 'c', c)
        for l in o.splitlines()[:12]: print('   ', l[:150])
