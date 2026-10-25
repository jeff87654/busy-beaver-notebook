exec(open('lemB.py').read().split("print('B1'")[0])
print('B1',prove('B1','[D]0 0 0 1 01^2*a+1 101^k+5 1 01^2*d+3', predA, '1 [A]1 1 01^2*a+4 1 1 011^k+4 01^2*d+3'))
print('B2',prove('B2','1^m [A]1 1 01^p+4 1 1 011^n+3 01^d', predA, '1^m+3 [A]1 1 01^p+4 1 1 011^n+2 01^d'))
print('B2r2',prove('B2r2','1^m [A]1 1 01^p+4 1 1 011 011 01^d', predA, '1^m+3 [A]1 1 01^p+4 1 1 011 01^d'))
print('B2r1',prove('B2r1','1^m [A]1 1 01^p+4 1 1 011 01^d', predA, '1^m+3 [A]1 1 01^p+4 1 1 01^d'))
items,h,q=build('1^3*k+10 [A]1 1 01^2*a+4 1 1 01^2*d+3'); s=Sim(items,h,q)
while True:
    ev=s.run(lambda e,S: e[0]=='Lnew' and e[1]=='D')
    dd=decode(s.t,s.h)
    if dd is not None or ev[0]=='HALT': break
print('B3',show(dd), 'rnew',getattr(s,'rnew',0))
r,s=next_K([V('a',0)*2+1, V('b',0)*2+3]); print('D',show(r),'rnew',getattr(s,'rnew',0))
