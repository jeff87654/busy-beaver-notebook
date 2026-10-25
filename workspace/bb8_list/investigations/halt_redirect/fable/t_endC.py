import sys; sys.path.insert(0, '.')
from st import run, fmt
print('--- [8 0 1 | 1 | r] -> 45 8 1^3 0 1 3 0 5 1^2 ?')
for r in [19, 2539, 5059]:
    print(f'r={r}: {fmt(run([8, 0, 1], 1, r, maxs=400_000_000))}', flush=True)
print('--- [8 3 1 | 1 | r] -> 8 0 2r+5 ?')
for r in [19, 2539]:
    print(f'r={r}: {fmt(run([8, 3, 1], 1, r, maxs=400_000_000))}', flush=True)
print('--- [8 11 104 48 0 | 1 | r] -> 8 9 403 ? (104 = 2P+66?, 48 = 2r+10 of an older r)')
for P104, P48 in [(104, 48), (104+2520, 48), (104, 48+2520)]:
    for r in [19, 2539]:
        print(f'P104={P104} P48={P48} r={r}: {fmt(run([8, 11, P104, P48, 0], 1, r, maxs=400_000_000))}', flush=True)
