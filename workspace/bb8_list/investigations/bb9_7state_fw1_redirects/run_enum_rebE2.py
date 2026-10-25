import sys, os, subprocess
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

HERE = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_7state_fw1_redirects'
os.environ['PATH'] = r'C:\msys64\ucrt64\bin;C:\msys64\mingw64\bin;' + os.environ.get('PATH', '')

cpp = os.path.join(HERE, 'enum_rebE2_9.cpp')
exe = os.path.join(HERE, 'enum_rebE2_9.exe')
subprocess.check_call(['g++', '-O3', cpp, '-o', exe])
print("Compiled enum_rebE2_9.exe successfully.")

p = subprocess.Popen([exe], cwd=HERE, creationflags=0x40, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
with open(os.path.join(HERE, 'pids.txt'), 'a') as pf:
    pf.write(f"enum_rebE2_9 {p.pid}\n")
out, _ = p.communicate()
print(out)
