"""famcheck.py NAME SEED NTESTS: validate a K-rule set (RULES[NAME]) against literal runs (random small configurations).
Rules: D [..,d+1;a]->[..,d;al a+be]; Bk [..,y+1,0^k;a]->[..,y,ga a+de+ep k,t^(k-1);a0]; leading zeros invisible;
E [;a] -> rules['E'](a) = 'HALT' or (list, a)."""
import idle, sys, random
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import kl
RULES = {
 'i': dict(M='1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_0LA0LG_---0LE', T='R,C,P=-,u=1,s=0,d=1d+0,b=3b+1,S=0', B=0,
           al=3, be=3, ga=3, de=3, ep=-2, t=2, a0=2, E=lambda a: 'HALT' if a % 2 else ([2] * (3 * a // 2 + 1), 2)),
'a': dict(M='1RB1RA_0LC0LF_0RD1LC_1RA1RE_0RF0RG_1LB1LF_---0RA', T='L,C,P=-,u=1,s=0,d=1d+0,b=3b+1,S=0', B=0,
           al=3, be=3, ga=3, de=3, ep=-2, t=2, a0=2, E=lambda a: 'HALT' if a % 2 else ([2] * (3 * a // 2 + 1), 2)),
 'b': dict(M='1RB1RA_0LC0LF_0RD1LC_1RA1RE_0RF1RG_1LB1LF_---0RA', T='L,B,P=-,u=1,s=0,d=1d+0,b=3b+2,S=-', B=0,
           al=3, be=3, ga=3, de=3, ep=-2, t=2, a0=2, E=lambda a: 'HALT' if a % 2 == 0 else ([2, 1] + [2] * ((3 * a - 1) // 2), 2)),
 'c': dict(M='1RB1RA_0LC0LF_0RD1LC_1RA1RE_1RF1RG_1LB1LF_---0RA', T='L,B,P=-,u=1,s=0,d=1d+0,b=3b+2,S=-', B=0,
           al=3, be=3, ga=3, de=3, ep=-2, t=2, a0=2, E=lambda a: 'HALT' if a % 2 == 0 else ([1] + [2] * ((3 * a + 1) // 2), 2)),
 't': dict(M='1RB1RE_1RC1RB_0LD0LG_0RA1LD_---1RF_0LC0RB_1LC1LG', T='L,C,P=-,u=1,s=0,d=1d+0,b=3b+2,S=-', B=0,
           al=3, be=3, ga=3, de=3, ep=-2, t=2, a0=2, E=lambda a: 'HALT' if a % 2 else ([2] * (3 * a // 2), 2)),
 'd': dict(M='1RB1RA_0LC0LF_1RD1LC_0RF1RE_1LB0RG_1LE1LF_---0RA', T='L,E,P=-,u=1,s=0,d=1d+0,b=3b+2,S=-', B=0, al=3, be=4,
           Bf=lambda k, a: (3 * a, [], 15) if k == 1 else ((3 * a - 1, [2], 12) if k == 2 else (3 * a + 3 - 2 * k, [3] + [2] * (k - 3) + [1], 12)),
           E=lambda a: 'HALT' if a % 2 == 0 else ([3] + [2] * ((3 * a - 3) // 2) + [1], 12)),
 'e': dict(M='1RB1RA_0LC0LF_1RD1LC_1LA1RE_1LB0RG_1LE1LF_---0RA', T='L,C,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0', B=3, al=5, be=6,
           Bf=lambda k, a: (5 * a + 2, [], 25) if k == 1 else ((5 * a + 1, [2], 20) if k == 2 else (5 * a + 5 - 2 * k, [3] + [2] * (k - 3) + [1], 20)),
           E=lambda a: 'HALT' if a % 2 == 0 else ([3] + [2] * ((5 * a - 1) // 2) + [1], 20)),
 'n': dict(M='1RB1LA_0RC1RD_1LD1LC_1LE0RF_0LA0LC_---0RG_1RE1RG', T='L,C,P=-,u=1,s=0,d=1d+0,b=1b+0,S=-', B=1, al=3, be=4,
           Bf=lambda k, a: (3 * a, [], 15) if k == 1 else ((3 * a - 1, [2], 12) if k == 2 else (3 * a + 3 - 2 * k, [3] + [2] * (k - 3) + [1], 12)),
           E=lambda a: 'HALT' if a % 2 == 0 else ([3] + [2] * ((3 * a - 3) // 2) + [1], 12)),
 'j': dict(M='1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_1RA1LG_---0LE', T='R,A,P=-,u=1,s=0,d=1d+0,b=1b+0,S=-', B=1,
           al=3, be=3, ga=3, de=3, ep=-2, t=2, a0=2, E=lambda a: 'HALT' if a % 2 == 0 else ([3] + [2] * ((3 * a - 1) // 2), 2)),
}
def strip(ds):
    i = 0
    while i < len(ds) and ds[i] == 0: i += 1
    return ds[i:]
def pred(R, ds, a):
    ds = strip(ds)
    if not ds: return R['E'](a)
    if ds[-1] > 0: return (strip(ds[:-1] + [ds[-1] - 1]), R['al'] * a + R['be'])
    k = 0
    while ds[-1 - k] == 0: k += 1
    y = ds[-1 - k]
    if 'Bf' in R:
        ref, tail, a0 = R['Bf'](k, a); return (strip(ds[:-1 - k] + [y - 1, ref] + tail), a0)
    return (strip(ds[:-1 - k] + [y - 1, R['ga'] * a + R['de'] + R['ep'] * k] + [R['t']] * (k - 1)), R['a0'])
def literal(R, T, ds, a, steps=3 * 10**7):
    ev = kl.run(R['M'], ds, a, R['B'], steps, 0, 100000, T=T, pall=1)
    for e in ev[1:]:
        if e[0] == 'H': return 'HALT'
        if e[0] == 'K' and e[4] == R['B']: return (strip(e[2]), e[3])
    return 'T'
if __name__ == '__main__':
    name = sys.argv[1]; R = dict(RULES[name.split(':')[0]]); p = name.split(':'); R['M'] = p[1] if len(p) > 1 else R['M']; R['T'] = p[2] if len(p) > 2 else R['T']; T = kl.tmpl(R['M'], R['T'])
    random.seed(int(sys.argv[2])); NT = int(sys.argv[3]); ok = bad = to = 0
    for i in range(NT):
        n = random.randint(0, 4)
        ds = [random.randint(1, 4)] + [random.choice([0, 0, 1, 2, 3, 5]) for _ in range(n)] if random.random() < .9 else []
        s = strip(ds); k = 0
        while s and s[-1 - k] == 0 if k < len(s) else False: k += 1
        a = random.randint(max(1, (2 * k + 2) // 3 + 1), 9)
        p, l = pred(R, ds, a), literal(R, T, ds, a)
        if l == 'T': to += 1; print('TIMEOUT', ds, a, 'pred', p); continue
        if p == l: ok += 1
        else: bad += 1; print('BAD', ds, a, 'pred', p, 'lit', l)
    print(name, R['M'], f'ok {ok} bad {bad} timeout {to}', flush=True)
