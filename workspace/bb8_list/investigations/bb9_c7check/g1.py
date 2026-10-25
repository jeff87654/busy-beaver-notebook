# g1.py: run c7sim from constructed Kt starts until the first CL (or halt); print the J1 line compactly.
import idle, subprocess, sys, re
EXE = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_c7check\c7sim.exe'
C7 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_1RG1LD_0RG0RF_0LI---_1LC0RA'
def run(kt, machine=C7, stopj=1, maxs='2e10', extra=()):
    p = subprocess.run([EXE, machine, '--kt', kt, '--Rdef', '366', '--stopj', str(stopj), '--maxs', maxs, '--view', '600'] + list(extra),
                       capture_output=True, text=True, creationflags=0x40)
    out = []
    for l in p.stdout.splitlines():
        if l.startswith('J') or l.startswith('HALT') or l.startswith('MAXS'):
            m = re.search(r't=(\d+).*H0one=(\d+) H0zero=(\d+) \| (.*)', l)
            if l.startswith('J') and m: out.append(f't={m.group(1)} h1={m.group(2)} h0={m.group(3)} | {m.group(4)}')
            else: out.append(l[:300])
    return out
if __name__ == '__main__':
    for kt in sys.argv[1:]:
        print(kt, '=>', ' ;; '.join(run(kt)), flush=True)
