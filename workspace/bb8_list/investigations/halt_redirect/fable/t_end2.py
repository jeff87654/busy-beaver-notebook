import sys; sys.path.insert(0, '.')
from st import run, fmt
print('--- after the non-rebuild branch: [Y 0 | 0 | r]')
for Y in [43, 2563]:
    for r in [5083, 10123, 2563+2520*0]:
        o = run([Y, 0], 0, r, maxs=400_000_000)
        print(f'Y={Y} r={r}: {fmt(o)}', flush=True)
