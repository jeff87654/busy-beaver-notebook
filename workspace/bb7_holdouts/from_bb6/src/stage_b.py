"""stage_b.py: for every (b) base in tops6.txt: generic worlds (genw.py, mod 4 and 6) + the rule worlds (w_champ, w_k3, w_k2),
enum7 extensions of its halt slot, ext.exe follow (2e6 steps). Outputs o_b<rank>.tsv. Idle priority."""
import sys, os, subprocess
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import idle
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); S = os.path.join(R, 'src')
os.chdir(R)
rule = {1: ['w_champ.txt'], 2: ['w_k2.txt'], 3: ['w_k3.txt']}
for l in open('tops6.txt'):
    f = l.split('\t'); base, rank = f[0], int(f[1])
    if rank == 1: continue   # champion done by q1 (rule worlds); its generic worlds below too
    rows = base.split('_'); slot = None
    for i, r in enumerate(rows):
        for c in range(2):
            if r[3*c+2] == 'Z': slot = chr(65 + i) + str(c)
    ws = []
    for m in ('4', '6'):
        fn = f'wg/w_gen_b{rank}_{m}.txt'
        if not os.path.exists(fn):
            os.makedirs('wg', exist_ok=True)
            print(subprocess.run([sys.executable, os.path.join(S, 'genw.py'), base, fn, m, '3000000'], capture_output=True, text=True).stdout.strip(), flush=True)
        ws.append(fn)
    ws += rule.get(rank, [])
    allw, seen = [], set()
    for fn in ws:
        for w in open(fn):
            k = tuple(w.split()[2:])
            if k not in seen: seen.add(k); allw.append(w.strip())
    wfile = f'wg/w_all_b{rank}.txt'; open(wfile, 'w').write('\n'.join(allw) + '\n')
    exts = subprocess.run([sys.executable, os.path.join(S, 'enum7.py'), base, slot], capture_output=True, text=True).stdout
    efile = f'wg/ext_b{rank}.txt'; open(efile, 'w').write(exts)
    inf = f'wg/in_b{rank}.txt'; subprocess.run([sys.executable, os.path.join(S, 'mkin.py'), efile, wfile, inf])
    out = f'o_b{rank}.tsv'
    if not os.path.exists(out):
        with open(inf) as fi, open(out + '.tmp', 'w') as fo:
            subprocess.run([os.path.join(S, 'ext.exe'), '2000000', slot], stdin=fi, stdout=fo)
        os.replace(out + '.tmp', out)
    os.remove(inf)
    print(f'b{rank} {base} slot {slot}: worlds {len(allw)}, ext {len(exts.split())}', flush=True)
