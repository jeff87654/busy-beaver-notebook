"""gs4.py: follow machines (col 1 of IN.tsv) from the real start (b0 = 6, std policy) for N stages; summarise the
D6-counter count and the zeros per stage.  usage: python gs4.py IN.tsv OUT.tsv [stages=50] [maxs=3e7]"""
import sys, threading, re
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/halt_redirect/mf')
import ord_run
sys.setrecursionlimit(30000); threading.stack_size(64 * 1024 * 1024)
src, out = sys.argv[1], sys.argv[2]
ST = int(sys.argv[3]) if len(sys.argv) > 3 else 50; MS = int(float(sys.argv[4])) if len(sys.argv) > 4 else 30_000_000
done = set()
try:
    done = set(l.split('\t')[0] for l in open(out))
except FileNotFoundError:
    pass
def summarise(lines):
    res = []
    for x in lines:
        if ' K: ' in x:
            body = x.split(' K: ', 1)[1]
            m6 = re.match(r'6\^(\d+) ', body) or re.match(r'6 ', body)
            c6 = int(m6.group(1)) if m6 and m6.groups() else (1 if m6 else 0)
            mz = re.search(r'1\^(\d+) \| a=', body)
            z = int(mz.group(1)) if mz else 0
            res.append(f'{c6}:{z}')
        elif 'HALT' in x or 'JUMPFAIL' in x or ' T ' in x or ' W ' in x:
            res.append(x.split(' ', 1)[1][:30])
    return res
def main():
    with open(out, 'a') as f:
        for l in open(src):
            m = l.split('\t')[0].strip()
            if not m or m in done: continue
            done.add(m)
            lines = []
            try:
                k = ord_run.follow(6, 'std', ST, MS, 1, log=lines.append, FAM='GH', M=m)
            except Exception as ex:
                k = 'CRASH ' + repr(ex)[:60]
            s = summarise(lines)
            f.write(f'{m}\t{k}\t{len(s)}\t' + ' '.join(s) + '\n'); f.flush()
t = threading.Thread(target=main); t.start(); t.join()
