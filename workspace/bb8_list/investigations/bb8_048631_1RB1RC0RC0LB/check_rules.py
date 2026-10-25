"""Exact literal checks (no acceleration) of the rules proved in BB8_48631_1RB1RC.v.

P(j,n) = 0^inf B>0 0 0 (0000)^j (1010)^n 11111 0^inf   (head in state B on the first 0 shown)

  S00   : P(0,0)     -->+ P(0,3)
  S0n   : P(0,n+1)   -->+ P(1,n)
  Step1 : P(j+1,n+1) -->+ P(3j+4,n)
  Step0 : P(j+1,0)   -->+ P(0,3j+6)
  init  : blank tape -->* P(0,3)

Each run starts from the exact tape, simulates one step at a time, and stops at the first configuration
in state B whose tape equals the predicted target, with the head on the target's head cell and nothing
nonzero outside the target word.  The run must not halt and must not touch any cell left of the target's
head (the target's left side is blank).  Step counts are reported.
"""
import json, sys
from lit import T

def P_word(j, n):
    return [0, 0, 0] + [0, 0, 0, 0] * j + [1, 0, 1, 0] * n + [1, 1, 1, 1, 1]

def run_to(tape_word, head, target_word, limit=10**8):
    # tape: dict pos->sym, head position; start state B
    tape = {i: s for i, s in enumerate(tape_word) if s}
    pos, q = head, 'B'
    tgt_ones = [i for i, s in enumerate(target_word) if s]
    nnz_target = len(tgt_ones)
    minpos = pos
    for step in range(1, limit + 1):
        s = tape.get(pos, 0)
        tr = T[(q, s)]
        if tr is None:
            return ('HALT', step, None)
        w, d, q = tr
        if w: tape[pos] = 1
        else: tape.pop(pos, None)
        pos += d
        minpos = min(minpos, pos)
        if q == 'B' and tape.get(pos, 0) == 0 and len(tape) == nnz_target:
            # candidate: target word placed with head at pos
            if all(tape.get(pos + i, 0) == 1 for i in tgt_ones):
                return ('OK', step, (pos, minpos))
    return ('LIMIT', limit, None)

def blank_run(target_word, limit=10**6):
    tape = {}; pos = 0; q = 'A'
    tgt_ones = [i for i, s in enumerate(target_word) if s]
    for step in range(1, limit + 1):
        s = tape.get(pos, 0)
        tr = T[(q, s)]
        if tr is None:
            return ('HALT', step)
        w, d, q = tr
        if w: tape[pos] = 1
        else: tape.pop(pos, None)
        pos += d
        if q == 'B' and tape.get(pos, 0) == 0 and len(tape) == len(tgt_ones) \
                and all(tape.get(pos + i, 0) == 1 for i in tgt_ones) and min(tape) > pos:
            return ('OK', step)
    return ('LIMIT', limit)

results = {'init': blank_run(P_word(0, 3))}
print('init', results['init'])
fails = 0; cases = 0
rows = []
for j in range(0, 9):
    for n in range(0, 9):
        if j == 0 and n == 0: tgt = (0, 3); rule = 'S00'
        elif j == 0: tgt = (1, n - 1); rule = 'S0n'
        elif n == 0: tgt = (0, 3 * (j - 1) + 6); rule = 'Step0'
        else: tgt = (3 * (j - 1) + 4, n - 1); rule = 'Step1'
        res, steps, info = run_to(P_word(j, n), 0, P_word(*tgt))
        cases += 1
        ok = res == 'OK' and info[1] >= info[0]   # never visited left of the target head
        if not ok: fails += 1
        rows.append(dict(rule=rule, j=j, n=n, target=tgt, result=res, steps=steps, ok=ok))
        print(rule, (j, n), '->', tgt, res, steps, 'ok' if ok else 'FAIL')
# the only halting exit: odd number of ones in the G/H sweep, i.e. X(z,0) with z even
print('cases', cases, 'fails', fails)
json.dump(dict(init=results['init'], rows=rows, cases=cases, fails=fails), open('check_rules.json', 'w'), indent=1)
