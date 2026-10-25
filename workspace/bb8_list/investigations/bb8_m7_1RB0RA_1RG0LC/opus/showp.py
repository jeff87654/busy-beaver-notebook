# showp.py PATHFILE [from] [to]: print a tcps3 path oldest first as a tape picture: left end ... [Qm] ... right end
import sys,re
L=open(sys.argv[1]).read().splitlines()
st=[]
for l in L:
    mm=re.match(r'\s+([A-H])(\d) \| L \[(\d*)\] (.*?) \| R \[(\d*)\] (.*)$',l)
    if mm: st.append(mm.groups())
st.reverse()
a=int(sys.argv[2]) if len(sys.argv)>2 else 0; b=int(sys.argv[3]) if len(sys.argv)>3 else len(st)
def side(u,s):
    g=''
    m=re.match(r'g(\w\w) (.*)',s)
    if m: g=m.group(1); s=m.group(2)
    s=s.replace(' 0^inf','').strip()
    if '..?' in s:
        h,t=s.split(' ..? '); return u+'.'+h+'~'+t+'$', g
    return u+'.'+s+'$', g
for i in range(a,min(b,len(st))):
    q,m,ul,sl,ur,sr=st[i]
    Ls,_=side(ul,sl); Rs,g=side(ur,sr)
    print('%5d %s%s %60s [%s%s] %-50s g=%s'%(i,q,m,Ls[::-1][-60:],q,m,Rs[:50],g))
