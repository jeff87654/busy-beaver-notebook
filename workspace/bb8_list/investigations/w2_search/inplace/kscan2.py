"""kscan2.py IN OUT [--kmax 3]: hook scan at the REAL depth class.  For each machine: (1) RSIGs from far_17 +
[0 1^329|1|19] (std; 329 = the real-start std depth at the round-1 end, = 35 mod 42 like the big real run);
(2) if >= 2 RSIGs: normal = all k-grams of the real-start round 1 (b0 = 6 std, stages 0..37) + constructed stages
0 .. s2-w-1 at k = 17, 29, 41; special = stages s2-w .. s2 at k = 17 (w = s1 + 3).  Prints special-only grams."""
import sys, os, subprocess, threading, argparse
from ilib import stage, rsig, far_of, word_of, SUF, real_start
HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser(); ap.add_argument('inp'); ap.add_argument('out'); ap.add_argument('--kmax', type=int, default=3)
ap.add_argument('--n', type=int, default=329); ap.add_argument('--S', type=int, default=140)
a = ap.parse_args()
def kg(M, word, head=None, state='G'):
    head = len(word) if head is None else head
    p = subprocess.run([os.path.join(HERE, 'kgram.exe'), M, state, str(head), str(10**9), 'G', SUF, '1', str(a.kmax), '600'],
                       input=word, capture_output=True, text=True, creationflags=0x40)
    d = set()
    for l in p.stdout.splitlines()[1:]:
        _, k, g, c, f = l.split(); d.add((int(k), g))
    return d
def rsigs(M, k):
    word = far_of(k) + word_of([0] + [1] * a.n + [1, 19]) + SUF; rs = []
    for st in range(a.S):
        kind, d = stage(M, word, 10**9)
        if kind != 'K': return rs, f'{kind}{d.get("slot","")}@{st}'
        r = rsig(d['toks'])
        if r and st > 0 and (not rs or st - rs[-1][0] > 3): rs.append((st, len(r[0]), r[1], r[2]))
        if len(rs) >= 3: return rs, 'RS3'
        word = d['newword']
    return rs, 'MAX'
REAL = None
def real_grams(M):
    word, head, state = real_start(6); N = set()
    for st in range(38):
        N |= kg(M, word, head, state)
        kind, d = stage(M, word, 10**9, head=head, state=state); head, state = None, 'G'
        if kind != 'K': break
        word = d['newword']
    return N
def scan(M, s1, s2):
    w = s1 + 3; N = real_grams(M); S = set()
    for i, k in enumerate((17, 29, 41)):
        word = far_of(k) + word_of([0] + [1] * a.n + [1, 19]) + SUF
        for st in range(s2 + 1):
            if st < s2 - w: N |= kg(M, word)
            elif i == 0: S |= kg(M, word)
            else: break
            kind, d = stage(M, word, 10**9)
            if kind != 'K': return f'stop k={k} st={st} {kind}', []
            word = d['newword']
    return 'ok', sorted(S - N)
def go():
    fo = open(a.out, 'w')
    for line in open(a.inp):
        M = line.split('\t')[0].strip()
        rs, out = rsigs(M, 17)
        rss = ' '.join(f'{s}:P{p}:c{c}:z{z}' for s, p, c, z in rs)
        if len(rs) < 2:
            row = f'{M}\t{rss}\t{out}\tskip'
        else:
            r, u = scan(M, rs[0][0], rs[1][0])
            cnt = {k: sum(1 for g in u if g[0] == k) for k in range(2, a.kmax + 1)}
            row = f'{M}\t{rss}\t{r}\t{cnt}\t' + ' '.join(g[1] for g in u[:10])
        print(row, flush=True); fo.write(row + '\n'); fo.flush()
threading.stack_size(250 * 1024 * 1024); sys.setrecursionlimit(300000)
t = threading.Thread(target=go); t.start(); t.join()
