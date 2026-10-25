import sys; sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts'); import idle
import subprocess, time, os

os.environ['PATH'] = r'C:\msys64\ucrt64\bin;' + os.environ.get('PATH', '')
HERE = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb7_record_hunt'
PIDS = os.path.join(HERE, 'pids.txt')
EXE = os.path.join(HERE, 'hunt_neighbors.exe')
OUT_TSV = os.path.join(HERE, 'neighbors_out.tsv')

p = subprocess.Popen([EXE, OUT_TSV], creationflags=getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0x40))
with open(PIDS, 'a', encoding='utf-8') as pf:
    pf.write(f"{p.pid}\t{time.strftime('%Y-%m-%d %H:%M:%S')}\thunt_neighbors.exe\n")
ret = p.wait()
print("hunt_neighbors exited with", ret)
