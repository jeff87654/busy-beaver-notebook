"""run9.py TAG SLOT MAXDEF BLANKBUD: 9-state henum9 on one root slot -> h9_TAG_SLOT.tsv"""
import idle, sys, subprocess, os, time
from bcfg import *
tag, slot, md, bb = sys.argv[1:5]; M, tt, B0, fam = BASES[tag]
cmd = [os.path.abspath('henum9.exe'), M] + targs(tag) + [f'starts_{tag}.txt', bb, '20000', str(B0), slot, md]
with open(f'h9_{tag}_{slot}.tsv', 'w') as f:
    p = subprocess.Popen(cmd, stdout=f, creationflags=0x40); open('pids.txt', 'a').write(f"{p.pid} henum9 {tag} {slot}\n"); p.wait()
open('notes.txt', 'a').write(time.strftime('%H:%M') + f' henum9 {tag} {slot} maxdef {md} done\n')
