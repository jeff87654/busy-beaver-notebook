"""Build a candidate machine from a climb JSON: writes NAME.tm and NAME.json; prints state counts."""
import sys, json
import zfp
cfg = json.load(open(sys.argv[1])); name = sys.argv[2]
perm = {k: tuple(v) for k, v in cfg.get('perm', {}).items()}
z = zfp.build(zfp.make(cfg['clauses'], perm, cfg.get('opt', []), cfg.get('vmap', {}), cfg.get('flips', {})), cfg['order'])
z.tm.save(name + '.tm')
json.dump({'clauses': cfg['clauses'], 'order': cfg['order'], 'perm': cfg.get('perm', {}), 'opt': cfg.get('opt', []), 'vmap': cfg.get('vmap', {}), 'flips': cfg.get('flips', {})},
          open(name + '.json', 'w'), indent=1)
st = set(s[0] for s in z.tm.states)
print(name, 'total', len(st), 'framework', sum(1 for s in st if s[0].isdigit()), 'dag', sum(1 for s in st if not s[0].isdigit()))
