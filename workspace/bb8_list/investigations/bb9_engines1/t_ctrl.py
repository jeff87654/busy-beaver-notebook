import fam, mf35g, mf35
GH='1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_0RG1LD_1RH1LG_1LC0RG'
F=fam.register('xGH', GH, 'R,G,P=1,u=01,s=1,d=3d+1,b=3b+1,S=1010', 35)
print(F['SUF'], F['E'], F['Q'])
w,h,q,sl=fam.start('xGH',6)
mf35g._XC.pop(('GH',6),None)
w2,h2,q2=mf35g.xstart('GH',6)
print('same as mf35g GH start:', (w.strip('0'),q)==(w2.strip('0'),q2), sl, len(w), h, len(w2), h2)
m='1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RI0LC_0RG1LD_1RH1LG_1LC0RG_---0RG_------'
k,hist=mf35g.follow('xGH', m, 10, 3_000_000)
print(k); print('\n'.join(hist))
m='1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_---0LC'
k,hist=mf35g.follow('xGH', m, 10, 3_000_000)
print(k); print('\n'.join(hist))
