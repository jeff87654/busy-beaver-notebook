import sys
sys.path.insert(0, r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_pool8_and_noinv53")
from resid_groupB import eval_list, M

def step_round(ds, a, b_rel):
    Uo, ro = eval_list(ds, a, b_rel)
    b_out = 2 if ((Uo + ro) % 2 == 0) else 1
    a_out = ((Uo + ro - b_out) // 2) % (M // 2)
    status = "REBUILD" if (a_out + b_out) % 2 == 0 else "HALT"
    return Uo, ro, a_out, b_out, status

# Wait: when status == "REBUILD", what list does E(a_out, b_out) rebuild?
# Let's check! In Group B (#17):
# At Blank E1: a=45, b_rel=1 (so a_out + b_out = 46 even -> REBUILD!).
# And E(a_out, b_out) with U_E = 2*a_out + b_out = 91 rebuilt:
# ([3, 2^{U_E//2 - 1}], a=3, b_rel=0) = ([3, 2^44], a=3, b_rel=0), which is ([3, 2^{43}, 1], a=8, b_rel=1)!
# Let's check E(3, b_rel=1): U_E = 2*3 + 1 = 7 -> U_E//2 - 1 = 2 -> ([3, 2^2], a=3, b_rel=0) = ([3, 2, 1], a=8, b_rel=1)!
# What about E(1, b_rel=1)? U_E = 3 -> ([2], a=8, b_rel=1)!
# In general, for ANY even (a_out + b_out), let N_2 = (2*a_out + b_out - 3) // 2.
# Wait: for a_out=3, b_out=1: N_2 = (7-3)//2 = 2 -> [3, 2^1, 1]; a=8; b_rel=1 (which is [3, 2^2]; a=3; b_rel=0)!
# For a_out=5, b_out=1: N_2 = (11-3)//2 = 4 -> [3, 2^3, 1]; a=8; b_rel=1 (which is [3, 2^4]; a=3; b_rel=0)!
# Wait: in general, E(a_out, b_out) when (a_out + b_out) is even rebuilds ([3] + [2]*N_2, a=3, b_rel=0) where N_2 = a_out + (b_out - 3)//2?
# Wait: if b_out=1, 2*a_out + b_out = 2*a_out + 1 (odd), so (a_out + b_out) is even iff a_out is odd! Then N_2 = a_out - 1.
# What if b_out=2 and a_out is even? Let's check with kmap2 or resid_groupB what E([], a_even, b_rel=2) does!

print("Testing the 4 startup profiles of the 24 rescued Group B leaves + cls53 #17:")
profiles = [
    ("cls53_17 (E1(45)->[3,2^43,1];8;1)", [3] + [2]*43 + [1], 8, 1),
    ("rescued_prof1 (E1(3)->[3,2,1];8;1)", [3, 2, 1], 8, 1),
    ("rescued_prof2 (start [3,2];3;1)", [3, 2], 3, 1),
    ("rescued_prof3 (start [3,1];8;1)", [3, 1], 8, 1),
    ("rescued_prof4 (start [3,2^3];3;1)", [3, 2, 2, 2], 3, 1),
]

for name, ds, a, b_rel in profiles:
    Uo, ro, a_out, b_out, st = step_round(ds, a, b_rel)
    print(f"  {name:38s} -> U={Uo:6d} r={ro} => a_out={a_out:6d} b_out={b_out} => {st}")
