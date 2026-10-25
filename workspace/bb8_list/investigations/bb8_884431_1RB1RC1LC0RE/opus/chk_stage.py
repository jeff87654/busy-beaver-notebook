from pieces import *
A = ('F', [1, 0] + [1]*7 + [BLANK], [1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1] + mkrun(U, {'y': 1}) + TT, '>')
print(pl.show(A))
tg = engine.subst(engine.subst(G3, 'b', (), 1), 'k', (), 2)
print(pl.show(tg))
st = engine.subst(engine.subst(M3, 'b', (), 1), 'k', (), 2)
print('M3(2,1)->A', validate.reaches(st, A, {'y': 1}), ' A->G3', validate.reaches(A, tg, {'y': 1}), ' M3->G3', validate.reaches(st, tg, {'y': 1}))
