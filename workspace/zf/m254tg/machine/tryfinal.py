import sys, json, itertools
sys.path.insert(0, '.')
import gen, search
lab = dict(search.FIXED, w='d', x='b', u2='c', W='c', z='d', u1='c', C='c', p='c')
recs = [json.loads(l) for f in ['search_ug0d_%d.jsonl' % i for i in range(4)] for l in open(f)]
recs.sort(key=lambda r: r['states'])
best = [r for r in recs if r['states'] <= 289]
res = []
for r in best:
    ug = search.render(search.base('ug0d', r['o']), lab)
    Vi, Ve = gen.V()[1], gen.V()[2]
    for top in range(6):
        V2 = ('and', Ve, Vi) if r['vflip'] else ('and', Vi, Ve)
        f = [('and', ug, V2), ('and', V2, ug), ('and', ('and', ug, Vi), Ve), ('and', ('and', ug, Ve), Vi),
             ('and', Vi, ('and', ug, Ve)), ('and', Ve, ('and', ug, Vi))][top]
        gen.gen_source('tryfinal', fn=lambda f=f: f)
        z, ns = gen.compile_variant('tryfinal')
        res.append((ns, top, r['o'], r['vflip']))
res.sort(key=lambda x: x[0])
for x in res[:8]: print(x)
