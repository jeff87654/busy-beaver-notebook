import sys, os, re
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import idle
import kl
from egrid import short

os.environ['PATH'] = r'C:\msys64\ucrt64\bin;C:\msys64\mingw64\bin;' + os.environ.get('PATH', '')
HERE = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_7state_fw1_redirects'
tsv = os.path.join(HERE, 'enum_rebE2_9.tsv')

# First scan enum_rebE2_9.tsv for clean blank K-configurations:
# A clean blank K-config has d_top >= 2 (or d_top == 1 with >= 4 inner even digits >= 2)
# and all inner digits EVEN (or at most one odd digit).
clean_e1_halt = []
clean_e2_halt = []
clean_e1_mod = []

with open(tsv, 'r') as f:
    header = f.readline()
    for line in f:
        parts = line.rstrip('\r\n').split('\t')
        if len(parts) < 7:
            continue
        redir, typ, tm, blank_s, e1_7, e1_9, e2_7 = parts
        m = re.match(r'blank=\[([0-9,]+)\];(\d+)@(\d+)', blank_s)
        if not m:
            continue
        ds = [int(x) for x in m.group(1).split(',')]
        a0 = int(m.group(2))
        st0 = int(m.group(3))
        # Check if ds is a genuine tower:
        # Either ds[0] >= 3 (odd) and all ds[1:] are even and at least 3 of them are >= 2
        # Or ds[0] >= 2 (even) and all ds[1:] are even and at least 3 of them are >= 2
        # Or ds[0] == 1 and at least 4 of ds[1:] are >= 2
        inner_even = all(x % 2 == 0 for x in ds[1:])
        nonzero_inner = sum(1 for x in ds[1:] if x >= 2)
        if nonzero_inner >= 3 and (inner_even or sum(1 for x in ds[1:] if x % 2 == 1) == 1):
            if typ == 'E1_HALT':
                clean_e1_halt.append((redir, tm, ds, a0, st0, e1_7, e1_9, e2_7))
            elif typ == 'E2_HALT':
                clean_e2_halt.append((redir, tm, ds, a0, st0, e1_7, e1_9, e2_7))
            else:
                clean_e1_mod.append((redir, tm, ds, a0, st0, e1_7, e1_9, e2_7))

print(f"Clean tower candidates: E1_HALT={len(clean_e1_halt)}, E2_HALT={len(clean_e2_halt)}, E1_MOD={len(clean_e1_mod)}")

print("\n=== Clean Tower E1_HALT machines ===")
for item in clean_e1_halt:
    redir, tm, ds, a0, st0, e1_7, e1_9, e2_7 = item
    # Note: if ds[0] is odd and inner_even, Round 1 exhaustion is K(1, 0^(len(ds)-1); A_1; 1)!
    if ds[0] % 2 == 1 and all(x % 2 == 0 for x in ds[1:]):
        print(f"  [ODD-TOP {redir}] {tm} | blank=K({short(ds)};{a0})@{st0} | {e1_7} {e1_9}")

print("\n=== Clean Tower E2_HALT machines ===")
for item in clean_e2_halt:
    redir, tm, ds, a0, st0, e1_7, e1_9, e2_7 = item
    print(f"  [{redir}] {tm} | blank=K({short(ds)};{a0})@{st0} | {e1_7} {e1_9} {e2_7}")
