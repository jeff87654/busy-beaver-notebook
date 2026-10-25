import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

from enum_c1_new_8_and_9 import parse_tm, format_tape, make_c1_new_halt_tape

C1_NEW = "1RB0RA_1LC1LF_0LD0LB_1RE0LB_1RA---_1RG1LE_0RG0RF"

def step_tr(tr, tape, head, state):
    v = tape.get(head, 0)
    t = tr.get((state, v))
    if t is None:
        return tape, head, -1
    w, d, ns = t
    if w == 0: tape.pop(head, None)
    else: tape[head] = 1
    return tape, head + d, ns

def check_classes():
    base_tr = parse_tm(C1_NEW)
    STATES = 8
    all_trans = [(w, d, s) for w in (0, 1) for d in (-1, 1) for s in range(STATES)]
    
    classes = {}
    for e1 in all_trans:
        if e1[2] != 7:
            continue
        for h0 in [None] + all_trans:
            for h1 in [None] + all_trans:
                tr = dict(base_tr)
                tr[(4, 1)] = e1
                if h0 is not None: tr[(7, 0)] = h0
                if h1 is not None: tr[(7, 1)] = h1
                
                res = []
                ok = True
                for b in (4, 5, 6):
                    tape, head, state = make_c1_new_halt_tape(b)
                    found = None
                    for step in range(1, 2000):
                        tape, head, state = step_tr(tr, tape, head, state)
                        if state == -1:
                            found = ('HALT', step, format_tape(tape, head, state))
                            break
                        if state == 1 and tape.get(head, 0) == 0 and tape and head > max(tape.keys()):
                            cstr = format_tape(tape, head, state)
                            if cstr.endswith("001001001B[0]"):
                                found = ('B0', step, cstr)
                                break
                    if not found:
                        ok = False
                        break
                    res.append(found)
                if ok and res[0][0] == 'B0' and res[1][0] == 'B0' and res[2][0] == 'B0':
                    sig = (res[0][2], res[1][2], res[2][2])
                    if sig not in classes:
                        classes[sig] = (e1, h0, h1, res)
    print(f"Unique B[0] right-cap classes on C1_new: {len(classes)}")
    names = "ABCDEFGH"
    for idx, (sig, (e1, h0, h1, res)) in enumerate(classes.items()):
        e1_s = f"{e1[0]}{'L' if e1[1]==-1 else 'R'}{names[e1[2]]}"
        h0_s = "---" if h0 is None else f"{h0[0]}{'L' if h0[1]==-1 else 'R'}{names[h0[2]]}"
        h1_s = "---" if h1 is None else f"{h1[0]}{'L' if h1[1]==-1 else 'R'}{names[h1[2]]}"
        print(f"\nClass {idx+1}: E1={e1_s} H0={h0_s} H1={h1_s}")
        for b, r in zip((4, 5, 6), res):
            print(f"  b={b}: step={r[1]:4d} {r[2]}")
            
        # Continue running b=4 up to 50,000 steps to see what happens in Round 2!
        tr = dict(base_tr)
        tr[(4, 1)] = e1
        if h0 is not None: tr[(7, 0)] = h0
        if h1 is not None: tr[(7, 1)] = h1
        tape, head, state = make_c1_new_halt_tape(4)
        events = []
        for step in range(1, 50000):
            tape, head, state = step_tr(tr, tape, head, state)
            if state == -1:
                events.append(f"HALT at step {step}: {format_tape(tape, head, state)[:80]}")
                break
            if state == 1 and tape.get(head, 0) == 0 and tape and head > max(tape.keys()):
                cstr = format_tape(tape, head, state)
                if len(events) < 8:
                    events.append(f"step {step:6d}: {cstr[:90]}")
            if state == 4 and tape.get(head, 0) == 1 and tape and head <= min(tape.keys()) + 4:
                if len(events) < 12:
                    events.append(f"step {step:6d} E[1] near left: {format_tape(tape, head, state)[:90]}")
        for ev in events:
            print(f"    {ev}")

if __name__ == '__main__':
    check_classes()
