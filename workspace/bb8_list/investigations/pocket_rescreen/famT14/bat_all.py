"""bat_all.py: per machine: event-state choice (sim2 CNT), coding detect, battery signature -> bat.jsonl (resumable)"""
import sys, json, subprocess, os
sys.path.insert(0, '.')
import idle  # noqa
from ucode import detect
from battery import signature
HERE = os.path.dirname(os.path.abspath(__file__)); SIM2 = os.path.join(HERE, 'sim2.exe')
ms = [l.split()[0] for l in open('roots1043.txt')]
done = set()
if os.path.exists('bat.jsonl'):
    for l in open('bat.jsonl'): done.add(json.loads(l)['M'])
out = open('bat.jsonl', 'a')
for m in ms:
    if m in done: continue
    r = subprocess.run([SIM2, m, '1', 'A', '-', '0', '3000000', '*', '1'], capture_output=True, text=True).stdout
    cnt = [int(x) for x in r.split('CNT')[1].split('\n')[0].split()] if 'CNT' in r else []
    rec = dict(M=m, cnt=cnt)
    if not cnt or max(cnt) < 50:
        rec['status'] = 'UNFIT'; rec['why'] = 'few right-end events %s %s' % (cnt, r.strip().split('\n')[-1][:40])
    else:
        best = None
        for q in [chr(65 + i) for i, c in enumerate(cnt) if c >= 0.3 * max(cnt)]:
            C, why = detect(m, q, 3000000)
            ch = int(why.split('chains=')[1].split()[0]) if C else -1
            if C and (best is None or ch > best[2]): best = (C, why, ch)
        if best is None:
            rec['status'] = 'UNFIT'; rec['why'] = 'no coding: ' + why
        else:
            C = best[0]; rec['C'] = C; rec['why'] = best[1]
            rec['sig'] = signature(C)
            rec['status'] = 'BAT'
    out.write(json.dumps(rec) + '\n'); out.flush()
