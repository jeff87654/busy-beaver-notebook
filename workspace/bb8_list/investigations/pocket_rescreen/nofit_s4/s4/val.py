import sys, subprocess, re
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\pocket_rescreen')
import idle
V = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\pocket_rescreen\nofit_s4\s4\v4.exe'
def run(machine, Q, side, cases, shape_rx, maxsteps=10**9):
    """cases: list of (s0, left, right, expected_word or None, tag). returns (#ok, #bad, outputs)"""
    inp = ''.join(f"{s0} {l or '-'} {r or '-'} {shape_rx}\n" for s0,l,r,e,tag in cases)
    out = subprocess.run([V, machine, Q, side, str(maxsteps)], input=inp, capture_output=True, text=True).stdout.split('\n')
    ok = bad = 0; res = []
    for (s0,l,r,e,tag), o in zip(cases, out):
        parts = o.split()
        w = parts[3] if parts and parts[0]=='M' else o
        good = (e is None) or (w == e)
        ok += good; bad += (not good); res.append((tag, good, o[:120] if not good else parts[1]))
    return ok, bad, res
