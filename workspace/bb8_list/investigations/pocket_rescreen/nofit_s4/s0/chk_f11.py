import sys; sys.path.insert(0,'.'); from chk import expand,run_seq
M='1RB1RA_1RC1RH_0LD0RH_1RA1LE_---0LF_1LG1LF_1LC0RA_0RC1RB'
def R(c,x): return '1'*c+'0'+'1'*x+'011B0'
def nextR(c,x):
    spec=('1^%d '%c if c else '')+'0 '+('1^%d '%x if x else '')+'0 11 0'
    L=c+1+x+1+2+1
    p=run_seq(M,10**9,'R:B','B',L-1,spec)
    for l in p.stdout:
        if l.startswith(('HALT','END','TAPE')): p.kill(); return l.strip()
        if '|' in l:
            e=expand(l.split('|',1)[1]).lstrip('0')
            if e.endswith('011B0') and e.count('0') in (2,3):
                p.kill(); return e
    return None
ok=bad=0
for c in range(0,12):
    for x in range(0,12):
        r=nextR(c,x)
        exp=R(c-1,4*x+4) if c>=1 else R(4*x+5,0)
        if r==exp.lstrip('0'): ok+=1
        else: bad+=1; print(c,x,r[:80] if r else r)
print('ok',ok,'bad',bad)
