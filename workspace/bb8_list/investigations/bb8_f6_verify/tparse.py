import sys, re
# parse lit.exe 't' output: "<step> E0 @p | <rle tokens with (..)^k groups>"
def expand(s):
    # expand rle string into a 0/1 string; handles (x y)^k and a^k tokens, [E0] head
    out=[]; head=None
    toks=re.findall(r'\(([^)]*)\)\^(\d+)|(\[[A-Z]\d\])|(\d)\^(\d+)|(\d)', s)
    for g,k,hd,a,ak,b in toks:
        if g:
            sub=''.join(expand(g)[0])*int(k); out.extend(sub)
        elif hd: head=len(out); out.append(hd[2])
        elif a: out.extend(a*int(ak))
        else: out.append(b)
    return out, head
def runs(s):
    r=[]; i=0
    while i<len(s):
        j=i
        while j<len(s) and s[j]==s[i]: j+=1
        r.append((s[i],j-i)); i=j
    return r
def lefttok(L):
    # L: string left of head (ends with '110'), tokens from the right: '1100' = P
    t=[]; s=L
    # strip trailing '110'
    assert s.endswith('110'), s[-10:]
    s=s[:-3]
    out=[]
    while s:
        if s.endswith('1100'): out.append('P'); s=s[:-4]
        else:
            # take a run-based junk token: trailing zeros + ones
            m=re.search(r'(1+0*)$', s) ; tok=m.group(1); out.append('J'+str(tok.count('1'))+'.'+str(tok.count('0'))); s=s[:-len(tok)]
    # compress
    c=[]; 
    for x in out:
        if c and c[-1][0]==x: c[-1][1]+=1
        else: c.append([x,1])
    return ' '.join(x if k==1 else '%s^%d'%(x,k) for x,k in c)
def rvec(R):
    # R: string right of head (head excluded), form 1^u 00 1^r 00 ... 1 (sentinel)
    rr=runs(R.rstrip('0')); v=[]; i=0
    while i<len(rr):
        sym,l=rr[i]
        if sym=='1':
            if i==len(rr)-1: v.append('s%d'%l); break
            v.append(l)
        else:
            if l%2: v.append('!z%d'%l)
            else: v.extend([0]*((l-2)//2))
        i+=1
    return v
for line in sys.stdin:
    if '|' not in line or 'E0' not in line.split('|')[0]: continue
    step=line.split()[0]; body=line.split('|',1)[1].strip()
    t,h=expand(body); s=''.join(t)
    L=s[:h]; R=s[h+1:]
    try: lt=lefttok(L)
    except AssertionError: lt='?'
    print(step, '| L:', lt, '| R:', ' '.join(map(str,rvec(R))))
