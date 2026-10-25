import fam, mfx
GH='1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_0RG1LD_1RH1LG_1LC0RG'
fam.register('xGH', GH, 'R,G,P=1,u=01,s=1,d=3d+1,b=3b+1,S=1010', 35); fam.start('xGH',6)
for m in ['1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RI0LC_0RG1LD_1RH1LG_1LC0RG_---0RG',
          '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RI0LC_0RG1LD_1RH1LG_1LC0RG_---0RH',
          '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LA0LC_0RG1LD_1RH1LG_1LC0RG',
          '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_---0LC']:
    r=mfx.screen('xGH', m, 12)
    print(m, r['kind'], r['kindB'], 'stages', r['stages'], 'cycles', r['cycles'], 'grow', r['grow'])
    print('  A:', mfx.zs(r['histA']), r['histA'][-1][:60]); print('  B:', mfx.zs(r['histB']), r['histB'][-1][:60])
