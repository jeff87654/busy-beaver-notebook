"""summ.py: per-base outcome table from o_b*.tsv (+ champion o_champ_2e6.tsv) via cls.py logic."""
import subprocess, sys, os, collections
rows = []
bases = [('b1', 'o_champ_2e6.tsv', 'w_champ.txt')] + [(f'b{r}', f'o_b{r}.tsv', f'wg/w_all_b{r}.txt') for r in range(2, 21)]
print('base\tworlds\tmachines\tIMM\tSOON-only\tREHALT\tLOOP-any\tbest_halt_ratio\tREHALT machines')
for b, o, w in bases:
    if not os.path.exists(o): continue
    out = subprocess.run([sys.executable, 'src/cls.py', o, w], capture_output=True, text=True).stdout.splitlines()
    nw = sum(1 for _ in open(w))
    c = collections.Counter(); best = 0; reh = []
    for l in out:
        f = l.split('\t'); k = f[1]
        if 'REHALT' in k: c['REHALT'] += 1; reh.append(f[0] + '(' + f[3].split('=')[1] + ')')
        elif k.startswith('IMM') and 'LOOP' not in k and 'SOON' not in k: c['IMM'] += 1
        elif 'LOOP' in k: c['LOOP'] += 1
        else: c['SOON'] += 1
        best = max(best, float(f[3].split('=')[1]))
    print(f"{b}\t{nw}\t{len(out)}\t{c['IMM']}\t{c['SOON']}\t{c['REHALT']}\t{c['LOOP']}\t{best:.2f}\t{' '.join(reh)}")
