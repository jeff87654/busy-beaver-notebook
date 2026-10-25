import idle
"""Run BB9/verify_c7/compile_clean.sh (whole build + probe) at IDLE priority with J=3 and the Idle COQC wrapper.
python launch.py [extra args for compile_clean.sh]"""
import subprocess, sys, os, time
D = r'C:\Users\jeffr\Downloads\bb9c7_wt\BB9\verify_c7'
env = dict(os.environ, BUSYCOQ='/c/Users/jeffr/Downloads/bb8/bb8_list/investigations/bb9_f3_coq/ext/busycoq/verify',
           COQC='/c/Users/jeffr/Downloads/bb8/bb8_list/investigations/bb9_c7_coq/pkg/coqc_idle', J='3')
BASH = r'C:\Program Files\Git\usr\bin\bash.exe'
if not os.path.exists(BASH): BASH = 'bash'
logname = sys.argv[1] if len(sys.argv) > 1 else 'compile_clean.log'
with open(os.path.join(D, logname), 'w', newline='\n') as lf:
    p = subprocess.Popen([BASH, './compile_clean.sh'] + sys.argv[2:], cwd=D, env=env, stdout=lf, stderr=subprocess.STDOUT)
    with open(r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_c7_coq\pids_pkg.txt', 'a') as f:
        f.write('%d bash compile_clean.sh (launch.py %d) %s\n' % (p.pid, os.getpid(), time.strftime('%Y-%m-%d %H:%M:%S')))
    rc = p.wait()
print('compile_clean.sh exit', rc)
sys.exit(rc)
