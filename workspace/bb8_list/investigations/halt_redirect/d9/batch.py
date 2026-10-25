"""Run d9run.follow on every machine of a list from the halting tape, in parallel threads (stage servers at IDLE)."""
import sys, os, io, threading, queue, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib
args = sys.argv[1:]
ml = [l.split()[0] for l in open(args[0]) if l.strip()]
A, r = map(int, args[1].split(':')); stages = int(args[2]); maxs = int(args[3]); policy = args[4]; bigk = int(args[5]); out = args[6]
nth = 1
from mkhalt import halt_word
os.environ['GHM'] = ml[0]
import d9run
w, h = halt_word(A, r)
q = queue.Queue()
for m in ml: q.put(m)
lock = threading.Lock(); fo = open(out, 'w')
def worker():
    while True:
        try: m = q.get_nowait()
        except queue.Empty: return
        lines = []
        d9run.M = m      # module global used by follow()
        try:
            res = d9run.follow(0, policy, stages, maxs, bigk, 1000, 3, lines.append, None, (w, h, 'I'))
        except Exception as ex:
            res = f'EXC {ex!r}'
        with lock:
            fo.write(f'### {m} RESULT {res} stages={len(lines)}\n' + '\n'.join(lines) + '\n'); fo.flush()
# d9run.M is a module global: threads would race.  Run sequentially instead (simple, correct).
for m in ml:
    lines = []
    d9run.M = m
    try:
        res = d9run.follow(0, policy, stages, maxs, bigk, 1000, 3, lines.append, None, (w, h, 'I'))
    except Exception as ex:
        res = f'EXC {ex!r}'
    fo.write(f'### {m} RESULT {res} n={len(lines)}\n' + '\n'.join(lines) + '\n'); fo.flush()
