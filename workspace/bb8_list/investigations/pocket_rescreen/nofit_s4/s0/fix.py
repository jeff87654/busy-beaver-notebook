L=open('tv.cpp').read().split('\n')
i=[k for k,l in enumerate(L) if 'STOP %lld' in l][0]
L[i]=L[i].rstrip('\r')+'\n'+L[i+1]; del L[i+1]
open('tv.cpp','w').write('\n'.join(L))
