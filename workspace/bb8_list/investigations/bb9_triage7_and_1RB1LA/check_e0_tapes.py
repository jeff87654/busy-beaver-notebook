import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import idle
import kl
from inspect_r4_2_3_e0 import inspect_halt_tape

print("=== Tape at E0 halt for [0; 4m+2], [1, 0, 0; 4m+1], [2, 0, 0; 4m], [3, 0, 0; 4m+3] ===")
for ds, a in [
    ([0], 2),
    ([0], 6),
    ([0], 10),
    ([1, 0, 0], 1),
    ([1, 0, 0], 5),
    ([2, 0, 0], 4),
    ([3, 0, 0], 3),
]:
    inspect_halt_tape(ds, a)
