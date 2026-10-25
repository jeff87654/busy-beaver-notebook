import sys, time, re, subprocess
sys.path.insert(0, '.')
import d9f, mf35
line = [l for l in open('runs/C2565_0LJ0LH_xxx0LB.log') if l.startswith('700 J:')][0]
after = line.split('-> ', 1)[1]
lst, ar = after.split(' | a=')
a, r = ar.split(' r=')
toks = d9f_expand = []
for t in lst.split():
    if '^' in t: x, c = t.split('^'); toks += [int(x)] * int(c)
    else: toks.append(int(t))
toks += [int(a), int(r.split()[0])]
w = mf35.word_of_tokens(toks) + '1010'
M = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LH_---0LB'
for i in range(3):
    t0 = time.time(); o, u = d9f.stage(M, w, len(w), 'G', 10**9); print(len(w), o[:60], time.time() - t0)
