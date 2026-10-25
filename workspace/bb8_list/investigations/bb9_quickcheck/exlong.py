"""exlong.py IN.tsv OUT.txt : rows whose exprobe probes timed out: K(0^n;0;b), n = start length, b = 5, 6, run 2e9
literal steps (sim9, Idle) and print the 1e8/1e9/final tape summaries."""
import re, subprocess, sys
sys.path.insert(0, '.')
from exprobe import word, NST, SIM
out = open(sys.argv[2], 'w')
for l in open(sys.argv[1]):
    r = l.rstrip('\n').split('\t')
    if 'T' not in r[5].split()[-1]: continue
    full = [x.rstrip('\n').split('\t') for x in open('roots9_dl3_withparent.tsv') if x.split('\t')[3] == r[3]][0]
    for b in (5, 6):
        w, q = word(full[7], NST[r[0]], b)
        p = subprocess.run([SIM, r[3], w, str(len(w)), q, '2000000000', '160'], capture_output=True, text=True,
                           creationflags=0x40).stdout
        out.write(f'== {r[0]} {r[1]} {r[4]} {r[3]} n={NST[r[0]]} b={b}\n')
        ls = p.splitlines()
        out.write('\n'.join(ls[-7:]) + '\n'); out.flush()
