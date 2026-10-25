import sys, os
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

def abstract_step(W, b):
    # Strip trailing zeros from W
    while W and W[-1] == 0:
        W = W[:-1]
    if not W:
        return 'R4', ([2] * (b + 1), 0), {'b': b}
    j = 0
    while j < len(W) and W[j] == 0:
        j += 1
    y = W[j] - 1
    t = W[j+1:]
    if j == 0:
        return 'R1', ([y] + t, b + 1), {'a': y + 1, 'b': b}
    elif j <= b:
        r = b - j
        return 'R3A', ([2] * (j - 1) + [2 * (b - j + 2), y] + t, 0), {'j': j, 'b': b, 'r': r}
    elif j == b + 1:
        return 'R3B', ([2] * b + [y + 3] + t, 0), {'j': j, 'b': b}
    else:
        return 'R3C', ([2] * (b + 1) + [0] * (j - b - 2) + [y + 1] + t, 0), {'j': j, 'b': b}

W, b = [2, 2], 0
counts = {}
r3a_min_r = 999999
for step in range(500):
    rule, (W_next, b_next), info = abstract_step(W, b)
    counts[rule] = counts.get(rule, 0) + 1
    if rule == 'R3A':
        r3a_min_r = min(r3a_min_r, info['r'])
    if step < 35 or rule in ('R3B', 'R3C', 'R4') or (rule == 'R3A' and info['r'] <= 1):
        print(f"event {step:3d}: {rule:4s} info={info} W={W[:6]}{'...' if len(W)>6 else ''} (len={len(W)}) b={b} -> len={len(W_next)}, b'={b_next}")
    W, b = W_next, b_next
    if step == 40:
        break

print("Counts in first 40 abstract events:", counts, "min r in R3A:", r3a_min_r)
