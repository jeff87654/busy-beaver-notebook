import idle, json, sys
from concurrent.futures import ThreadPoolExecutor
from probe import tmpl, hpc
pool = {l.split('\t')[0]: l.rstrip('\n').split('\t') for l in open('pool.tsv')}
def job(m):
    T = tmpl(pool[m][4]); res = {}
    for b1 in (3, 4):
        rs, _ = hpc(m, T, b1, rounds=4, maxs=300000000)
        res[b1] = [(x['r'], x.get('n'), x.get('lo'), x.get('O', '')[:30], x.get('halt'), x.get('timeout'), x.get('wide')) for x in rs]
    return m, res
with ThreadPoolExecutor(2) as ex:
    for m, res in ex.map(job, [l.strip() for l in open('tlist.txt')]):
        print(m, json.dumps(res), flush=True)
