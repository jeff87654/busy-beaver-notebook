import json, re, sys
from collections import Counter, defaultdict
R = [json.loads(l) for l in open('bat2.jsonl')]
def gen(s): return re.sub(r'( 1){3,}', ' 1^n', re.sub(r'( 0){3,}', ' 0^n', s))
st = Counter(r['status'] for r in R); print(len(R), dict(st))
W = Counter(r['why'].split('(')[0] for r in R if r['status'] == 'UNFIT'); print('UNFIT reasons', dict(W))
G = defaultdict(list)
for r in R:
    if r['status'] != 'BAT': continue
    key = (r['e2'],) + tuple((k, gen(v[0]), gen(v[1])) for k, v in sorted(r['sig'].items()))
    G[key].append(r['M'])
print('groups', len(G))
for i, (key, ms) in enumerate(sorted(G.items(), key=lambda x: -len(x[1]))[:int(sys.argv[1]) if len(sys.argv) > 1 else 5]):
    print('== G%d n=%d e2=%s ex %s' % (i, len(ms), key[0], ms[0]))
    for k, a, b in key[1:]: print('   %-6s %s | %s' % (k, a[:60], b[:60]))
