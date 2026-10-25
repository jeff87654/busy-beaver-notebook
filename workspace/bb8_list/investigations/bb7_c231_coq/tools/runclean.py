import sys, os, shutil, subprocess, time, glob
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb7_c231_coq')
import idle
W = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
d = os.path.join(W, sys.argv[1])
if os.path.exists(d): shutil.rmtree(d)
os.makedirs(d)
for f in glob.glob(os.path.join(W, 'v2', '*.v')) + [os.path.join(W, 'v2', 'compile_clean.sh'), os.path.join(W, 'v2', '_CoqProject')]:
    shutil.copy(f, d)
busy = os.path.join(W, '..', 'bb9_f3_coq', 'ext', 'busycoq', 'verify').replace(os.sep, '/')
env = dict(os.environ, BUSYCOQ=busy, COQC='C:/Coq-Platform~8.20~2025.01/bin/coqc.exe')
t0 = time.time()
with open(os.path.join(d, 'compile_clean.log'), 'w', newline='\n') as lf:
    p = subprocess.Popen([r'C:\Program Files\Git\bin\bash.exe', './compile_clean.sh'], cwd=d, env=env, stdout=lf,
                         stderr=subprocess.STDOUT, creationflags=subprocess.IDLE_PRIORITY_CLASS)
    open(os.path.join(W, 'pids.txt'), 'a').write('%d bash compile_clean.sh %s %s\n' % (p.pid, d, time.strftime('%Y-%m-%d %H:%M:%S')))
    rc = p.wait()
print('exit', rc, '%.0fs' % (time.time() - t0))
