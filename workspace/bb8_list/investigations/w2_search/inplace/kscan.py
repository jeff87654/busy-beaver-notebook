"""kscan.py IN OUT [--kmax 3]: for each (machine, RSIG string) line, k-gram hook scan: normal = stages 0 .. s2-w-1 for
k = 17, 29, 41 (std, far_k + [0 1^41|1|19]); special = stages s2-w .. s2 for k = 17, where s1, s2 = the first two
RSIG stages and w = s1 + 3.  Prints the number of special-only grams per k and the first few."""
import sys, os, subprocess, threading, argparse
from ilib import stage, far_of, word_of, SUF
HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser(); ap.add_argument('inp'); ap.add_argument('out'); ap.add_argument('--kmax', type=int, default=3)
ap.add_argument('--ks', default='17,29,41')
a = ap.parse_args()
def kg(M, word):
    p = subprocess.run([os.path.join(HERE, 'kgram.exe'), M, 'G', str(len(word)), str(10**9), 'G', SUF, '1', str(a.kmax), '600'],
                       input=word, capture_output=True, text=True, creationflags=0x40)
    d = set()
    for l in p.stdout.splitlines()[1:]:
        _, k, g, c, f = l.split(); d.add((int(k), g))
    return d
def scan(M, s1, s2):
    w = s1 + 3; N = set(); S = set()
    for i, k in enumerate(map(int, a.ks.split(','))):
        word = far_of(k) + word_of([0] + [1] * 41 + [1, 19]) + SUF
        for st in range(s2 + 1):
            if st < s2 - w: N |= kg(M, word)
            elif i == 0: S |= kg(M, word)
            else: break
            kind, d = stage(M, word, 10**9)
            if kind != 'K': return f'stop k={k} st={st} {kind}', []
            word = d['newword']
    u = sorted(S - N)
    return 'ok', u
def go():
    fo = open(a.out, 'w')
    for line in open(a.inp):
        M, s = line.rstrip('\n').split('\t')
        st = [int(x.split(':')[0]) for x in s.split()]
        r, u = scan(M, st[0], st[1])
        cnt = {k: sum(1 for g in u if g[0] == k) for k in range(2, a.kmax + 1)}
        row = f'{M}\t{s[:60]}\t{r}\t{cnt}\t' + ' '.join(g[1] for g in u[:8])
        print(row, flush=True); fo.write(row + '\n'); fo.flush()
threading.stack_size(250 * 1024 * 1024); sys.setrecursionlimit(300000)
t = threading.Thread(target=go); t.start(); t.join()
