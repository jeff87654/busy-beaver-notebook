"""Level-end outcomes via macro.js (literal simulation)."""
import json, subprocess, sys
def word(p, kind, a, n):
    return p + '010' * a + ('01110111' if kind == 'P' else '0') + '1' * n + '01010'
def run(w, maxsteps=10**9):
    r = subprocess.run(['node', 'macro.js', 'W', w, str(maxsteps)], capture_output=True, text=True)
    return json.loads(r.stdout)
if __name__ == '__main__':
    ns = [int(x) for x in sys.argv[1].split(',')]
    for p in ('1', '11'):
        for kind, amax in (('P', 5), ('Q', 6)):
            for a in range(amax):
                for n in ns:
                    r = run(word(p, kind, a, n))
                    print(p, kind, a, n, r['result'], r['via'][:8], flush=True)
