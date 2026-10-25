import sys, re
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from test_exhaustion import parse_tm, format_tape
from test_c4_8state_general_k_M import make_exhaustion_tape

tm_str = "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---1RC"
tr = parse_tm(tm_str)

def trace_c1_visits(k, M, max_steps=100000):
    tape, head, state = make_exhaustion_tape(k, M)
    c1_list = []
    for step in range(1, max_steps + 1):
        v = tape.get(head, 0)
        if state == 2 and v == 1:
            ft = format_tape(tape, head, state)
            c1_list.append((step, ft))
        if state == 4 and v == 0 and (not tape or head <= min(tape.keys())):
            ft = format_tape(tape, head, state)
            m = re.match(r'^E\[0\](1+)((?:00(?:11)*)*)001$', ft)
            if m:
                b_new = len(m.group(1))
                ds = [len(p)//2 for p in m.group(2).split('00')[1:]]
                return ("CLEAN_K", step, b_new, ds, c1_list)
        t = tr.get((state, v))
        if t is None:
            return ("HALT", step - 1, len(tape), format_tape(tape, head, state), c1_list)
        w, d, ns = t
        if w == 0: tape.pop(head, None)
        else: tape[head] = 1
        head += d; state = ns
    return ("TIMEOUT", max_steps, len(tape), "", c1_list)

if __name__ == '__main__':
    for k in (2, 3, 4, 5, 7, 8, 12, 13, 24, 25):
        res = trace_c1_visits(k, M=5)
        print(f"=== k={k}, M=5: {res[0]} at step {res[1]}, b={res[2]}, d={res[3]} (C1 visits: {len(res[4])}) ===")
        for step, ft in res[4][:6]:
            print(f"  step {step:5d}: {ft}")
        if len(res[4]) > 6:
            print("  ...")
            for step, ft in res[4][-3:]:
                print(f"  step {step:5d}: {ft}")
