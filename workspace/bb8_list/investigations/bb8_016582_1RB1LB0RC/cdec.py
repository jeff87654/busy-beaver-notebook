from canon import *
import re,sys
def s(L): return re.sub('110','T',''.join(map(str,L)))
m=int(sys.argv[1]); h=int(sys.argv[2])
L=[1,1,0]; P='11'; G=[2]*m+[h,99]
tgt=([],'11',[2]*(m+1)+[h,99])
i=0
while (L,P,G)!=tgt:
    if P in('11','01'): print(i,('B'+s(L)).rjust(16),P.ljust(3),G)
    L,P,G=step(L,P,G); i+=1
print(i,'done')
