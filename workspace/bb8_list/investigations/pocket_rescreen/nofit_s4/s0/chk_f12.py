import sys,re; sys.path.insert(0,'.'); from chk import expand,run_seq
M='1RB1RG_0RC---_1LD1LH_0LE1LC_1RF0LC_0RA1RC_1RC0RA_0RF0LE'
rx=re.compile(r'0*((?:10)*)1((?:10)*)11010A0')
def nextR(c,x):
    spec=('10^%d '%c if c else '')+'1 '+('10^%d '%x if x else '')+'1 10^2 0'
    L=2*c+1+2*x+1+4+1
    p=run_seq(M,10**9,'R:A','A',L-1,spec)
    for l in p.stdout:
        if l.startswith(('HALT','END','TAPE')): p.kill(); return l.strip()
        if '|' in l:
            e=expand(l.split('|',1)[1]); m=rx.fullmatch(e)
            if m: p.kill(); return (len(m.group(1))//2,len(m.group(2))//2)
ok=bad=0
for c in range(0,12):
    for x in range(1,25,2):
        r=nextR(c,x); exp=(c-1,2*x+3) if c else (4*x+10,1)
        if r==exp: ok+=1
        else: bad+=1; print(c,x,r,exp)
print('ok',ok,'bad',bad)
