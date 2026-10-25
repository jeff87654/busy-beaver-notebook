import idle, sys, itertools
def parse(m):
    rows = m.split('_'); t = {}
    for i, r in enumerate(rows):
        for c in range(2):
            x = r[3*c:3*c+3]
            t[(i, c)] = None if x[0] == '-' else (int(x[0]), x[1], ord(x[2]) - 65)
    return t, len(rows)
def mirror(t):
    return {k: (None if v is None else (v[0], 'L' if v[1] == 'R' else 'R', v[2])) for k, v in t.items()}
def mapped(t, perm):  # perm: sibling state -> parent state
    out = {}
    for (s, c), v in t.items():
        out[(perm[s], c)] = None if v is None else (v[0], v[1], perm[v[2]])
    return out
def diff(a, b):
    return [k for k in a if a[k] != b[k] and not (a[k] is None and b[k] is None)]
def fmt(v): return '---' if v is None else '%d%s%s' % (v[0], v[1], chr(65 + v[2]))
PAR = {
 'A1': '1RB0LF_1RC1RF_1LD1RE_0LA1LD_---1RA_0RB1RG_0RA0LE',
 'A2': '1RB0LF_1RC1RF_1LD1RE_0LA1LD_---1RA_0RB1RG_0RA1RB',
 'B1': '1RB0RD_0LC1LC_1LE1LD_1RE1LB_1RG1LF_---0LE_1RA1RG',
 'C1': '1RB0RD_0RC1RG_1RD1RC_1LD0LE_0RB1LF_0LC1LE_---1RA',
 'M1': '1RB---_1RC0RG_1RD1RA_0LE0RF_1LG0LF_0RD1LB_1RE0LF',
 'M2': '1RB0RG_1RC1RF_0LD0RE_1LG0LE_0RC1LA_1RA---_1RD0LE',
 'M6': '1RB1LA_0LC0RE_1LA1LD_1LC1LB_0LG0RF_1RD1RE_---0LF',
 'M7': '1RB0LA_1LC1LG_0LD1LB_1RE0RB_0RF1RF_0LA0RE_0LC---',
 'M9': '1RB1LA_1LC0RC_0LA0LD_0RE1LD_0RF1LB_---0RG_1RC1RG',
 'N1': '1RB0RC_1LA0RC_0LG1RD_1LE0LB_1LG1LF_1LD---_0RA0LC',
 'N2': '1RB0RC_1RC0RA_1LD0LB_1LE0LA_0LF---_1RC0LG_1LF1LA',
 'R7': '1RB1RE_1LC1LB_0RE0LD_1LA1RG_0RD1RF_0LC1RA_0RA---',
 'C04': '1RB0RA_0RC0RA_1LD1RE_1LE1LD_---0RF_0RG0LB_1RB---',
 'X16384': '1RB1LD_0RC1RD_0LD1RE_1LA0LE_1RF1RC_0RG---_1RB0RD',
}
if __name__ == '__main__':
    for ln in open(sys.argv[1]):
        if not ln.strip(): continue
        m, blk = ln.split()
        ts, n = parse(m)
        best = []
        for name, pm in PAR.items():
            tp, _ = parse(pm)
            for mir in (False, True):
                t2 = mirror(ts) if mir else ts
                for perm in itertools.permutations(range(n)):
                    pass
                    d = diff(mapped(t2, perm), tp)
                    best.append((len(d), name, mir, perm, d))
        best.sort(key=lambda x: x[0])
        b = best[0]
        tm = mapped(mirror(ts) if b[2] else ts, b[3]); tp, _ = parse(PAR[b[1]])
        ds = ' '.join('%s%d:%s->%s' % (chr(65 + k[0]), k[1], fmt(tp[k]), fmt(tm[k])) for k in b[4])
        print(m, blk, 'best=%s ndiff=%d mir=%s start->%s' % (b[1], b[0], b[2], chr(65+b[3][0])), ds, '| 2nd=%s/%d' % (best[1][1], best[1][0]) if best[1][1] != b[1] else '')
    