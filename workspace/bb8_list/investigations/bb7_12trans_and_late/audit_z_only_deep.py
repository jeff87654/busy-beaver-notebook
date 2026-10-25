import os
import sys
os.environ['PATH'] = r'C:\msys64\ucrt64\bin;' + os.environ.get('PATH', '')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7')
import idle
import fit7

print("Files in rank/:", os.listdir(r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\rank'))
print("Files in reb7/counters/:", os.listdir(r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\counters'))
print("Files in reb7/counters/pf/:", os.listdir(r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\counters\pf'))

def replace_P(tmpl_str, new_P):
    parts = tmpl_str.split(',')
    out = []
    for p in parts:
        if p.startswith('P='):
            out.append('P=' + (new_P if new_P else '-'))
        else:
            out.append(p)
    return ','.join(out)

# Read sweep12_analyzed.txt and find all z_only=True classes
with open('sweep12_analyzed.txt', encoding='utf-8') as f:
    text = f.read()

blocks = [b.strip() for b in text.split('\n\n') if b.strip().startswith('CLASS')]
z_blocks = [b for b in blocks if '(z_only=True)' in b]
print(f"\nTotal z_only=True classes in sweep12_analyzed.txt: {len(z_blocks)}")

with open('sweep12_survivors.tsv', encoding='utf-8') as f:
    hdr = f.readline().rstrip('\n').split('\t')
    rows = [dict(zip(hdr, line.rstrip('\n').split('\t'))) for line in f if line.strip()]
by_m = {r['machine']: r for r in rows}

for b in z_blocks:
    lines = b.splitlines()
    rep = lines[0].split('rep=')[1].split()[0]
    r = by_m[rep]
    verdict_line = [l for l in lines if l.strip().startswith('reb7   :')][0]
    verdict = verdict_line.split('verdict=')[1].split()[0]
    print(f"\n{lines[0]}")
    print(f"  {lines[1].strip()}")
    print(f"  {lines[2].strip()}")
    print(f"  verdict={verdict}")
    if verdict in ('NOFIT', 'NO-K'):
        # Trace with rk7.exe on both original template and P=- and P=obs_O.lstrip('0')
        tmpl = r['template']
        obs_O = r['obs_O'].lstrip('0') if r['obs_O'] != '-' else ''
        for tag, t in [('orig_tmpl', tmpl), ('P_empty', replace_P(tmpl, '')), ('P_obs', replace_P(tmpl, obs_O))]:
            P = fit7.Prober(rep, t)
            ks, end = P.trace(5000000, 100)
            if ks or (end and end[0] == 'HALT'):
                print(f"    [{tag}: {t}] nK={len(ks)} end={end}")
                if ks:
                    print(f"      first_K: step={ks[0][0]} len={len(ks[0][1])} ds={ks[0][1][:15]} a={ks[0][2]} b={ks[0][3]}")
                    print(f"      last_K : step={ks[-1][0]} len={len(ks[-1][1])} ds={ks[-1][1][:15]} a={ks[-1][2]} b={ks[-1][3]}")
                # Also probe E0 (ds=[], a=0, b=16..23) and E1 (ds=[0], a=0, b=16..23) using rk7.exe!
                e0 = P.probe([([], 0, b_val) for b_val in range(16, 24)], N=1000000)
                e1 = P.probe([([0], 0, b_val) for b_val in range(16, 24)], N=1000000)
                e0_str = ''.join(x[0] for x in e0)
                e1_str = ''.join(x[0] for x in e1)
                print(f"      rk7 E0={e0_str} E1={e1_str}")
                break
        else:
            print(f"    [rk7 found nK=0 on all template variants!]")
