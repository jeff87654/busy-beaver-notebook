"""drive.py STAGE W: resumable reach7 driver (Idle, W workers, PIDs -> ../pids.txt).
  A: in/sNNN -> outA/sNNN.tsv   (1e6 macro, stop at 1e10 base steps)
  B: inB/sNNN -> outB/sNNN.tsv  (MAXMACRO from env RB_MACRO, default 2e7; stop at 1e10, or 1e11 for pf7 passers in inB11)
  C: children: kin/sNNN -> kout/sNNN.tsv (3e7 macro, stop at 1e11)
A file is done when it ends with '#summary'."""
import idle  # noqa
import os, sys, subprocess, time, glob
from concurrent.futures import ThreadPoolExecutor
H = os.path.dirname(os.path.abspath(__file__)); EXE = os.path.join(H, 'reach7.exe')
st, W = sys.argv[1], int(sys.argv[2])
cfg = {'A': ('in', 'outA', '1000000', '10'), 'B': ('inB', 'outB', os.environ.get('RB_MACRO', '10000000'), '11'),
       'B11': ('inB11', 'outB11', os.environ.get('RB_MACRO', '30000000'), '11'), 'B2': ('inB2', 'outB2', os.environ.get('RB_MACRO', '3000000'), '11'), 'C': ('kin', 'kout2', '30000000', '13')}[st]
os.makedirs(os.path.join(H, cfg[1]), exist_ok=True)
def done(p):
    if not os.path.exists(p): return False
    with open(p, 'rb') as f: f.seek(0, 2); n = f.tell(); f.seek(max(0, n - 200)); return b'#summary' in f.read()
def job(src):
    out = os.path.join(H, cfg[1], os.path.basename(src) + '.tsv')
    if done(out): return
    p = subprocess.Popen([EXE.replace('reach7.exe', 'reach7b.exe') if st == 'C' else EXE, src, out + '.tmp', cfg[2], cfg[3]])
    with open(os.path.join(H, '..', 'pids.txt'), 'a') as f: f.write(f'{time.strftime("%F %T")} cont/{st} reach7 child={p.pid} {os.path.basename(src)}\n')
    if p.wait() == 0 and done(out + '.tmp'): os.replace(out + '.tmp', out)
srcs = sorted(glob.glob(os.path.join(H, cfg[0], 's*')))
with ThreadPoolExecutor(W) as ex: list(ex.map(job, srcs))
print('stage', st, 'done', time.strftime('%F %T'))
