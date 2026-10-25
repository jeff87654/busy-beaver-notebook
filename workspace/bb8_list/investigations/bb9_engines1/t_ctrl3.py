import fam, mfx, sys
GH='1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_0RG1LD_1RH1LG_1LC0RG'
fam.register('xGH', GH, 'R,G,P=1,u=01,s=1,d=3d+1,b=3b+1,S=1010', 35)
m='1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_---0LC'
for b0 in map(int, sys.argv[1:]):
    fam.start('xGH', b0)
    r=mfx.screen('xGH', m, 60, b0=b0)
    print(b0, r['kind'], r['kindB'], 'stages', r['stages'], 'cycles', r['cycles'], 'grow', r['grow'], r['histA'][-1][:50], '|', r['histB'][-1][:50], flush=True)
    print('  A:', mfx.zs(r['histA']))
