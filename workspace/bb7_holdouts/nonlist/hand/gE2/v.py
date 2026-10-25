"""v.py MACHINE K MACRO SHOWN [extra]: nlp7v --show at idle priority."""
import sys, subprocess, tempfile, os
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\nonlist'); import idle
D = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\nonlist'
m, K, mm, sh = sys.argv[1:5]
fd, fn = tempfile.mkstemp(suffix='.txt', dir=os.path.dirname(os.path.abspath(__file__))); os.write(fd, (m + '\n').encode()); os.close(fd)
args = [D + r'\nlp7v.exe', fn, 'NUL', mm, '--life', '--K=' + K] + (['--show=' + sh] if sh != '0' else []) + sys.argv[5:]
p = subprocess.Popen(args, creationflags=0x40)
open(D + r'\pids.txt', 'a').write(f'{p.pid}\tgroupE2\tnlp7v {K} {mm}\n'); p.wait(); os.remove(fn)
