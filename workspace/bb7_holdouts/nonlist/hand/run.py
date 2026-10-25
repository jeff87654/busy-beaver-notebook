"""run.py ARGS...: run nlp7v.exe at idle priority, record pid, pass stdout."""
import sys, subprocess
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\nonlist'); import idle
exe = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\nonlist\nlp7v.exe'
args = sys.argv[1:]
if args and args[0].endswith('.exe') or (args and args[0].endswith('.py')): cmd = args
else: cmd = [exe] + args
if cmd[0].endswith('.py'): cmd = [sys.executable] + cmd
p = subprocess.Popen(cmd, creationflags=0x40)
open(r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\nonlist\pids.txt','a').write(f'{p.pid}\tgroupB\t{" ".join(cmd)[:80]}\n')
p.wait()
