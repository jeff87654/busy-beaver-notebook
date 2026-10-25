import os, re, subprocess
from collections import Counter, defaultdict

os.environ["PATH"] = r"C:\msys64\ucrt64\bin;C:\msys64\mingw64\bin;" + os.environ.get("PATH", "")
WORKDIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_f89_and_cascade"
C231F_SRC = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_twoslot_x\src\c231f.cpp"
C231F_EXE = os.path.join(WORKDIR, "c231f.exe")
OUT_TXT = os.path.join(WORKDIR, "partB_screen_x_parents.out.txt")
FLAGS = 0x08000000 | 0x40

# Compile c231f.exe
res = subprocess.run([r"C:\msys64\ucrt64\bin\g++.exe", "-O3", C231F_SRC, "-o", C231F_EXE],
                     cwd=WORKDIR, capture_output=True, text=True, creationflags=FLAGS)
if res.returncode != 0:
    print("Compile failed:", res.stderr)
    raise SystemExit(1)
print("Compiled c231f.exe successfully.")

with open(OUT_TXT, "r") as f:
    lines = [line.strip() for line in f if line.startswith("[MIXED")]

# Group by (cat, cdesc, k1, res_str) so we test every distinct (profile, k1) pair with c231f.exe
groups = defaultdict(list)
for line in lines:
    m = re.match(r"\[MIXED (\S+) (\S+) (\S+) k1=(\d+)\] (\S+) \| (.*)", line)
    if not m:
        m = re.match(r"\[MIXED (\S+) (\S+) k1=(\d+)\] (\S+) \| (.*)", line)
        cat, pname, k1, tm, res_str = m.group(1), m.group(2), int(m.group(3)), m.group(4), m.group(5)
        cdesc = "NONE"
    else:
        cat, pname, cdesc, k1, tm, res_str = m.group(1), m.group(2), m.group(3), int(m.group(4)), m.group(5), m.group(6)
    groups[(cat, cdesc, k1, res_str)].append((pname, tm))

print(f"Total MIXED machines: {len(lines)} across {len(groups)} distinct (cat, cdesc, k1, res_str) groups.")

# Run c231f.exe on a representative of each group (with --maxt 20000000 --jumps 80)
summary_counts = Counter()
multi_round_halters = []

for (cat, cdesc, k1, res_str), items in sorted(groups.items()):
    pname, tm = items[0]
    p = subprocess.run([C231F_EXE, tm, "--maxt", "5000000", "--excap", "100", "--fixed", "--jumps", "300"],
                       cwd=WORKDIR, capture_output=True, text=True, creationflags=FLAGS)
    out_lines = [l.strip() for l in p.stdout.splitlines() if l.strip()]
    status_line = out_lines[-2] if len(out_lines) >= 2 else (out_lines[-1] if out_lines else "EMPTY")
    zeros_line = out_lines[-1] if out_lines and out_lines[-1].startswith("zeros:") else "zeros:"
    zs = [int(x) for x in zeros_line.replace("zeros:", "").split()]
    # Count how many rounds (each round starts at a local maximum of z in zs, or count transitions where z increases!)
    rounds = []
    if zs:
        cur_start = zs[0]
        for i in range(1, len(zs)):
            if zs[i] > zs[i-1]:
                rounds.append(cur_start)
                cur_start = zs[i]
        rounds.append(cur_start)
    n_rounds = len(rounds)
    if status_line.startswith("HALT"):
        key = f"HALT_R{n_rounds}"
        if n_rounds >= 2:
            multi_round_halters.append((n_rounds, len(items), cat, cdesc, k1, pname, tm, rounds, status_line, res_str))
    elif status_line.startswith("END"):
        key = f"END_JUMPS_R{n_rounds}"
    else:
        key = f"STOP_R{n_rounds}"
    summary_counts[key] += len(items)

print("\n=== c231f MULTI-ROUND SUMMARY ACROSS ALL 743 MIXED MACHINES ===")
for k, v in sorted(summary_counts.items()):
    print(f"  {k:20s}: {v}")

multi_round_halters.sort(key=lambda x: (-x[0], -x[1]))
print(f"\n=== MULTI-ROUND HALTERS (R >= 2): {len(multi_round_halters)} groups ({sum(x[1] for x in multi_round_halters)} machines) ===")
for n_rounds, cnt, cat, cdesc, k1, pname, tm, rounds, status_line, res_str in multi_round_halters:
    print(f"  [E_{n_rounds} | cnt={cnt:3d} | {cat} {cdesc:10s} | k1={k1} | {pname:15s}] {tm}")
    print(f"      rounds k_r = {rounds} | {status_line}")
    print(f"      table: {res_str}")
