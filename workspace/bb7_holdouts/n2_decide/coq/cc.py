import idle, subprocess, sys, time
from pathlib import Path
BUSY = r'C:\Users\jeffr\Downloads\bb8\third_party\busycoq\verify'
PROOFS = r'C:\Users\jeffr\Downloads\bb8\bb8_list\proofs'
COQC = r'C:\Coq-Platform~8.20~2025.01\bin\coqc.exe'
f = sys.argv[1]
t = time.time()
p = subprocess.Popen([COQC, '-Q', BUSY, 'BusyCoq', '-Q', PROOFS, 'BB8', '-Q', '.', 'N2', f], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, creationflags=0x40)
open(r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\n2_decide\pids.txt', 'a').write('%d coqc %s\n' % (p.pid, f))
out, _ = p.communicate()
print(out[-6000:])
print('rc', p.returncode, 'time %.1fs' % (time.time() - t))
