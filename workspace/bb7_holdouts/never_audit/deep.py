"""deep.py LIST OUT.jsonl : medium audit2 over the machines of LIST (first column), in order; detection via detect2 (cached
in det_deep.tsv). Env: NCL (48), LSTEPS (1e9), MED=1 default."""
import sys, os, json, time, traceback, idle_guard
LIST, BOUT = sys.argv[1], sys.argv[2]
sys.argv = sys.argv[:1]
os.environ.setdefault('MED', '1')
from audit2 import audit
from fam import detect2
os.makedirs('logs', exist_ok=True)
cache = {}
for f in ('detect2.tsv', 'det_deep.tsv'):
    try:
        for l in open(f):
            d = l.rstrip('\n').split('\t')
            if len(d) >= 7: cache[d[0]] = d
    except Exception: pass
done = set()
try: done = set(json.loads(l)['machine'] for l in open(BOUT))
except Exception: pass
for line in open(LIST):
    m = line.split()[0]
    if m in done: continue
    d = cache.get(m)
    if d is None:
        x = detect2(m, 1500000)
        d = [m, '-'] if x is None else [m, x[1], x[2], ','.join(map(str, x[3])) or '-', str(x[4]), x[5], '%.3f' % x[6]]
        with open('det_deep.tsv', 'a') as f: f.write('\t'.join(d) + '\n')
    if len(d) < 7 or float(d[6]) < 0.9:
        R = {'machine': m, 'verdict': 'NO-TEMPLATE (detect score %s)' % (d[6] if len(d) > 6 else '-')}
    else:
        Q, side, TF, Z, cod = d[1], d[2], d[3], int(d[4]), d[5]
        TF = [] if TF == '-' else [int(x) for x in TF.split(',')]
        lf = open('logs/%s.txt' % m, 'w')
        def out(s): lf.write(time.strftime('%H:%M:%S ') + s + '\n'); lf.flush()
        t0 = time.time()
        try:
            R = audit(m, Q, side, TF, Z, int(os.environ.get('LSTEPS', '1000000000')), int(os.environ.get('NCL', '48')),
                      light=bool(os.environ.get('LIGHT')), out=out, coding=cod)
        except Exception as ex:
            R = {'machine': m, 'verdict': 'ERROR ' + repr(ex)[:200]}; out(traceback.format_exc())
        R['secs'] = round(time.time() - t0); R['template'] = d[1:6]
        lf.close()
    with open(BOUT, 'a') as f: f.write(json.dumps(R, default=str) + '\n')
