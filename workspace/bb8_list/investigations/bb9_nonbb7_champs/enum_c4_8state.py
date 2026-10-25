import sys, re
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from test_exhaustion import parse_tm, format_tape

# We test all 8-state extensions of C4_1:
# C1 = w d H (4 choices)
# H0, H1 in {---} U ({0,1} x {L,R} x {A..H}) (33 x 33 choices)
base_states = "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB".split('_')

moves = ['---'] + [f"{w}{d}{s}" for w in (0, 1) for d in ('L', 'R') for s in 'ABCDEFGH']
c1_moves = [f"{w}{d}H" for w in (0, 1) for d in ('L', 'R')]

def sim_from_halt(tr, k, M, max_steps=1500):
    cfg = ('10' * (2*k - 3)) + '11001C[1]1' + ('0011' * M) + '001'
    tape = {}; pos = 0; i = 0
    while i < len(cfg):
        if cfg[i].isalpha():
            state = ord(cfg[i]) - ord('A')
            if int(cfg[i+2]) == 1: tape[pos] = 1
            head = pos; pos += 1; i += 4
        else:
            if int(cfg[i]) == 1: tape[pos] = 1
            pos += 1; i += 1
    visited_h = set()
    for step in range(1, max_steps + 1):
        v = tape.get(head, 0)
        if state == 7:
            visited_h.add(v)
        t = tr.get((state, v))
        if t is None:
            return ('HALT', step - 1, f"{chr(ord('A')+state)}{v}", len(tape), format_tape(tape, head, state), visited_h)
        w, d, ns = t
        if w == 0: tape.pop(head, None)
        else: tape[head] = 1
        head += d; state = ns
        # Check if we reached a clean Left E[0] configuration: E[0] 1^B (00 (11)^d)* 001
        if state == 4 and tape.get(head, 0) == 0 and (not tape or head <= min(tape.keys())):
            ft = format_tape(tape, head, state)
            m = re.match(r'^E\[0\](1+)((?:00(?:11)*)*)001$', ft)
            if m:
                b_new = len(m.group(1))
                ds = [len(p)//2 for p in m.group(2).split('00')[1:]]
                return ('CLEAN_K', step, b_new, ds, visited_h)
    return ('TIMEOUT', max_steps, len(tape), format_tape(tape, head, state)[:80], visited_h)

clean_hits = []
interesting_halts = []

for c1 in c1_moves:
    for h0 in moves:
        for h1 in moves:
            tm_str = f"1RB0RG_1RC1RB_0RD{c1}_0LE0LD_0LF1LE_1RA1LF_0LD0RB_{h0}{h1}"
            tr = parse_tm(tm_str)
            res = sim_from_halt(tr, k=3, M=3, max_steps=1000)
            if res[0] == 'CLEAN_K':
                # Test across k=2,3,4,5 and M=2,3,4
                all_ok = True
                summary = []
                for k_test in (2, 3, 4, 5):
                    r2 = sim_from_halt(tr, k=k_test, M=3, max_steps=1500)
                    summary.append((k_test, r2[:4]))
                    if r2[0] != 'CLEAN_K':
                        all_ok = False
                clean_hits.append((tm_str, all_ok, summary, res[4]))
            elif res[0] == 'HALT' and res[1] > 100:
                # Check if step count grows super-polynomially with M!
                r_m2 = sim_from_halt(tr, k=3, M=2, max_steps=5000)
                r_m3 = res
                r_m4 = sim_from_halt(tr, k=3, M=4, max_steps=20000)
                if r_m2[0] == 'HALT' and (r_m4[0] == 'TIMEOUT' or r_m4[1] > 3 * r_m3[1]):
                    interesting_halts.append((tm_str, r_m2[:4], r_m3[:4], r_m4[:4]))

print(f"Total CLEAN_K hits (at k=3, M=3): {len(clean_hits)}")
for tm_str, all_ok, summary, vh in clean_hits[:30]:
    print(f"  {tm_str} (all_k={all_ok}, H_used={vh}): {summary}")

print(f"\nTotal super-linear HALT hits: {len(interesting_halts)}")
for tm_str, rm2, rm3, rm4 in interesting_halts[:30]:
    print(f"  {tm_str}: M=2->{rm2}, M=3->{rm3}, M=4->{rm4}")
