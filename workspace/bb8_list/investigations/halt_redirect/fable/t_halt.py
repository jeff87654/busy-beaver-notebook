import sys; sys.path.insert(0, '.')
from st import run, fmt
for A in [45, 45+2520]:
    for z in [3, 5, 216, 1500]:
        for r in [19, 2539]:
            o = run([A, 8] + [1]*z + [0, 1, 3, 0, 2, 1, 1], 1, r, maxs=400_000_000)
            print(f'A={A} z={z} r={r}: {fmt(o)}', flush=True)
