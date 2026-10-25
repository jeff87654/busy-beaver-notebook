"""r.py ARGS...: run nlp7v.exe (or given exe) at idle priority, record pid (groupC), pass stdout."""
import sys, subprocess
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\nonlist'); import idle
exe = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\nonlist\nlp7v.exe'
args = sys.argv[1:]
cmd = args if args and args[0].endswith('.exe') else [exe] + args
p = subprocess.Popen(cmd, creationflags=0x40)
open(r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\nonlist\pids.txt','a').write(f'{p.pid}\tgroupC\t{" ".join(cmd)[:80]}\n')
p.wait()
