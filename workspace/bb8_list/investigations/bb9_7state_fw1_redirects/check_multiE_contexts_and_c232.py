import sys, os, subprocess, glob
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import idle
import kl
from egrid import short

os.environ['PATH'] = r'C:\msys64\ucrt64\bin;C:\msys64\mingw64\bin;' + os.environ.get('PATH', '')
OUT_DIR = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_7state_fw1_redirects'
EXE = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\nested_detector\dlscan3.exe'

def sim_contexts(tm_str, tape_dict, head, state, max_steps):
    trans = {}
    for s_idx, block in enumerate(tm_str.split('_')):
        for b in (0, 1):
            cell = block[3*b:3*b+3]
            if cell == '---':
                trans[(s_idx, b)] = None
            else:
                w = int(cell[0])
                d = -1 if cell[1] == 'L' else 1
                ns = ord(cell[2]) - ord('A')
                trans[(s_idx, b)] = (w, d, ns)
    ctxs = {r: set() for r in range(5)}
    trans_ctxs = set()
    prev_slot = None
    for step in range(max_steps):
        b = tape_dict.get(head, 0)
        slot = (state, b)
        for r in range(5):
            win = tuple(tape_dict.get(head + o, 0) for o in range(-r, r+1))
            ctxs[r].add((slot, win))
        b_l = tape_dict.get(head - 1, 0)
        b_r = tape_dict.get(head + 1, 0)
        trans_ctxs.add((prev_slot, slot, b_l, b_r))
        t = trans.get(slot)
        if t is None:
            break
        w, d, ns = t
        tape_dict[head] = w
        head += d
        state = ns
        prev_slot = slot
    return ctxs, trans_ctxs

# Check multi_E_1 and multi_E_2 blank tape contexts vs E(;a;1) contexts
# Template L,E,P=1,u=01,s=0,d=1d+0,b=1b+0,S=-
# Let's run blank tape for 30,000 steps (which covers init(1..169), D, B1, etc.) plus synthetic B2, [0,0,2;4]
for name, tm in [
    ("multi_E_1", "1RB1LD_1RC1RD_1LB0RG_0RC1RE_0LA0LF_0RA1LE_0LA---"),
    ("multi_E_2", "1RB1LD_1RC1RD_1LB1RG_0RC1RE_0LA0LF_0RA1LE_1RC---"),
]:
    ctxs_idb, t_idb = sim_contexts(tm, {}, 0, 0, 30000)
    # Wait: let's check what steps 1..30000 on blank tape cover!
    # At step 169 it's at K(2,1;1;1), at step 76145 it's at K(1,3;190;1) (still in D and B1).
    # What if we compare against a synthetic full cascade of K(2,1,0; 1; 1) -> ... -> K(; A; 1) -> K(2, 1^...)?
    T = kl.tmpl(tm, "L,E,P=1,u=01,s=0,d=1d+0,b=1b+0,S=-")
    evs = kl.run(tm, [1, 1], 1, 1, steps=200000, nchg=0, maxl=80, T=T, pall=1)
    k_evs = [f"K({short(e[2])};{e[3]};{e[4]})@{e[1]}" for e in evs if e[0]=='K' and e[4]==1]
    print(f"\n[{name}] K(1,1;1;1) cascade ({len(k_evs)} lines): {' -> '.join(k_evs[:15])}")
    print(f"  ... {' -> '.join(k_evs[-8:])}")

# Also scan c00232+ with dlscan3.exe
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
subprocess.run([EXE, '--in', in_txt, '--out', out_tsv, '--threads', '1'], check=True)
with open(out_tsv) as fp:
    print("\n=== c232_plus_dl3.tsv ===")
    print(fp.read())
