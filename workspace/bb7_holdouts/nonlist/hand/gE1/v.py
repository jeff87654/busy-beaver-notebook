"""v.py MACHINE K MACRO SHOWN [extra]: nlp7v --show at idle priority (groupE1); prints last N lines via --tail=N, width W."""
import sys, subprocess, tempfile, os
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\nonlist'); import idle
D = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\nonlist'
a = sys.argv[1:]; tail = None; W = 220
for x in list(a):
    if x.startswith('--tail='): tail = int(x[7:]); a.remove(x)
    if x.startswith('--w='): W = int(x[4:]); a.remove(x)
m, K, mm, sh = a[:4]
fd, fn = tempfile.mkstemp(suffix='.txt', dir=os.path.dirname(os.path.abspath(__file__))); os.write(fd, (m + '\n').encode()); os.close(fd)
args = [D + r'\nlp7v.exe', fn, 'NUL', mm, '--life', '--K=' + K] + (['--show=' + sh] if sh != '0' else []) + a[4:]
p = subprocess.Popen(args, creationflags=0x40, stdout=subprocess.PIPE, text=True)
open(D + r'\pids.txt', 'a').write(f'{p.pid}\tgroupE1\tnlp7v {K} {mm}\n')
out = p.stdout.read().splitlines(); p.wait(); os.remove(fn)
if tail: out = out[-tail:]
for l in out: print(l[:W])
