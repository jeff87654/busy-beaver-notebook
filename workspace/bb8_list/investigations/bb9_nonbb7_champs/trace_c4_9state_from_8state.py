import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

from test_c4_8state_full import parse_tm, step_tm, make_exhaustion_tape, parse_e0_config

C4_1 = "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB"
C4_2 = "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_1LC0RB"

def trace_second_c1(base_str, c1_act, h0_act, h1_act, k=3, M=2, max_steps=100000):
    """
    Suppose in Context 1 we use (c1_act, h0_act, h1_act), where one of h0_act or h1_act
    can be redirected to state I in 9 states, OR where in Round 2 the machine hits C1 again
    in Context 2!
    Let's record EVERY visit to state C1 (state 2, bit 1) or state H (state 7) during Round 1->2!
    """
    parts = base_str.split('_')
    tm_str = "_".join(parts[:2] + [parts[2][:3] + c1_act] + parts[3:] + [h0_act + h1_act])
    trans = parse_tm(tm_str)
    tape, head, state = make_exhaustion_tape(k, M)
    
    visits = []
    e0_visits = []
    in_round2 = False
    for step in range(1, max_steps + 1):
        bit = tape.get(head, 0)
        if state == 4 and bit == 0:
            parsed = parse_e0_config(tape, head)
            if parsed is not None:
                in_round2 = True
                e0_visits.append((step, parsed[0], parsed[1]))
        if in_round2 and (state == 7 or (state == 2 and bit == 1)):
            mn = min(tape.keys())
            mx = max(tape.keys())
            left_s = "".join(str(tape.get(i, 0)) for i in range(max(mn, head-12), head))
            right_s = "".join(str(tape.get(i, 0)) for i in range(head+1, min(mx+1, head+20)))
            sname = f"{chr(ord('A')+state)}{bit}"
            visits.append((step, sname, left_s, right_s, sum(tape.values())))
            if len(visits) >= 10:
                break
        res = step_tm(trans, tape, head, state)
        if res is None:
            break
        head, state = res
    return e0_visits, visits

if __name__ == '__main__':
    # Test the even-B_new CLEAN_K gadgets from earlier:
    candidates = [
        ("C4_1", C4_1, "1RH", "0LG", "1LH"),
        ("C4_1", C4_1, "0LH", "1LE", "1LH"),
        ("C4_2", C4_2, "1RH", "0LG", "1LH"),
        ("C4_2", C4_2, "0LH", "1LE", "1LH"),
    ]
    for bname, bstr, c1, h0, h1 in candidates:
        print(f"=== {bname} C1={c1} H0={h0} H1={h1} ===")
        for k in (2, 3, 4):
            for M in (2, 3):
                e0v, vis = trace_second_c1(bstr, c1, h0, h1, k=k, M=M, max_steps=100000)
                print(f"  k={k}, M={M}: first E0={e0v[0] if e0v else None}, total E0={len(e0v)}")
                for v in vis[:4]:
                    print(f"    Round2 visit: step={v[0]} {v[1]} left=...{v[2]} right={v[3]}... ones={v[4]}")
