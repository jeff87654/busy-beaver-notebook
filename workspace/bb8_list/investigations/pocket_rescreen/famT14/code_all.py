import sys, json, subprocess, os
sys.path.insert(0, '.')
import idle  # noqa
from detect2 import detect2
HERE = os.path.dirname(os.path.abspath(__file__)); SIM2 = os.path.join(HERE, 'sim2.exe')
ms = [l.split()[0] for l in open('roots1043.txt')]
out = open('code_all.jsonl', 'w')
for i, m in enumerate(ms):
    r = subprocess.run([SIM2, m, '1', 'A', '-', '0', '3000000', '*', '1'], capture_output=True, text=True).stdout
    cnt = [int(x) for x in r.split('CNT')[1].split('\n')[0].split()] if 'CNT' in r else []
    rec = dict(M=m, src='big' if i < 1043 else 'mid', cnt=cnt)
    if not cnt or max(cnt) < 50:
        rec['C'] = None; rec['why'] = 'few right-end events'
    else:
        qs = sorted([chr(65 + j) for j, c in enumerate(cnt) if c >= 0.3 * max(cnt)], key=lambda q: -cnt[ord(q) - 65])
        rec['C'] = None; whys = []
        for q in qs:
            C, e = detect2(m, q)
            if C: rec['C'] = C; rec['e2'] = e; break
            whys.append(q + ':' + str(e))
        if rec['C'] is None: rec['why'] = '; '.join(whys)[:120]
    out.write(json.dumps(rec) + '\n'); out.flush()
