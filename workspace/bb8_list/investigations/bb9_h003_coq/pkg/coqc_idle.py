import idle
"""COQC wrapper for BB9/verify_h003/compile_clean.sh: runs coqc.exe at IDLE priority, records its PID (and CPU/wall
time and peak working set at exit) in bb9_h003_coq/pids_pkg.txt, and kills THIS coqc (its own PID only) if its
working set exceeds MEMKB (default 6,000,000 K).  Usage: python coqc_idle.py <coqc args...>"""
import subprocess, sys, time, os, ctypes
from ctypes import wintypes
COQC = os.path.join('C:' + os.sep, 'Coq-Platform~8.20~2025.01', 'bin', 'coqc.exe')
W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIDS = os.path.join(W, 'pids_pkg.txt')
LIM = int(os.environ.get('MEMKB', '6000000'))
args = sys.argv[1:]
name = args[-1] if args else ''
t0 = time.time()
p = subprocess.Popen([COQC] + args, creationflags=subprocess.IDLE_PRIORITY_CLASS)
with open(PIDS, 'a') as f:
    f.write('%d coqc %s %s %s\n' % (p.pid, os.getcwd(), name, time.strftime('%Y-%m-%d %H:%M:%S')))


class PMC(ctypes.Structure):
    _fields_ = [('cb', wintypes.DWORD), ('PageFaultCount', wintypes.DWORD), ('PeakWorkingSetSize', ctypes.c_size_t),
                ('WorkingSetSize', ctypes.c_size_t), ('QuotaPeakPagedPoolUsage', ctypes.c_size_t),
                ('QuotaPagedPoolUsage', ctypes.c_size_t), ('QuotaPeakNonPagedPoolUsage', ctypes.c_size_t),
                ('QuotaNonPagedPoolUsage', ctypes.c_size_t), ('PagefileUsage', ctypes.c_size_t),
                ('PeakPagefileUsage', ctypes.c_size_t)]


psapi = ctypes.WinDLL('psapi')
psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(PMC), wintypes.DWORD]


def mem():
    m = PMC(); m.cb = ctypes.sizeof(PMC)
    if psapi.GetProcessMemoryInfo(wintypes.HANDLE(int(p._handle)), ctypes.byref(m), m.cb):
        return m.WorkingSetSize // 1024, m.PeakWorkingSetSize // 1024
    return 0, 0


rc = None
while rc is None:
    try:
        rc = p.wait(timeout=5)
    except subprocess.TimeoutExpired:
        ws, _ = mem()
        if ws > LIM:
            p.kill(); p.wait(); rc = 'MEMKILL'
            with open(os.path.join(W, 'notes_pkg.txt'), 'a') as f:
                f.write('%s coqc_idle.py memory guard killed my own coqc %d (%s, %d K)\n' % (time.strftime('%Y-%m-%d %H:%M:%S'), p.pid, name, ws))
cpu = -1.0
peak = mem()[1]
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
    f.write('%d exit %s cpu %.0fs wall %.0fs peak %dK %s %s\n' % (p.pid, rc, cpu, time.time() - t0, peak, name, time.strftime('%Y-%m-%d %H:%M:%S')))
sys.exit(rc if isinstance(rc, int) else 1)
