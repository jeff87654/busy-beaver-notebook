"""Scan the C7 cascade from Kx(1^n;1;3R+2;4;blank): L sequence and fate.  python r2scan.py n0 n1 > out"""
import idle, subprocess, sys, re
C7 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_1RG1LD_0RG0RF_0LI---_1LC0RA'
EXE = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_c7_coq\tools\c7m.exe'
for n in range(int(sys.argv[1]), int(sys.argv[2])):
    out = subprocess.run([EXE, C7, '|1*%d|1|50|4' % n, '2e8', 'noh', 'far=100'], capture_output=True, text=True,
                         creationflags=0x40).stdout
    Ls = [int(m.group(1)) for m in re.finditer(r'^D0 .*? L=(\d+)', out, re.M)]
    fate = 'HALT' if 'HALT' in out else 'MAX'
    print(n, fate, Ls, flush=True)
