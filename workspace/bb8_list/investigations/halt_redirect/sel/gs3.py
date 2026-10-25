"""gs3.py: for each machine in IN.tsv (col 1), follow (std policy) from a start configuration for N stages; report HALT/LOOP/...
usage: python gs3.py IN.tsv OUT.tsv "start tokens" [stages=12] [maxs=3e7]"""
import sys, io, threading
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/halt_redirect/mf')
import ord_run
sys.setrecursionlimit(30000); threading.stack_size(64 * 1024 * 1024)
def expand(s):
    v = []
    for t in s.split():
        if '^' in t:
            x, c = t.split('^'); v += [int(x)] * int(c)
        else: v.append(int(t))
    return v
src, out, start = sys.argv[1], sys.argv[2], expand(sys.argv[3])
ST = int(sys.argv[4]) if len(sys.argv) > 4 else 12; MS = int(float(sys.argv[5])) if len(sys.argv) > 5 else 30_000_000
def main():
    seen = set()
    with open(out, 'w') as f:
        for l in open(src):
            m = l.split('\t')[0].strip()
            if not m or m in seen: continue
            seen.add(m)
            lines = []
            try:
                k = ord_run.follow(6, 'std', ST, MS, 1, log=lines.append, start=list(start), FAM='GH', M=m)
            except Exception as ex:
                k = 'CRASH ' + repr(ex)[:60]
            ks = [x for x in lines if ' K: ' in x or 'HALT' in x]
            f.write(f'{m}\t{k}\t{len(ks)}\t' + ' ;; '.join(x[:70] for x in ks) + '\n'); f.flush()
t = threading.Thread(target=main); t.start(); t.join()
