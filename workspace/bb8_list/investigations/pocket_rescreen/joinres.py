import json, collections
L = [l.rstrip('\n').split('\t') for l in open('rank_main.tsv')]
reb = {json.loads(l)['machine']: str(json.loads(l).get('verdict')) for l in open('reb_all.jsonl')}
mr = {json.loads(l)['machine']: str(json.loads(l).get('verdict')) for l in open('mr.jsonl')}
def short(v): return v.split('(')[0].split('+')[0] if v != '-' else '-'
c = collections.Counter()
with open('joined.tsv', 'w', newline='\n') as o:
    o.write('rank\tmachine\tgrade\trank_verdict\test_level\treb7\tmrounds\n')
    for f in L[1:]:
        m = f[1]; r = reb.get(m, '-'); x = mr.get(m, '-')
        fin = short(x) if x != '-' else short(r)
        c[(short(f[3]), fin)] += 1
        o.write('\t'.join([f[0], m, f[2], f[3], f[4], r[:90], x[:90]]) + '\n')
for k, v in sorted(c.items(), key=lambda t: -t[1]): print(v, k)
