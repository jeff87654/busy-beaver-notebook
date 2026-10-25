import sys; sys.path.insert(0, '.')
from st import run, fmt
print('--- rebuild stage 252: [3 X 0 | 1 | r]')
for X in [41, 41+2520, 41+5040]:
    for r in [19, 2539, 5059]:
        o = run([3, X, 0], 1, r, maxs=400_000_000)
        print(f'X={X} r={r}: {fmt(o)}', flush=True)
print('--- halting stage 297: [X 0 | 1 | r]')
for X in [225, 225+2520, 225+5040]:
    for r in [19, 2539, 5059]:
        o = run([X, 0], 1, r, maxs=400_000_000)
        print(f'X={X} r={r}: {fmt(o)}', flush=True)
