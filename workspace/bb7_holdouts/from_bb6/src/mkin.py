"""mkin.py MACHINES WORLDS OUT: ext.exe input (M line + all W lines per machine)"""
import sys
ms = [l.split()[0] for l in open(sys.argv[1]) if l.strip()]
ws = [l.strip() for l in open(sys.argv[2]) if l.startswith('W ')]
with open(sys.argv[3], 'w') as f:
    for m in ms:
        f.write('M ' + m + '\n')
        for w in ws: f.write(w + '\n')
