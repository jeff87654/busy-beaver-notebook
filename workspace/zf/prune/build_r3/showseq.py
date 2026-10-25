"""Print the outlined sequence structure (before cons reduction) of a candidate config."""
import sys, json, zfp
cfg = json.load(open(sys.argv[1]))
perm = {k: tuple(v) for k, v in cfg.get('perm', {}).items()}
z = zfp.make(cfg['clauses'], perm, cfg.get('opt', []), cfg.get('vmap', {}), cfg.get('flips', {}))()
z.debug = False; z.AXIOMORDER = cfg['order']
z.main(); z.breakout_common_subsequences()
def nm(v):
    if isinstance(v, int):
        s = z.sequences[v]; return s.name or f'#{v}'
    return v[2:] if v.startswith('3.') else v
for i in sorted(z.reachable()):
    s = z.sequences[i]
    print(f'{i:4d} {str(s.name or ""):40s} len={len(s.seq):3d} :', ' '.join(nm(v) for v in s.seq))
