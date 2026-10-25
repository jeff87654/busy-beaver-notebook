import traceback
try:
    from solve_rounds import R
    print([R(1, 7), R(0, 7), R(1, 5), R(0, 5), R(1, 1024), R(0, 1024), R(1, 27), R(0, 27)])
    ok = all(R(I, a * b) % a == R(I, a) for I in (0, 1) for a in range(2, 40) for b in range(1, 12))
    print('consistent', ok)
except Exception:
    traceback.print_exc()
