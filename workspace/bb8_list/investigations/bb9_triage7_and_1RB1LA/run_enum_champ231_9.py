import sys, os, subprocess, time
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

os.environ['PATH'] = r'C:\msys64\ucrt64\bin;C:\msys64\mingw64\bin;' + os.environ.get('PATH', '')
exe = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_triage7_and_1RB1LA\enum_champ231_9.exe'
pids_file = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_triage7_and_1RB1LA\pids.txt'

t0 = time.time()
p = subprocess.Popen([exe], creationflags=0x40, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
with open(pids_file, 'a') as f:
    f.write(f"enum_champ231_9 {p.pid}\n")

for line in p.stdout:
    print(f"[{time.time()-t0:.1f}s] {line}", end='', flush=True)
p.wait()
