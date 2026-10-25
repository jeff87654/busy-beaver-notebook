import idle
"""COQC wrapper for compile_clean.sh: runs coqc.exe at IDLE priority, records the PID (and CPU/wall time at exit) in
bb9_f3_coq/pids_pkg.txt.  Usage: python coqc_idle.py <coqc args...>"""
import subprocess, sys, time, os, ctypes
from ctypes import wintypes
COQC = os.path.join('C:' + os.sep, 'Coq-Platform~8.20~2025.01', 'bin', 'coqc.exe')
PIDS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'pids_pkg.txt')
args = sys.argv[1:]
t0 = time.time()
p = subprocess.Popen([COQC] + args, creationflags=subprocess.IDLE_PRIORITY_CLASS)
with open(PIDS, 'a') as f:
    f.write('%d coqc %s %s %s\n' % (p.pid, os.getcwd(), args[-1] if args else '', time.strftime('%Y-%m-%d %H:%M:%S')))
rc = p.wait()
cpu = -1.0
try:
    k = ctypes.windll.kernel32
    ft = [wintypes.FILETIME() for _ in range(4)]
    k.GetProcessTimes.argtypes = [wintypes.HANDLE] + [ctypes.POINTER(wintypes.FILETIME)] * 4
    if k.GetProcessTimes(wintypes.HANDLE(int(p._handle)), *[ctypes.byref(x) for x in ft]):
        tot = lambda x: (x.dwHighDateTime << 32 | x.dwLowDateTime) / 1e7
        cpu = tot(ft[2]) + tot(ft[3])
except Exception:
    pass
with open(PIDS, 'a') as f:
    f.write('%d exit %s cpu %.0fs wall %.0fs %s %s\n' % (p.pid, rc, cpu, time.time() - t0, args[-1] if args else '', time.strftime('%Y-%m-%d %H:%M:%S')))
sys.exit(rc)
