"""Re-run every literal stage of a recorded trajectory under a different representative scheme and compare.
python recheck.py traj.pkl [first_stage] [last_stage]     env: REPMODE, GROW, MREP, NTR"""
import sys, os, pickle
import vals
import absim
from absim import *

d = pickle.load(open(sys.argv[1], 'rb'))
vals.ATOMS.update(d['ATOMS'])
vals._next[0] = max(d['ATOMS']) + 1
TR = d['TRAJ']
lo = int(sys.argv[2]) if len(sys.argv) > 2 else 1
hi = int(sys.argv[3]) if len(sys.argv) > 3 else len(TR)
ntr = int(os.environ.get('NTR', 2))
print('REPMODE', absim.REPMODE, 'GROW', absim.GROW, 'MREP', absim.MREP, flush=True)
bad = 0
for i in range(lo - 1, min(hi, len(TR))):
    runs = TR[i]
    if is_bform(runs):
        p = period_macro(runs) if False else None
        c = None
        # skip transitions that were macros: detect by re-deriving (CLR / PERIOD shapes)
        pm = absim.period_macro.__wrapped__(runs) if hasattr(absim.period_macro, '__wrapped__') else None
    nxt = TR[i + 1] if i + 1 < len(TR) else None
    # a literal transition is recognised by: not a CLR/PERIOD shape
    if is_bform(runs):
        save = dict(vals.ATOMS)
        pmc = absim.period_macro(runs)
        if pmc and pmc[0] == 'period':
            continue
        cc = absim.clr(runs)
        if cc and cc[0] == 'clr':
            continue
    try:
        kind, out, info = literal_stage(runs, ntr=ntr, seed=7)
    except NonUniform as e:
        print('stage %d NONUNIFORM %s' % (i + 1, str(e)[:300]), flush=True)
        bad += 1
        continue
    if kind == 'B':
        same = nxt is not None and len(out) == len(nxt) and all(
            tuple((x if isinstance(x, tuple) else Val.of(x)) for x in a[1:]) == tuple((x if isinstance(x, tuple) else Val.of(x)) for x in b[1:]) and a[0] == b[0] for a, b in zip(out, nxt))
        print('stage %d %s%s steps=%s t=%.1fs maxlen=%d' % (i + 1, 'SAME' if same else 'DIFFERENT', '' if same else (' (same shape)' if nxt is not None and [r[0] for r in out] == [r[0] for r in nxt] else ' (SHAPE DIFFERS)'), info['steps'][0],
                                                       info['time'], max(info['lens'])), flush=True)
        if not same:
            bad += 1
            print('   got ', show(out))
            print('   was ', show(nxt) if nxt else None)
    else:
        print('stage %d kind %s q=%s sym=%s steps=%s' % (i + 1, kind, info.get('q'), info.get('sym'), info['steps']), flush=True)
print('BAD', bad)
