import idle, subprocess, os, random, re
HERE=os.path.dirname(os.path.abspath(__file__))
EV=os.path.join(HERE,'ev.exe')
BASES={
 # name: (machine, O, Q, family)
 'B1':('1RB0RF_0LC---_1LE1LD_1LC1LF_0RA0RF_0LG1RE_1RE0LB','R','E','B'),
 'B2':('1RB0LD_0RC0RG_1RD0RG_0LE---_1LB1LF_1LE1LG_0LA1RB','R','B','B'),
 'B3':('1RB0LE_1RC1RE_1RD1RB_0LA0LE_0RF1LD_1LD0RG_0RC---','L','D','B'),
 'B4':('1RB0LG_0RC0RF_1LD0RF_1LE1LF_1LB1LD_0LA1RB_0LE---','R','B','B'),
 'A1':('1RB0LD_0RC0RG_1LD0RG_0LE---_1LB1LF_1LE1LG_0LA1RB','R','A','A'),
}
_c=[l.split() for l in open(os.path.join(HERE,'..','..','..','bb7_holdouts','reb7','counters','famC.txt')) if l.strip()]
for i,l in enumerate(_c): BASES['C%d'%(i+1)]=(l[0],l[1],l[2],'C')
for k,o,q in (('C7','R','F'),('C8','L','F'),('C9','L','F')): BASES[k]=(BASES[k][0],o,q,'C')
def run(m,O,Q,jobs,N=10**7,maxout=1,fam='-'):
    p=subprocess.Popen([EV,m,O,Q,str(N),str(maxout),fam],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True,creationflags=0x40)
    with open(os.path.join(HERE,'pids.txt'),'a') as f: f.write('%d ev.exe\n'%p.pid)
    out,_=p.communicate('\n'.join(jobs)+'\n')
    return [l.split(' ; ') for l in out.strip().split('\n')]
# ---- codecs
def encB(c,R,y): return ('10'*c+'1' if c is not None else '')+'0'.join('10'*r for r in list(R)+[0,y])+'1'
def encC(R,y): return '0'.join('1'*r for r in list(R)+[0,y])+'0'
def encA(runs,seps): # runs include [...,0,y]
    w='10'*runs[0]
    for s,r in zip(seps,runs[1:]): w+=('0' if s==' ' else '1')+'10'*r
    return w
def parse_u(b):
    runs=[];seps=[];cur=0;i=0
    while i<len(b):
        if b.startswith('10',i): cur+=1; i+=2
        elif b[i]=='0': runs.append(cur); seps.append(' '); cur=0; i+=1
        else: runs.append(cur); seps.append('|'); cur=0; i+=1
    runs.append(cur)
    o=str(runs[0])
    for s,r in zip(seps,runs[1:]): o+=s+str(r)
    return o
def comp(o):
    t=o.replace('|',' | ').split(' ')
    out=[];i=0
    while i<len(t):
        j=i
        while j<len(t) and t[j]==t[i]: j+=1
        out.append(t[i]+('x%d'%(j-i) if j-i>1 and t[i] not in ('|','') else '')); i=j
    return ' '.join(x for x in out if x!='')
def dec(fam,bits):
    if fam=='B':
        if not bits.endswith('1'): return 'raw:'+bits
        return comp(parse_u(bits[:-1]))
    if fam=='A': return comp(parse_u(bits))
    if fam=='C':
        if not bits.endswith('0'): return 'raw:'+bits
        r=[len(x) for x in bits[:-1].split('0')]
        return comp(' '.join(map(str,r)))

# siblings (reb7 counters/classify_d.log): (machine,O,Q,family,variant)  variant: S1 = tape+'1' (A with S=1), S- = C without trailing S
SIB={
 'Bs1':('1RB1RE_1RC1RA_0LD0LE_1LF0LE_0RG1LC_0RB---_1LC0RF','L','C','B',''),
 'Bs2':('1RB1RG_0LC0LD_1LF0LD_0RE1LB_1LB0RF_0RA---_1RA1RD','L','B','B',''),
 'Bs3':('1RB1RE_1RC1RA_0LD0LE_1RA0LE_0RF1LC_1LC0RG_0RB---','L','C','B',''),
 'Bs4':('1RB1RF_0LC0LD_1RF0LD_0RE1LB_1LB0RG_1RA1RD_0RA---','L','B','B',''),
 'As1':('1RB1RE_1RC1RA_0LD0LE_1RF0LE_0RG1LC_0RB---_1LC0RF','L','C','A','S1'),
 'As2':('1RB1RG_0LC0LD_1RF0LD_0RE1LB_1LB0RF_0RA---_1RA1RD','L','B','A','S1'),
}
for i,(r,q,v) in enumerate([('0LD0RG_---0RB','C','S-'),('0RC0RG_---0RA','C','S-'),('0RD0RG_---0RA','C','S-'),('0RE0RG_---0RA','C','S-'),('0RB0RG_---0RB','C','S-'),('0RD0RG_---0RB','C','S-'),
                            ('1LA0RG_---0RB','D',''),('1RA0RG_---0RB','D',''),('0RC0RG_---0RB','D',''),('0RE0RG_---0RB','D',''),('1LB0RG_---0RB','D','')]):
    SIB['Cs%d'%(i+1)]=('1RB1RA_0LC0LD_0LD1LD_0RE1LC_1RA1RF_'+r,'L',q,'C',v)
VAR={}
for k,v in SIB.items(): BASES[k]=v[:4]; VAR[k]=v[4]
def filt(nm):
    f=BASES[nm][3]; v=VAR.get(nm,'')
    if f=='A' and v=='S1': return 'B'
    if f=='C' and v=='S-': return 'c'
    return f
def fixtape(nm,t):
    v=VAR.get(nm,'')
    if v=='S1': return t+'1'
    if v=='S-': return t[:-1]
    return t

def dec2(nm,bits):
    fam=BASES[nm][3]; v=VAR.get(nm,'')
    if v=='S-': bits=bits+'0'
    if v=='S1' and bits.endswith('1'): bits=bits[:-1]
    return dec(fam,bits)
