"""Wait until fewer than 3 of MY coqc processes are alive, then compile with cq.py.  python cqw.py FILE.v [TIMEOUT]"""
import subprocess, sys, time
from pathlib import Path
W = Path(__file__).resolve().parents[1]
def alive():
    pids = [int(l.split()[0]) for l in open(W / 'pids.txt') if ' coqc ' in l]
    tl = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq coqc.exe', '/FO', 'CSV', '/NH'], capture_output=True, text=True).stdout
    live = {int(x.split('","')[1]) for x in tl.strip().splitlines() if x.startswith('"coqc')}
    return len([p for p in pids if p in live])
while alive() >= 3: time.sleep(10)
sys.exit(subprocess.call([sys.executable, str(W / 'tools' / 'cq.py')] + sys.argv[1:]))
