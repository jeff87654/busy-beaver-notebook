import os, subprocess

os.environ["PATH"] = r"C:\msys64\ucrt64\bin;C:\msys64\mingw64\bin;" + os.environ.get("PATH", "")
WORKDIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_f89_and_cascade"
SRC = os.path.join(WORKDIR, "partA_f89_tnf_search.cpp")
EXE = os.path.join(WORKDIR, "partA_f89_tnf_search.exe")
OUT = os.path.join(WORKDIR, "partA_f89_tnf_search.out.txt")
FLAGS = 0x08000000 | 0x40

res = subprocess.run([r"C:\msys64\ucrt64\bin\g++.exe", "-O3", "-std=c++17", SRC, "-o", EXE],
                     cwd=WORKDIR, capture_output=True, text=True, creationflags=FLAGS)
if res.returncode != 0:
    print("Compile failed:", res.stderr)
    raise SystemExit(1)

print("Compiled partA_f89_tnf_search.exe successfully. Running...")
with open(OUT, "w") as f:
    p = subprocess.run([EXE], cwd=WORKDIR, stdout=f, stderr=subprocess.PIPE, text=True, creationflags=FLAGS)

print("Return code:", p.returncode)
if p.stderr:
    print("Stderr:", p.stderr)

with open(OUT, "r") as f:
    lines = [l.strip() for l in f if l.strip()]

print(f"Total output lines: {len(lines)}")
summaries = [l for l in lines if l.startswith("=== SUMMARY")]
for s in summaries:
    print(s)
halters = [l for l in lines if l.startswith("[HALT")]
print(f"\nTotal R >= 2 halters logged: {len(halters)}")
for h in halters[:35]:
    print(h)
