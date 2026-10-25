import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

from test_c4_8state_full import parse_tm, step_tm, make_exhaustion_tape, parse_e0_config

C4_1 = "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB"
C4_2 = "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_1LC0RB"

def generate_all_1slot_8state(base_str):
    """All 8-state extensions of base_str that leave exactly 1 slot as '---'."""
    parts = base_str.split('_')
    # Either H0 is '---' or H1 is '---'
    states = range(8)
    choices = []
    for w in (0, 1):
        for d in ('L', 'R'):
            for s in states:
                choices.append(f"{w}{d}{chr(ord('A')+s)}")
    out = []
    for c1 in choices:
        if c1[2] != 'H':
            continue # C1 must jump to H to use H
        # Case 1: H0 = ---, H1 in choices
        for h1 in choices:
            c_part = parts[2][:3] + c1
            h_part = "---" + h1
            tm = "_".join(parts[:2] + [c_part] + parts[3:] + [h_part])
            out.append((f"C1={c1} H0=--- H1={h1}", tm))
        # Case 2: H0 in choices, H1 = ---
        for h0 in choices:
            c_part = parts[2][:3] + c1
            h_part = h0 + "---"
            tm = "_".join(parts[:2] + [c_part] + parts[3:] + [h_part])
            out.append((f"C1={c1} H0={h0} H1=---", tm))
    return out

def sim_from_exhaustion(tm_str, k, M, max_steps=200000):
    trans = parse_tm(tm_str)
    tape, head, state = make_exhaustion_tape(k, M)
    e0_hits = []
    for step in range(1, max_steps + 1):
        if state == 4 and tape.get(head, 0) == 0:
            parsed = parse_e0_config(tape, head)
            if parsed is not None:
                e0_hits.append((step, parsed[0], parsed[1]))
        res = step_tm(trans, tape, head, state)
        if res is None:
            ones = sum(tape.values())
            return "HALT", step, ones, e0_hits
        head, state = res
    return "TIMEOUT", max_steps, sum(tape.values()), e0_hits

if __name__ == '__main__':
    for bname, bstr in [("C4_1", C4_1), ("C4_2", C4_2)]:
        cands = generate_all_1slot_8state(bstr)
        print(f"=== {bname}: testing {len(cands)} 8-state 1-halt-slot extensions ===")
        interesting = []
        for label, tm in cands:
            status, step, ones, e0_hits = sim_from_exhaustion(tm, k=3, M=2, max_steps=50000)
            # Filter out quick halts that didn't even do a cascade in Round 2
            if status == "HALT" and step > 500:
                status2, step2, ones2, e0_hits2 = sim_from_exhaustion(tm, k=3, M=3, max_steps=200000)
                interesting.append((label, status, step, ones, len(e0_hits), status2, step2, ones2, len(e0_hits2), e0_hits[:5]))
            elif status == "TIMEOUT" and len(e0_hits) >= 3:
                # Check if it's doing a cascade
                max_b = max(x[1] for x in e0_hits)
                if max_b >= 20:
                    interesting.append((label, status, step, ones, len(e0_hits), "-", 0, 0, 0, e0_hits[:5]))
        print(f"Found {len(interesting)} interesting 8-state 1-halt-slot extensions for {bname}:")
        for item in interesting:
            print(" ", item[:9], "first_e0:", item[9][:2])
