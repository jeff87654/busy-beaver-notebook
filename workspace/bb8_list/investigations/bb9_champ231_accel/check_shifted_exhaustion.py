import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from verify_rule_d import parse_tm

tr = parse_tm("1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB")

print("=== Testing S_even ([E0] 1100 (11)^a (00)^k 1) and S_odd ([E0] 100 1^(2a+1) (00)^k 1) ===")
for mode in ["S_even", "S_odd"]:
    print(f"\n--- {mode} ---")
    for d1 in [0, 1, 2, 3]:
        a = 2
        if mode == "S_even":
            s_right = "1100" + "11"*a + "00" + "11"*d1 + "001"
        else:
            s_right = "100" + "1"*(2*a+1) + "00" + "11"*d1 + "001"
        tape = {i+1: int(c) for i, c in enumerate(s_right) if c == '1'}
        h, q = 0, 4
        for step in range(1, 200000):
            b = tape.get(h, 0)
            act = tr[2*q + b]
            if act == "---":
                mn, mx = min(min(tape), h), max(max(tape), h)
                cfg = "".join(f"[{chr(65+q)}{tape.get(i,0)}]" if i == h else str(tape.get(i,0)) for i in range(mn, mx+1))
                print(f"  d1={d1}: HITS C1 at step {step:6d}: {cfg[:80]}...")
                break
            if int(act[0]): tape[h] = 1
            else: tape.pop(h, None)
            h += 1 if act[1] == 'R' else -1
            q = ord(act[2]) - 65
            if q == 4 and tape.get(h, 0) == 0 and tape and h == min(tape) - 1:
                mx = max(tape)
                r_str = "".join(str(tape.get(i, 0)) for i in range(h+1, mx+1))
                if r_str.startswith("100") and r_str.endswith("001"):
                    parts = r_str[3:-3].split("00")
                    if all(len(p)%2==0 and not (set(p)-{'1'}) for p in parts):
                        print(f"  d1={d1}: Reaches CLEAN b=0 K at step {step}: {[len(p)//2 for p in parts]}")
                        break
                if r_str.startswith("1100") and r_str.endswith("001"):
                    parts = r_str[4:-3].split("00")
                    if all(len(p)%2==0 and not (set(p)-{'1'}) for p in parts):
                        print(f"  d1={d1}: Reaches S_even at step {step}: a={len(parts[0])//2}, ds={[len(p)//2 for p in parts[1:]]}")
                if r_str.startswith("1001") and r_str.endswith("001"):
                    parts = r_str[3:-3].split("00")
                    if len(parts[0])%2 == 1 and not (set(parts[0])-{'1'}) and all(len(p)%2==0 and not (set(p)-{'1'}) for p in parts[1:]):
                        print(f"  d1={d1}: Reaches S_odd at step {step}: 2a+1={len(parts[0])}, ds={[len(p)//2 for p in parts[1:]]}")
