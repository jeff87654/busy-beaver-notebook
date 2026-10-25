import subprocess, os

os.environ['PATH'] = r'C:\msys64\ucrt64\bin;C:\msys64\mingw64\bin;' + os.environ.get('PATH', '')

CREATE_NO_WINDOW = 0x08000000
IDLE_PRIORITY_CLASS = 0x40
FLAGS = CREATE_NO_WINDOW | IDLE_PRIORITY_CLASS

workdir = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_f89_and_cascade"
cpp_file = os.path.join(workdir, "partB_screen_x_parents.cpp")
exe_file = os.path.join(workdir, "partB_screen_x_parents.exe")
out_file = os.path.join(workdir, "partB_screen_x_parents.out.txt")

r_comp = subprocess.run(
    [r"C:\msys64\ucrt64\bin\g++.exe", "-O3", "-o", exe_file, cpp_file],
    cwd=workdir,
    creationflags=FLAGS,
    capture_output=True,
    text=True
)
if r_comp.returncode != 0:
    print("COMPILE ERROR:", r_comp.stderr)
    raise SystemExit(1)

print("Compiled partB_screen_x_parents.exe successfully. Running...")
with open(out_file, "w") as fout:
    r_run = subprocess.run(
        [exe_file],
        cwd=workdir,
        creationflags=FLAGS,
        stdout=fout,
        stderr=subprocess.PIPE,
        text=True
    )
print("Return code:", r_run.returncode)
with open(out_file, "r") as fin:
    lines = fin.readlines()
print(f"Total output lines: {len(lines)}")
for line in lines[:50]:
    print(line, end="")
if len(lines) > 50:
    print("...")
    for line in lines[-20:]:
        print(line, end="")
