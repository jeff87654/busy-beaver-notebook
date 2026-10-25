exec(open('lemB.py').read().split("print('B1'")[0])
print('T1',prove('T1','[D]0 0 0 1 01^2*a+1 101^k+5', predA, '1 [A]1 1 01^2*a+4 110^k+4 1'))
print('T2',prove('T2','1^m [A]1 1 01^p+4 110^n+3 1', predA, '1^m+3 [A]1 1 01^p+4 110^n+2 1'))
print('T2r2',prove('T2r2','1^m [A]1 1 01^p+4 110 110 1', predA, '1^m+3 [A]1 1 01^p+4 110 1'))
print('T2r1',prove('T2r1','1^m [A]1 1 01^p+4 110 1', predA, '1^m+3 [A]1 1 01^p+4 1'))
for A in ('2*a+4','2*a+10'):
  try:
    items,h,q=build('1^3*k+10 [A]1 1 01^%s 1'%A); s=Sim(items,h,q)
    while True:
        ev=s.run(lambda e,S: e[0]=='Lnew' and e[1]=='D')
        dd=decode(s.t,s.h)
        if dd is not None or ev[0]=='HALT': break
    print('T3',A,show(dd) if dd else ev)
  except Fail as e: print('T3',A,'FAIL',e)
