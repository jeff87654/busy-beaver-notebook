"""classify.py IN.jsonl [OUT.tsv]: classify base host-probe chains.
Per machine: geometry of the MSD (outer) end over rounds r>=2 (dlo = lo_r - lo_(r-1), template frame, outward = negative):
  STATIC (dlo = 0), OUT (dlo < 0: rebuild extends outward past the old separator), IN (dlo > 0), MIXED;
  CREATES if the outer prefix O depends on b1 (longer for b1 = 4) or grows over rounds;
  NONE if a chain halts / times out / has < 3 rounds. growth: n(R2, b1=4) vs n(R2, b1=3).
  peek = how far beyond the previous leftmost 1 the head went in a round (max over r>=2)."""
import idle, json, sys, collections
def cls(r):
    if 'err' in r: return dict(cls='NONE', why='err')
    ch = {int(k): v for k, v in r['ch'].items()}
    why = []
    for b in (3, 4):
        rs = ch.get(b, [])
        bad = [x for x in rs if 'n' not in x]
        if bad: why.append(f"b{b}:{'H' + bad[0]['halt'] if 'halt' in bad[0] else 'T'}@R{bad[0]['r']}")
    good = {b: [x for x in ch.get(b, []) if 'n' in x] for b in (3, 4)}
    if min(len(good[3]), len(good[4])) < 3: return dict(cls='NONE', why=' '.join(why) or 'short')
    n3, n4 = good[3][2]['n'], good[4][2]['n']
    growth = 'grow' if n4 > n3 else ('fixed' if n4 == n3 else 'shrink')
    dl = []; pk = []
    for b in (3, 4):
        g = good[b]
        for i in range(2, len(g)):
            dl.append(g[i]['lo'] - g[i - 1]['lo']); pk.append(g[i - 1]['lo'] - g[i]['vis'])
    nr = len(good[3]) - 2
    dl3, dl4 = dl[:nr], dl[nr:]
    if all(d == 0 for d in dl): geo = 'STATIC'
    elif all(d < 0 for d in dl) and len(set(dl)) == 1: geo = 'SHIFT'
    elif all(d < 0 for d in dl) and min(dl4) < min(dl3): geo = 'OUT'
    elif all(d < 0 for d in dl): geo = 'OUTc'
    elif all(d > 0 for d in dl): geo = 'IN'
    else: geo = 'MIXED'
    Os3 = [x['O'] for x in good[3][1:]]; Os4 = [x['O'] for x in good[4][1:]]
    Ol3 = [x['Ol'] for x in good[3][1:]]; Ol4 = [x['Ol'] for x in good[4][1:]]
    creates = (Ol4[0] > Ol3[0]) or (Ol3[-1] > Ol3[0]) or (Ol4[-1] > Ol4[0])
    ovar = len(set(Os3)) > 1 or len(set(Os4)) > 1
    return dict(cls=geo, growth=growth, n=f'{n3}/{n4}', dlo=dl, peek=max(pk), creates=creates, ovar=ovar, O3=Os3[-1][:40], O4=Os4[-1][:40], why=' '.join(why))
if __name__ == '__main__':
    rows = [json.loads(l) for l in open(sys.argv[1])]
    out = open(sys.argv[2], 'w', newline='\n') if len(sys.argv) > 2 else None
    C = collections.Counter()
    for r in rows:
        c = cls(r); r['c'] = c
        key = (r.get('ns'), c['cls'], c.get('growth', '-'), 'C' if c.get('creates') else '', 'Ov' if c.get('ovar') else '')
        C[key] += 1
        if out: out.write('\t'.join(map(str, [r['m'], r.get('ns'), r.get('src'), r.get('grade'), c['cls'], c.get('growth', '-'), c.get('n', '-'),
                                             'CREATES' if c.get('creates') else '-', 'Ovar' if c.get('ovar') else '-', c.get('peek', '-'),
                                             ','.join(map(str, c.get('dlo', [])))[:60], c.get('O3', ''), c.get('O4', ''), c['why']])) + '\n')
    for k, v in sorted(C.items(), key=lambda kv: (str(kv[0][0]), -kv[1])): print(k, v)
