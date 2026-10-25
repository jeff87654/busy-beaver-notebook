import idle, subprocess, sys
# idlerun.py CMD ARGS... : run at idle priority, record pid, pass stdout through
p = subprocess.Popen(sys.argv[1:], creationflags=0x40)
with open(r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_fw1_counter\pids.txt', 'a') as f: f.write(f'{p.pid} {" ".join(sys.argv[1:])[:120]}\n')
sys.exit(p.wait())
