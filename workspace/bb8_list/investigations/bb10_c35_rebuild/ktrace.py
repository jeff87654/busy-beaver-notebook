"""Print the event configurations (IN) and jump K-moments (J) of a mini-follower run, tokens left-to-right,
huge tokens kept.  python ktrace.py MACHINE MODE STAGES [FIXREP] [SHOWFROM]"""
import sys, threading
sys.setrecursionlimit(200000)
threading.stack_size(256 * 1024 * 1024 - 4096)
import mf35
M, mode, st = sys.argv[1], sys.argv[2], int(sys.argv[3])
if len(sys.argv) > 4 and int(sys.argv[4]):
    mf35.FIXREP = int(sys.argv[4])
show = int(sys.argv[5]) if len(sys.argv) > 5 else 0
cnt = [0]
orig = mf35.run_stage
def toks(w):
    t = []; i = 0
    while i < len(w):
        if w[i] == '1':
            j = i; c = 0
            while w[j + 1:j + 3] == '01':
                j += 2; c += 1
            t.append(c); i = j + 1
        else:
            t.append('_'); i += 1
    return t
def rs(m, w, h, s, mx, maxw=None, rcap=600):
    o = orig(m, w, h, s, mx, maxw, rcap)
    cnt[0] += 1
    if cnt[0] >= show:
        print(cnt[0], 'IN ', mf35.rle(toks(w))[-160:])
        if o.startswith('J'):
            p = o.split('|'); tt = [int(x) for x in p[1].split()]
            print('    J', p[0].split()[1], mf35.rle(tt[::-1])[-160:])
        else:
            print('    ', o[:120])
    return o
mf35.run_stage = rs
def main():
    k, h = mf35.follow(M, mode, st, 400_000_000)
    print(k, len(h), h[-1])
t = threading.Thread(target=main); t.start(); t.join()
