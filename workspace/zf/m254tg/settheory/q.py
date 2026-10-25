"""q.py 'Coq commands' : run a query file (Requires + commands) against this dev at Idle priority."""
import sys, subprocess, tempfile, os, ctypes
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)
sys.argv_saved = sys.argv; sys.argv = ['build.py']
import importlib.util
spec = importlib.util.spec_from_file_location('b', os.path.join(os.path.dirname(__file__), 'build.py'))
b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
src = open(sys.argv_saved[1], encoding='utf-8').read() if os.path.exists(sys.argv_saved[1]) else sys.argv_saved[1]
d = tempfile.mkdtemp()
f = os.path.join(d, 'Q.v'); open(f, 'w', encoding='utf-8').write(src)
r = subprocess.run([b.COQC, *b.FLAGS, f], cwd=d, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(r.stdout + r.stderr)
