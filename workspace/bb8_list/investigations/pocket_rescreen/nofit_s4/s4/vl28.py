import sys
from val import run
m=sys.argv[1]
w=lambda K: '0'+'1'*12+'01'*3+('0'+'01'*10)*K+'0'+'01'*22
cs=[('B','',w(K),w(K+1),K) for K in range(1,121)]
ok,bad,res=run(m,'B','L',cs,'01{12}(01){3}(0(01){10})*0(01){22}')
print('K',ok+bad,'bad',bad,[r for r in res if not r[1]][:2])
