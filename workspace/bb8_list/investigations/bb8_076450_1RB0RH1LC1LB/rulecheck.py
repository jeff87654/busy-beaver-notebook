"""Literal checks of the counter rules (context rules only; not needed for the nonhalting proof).
Runs famstep.js (literal simulation to the next family configuration) and compares with the predicted configuration."""
import subprocess, sys
cases = []
for n in range(1, 61):
    for k in range(1, 4):
        cases.append((f"z3 [{n};{k}][7;3][2;0]", f"z3 [{n+9};{k-1}][7;3][2;0]", "R1"))
for n in range(3, 61):
    for m in range(1, 13):
        for j in range(1, 4):
            ctx = f"[{m};{j}][5;3][2;0]"; nxt = f"[{m+4};{j-1}][5;3][2;0]"
            if n % 3 == 1 and n >= 7: exp = f"z3 [19;{(n-7)//3}]" + nxt
            elif n % 3 == 0: exp = f"z3 [2;0][1;{n//3}]" + nxt
            elif n % 3 == 2: exp = f"z4 [1;1][3;{(n-2)//3}]" + nxt
            else: continue
            cases.append((f"z3 [{n};0]" + ctx, exp, "R2"))
for n in range(2, 91):
    if n % 3 == 0: exp = f"z3 [19;{(n-3)//3}][2;0]"
    elif n % 3 == 2: exp = f"z3 [2;0][1;{(n+4)//3}][2;0]"
    else: exp = f"z4 [1;1][3;{(n+2)//3}][2;0]"
    cases.append((f"z3 [{n};0][2;0]", exp, "T"))
inp = "\n".join(c[0] for c in cases) + "\n"
import os
env = dict(os.environ, EVENTS="1", MAXSTEPS="5000000")
r = subprocess.run(["node", "famstep.js"], input=inp, capture_output=True, text=True, env=env, shell=(os.name == "nt"))
out = [x for x in r.stdout.splitlines() if x.strip()]
if len(out) != len(cases): print("node output problem", len(out), r.stderr[:500]); sys.exit(1)
bad = 0; stats = {}
for (c, exp, tag), line in zip(cases, out):
    got = line.split("  ->  ")[1].split(" @")[0]
    ok = got == exp
    stats.setdefault(tag, [0, 0])[0 if ok else 1] += 1
    if not ok:
        bad += 1
        if bad < 10: print("MISMATCH", tag, c, "expected", exp, "got", got)
print("cases", len(cases), "mismatches", bad, stats)
