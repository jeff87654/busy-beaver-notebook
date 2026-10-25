import sys, os, subprocess, glob
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import idle
import kl
from egrid import short

os.environ['PATH'] = r'C:\msys64\ucrt64\bin;C:\msys64\mingw64\bin;' + os.environ.get('PATH', '')
OUT_DIR = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_7state_fw1_redirects'
EXE = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\nested_detector\dlscan3.exe'

def parse_tm(tm_str):
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
    return trans

def build_LE_tape(ds, a, B=1):
    # Template: L,E,P=1,u=01,s=0,d=1d+0,b=1b+0,S=-
    # Since side=L, outer digits and P=1 are on the LEFT, or let's check kview's exact convention!
    # Wait: instead of guessing the tape encoding, we can run blank tape through a full synthetic round!
    pass

# Wait: on blank tape, multi_E_1 starts at K(2,1;1;1)@169 -> K(2,0;4;1)@247 -> K(1,9;1;1)@581 ...
# How many steps until K(2,1;1;1) reaches K(0; A; 1) -> K(; 2A+1; 1)?
# Wait: K(1,9;1;1) takes ~2^9 steps to reach K(1,0; 3070; 1), and then K(0, 6141; 1; 1) takes 2^6141 steps!
# So we can't run blank tape to E_1 directly, bit we CAN see the exact tape configuration of K(2,1;1;1)@169 and K(2,0;4;1)@247 and K(1,9;1;1)@581!
for name, tm in [
    ("multi_E_1", "1RB1LD_1RC1RD_1LB0RG_0RC1RE_0LA0LF_0RA1LE_0LA---"),
    ("multi_E_2", "1RB1LD_1RC1RD_1LB1RG_0RC1RE_0LA0LF_0RA1LE_1RC---"),
]:
    trans = parse_tm(tm)
    tape = {}
    head = 0
    state = 0
    target_steps = {147, 169, 211, 247, 461, 525, 581, 659}
    for step in range(1, 700):
        b = tape.get(head, 0)
        w, d, ns = trans[(state, b)]
        tape[head] = w
        head += d
        state = ns
        if step in target_steps:
            mn = min(tape.keys())
            mx = max(tape.keys())
            s = ''.join(f"[{chr(ord('A')+state)}{tape.get(i,0)}]" if i == head else str(tape.get(i,0)) for i in range(mn-1, mx+2))
            print(f"{name} step {step:3d}: {s}")

# Also run dlscan3 on c00232+
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
log_txt = os.path.join(OUT_DIR, 'c232_plus_dl3.log')
with open(in_txt, 'w') as fp:
    for tm in sorted(set(tms)):
        fp.write(tm + '\n')
with open(log_txt, 'w') as lf:
    p = subprocess.Popen([EXE, in_txt, out_tsv], creationflags=0x40, stdout=lf, stderr=subprocess.STDOUT)
    with open(os.path.join(OUT_DIR, 'pids.txt'), 'a') as pf:
        pf.write(f"dlscan3_232 {p.pid}\n")
    p.wait()
with open(out_tsv) as fp:
    print("\n=== c232_plus_dl3.tsv ===")
    print(fp.read())
