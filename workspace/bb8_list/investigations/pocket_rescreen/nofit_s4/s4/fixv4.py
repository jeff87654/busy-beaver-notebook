L=open('v4.cpp',newline='').read().split('\n')
i=[k for k,l in enumerate(L) if 'if(rx=="ALL")' in l][0]
L[i]='     if(rx=="ALL"){ printf("E %lld %s'+chr(92)+'n",st+1,w.c_str()); if(ev>=80){done=true;break;} continue; }'
if L[i+1].startswith('",st+1'): del L[i+1]
open('v4.cpp','w',newline='').write('\n'.join(L))
