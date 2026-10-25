"""Rank Quick_Sim results (ligocki_runner.py output) by decimal digits of the ones count reached.
Usage: python rank_growth.py result1.json [result2.json ...]"""
import json, sys, collections
rows = []
for p in sys.argv[1:]:
    for r in json.load(open(p))['results']:
        r['_src'] = p; rows.append(r)
def digits(r):
    o = r.get('ones') or {}
    k = o.get('kind')
    if k == 'integer': return len(o['decimal'])
    if k == 'large_integer': return o['bit_length'] * 0.30103
    if k == 'symbolic_expression': return float('inf')
    return -1
rows.sort(key=lambda r: -digits(r))
print(len(rows), 'machines;', collections.Counter(r['status'] for r in rows))
for i, r in enumerate(rows[:15]):
    print(f"{i+1:>3} {digits(r):>8.0f} {r['status']:>9} rules={r.get('rules_proven')} {r['machine']}")
