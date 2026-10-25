import subprocess, sys
sys.path.insert(0, '.')
import build
r = subprocess.run([build.COQC, *build.FLAGS, sys.argv[1]], capture_output=True, text=True)
print(r.stdout[-6000:], r.stderr[-6000:])
