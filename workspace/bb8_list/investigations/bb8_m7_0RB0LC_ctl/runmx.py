"""runmx.py TAG 'config' [timeout]: run mxdys decider (verified build) on the target machine at Idle priority"""
import subprocess, sys, os, time
from pathlib import Path
EXE = Path(r'C:\Users\jeffr\Downloads\bb8\candidate_deciders_deep_verified.exe')
M = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RB0LC_1RG1LD_0RH0RF_---0RE'
tag, cfg = sys.argv[1], sys.argv[2]; to = float(sys.argv[3]) if len(sys.argv) > 3 else 300
d = Path(__file__).parent / 'mx' / tag; d.mkdir(parents=True, exist_ok=True)
(d / 'input.txt').write_text(f'{M} {cfg}\n')
env = dict(os.environ); env['PATH'] = r'C:\msys64\ucrt64\bin;' + env['PATH']
t = time.time()
try:
    r = subprocess.run([str(EXE), 'exec', 'input.txt'], cwd=d, env=env, capture_output=True, text=True, timeout=to, creationflags=subprocess.IDLE_PRIORITY_CLASS)
    log = (d / 'log.txt').read_text() if (d / 'log.txt').exists() else ''
    st = 'NONHALT' if f'{M} N' in log else ('HALT' if f'{M} H' in log else 'unresolved')
    print(tag, st, round(time.time()-t,1), (r.stderr or '')[-300:].replace('\n',' | '))
except subprocess.TimeoutExpired:
    print(tag, 'timeout', round(time.time()-t,1))
