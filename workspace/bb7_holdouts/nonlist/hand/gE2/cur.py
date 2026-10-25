"""cur.py TAG K MACRO [SHOWN] [W]: show lines for one machine (trunc W)"""
import sys, subprocess
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\nonlist'); import idle
D = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\nonlist'
tag, K, mm = sys.argv[1:4]; sh = sys.argv[4] if len(sys.argv)>4 else '30'; W=int(sys.argv[5]) if len(sys.argv)>5 else 200
m = dict(l.split('\t')[:2] for l in open('list.tsv'))[tag]
fn = f'tmpc_{tag}.txt'; open(fn, 'w').write(m + '\n')
p = subprocess.Popen([D + r'\nlp7v.exe', fn, 'NUL', mm, '--life', '--K=' + K, '--show=' + sh] + sys.argv[6:], stdout=subprocess.PIPE, text=True, creationflags=0x40)
open(D + r'\pids.txt', 'a').write(f'{p.pid}\tgroupE2\tnlp7v {tag} K{K}\n')
for l in p.communicate()[0].splitlines(): print(l[:W])
