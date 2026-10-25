"""batch_kv.py GRADES STEPS LINES OUT: kview every out.tsv row with grade in GRADES (comma list), sequentially, idle."""
import idle, subprocess, sys, re
from pathlib import Path
H = Path(__file__).resolve().parent
grades, steps, lines, out = sys.argv[1].split(','), sys.argv[2], sys.argv[3], Path(sys.argv[4])
def tmpl(t):
    o, q, rest = t.split(',', 2)
    d = dict(x.split('=', 1) for x in rest.split(','))
    al, be = re.fullmatch(r'(\d+)d\+(-?\d+)', d['d']).groups(); alB, beB = re.fullmatch(r'(\d+)b\+(-?\d+)', d['b']).groups()
    return [o, q, d['P'], d['u'], d['s'], al, be, alB, beB, d['S']]
with open(out, 'a') as fo:
    for l in (H / 'out.tsv').read_text().splitlines()[1:]:
        f = l.split('\t')
        if len(f) < 5 or f[3] not in grades: continue
        args = [f[0]] + tmpl(f[4]) + [steps, lines]
        p = subprocess.Popen([str(H / 'kview.exe')] + args, creationflags=0x40, stdout=subprocess.PIPE, text=True)
        with open(H / 'pids.txt', 'a') as pf: pf.write(f'{p.pid} kview {f[0]}\n')
        o, _ = p.communicate()
        fo.write(f'=== {f[0]} {f[3]} {f[4]}\n    {f[6]}\n    {f[5][:200]}\n{o}\n'); fo.flush()
