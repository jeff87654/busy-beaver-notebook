import os, sys, subprocess, time

FW1_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect"
AUDIT_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect\small_nd_audit"
os.environ["PATH"] = r"C:\msys64\ucrt64\bin;" + os.environ["PATH"]
sys.path.insert(0, FW1_DIR)
sys.path.insert(0, r"C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits")
import idle
from bcfg import BASES, targs

cpp_file = os.path.join(AUDIT_DIR, "kblank_detail.cpp")
exe_file = os.path.join(AUDIT_DIR, "kblank_detail.exe")
subprocess.run(["g++", "-O3", "-static", "-o", exe_file, cpp_file], check=True, creationflags=0x40)
print("Compiled kblank_detail.exe successfully.")

tags_todo = sorted(BASES.keys())
running = []
while tags_todo or running:
    running = [(tag, p, fo) for (tag, p, fo) in running if p.poll() is None]
    while tags_todo and len(running) < 2:
        tag = tags_todo.pop(0)
        mf = os.path.join(AUDIT_DIR, f"mlist_919_{tag}.txt")
        if not os.path.exists(mf) or os.path.getsize(mf) == 0:
            continue
        B0 = BASES[tag][2]
        of = os.path.join(AUDIT_DIR, f"bdet_919_{tag}.tsv")
        fo = open(of, "w")
        cmd = [exe_file, mf] + targs(tag) + ["1000000", str(B0)]
        p = subprocess.Popen(cmd, stdout=fo, creationflags=0x40)
        running.append((tag, p, fo))
        print(f"Started kblank_detail for tag {tag}...")
    time.sleep(0.3)

# Merge into blank_detail_919.tsv
out_lines = []
for tag in sorted(BASES.keys()):
    of = os.path.join(AUDIT_DIR, f"bdet_919_{tag}.tsv")
    if os.path.exists(of):
        for l in open(of):
            out_lines.append(tag + "\t" + l)

with open(os.path.join(AUDIT_DIR, "blank_detail_919.tsv"), "w") as f:
    f.writelines(out_lines)

print(f"Wrote {len(out_lines)} rows to blank_detail_919.tsv!")
