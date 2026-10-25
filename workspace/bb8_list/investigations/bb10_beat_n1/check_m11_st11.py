"""Check exact stage trace of [11/11] under size-ordered representatives and test the single-zero step (..., C, 0, 1^Z | R, 2)."""
import sys, threading
from pathlib import Path

sys.setrecursionlimit(200000)
threading.stack_size(256 * 1024 * 1024 - 4096)

REBUILD_DIR = Path(r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb10_c35_rebuild')
sys.path.insert(0, str(REBUILD_DIR))
import mf35
mf35.LOW = 0x08000000 | 0x40

M11 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RI0LC_1RG1LD_1LC0RH_1RG1LF_0LJ0LI_---0RC'

def toks(w):
    t = []; i = 0
    while i < len(w):
        if w[i] == '1':
            j = i; c = 0
            while w[j + 1:j + 3] == '01':
                j += 2; c += 1
            t.append(c); i = j + 1
        else:
            t.append('_'); i += 1
    return t

def main():
    # Trace M11 where each new accumulator is assigned a representative based on the zero-count Z it cleared,
    # and when Z increases, R increases by at least 3x!
    print("=== Tracing M11 with realistic ordered representatives ===")
    w, hd, st = mf35.xword(6, 35)
    from follow2 import Aff, jump
    cur_r = 19
    last_z = 35
    for s in range(45):
        in_str = mf35.rle(toks(w))[-120:]
        o = mf35.run_stage(M11, w, hd, st, 200_000_000)
        if not o.startswith('J'):
            print(f"  st {s:2d} IN : {in_str}")
            print(f"        OUT: {o}")
            break
        parts = o.split('|')
        tt = [int(x) for x in parts[1].split()]
        far = parts[2].strip() if len(parts) > 2 else ''
        j_str = f"J step={parts[0].split()[1]} " + mf35.rle(tt[::-1])[-120:]
        print(f"  st {s:2d} IN : {in_str}")
        print(f"        OUT: {j_str}")
        digits = tt[3:][::-1]
        # Count trailing 1s in digits (the zero-list length being cleared by jump)
        z_cleared = 0
        for d in reversed(digits):
            if d == 1:
                z_cleared += 1
            else:
                break
        if z_cleared > last_z:
            # New omega-jump! Pick a representative > 2 * max token on tape (in the valid mod-12 class r = 7 mod 12)
            max_tok = max(digits or [19])
            cur_r = max(cur_r + 12, ((2 * max_tok + 20) // 12) * 12 + 7)
            last_z = z_cleared
        ent = []
        for m in digits:
            if ent and ent[-1][1] == m:
                ent[-1][2] += 1
            else:
                ent.append(['D', m, 1])
        left = [('D', Aff(m), Aff(c)) for _, m, c in ent] + [('D', Aff(tt[2]), Aff(1)), ('D', Aff(tt[1]), Aff(1))]
        tail = [('D', Aff(2), Aff(1))]
        items, newp, info = jump(left, tail, {}, 1)
        vals = {p: cur_r for p in newp}
        new = []
        for e in items:
            m = e[1].at(vals) if isinstance(e[1], Aff) else int(e[1])
            c = e[2].at(vals) if isinstance(e[2], Aff) else int(e[2])
            new += [m] * c
        if len(new) >= 3 and new[-2] > 2000:
            new[-2] = cur_r
        print(f"        JUMP: z_cleared={z_cleared} -> rep={cur_r}")
        w = far + mf35.word_of_tokens(new)
        hd, st = len(w), 'G'

    sv = getattr(mf35._LOCAL, 'sv', None)
    if sv is not None:
        sv.kill()

t = threading.Thread(target=main)
t.start()
t.join()
