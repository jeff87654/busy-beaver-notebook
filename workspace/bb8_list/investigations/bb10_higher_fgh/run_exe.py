import subprocess, sys, os

FLAGS = 0x08000000 | 0x40
for p_dir in [r"C:\msys64\ucrt64\bin", r"C:\msys64\mingw64\bin", r"C:\ProgramData\mingw64\mingw64\bin"]:
    if os.path.exists(p_dir):
        os.environ["PATH"] = p_dir + os.pathsep + os.environ.get("PATH", "")
GPP = r"C:\msys64\ucrt64\bin\g++.exe"
if not os.path.exists(GPP):
    GPP = "g++"

cmd = sys.argv[1]
if cmd == "compile":
    src, out = sys.argv[2], sys.argv[3]
    p = subprocess.run([GPP, "-O2", "-std=c++17", "-static", "-o", out, src],
                       capture_output=True, text=True, creationflags=FLAGS)
    print("compile rc=", p.returncode)
    if p.stdout: print(p.stdout)
    if p.stderr: print(p.stderr)
    sys.exit(p.returncode)
elif cmd == "run":
    exe = sys.argv[2]
    args = sys.argv[3:]
    out_file = None
    if len(args) >= 2 and args[0] == "--out":
        out_file = args[1]
        args = args[2:]
    if out_file:
        with open(out_file, "w", encoding="utf-8") as f:
            p = subprocess.run([exe] + args, stdout=f, stderr=subprocess.STDOUT, text=True, creationflags=FLAGS)
        sys.exit(p.returncode)
    else:
        p = subprocess.run([exe] + args, capture_output=True, text=True, creationflags=FLAGS)
        print(p.stdout, end="")
        if p.stderr: print(p.stderr, file=sys.stderr, end="")
        sys.exit(p.returncode)
