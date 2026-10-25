"""kv2.py MACHINE 'ds;a;b' STEPS MAXL [TMPL]: free-prefix K trace (kview2, idle) from a template word."""
import idle, sys, subprocess
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import kl
M = sys.argv[1]; d, a, b = sys.argv[2].split(';'); ds = [int(x) for x in d.split(',') if x]
T = kl.tmpl(M, sys.argv[5] if len(sys.argv) > 5 else None); ar = kl.args(T); ar[2] = '*'
w = kl.word(T, ds, int(a), int(b)) if not d.startswith('P') else None
p = subprocess.Popen([str(kl.H / 'kview2.exe'), M] + ar + [sys.argv[3], sys.argv[4], '0', w, str(len(w)), T['q'], '0'],
                     stdout=subprocess.PIPE, text=True, creationflags=0x40)
o, _ = p.communicate()
print('\n'.join(l[:180] for l in o.splitlines() if ' ? ' not in l))
