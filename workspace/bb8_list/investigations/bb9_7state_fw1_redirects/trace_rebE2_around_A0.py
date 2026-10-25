import sys, os
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import idle
import kl
from verify_rebE2_and_all_rules import parse_tm, format_full_tape

os.environ['PATH'] = r'C:\msys64\ucrt64\bin;C:\msys64\mingw64\bin;' + os.environ.get('PATH', '')

tm_rebE2 = "1RB0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_---0RC"
t_rebE2 = "L,F,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0"

def trace_window_steps(tm, tape_init, pos_init, q_init, start_st, end_st):
    tr = parse_tm(tm, mir=False)
    tape = dict(tape_init)
    pos = pos_init
    q = q_init
    for step in range(1, end_st + 1):
        c = tape.get(pos, 0)
        if start_st <= step <= end_st:
            print(f"  step {step:4d} ({chr(65+q)}{c}): {format_full_tape(tape, pos, q)}")
        if (q, c) not in tr:
            print(f"  HALT at step {step} ({chr(65+q)}{c})")
            break
        w, d, nq = tr[(q, c)]
        if w: tape[pos] = 1
        else: tape.pop(pos, None)
        pos += d
        q = nq

print("=== Blank tape steps 1..45 ===")
trace_window_steps(tm_rebE2, {}, 0, 0, 1, 45)

print("\n=== Blank tape steps 315..365 ===")
trace_window_steps(tm_rebE2, {}, 0, 0, 315, 365)

print("\n=== E_1: K(1, 0^2; a=3; 1) around A0 (steps 125..198) ===")
t = kl.tmpl(tm_rebE2, t_rebE2)
w = kl.word(t, [1, 0, 0], 3, 1)
tape_e1 = {-i: 1 for i, ch in enumerate(w) if ch == '1'}
pos_e1 = -len(w)
trace_window_steps(tm_rebE2, tape_e1, pos_e1, ord(t['q']) - 65, 125, 198)
