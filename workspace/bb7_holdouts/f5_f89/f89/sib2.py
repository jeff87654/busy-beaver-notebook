import itertools
F='1RB0RE_0RC---_1LD0RG_1RA0RF_1LF0LD_1LD0LE_1RC1RE'
S=['1RB0LG_1LC0LE_1LF0LD_1RE0RB_1RB0RD_0LA---_1LA1LD','1RB0RD_1LC0LA_1LE0LD_1RA0RB_0LF---_1RB0LG_1LF1LD','1RB0RF_1RC0RE_0RD---_1LA0RG_1LF0LA_1LA0LE_1RD1RE']
def tab(m):
    return {(q,s):(g[3*s:3*s+3]) for q,g in enumerate(m.split('_')) for s in range(2)}
TF=tab(F)
for m in S:
    TM=tab(m); found=[]
    for perm in itertools.permutations(range(7)):   # perm[q_F] = q_sib
        for mir in (False,True):
            ok=True
            for (q,s),t in TF.items():
                u=TM[(perm[q],s)]
                if t[2]=='-': ok = ok and u[2]=='-'
                else:
                    d=t[1] if not mir else ('L' if t[1]=='R' else 'R')
                    ok = ok and u==t[0]+d+chr(65+perm[ord(t[2])-65])
                if not ok: break
            if ok: found.append((perm,mir))
    for perm,mir in found:
        inv={v:k for k,v in enumerate(perm)}
        print(m,'= F89 relabeled',''.join(chr(65+perm[q]) for q in range(7)),'mirror' if mir else '','; sibling start A = F89 state',chr(65+inv[0]))
    if not found: print(m,'no relabel')
