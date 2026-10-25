"""Windows helper for verify.sh: run a command (coqc / coqchk) at Idle priority with a memory cap.

    COQC_WRAPPER="python tools/winidle.py" ./verify.sh -j 4

The child's PID is appended to $WINIDLE_PIDS (default _verify/pids.txt) and only that PID is ever killed: when its
working set exceeds $WINIDLE_MAXGB GB (default 6).  stdout/stderr are inherited; the exit code is passed through.
Peak working set per process goes to $WINIDLE_PEAKS (default _verify/peaks.txt).
Not needed for the proof, only to share a machine politely."""
import os, subprocess, sys, threading, time

cmd = sys.argv[1:]
if not cmd:
    sys.exit('usage: winidle.py COMMAND ARGS...')
flags = subprocess.IDLE_PRIORITY_CLASS if os.name == 'nt' else 0
p = subprocess.Popen(cmd, creationflags=flags)
pidfile = os.environ.get('WINIDLE_PIDS', os.path.join('_verify', 'pids.txt'))
try:
    with open(pidfile, 'a') as f:
        f.write('%d %s %s\n' % (p.pid, time.strftime('%Y-%m-%d %H:%M:%S'), ' '.join(cmd)[-160:]))
except OSError:
    pass
maxkb = float(os.environ.get('WINIDLE_MAXGB', '6')) * 1024 * 1024
killed = []
peak = [0]


def watch():
    while p.poll() is None:
        try:
            o = subprocess.run(['tasklist', '/FI', 'PID eq %d' % p.pid, '/FO', 'CSV', '/NH'],
                               capture_output=True, text=True).stdout
            kb = int(o.strip().split('","')[-1].replace('"', '').replace(',', '').replace('.', '')
                     .replace(' K', '').strip() or 0)
            peak[0] = max(peak[0], kb)
            if kb > maxkb:
                killed.append(kb)
                p.kill()
                return
        except Exception:
            pass
        time.sleep(3)


if os.name == 'nt':
    threading.Thread(target=watch, daemon=True).start()
rc = p.wait()
peakfile = os.environ.get('WINIDLE_PEAKS', os.path.join('_verify', 'peaks.txt'))
try:
    with open(peakfile, 'a') as f:
        f.write('%d %d MB rc=%d %s\n' % (p.pid, peak[0] // 1024, rc, cmd[-1]))
except OSError:
    pass
if killed:
    sys.stderr.write('winidle: killed PID %d, working set %d KB over the cap\n' % (p.pid, killed[0]))
    rc = rc or 137
sys.exit(rc)
