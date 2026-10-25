"""run1.py TAG [ONLY_T]: henum on one base at idle priority -> h_TAG[_T].tsv"""
import idle, sys, subprocess, os
from bcfg import *
tag = sys.argv[1]; M, tt, B0, fam = BASES[tag]
subprocess.run([sys.executable, 'mkstarts.py', tag], check=True, creationflags=0x40, stdout=subprocess.DEVNULL)
bb = '800000' if fam == 'F1' else '200000'
cmd = [os.path.abspath('henum.exe'), M] + targs(tag) + [f'starts_{tag}.txt', bb, '20000', str(B0)] + sys.argv[2:3]
out = f"h_{tag}{'_'+sys.argv[2] if len(sys.argv)>2 else ''}.tsv"
with open(out, 'w') as f:
    p = subprocess.Popen(cmd, stdout=f, creationflags=0x40)
    open('pids.txt', 'a').write(f"{p.pid} henum {tag} {' '.join(sys.argv[2:])}\n")
    p.wait()
