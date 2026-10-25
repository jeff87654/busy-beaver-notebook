"""plsum.py BASE.jsonl PLANTED.jsonl: summarise planted chains per machine and variant.
H<r>:<slot> halt in round r | T<r> timeout | SURV planted ones persist in O through the last round (vs base b1=3 chain)
| ABS<r> planted ones gone from O by round r. Flags machines with a late halt (r>=2) or SURV."""
import idle, json, sys, collections
base = {}
for l in open(sys.argv[1]):
    r = json.loads(l); base[r['m']] = r
def ones(O): return sum(int(p.split('^')[1]) if p.startswith('1^') else p.count('1') for p in O.split())
C = collections.Counter(); flag = []
for l in open(sys.argv[2]):
    p = json.loads(l); b = base[p['m']]; bch = [x for x in b['ch']['3'] if 'n' in x]
    bo = {x['r']: ones(x['O']) for x in bch}; bn = {x['r']: x['n'] for x in bch}
    outs = {}
    for v, rs in p['pl'].items():
        o = None
        for x in rs:
            if 'halt' in x: o = f"H{x['r']}:{x['halt']}"; break
            if 'timeout' in x: o = f"T{x['r']}"; break
        if o is None:
            good = [x for x in rs if 'n' in x]
            extra = [ones(x['O']) - bo.get(x['r'], 0) for x in good]
            if good and all(e > 0 for e in extra[1:]) and len(good) >= 4: o = 'SURV' + ('=' if good[-1]['n'] == bn.get(good[-1]['r']) else '~')
            else:
                k = next((i for i, e in enumerate(extra) if e <= 0), len(extra)); o = f'ABS{k}'
        outs[v] = o; C[o[:4] if not o.startswith('H') else 'H' + o[1]] += 1
    late = [v for v, o in outs.items() if (o.startswith('H') and int(o[1]) >= 2) or o.startswith('SURV')]
    if late: flag.append((p['m'], p['cls'], {v: outs[v] for v in late}))
print(C)
for f in flag: print(*f)
