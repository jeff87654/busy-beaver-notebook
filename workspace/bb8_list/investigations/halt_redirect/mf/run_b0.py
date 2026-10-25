import sys, mf35g
m = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_0RG1LD_1RH1LG_1LC0RG_---0LH_------'
b0 = int(sys.argv[1])
k, h = mf35g.follow('GH', m, 100000, 200_000_000, False, b0=b0)
with open(f'gh0LH_b{b0}.txt', 'w') as f:
    f.write(f'RESULT {k} stages={len(h)}\n' + '\n'.join(h) + '\n')
print(b0, k, len(h), h[-1][:120])
