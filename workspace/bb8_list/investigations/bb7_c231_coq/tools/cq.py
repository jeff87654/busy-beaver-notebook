import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb7_c231_coq')
import idle
"""Compile one .v in coq/ at Idle priority: python cq.py FILE.v [TIMEOUT_S]. busycoq bd2e36f = BusyCoq, coq/ = BB8.
Records the coqc PID in pids.txt; writes logs/<name>.log and logs/<name>.done."""
import subprocess, time, os
from pathlib import Path
W = Path(__file__).resolve().parents[1]
BUSY = W.parent / 'bb9_f3_coq' / 'ext' / 'busycoq' / 'verify'
COQC = r'C:\Coq-Platform~8.20~2025.01\bin\coqc.exe'
FLAGS = ['-Q', str(BUSY), 'BusyCoq', '-Q', str(W / 'coq'), 'BB8']
v = Path(sys.argv[1]).resolve()
log = W / 'logs' / (v.stem + '.log'); done = W / 'logs' / (v.stem + '.done')
if done.exists(): done.unlink()
t0 = time.time()
with open(log, 'w') as lf:
    p = subprocess.Popen([COQC] + FLAGS + [v.name], cwd=v.parent, stdout=lf, stderr=subprocess.STDOUT,
                         creationflags=subprocess.IDLE_PRIORITY_CLASS)
    with open(W / 'pids.txt', 'a') as f:
        f.write('%d coqc %s %s\n' % (p.pid, v, time.strftime('%Y-%m-%d %H:%M:%S')))
    import ctypes
    from ctypes import wintypes
    class PMC(ctypes.Structure):
        _fields_ = [('cb', wintypes.DWORD), ('PageFaultCount', wintypes.DWORD), ('PeakWorkingSetSize', ctypes.c_size_t),
                    ('WorkingSetSize', ctypes.c_size_t), ('QuotaPeakPagedPoolUsage', ctypes.c_size_t),
                    ('QuotaPagedPoolUsage', ctypes.c_size_t), ('QuotaPeakNonPagedPoolUsage', ctypes.c_size_t),
                    ('QuotaNonPagedPoolUsage', ctypes.c_size_t), ('PagefileUsage', ctypes.c_size_t),
                    ('PeakPagefileUsage', ctypes.c_size_t)]
    k32 = ctypes.windll.kernel32; psapi = ctypes.windll.psapi
    k32.OpenProcess.restype = wintypes.HANDLE
    psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(PMC), wintypes.DWORD]
    hproc = k32.OpenProcess(0x1000 | 0x0010, False, p.pid)
    def rss_mb():
        c = PMC(); c.cb = ctypes.sizeof(PMC)
        if not psapi.GetProcessMemoryInfo(hproc, ctypes.byref(c), c.cb): return 0
        return c.PagefileUsage // 2**20
    lim = int(os.environ.get('MEMLIM_MB', '3000'))
    tmax = int(sys.argv[2]) if len(sys.argv) > 2 else 3600
    rc = None
    while rc is None:
        try:
            rc = p.wait(timeout=2)
        except subprocess.TimeoutExpired:
            mb = rss_mb()
            if mb > lim:
                p.kill(); p.wait(); rc = 'MEMKILL %dMB' % mb
            elif time.time() - t0 > tmax:
                p.kill(); p.wait(); rc = 'TIMEOUT'
done.write_text('exit %s %.1fs\n' % (rc, time.time() - t0))
print(v.stem, 'exit', rc, '%.1fs' % (time.time() - t0))
print(open(log).read()[-3000:])
