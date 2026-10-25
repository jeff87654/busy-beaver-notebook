import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb7_c231_coq')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb7_c231_coq\tools')
import idle, random
from kcheck import run_k, M1
M2 = "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_1LC0RB"
random.seed(1)
bad = 0
for m in (M1, M2):
  # R1
  for _ in range(60):
    ds = [random.randint(0,3) for _ in range(random.randint(1,5))]
    a = random.randint(1,8); b = random.randint(0,10)
    r = run_k(ds, a, b, m)
    if r[0] != 'K' or r[2] != (ds, a-1, b+3): bad += 1; print('R1 bad', ds, a, b, r[:3])
  # R2
  for _ in range(60):
    t = [random.randint(0,3) for _ in range(random.randint(0,4))]
    y = random.randint(0,4); b = random.randint(0,10)
    r = run_k([y+1]+t, 0, b, m)
    if r[0] != 'K' or r[2] != ([y]+t, b+3, 0): bad += 1; print('R2 bad', y, t, b, r[:3])
  # R3
  for k in range(1, 9):
    for b in range(0, 12):
      t = [random.randint(0,2) for _ in range(random.randint(0,3))]
      y = random.randint(0,3)
      r = run_k([0]*k + [y+1] + t, 0, b, m, maxsteps=300000)
      exp = ([1]*(k-1) + [b+3-k, y] + t, 1, 0) if b + 3 >= k else None
      if r[0] != 'K' or r[2] != exp:
        if b >= k: bad += 1
        print('R3', "BAD" if b>=k else 'edge', k, b, y, t, r[:3])
  # R4
  for k in range(1, 22):
    for b in range(0, 25):
      r = run_k([0]*k, 0, b, m, maxsteps=300000)
      if r[0] != 'H': print('R4 nonhalt', k, b, r[:3]); bad += (b >= k)
print('bad', bad)
