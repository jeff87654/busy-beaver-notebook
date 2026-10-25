import idle, sys, subprocess, os
HERE=os.path.dirname(os.path.abspath(__file__))
def unrle(s):
    out=[]
    for tok in s.strip().strip('.').split('.'):
        if not tok: continue
        if '^' in tok: c,n=tok.split('^'); out.append(c*int(n))
        else: out.append(tok)
    return ''.join(out)
def runs(bits,u):
    # greedy left-to-right: count u blocks, other chars printed literally
    o=[];i=0;cnt=0
    while i<len(bits):
        if bits.startswith(u,i): cnt+=1;i+=len(u)
        else:
            if cnt: o.append(str(cnt)); cnt=0
            o.append(bits[i] if bits[i]!='0' else '.'); i+=1
    if cnt: o.append(str(cnt))
    s=' '.join(o)
    return s.replace(' . ',' . ')
def comp(s):
    t=s.split(' ');out=[];i=0
    while i<len(t):
        j=i
        while j<len(t) and t[j]==t[i]: j+=1
        out.append(t[i]+('x%d'%(j-i) if j-i>2 else (' '+t[i] if j-i==2 else ''))); i=j
    return ' '.join(out)
if __name__=='__main__':
    M,N,mo,side,every,u=sys.argv[1:7]
    p=subprocess.Popen([os.path.join(HERE,'ev.exe'),M,N,mo,side,every],stdout=subprocess.PIPE,text=True,creationflags=0x40)
    with open(os.path.join(HERE,'..','pids.txt'),'a') as f: f.write('%d ev.exe\n'%p.pid)
    for l in p.stdout:
        if '|' not in l: print(l.strip()); continue
        h,r=l.split('|'); print(h.strip(),'|',comp(runs(unrle(r),u))[:int(sys.argv[7]) if len(sys.argv)>7 else 220])
