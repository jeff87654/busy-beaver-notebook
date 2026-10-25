from plan_test import *
Z6=(0,1,0,1,0,1)
PH2 = {
 'T1': (D([0,0]+mkrun(S6,{'i':1})+[1,1,1,1,BLANK]), D([0,0,1]+mkrun(Z6,{'i':1})+[0,1]*5+[1,BLANK])),
 'T2': (D([0,0]+mkrun(S6,{'j':1})+[1,1,BLANK]), D([0,0,1,0,1,0,1,1,1]+mkrun(Z6,{'j':1})+[0,1,1,BLANK])),
}
for k,(s,t) in PH2.items():
    drive(k, s, t, matchers=(swF,), maxev=200)
