"""hcfg.py: halting configurations of the BB(9)/BB(10) champions at the used-up list Kd [] 0 b (b odd).
  python hcfg.py ch9|ch10 B1,B2,...  > starts.txt     (renum STARTS lines: label word head state, at the E0 read)
Kd [] 0 b = 0^inf [D on 0] 1^(b+1) 0^inf.  The champion is run literally from Kd [] 0 b until it reads E0 (its halt);
fails loudly if it does not get there within the budget or halts elsewhere."""
import sys
CH = {'ch9': '1RB1RA_0LC0LF_0RD1LC_1RA1RG_1RZ0RA_1LB1LF_1LH1RE_0LI1LH_1LB0LH',
      'ch10': '1RB1RA_0LC0LF_0RD1LC_1RA1RG_1RZ0RA_1LB1LF_1LH1RE_0LI1LH_0LF0LJ_1LH0LJ'}
def parse(M):
    t = {}
    for q, r in enumerate(M.split('_')):
        for c in (0, 1):
            x = r[3*c:3*c+3]
            if x == '---': continue
            if x[0] not in '01' or x[1] not in 'LR' or not x[2].isalpha(): raise ValueError(x)
            t[(q, c)] = (int(x[0]), 1 if x[1] == 'R' else -1, ord(x[2]) - 65)
    return t
def run_to_halt(M, b, budget=10**7):
    t = parse(M); tape = {}
    for i in range(b + 1): tape[1 + i] = 1
    h, q, n = 0, 3, 0
    while n < budget:
        c = tape.get(h, 0)
        tr = t[(q, c)]
        if tr[2] == 25: return tape, h, q, c, n           # Z = the halt transition (not executed)
        tape[h] = tr[0]; h += tr[1]; q = tr[2]; n += 1
    raise RuntimeError('no halt within budget for b=%d' % b)
if __name__ == '__main__':
    M = CH[sys.argv[1]]
    for b in map(int, sys.argv[2].split(',')):
        tape, h, q, c, n = run_to_halt(M, b)
        if (q, c) != (4, 0): raise RuntimeError('halted at %s%d' % (chr(65+q), c))
        lo = min([k for k, v in tape.items() if v] + [h]) - 2; hi = max([k for k, v in tape.items() if v] + [h]) + 2
        w = ''.join(str(tape.get(i, 0)) for i in range(lo, hi + 1))
        ones = sum(tape.values())
        sys.stderr.write('b=%d halt E0 after %d steps, ones=%d (+1 by 1RZ), head offset %d\n' % (b, n, ones, h - lo))
        print('b%d %s %d E' % (b, w, h - lo))
