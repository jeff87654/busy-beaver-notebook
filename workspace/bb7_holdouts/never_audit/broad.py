"""broad.py: light audit2 over every detected target row (sequential, idle). Writes broad.jsonl + logs/ROW.txt"""
import sys, idle_guard, json, os, traceback, time
sys.argv = sys.argv[:1]
from audit2 import audit
os.makedirs('logs', exist_ok=True)
det = [l.rstrip('\n').split('\t') for l in open(os.environ.get('DET', 'detect2.tsv'))]
done = set()
try: done = set(json.loads(l)['machine'] for l in open(os.environ.get('BOUT', 'broad.jsonl')))
except Exception: pass
only = set(open(os.environ['ONLY']).read().split()) if os.environ.get('ONLY') else None
for d in det:
    if len(d) < 7 or float(d[6]) < 0.9 or d[0] in done: continue
    if only is not None and d[0] not in only: continue
    m, Q, side, TF, Z, cod = d[0], d[1], d[2], d[3], int(d[4]), d[5]
    TF = [] if TF == '-' else [int(x) for x in TF.split(',')]
    lf = open('logs/%s.txt' % m, 'w')
    def out(s): lf.write(time.strftime('%H:%M:%S ') + s + '\n'); lf.flush()
    try:
        R = audit(m, Q, side, TF, Z, int(os.environ.get('LSTEPS', '100000000')), int(os.environ.get('NCL', '24')),
                  light=not os.environ.get('FULL'), out=out, coding=cod)
    except Exception as ex:
        R = {'machine': m, 'verdict': 'ERROR ' + repr(ex)[:200]}; out(traceback.format_exc())
    lf.close()
    with open(os.environ.get('BOUT', 'broad.jsonl'), 'a') as f: f.write(json.dumps(R, default=str) + '\n')
