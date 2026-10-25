"""Literal check of candidate 1's last stage: [D9^N, D8, D0, 0^k | a=0 | r] -> halt at I0, for many k, r, N.
Uses stage35.exe (C++).  Prints any case that does not halt, and ones-vs-r data."""
import mf35
M = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_1RG1LD_1LC0RH_1RG1LF_---0LA_------'
bad = 0; rows = []
for N in (1, 3, 16):
    for k in range(1, 130):
        for r in (1, 19, 43, 91):
            toks = [9] * N + [8, 0] + [1] * k + [1, r, 2]
            w = mf35.word_of_tokens(toks)
            o = mf35.run_stage(M, w, len(w), 'G', 50_000_000)
            if not o.startswith('H') or o.split()[2] != 'I' or o.split()[3] != '0':
                bad += 1; print('NOT HALT', N, k, r, o[:120])
            else:
                rows.append((N, k, r, int(o.split()[1]), int(o.split()[4])))
print('cases', len(rows) + bad, 'bad', bad)
# ones as a function of r (N=1): must grow with r (the accumulator run is on the tape)
for k in (5, 66):
    print('k', k, [(r, ones) for (N, kk, r, s, ones) in rows if N == 1 and kk == k])
