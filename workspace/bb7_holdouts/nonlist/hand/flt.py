"""flt.py DROP [W]: filter nlp7v --show lines: print when the line minus its last DROP tokens changes."""
import sys, re
D = int(sys.argv[1]); W = int(sys.argv[2]) if len(sys.argv) > 2 else 200
prev = None
for l in sys.stdin:
    if '|' not in l: continue
    a, b = l.split('|', 1); t = b.split()
    k = ' '.join(t[:-D]) if D else b
    if k != prev: print((a.strip() + ' | ' + b.strip())[:W]); prev = k
