# class sweep: start f3 and M8 from the f3 cascade-entry form (J5 form) with chosen L0', compare halts.
import subprocess, sys, os, re, time
from orbit import classify
HERE = os.path.dirname(os.path.abspath(__file__))
EXE = os.path.join(HERE, "wsim.exe")
F3 = "1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_1RG1LD_0RG0RF_0LI---_0RC1RF"
M8 = "1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_1RG1LD_0RG0RF_1RG---"
P = int(sys.argv[1]) if len(sys.argv) > 1 else 4400
PER = int(sys.argv[2]) if len(sys.argv) > 2 else 3
LMAX = int(sys.argv[3]) if len(sys.argv) > 3 else 40000
LMIN = int(sys.argv[4]) if len(sys.argv) > 4 else 1015
NPAR = int(sys.argv[5]) if len(sys.argv) > 5 else 2
STEP = int(sys.argv[6]) if len(sys.argv) > 6 else 30
picked = {}
for L0 in range(LMIN - (LMIN - 25) % 30, LMAX, STEP):
    key, rho, Pk, orb = classify((3 * L0 - 100) // 5, P)
    cl = (key, rho)
    if len(picked.setdefault(cl, [])) < PER: picked[cl].append(L0)
jobs = []
for cl in sorted(picked, key=str):
    for L0 in picked[cl]:
        k = (L0 - 25) // 5; A = (L0 + 26) // 3
        kt = f"0*2,{A},1*{P},0,2,z2,{k+7},1*{k-1};1;2;9"
        for name, M in (("f3", F3), ("m8", M8)):
            jobs.append((f"sweep/{name}_L{L0}_P{P}.txt", [EXE, M, "--kt", kt, "--Rdef", "366", "--cnt", "--d0", "--maxs", "3e11"], cl, L0))
print(len(jobs), "jobs;", {str(c): v for c, v in picked.items()}, flush=True)
running = []
with open(os.path.join(HERE, "pids.txt"), "a") as pf:
    while jobs or running:
        while jobs and len(running) < NPAR:
            out, cmd, cl, L0 = jobs.pop(0)
            if os.path.exists(os.path.join(HERE, out)) and "HALT" in open(os.path.join(HERE, out)).read(): continue
            f = open(os.path.join(HERE, out), "w")
            p = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT, cwd=HERE)
            pf.write(f"{p.pid} wsim.exe {out}\n"); pf.flush()
            running.append((p, f))
        time.sleep(1)
        for pr in running[:]:
            if pr[0].poll() is not None: pr[1].close(); running.remove(pr)
print("done", flush=True)
