"""towercls_all.py SHARD NSHARD : towercls for every pool base (resumable) -> towercls_SHARD.jsonl"""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import towercls
sh, ns = int(sys.argv[1]), int(sys.argv[2])
d = json.load(open('pool.json'))['pool']
ms = sorted(d)
out = 'towercls_%d.jsonl' % sh
done = set()
if os.path.exists(out):
    for l in open(out):
        try: done.add(json.loads(l)['machine'])
        except Exception: pass
with open(out, 'a') as f:
    for i, m in enumerate(ms):
        if i % ns != sh or m in done: continue
        try:
            o, R = towercls.towercls(m, d[m][0])
        except Exception as e:
            o = {'machine': m, 'err': repr(e)[:200]}
        f.write(json.dumps(o) + '\n'); f.flush()
