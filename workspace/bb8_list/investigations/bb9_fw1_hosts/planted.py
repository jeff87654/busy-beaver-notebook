"""planted.py BASE.jsonl OUT.jsonl [WORKERS=2] [FILTER=all|nonOUT]: planted-block chains. For each classified machine with
a round-0 reset word W0 (b1=3), start from X + 0^g + W0 (X in XS, g in 1..3), head right of it in the template state,
and run the MODE-1 chain (6 rounds, b1=3). Record each round's O, ones(O), n, lo, vis, halts/timeouts."""
import idle, json, sys, os
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe import tmpl, hpc, lock
from classify import cls
XS = {'1^8': '1' * 8, '1^9': '1' * 9, '(10)^6': '10' * 6, '(110)^5': '110' * 5, '(100)^5': '100' * 5, '(1100)^4': '1100' * 4}
def job(r, out):
    T = tmpl(r['t']); lo0, w0 = r['w0']
    res = dict(m=r['m'], cls=r['c']['cls'], pl={})
    for xn, X in XS.items():
        for g in (1, 2, 3):
            w = X + '0' * g + w0
            rs, _ = hpc(r['m'], T, 3, word=w, pos=len(w), state=T['q'], rounds=6, maxs=20000000, prw=0)
            for x in rs:
                if 'O' in x: x['ones'] = sum(int(p.split('^')[1]) if p.startswith('1^') else p.count('1') for p in x['O'].split())
            res['pl'][f'{xn}/g{g}'] = rs
    with lock:
        with open(out, 'a') as f: f.write(json.dumps(res) + '\n')
if __name__ == '__main__':
    base, out = sys.argv[1], sys.argv[2]; W = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    filt = sys.argv[4] if len(sys.argv) > 4 else 'all'
    done = set()
    if os.path.exists(out):
        for l in open(out): done.add(json.loads(l)['m'])
    rows = []
    for l in open(base):
        r = json.loads(l)
        if r['m'] in done or 'w0' not in r: continue
        r['c'] = cls(r)
        if r['c']['cls'] == 'NONE': continue
        if filt == 'nonOUT' and r['c']['cls'] == 'OUT' and not r['c'].get('creates'): continue
        rows.append(r)
    print(len(rows), 'to do', flush=True)
    with ThreadPoolExecutor(W) as ex:
        for r in rows: ex.submit(job, r, out)
