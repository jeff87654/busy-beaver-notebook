"""Level-end outcome table via macro.js (literal simulation, no acceleration).
For each prefix p, kind P (a=0..4) / Q (a=0..5) and n = 1 mod 3, run from
  0^inf p (010)^a (0111 0111 | 0) 1^n 01010 B>0 0^inf
until HALT or the first level start L(p', A') = p' (010)^A' 0 111 01010 B>0 with A' >= AMIN."""
import json, subprocess, sys
PREF = {'p1': '1', 'p2': '11', 'p3': '111101001'}
def word(p, kind, a, n):
    return p + '010' * a + ('01110111' if kind == 'P' else '0') + '1' * n + '01010'
def run(w, maxsteps=2 * 10**9):
    r = subprocess.run(['node', 'macro.js', 'W', w, str(maxsteps)], capture_output=True, text=True)
    return json.loads(r.stdout)
if __name__ == '__main__':
    ns = [int(x) for x in sys.argv[1].split(',')]
    prefs = sys.argv[2].split(',') if len(sys.argv) > 2 else ['p1', 'p2', 'p3']
    for pn in prefs:
        p = PREF[pn]
        for kind, amax in (('P', 5), ('Q', 6)):
            for a in range(amax):
                for n in ns:
                    r = run(word(p, kind, a, n))
                    print(pn, kind, a, n, json.dumps(r['result']), json.dumps(r['via'][:8]), flush=True)
