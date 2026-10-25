import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import kl

M4  = "1RB---_1RC0RC_0LD0LE_1RA0LE_0RF1LC_1RG0RC_1RA1RE"
M13 = "1RB---_1RC1RA_0LD0LE_1LE0LE_0RF1LC_1RG1RA_1RA1RE"
NEW_MULTI = "1RB0LB_1RC1RE_1LD1LF_1LB0LE_1LG0LC_0LD1RA_---0RF"

def analyze_machine(name, m_str, t_str, max_steps=50000):
    print(f"============================================================")
    print(f"MACHINE {name}: {m_str}")
    print(f"Template: {t_str}")
    T = kl.tmpl(m_str, t_str)
    ev = kl.blank(m_str, max_steps, maxl=50, T=T)
    for e in ev[:25]:
        print(" ", e)

    # Also let's do a literal step-by-step slot profile from blank tape up to 50,000 steps
    mirror = (T['o'] == 'L')
    tr = {}
    for q, row in enumerate(m_str.split('_')):
        for c in range(2):
            cell = row[3*c:3*c+3]
            if cell[0] != '-':
                w = int(cell[0])
                d = 1 if cell[1] == 'R' else -1
                if mirror: d = -d
                nx = ord(cell[2]) - ord('A')
                tr[(q, c)] = (w, d, nx, f"{chr(65+q)}{c}")
    tape = {}
    pos = 0
    q = 0
    uses = {f"{chr(65+q)}{c}": [] for q in range(7) for c in range(2)}
    counts = {f"{chr(65+q)}{c}": 0 for q in range(7) for c in range(2)}
    last_use = {f"{chr(65+q)}{c}": -1 for q in range(7) for c in range(2)}
    for st in range(1, max_steps + 1):
        c = tape.get(pos, 0)
        if (q, c) not in tr:
            print(f"HALT at step {st}")
            break
        w, d, nx, sl = tr[(q, c)]
        counts[sl] += 1
        last_use[sl] = st
        if len(uses[sl]) < 15:
            uses[sl].append(st)
        tape[pos] = w
        pos += d
        q = nx
    print("\nSlot usage from blank (50,000 steps):")
    for sl in sorted(uses):
        print(f"  {sl}: count={counts[sl]:6d} last={last_use[sl]:6d} first_uses={uses[sl]}")

analyze_machine("M4 (P=1 coding)", M4, "L,C,P=1,u=01,s=0,d=1d+0,b=1b+0,S=-", 50000)
analyze_machine("M13 (P=1 coding)", M13, "L,D,P=1,u=01,s=0,d=1d+0,b=1b+0,S=0", 50000)
analyze_machine("NEW_MULTI (P=1 coding)", NEW_MULTI, "R,E,P=1,u=011,s=0,d=1d+0,b=1b+0,S=1", 50000)
