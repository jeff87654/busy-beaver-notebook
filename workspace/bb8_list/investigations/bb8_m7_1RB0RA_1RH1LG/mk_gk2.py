s=open('gk.cpp').read()
old='''    bool ok=true; for(int i=0;i<6;i++) if(tape[p-6+i]!=S[i]-'0') ok=false; if(!ok) continue;
    long long i=mn+2, e=p-6;'''
new='''    long long tt=-1, e=0;
    { if(!(tape[p-1]==1&&tape[p-2]==0&&tape[p-3]==0&&tape[p-4]==1)) continue;
      long long x=p-4; long long t2=0; const int B8[8]={1,1,1,1,1,1,0,0};
      while(x-8>=mn+2){ bool bk=true; for(int u=0;u<8;u++) if(tape[x-8+u]!=B8[u]) {bk=false;break;} if(!bk) break; x-=8; t2++; }
      if(!(tape[x-1]==1&&tape[x-2]==1)) continue;
      tt=t2; e=x-2; }
    long long i=mn+2;'''
assert old in s
s=s.replace(old,new)
s=s.replace('printf("] r=%lld\n",r);','printf("] r=%lld t=%lld\n",r,tt);')
open('gk2.cpp','w').write(s)
