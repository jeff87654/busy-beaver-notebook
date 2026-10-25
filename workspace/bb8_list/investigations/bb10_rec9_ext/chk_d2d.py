import pickle, follow3 as F, fext, __main__
__main__.Aff = F.Aff
from numres import tau
L = pickle.load(open('logs/1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_0RH0RF_0RG0RE_0LH0LJ_---0LA.stages.pkl', 'rb'))
s1, res = L[1]
print(s1)
print(res['tail'])
ev, p2, info = F.jump(res['left'], res['tail'], {'R1': tau()}, res['e'])
print(F.fmt_sym(ev))
print(ev)
print(F.fmt_sym(fext.d2_input()) == F.fmt_sym(ev))
pickle.dump(ev, open('d2_input.pkl', 'wb'))
