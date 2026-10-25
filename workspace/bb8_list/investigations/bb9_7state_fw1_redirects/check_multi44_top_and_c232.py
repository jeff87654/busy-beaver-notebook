import sys, os, subprocess, glob
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import idle
import kl
from egrid import short

os.environ['PATH'] = r'C:\msys64\ucrt64\bin;C:\msys64\mingw64\bin;' + os.environ.get('PATH', '')
OUT_DIR = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_7state_fw1_redirects'

# Check multi_E_1 and multi_E_2 from [1, 0; a] and [0, d; a]
for name, tm in [
    ("multi_E_1", "1RB1LD_1RC1RD_1LB0RG_0RC1RE_0LA0LF_0RA1LE_0LA---"),
    ("multi_E_2", "1RB1LD_1RC1RD_1LB1RG_0RC1RE_0LA0LF_0RA1LE_1RC---"),
]:
    T = kl.tmpl(tm, "L,E,P=1,u=01,s=0,d=1d+0,b=1b+0,S=-")
    for ds, a in [([1, 0], 4), ([0, 2], 4), ([0, 0], 4), ([0], 4), ([], 4)]:
        evs = kl.run(tm, ds, a, 1, steps=50000, nchg=0, maxl=15, T=T, pall=1)
        nxt = next((e for e in evs[1:] if e[0] == 'H' or (e[0] == 'K' and e[4] == 1 and e[2] != ds)), evs[-1] if evs else None)
        print(f"{name} K({short(ds)};{a}) -> {f'K({short(nxt[2])};{nxt[3]};{nxt[4]})@{nxt[1]}' if nxt and nxt[0]=='K' else nxt}")

# Also check w1_G_1 and w1_E_1 on [0, 0; 4] with B=0 and B=1 and pall=1
for name, tm, t_str in [
    ("w1_G_1", "1RB1LD_0RC1LB_0LD0RE_1LA0LF_0RG1RC_1LG---_0LA0LB", "R,G,P=100,u=10,s=0,d=1d+0,b=1b+0,S=0"),
    ("w1_E_1", "1RB1LD_0RC1LB_0LD0RE_1LA1LF_1RB1RC_1LG---_0LA0LB", "R,E,P=100,u=10,s=0,d=1d+0,b=1b+0,S=-"),
]:
    T = kl.tmpl(tm, t_str)
    for ds, a in [([1, 0], 4), ([0, 0], 4), ([0], 4), ([], 4)]:
        evs = kl.run(tm, ds, a, 1, steps=100000, nchg=0, maxl=30, T=T, pall=1)
        k_evs = [f"K({short(e[2])};{e[3]};{e[4]})@{e[1]}" if e[0]=='K' else f"{e[0]}@{e[1]}" for e in evs[1:] if e[0] in ('K','H')]
        print(f"{name} K({short(ds)};{a};1) -> {' -> '.join(k_evs[:6])}")

# Run dlscan3.exe on c00232+
dl2_dir = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl2_out'
new_files = sorted(glob.glob(os.path.join(dl2_dir, 'c*.tsv')))
new_files = [f for f in new_files if int(os.path.basename(f)[1:6]) >= 232]
tms = []
for f in new_files:
    with open(f) as fp:
        for line in fp:
            if line.startswith('1RB') and '\t' in line:
                tms.append(line.split('\t')[0])
in_txt = os.path.join(OUT_DIR, 'c232_plus_in.txt')
out_tsv = os.path.join(OUT_DIR, 'c232_plus_dl3.tsv')
with open(in_txt, 'w') as fp:
    for tm in sorted(set(tms)):
        fp.write(tm + '\n')
subprocess.run([r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits\dlscan3.exe', '--in', in_txt, '--out', out_tsv, '--threads', '1'], check=True)
with open(out_tsv) as fp:
    print("\n=== c232_plus_dl3.tsv ===")
    print(fp.read())
