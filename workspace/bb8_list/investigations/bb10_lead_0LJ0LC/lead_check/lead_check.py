"""Lead's independent check of the BB(10) candidate (own simulator; does not use the agent's tools).
Family N(n_1..n_k) = 0^inf 1 ((10)^n_1 1) ... ((10)^n_k 1) G> 0^inf ; last entry = accumulator."""
import random, re, sys
M = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LJ0LC_1RG1LD_0RI0RH_1RG1LF_1RE1RI_---1LC'
TM = {}
for q, row in enumerate(M.split('_')):
    for s in (0, 1):
        t = row[3 * s:3 * s + 3]
        TM[(q, s)] = None if t[0] == '-' else (int(t[0]), 1 if t[1] == 'R' else -1, ord(t[2]) - 65)
G, J = 6, 9
WORD = re.compile(r'1((?:(?:10)*1)+)$')

def word(entries):
    return '1' + ''.join('10' * n + '1' for n in entries)

def parse(s):
    """entries of a family word, or None"""
    if not s.startswith('1'): return None
    rest, out = s[1:], []
    while rest:
        m = re.match(r'((?:10)*)1', rest)
        if not m: return None
        out.append(len(m.group(1)) // 2); rest = rest[m.end():]
    return out

def run(entries, maxsteps, stop_on_family=True, start_state=G):
    tape = {i: int(c) for i, c in enumerate(word(entries))}
    pos, q, steps = len(word(entries)), start_state, 0
    events = []
    while steps < maxsteps:
        s = tape.get(pos, 0)
        tr = TM[(q, s)]
        if tr is None:
            ones = sum(tape.values())
            return ('HALT', 'ABCDEFGHIJ'[q], s, ones, steps, events)
        w, d, nq = tr; tape[pos] = w; pos += d; q = nq; steps += 1
        if q == G and pos > max((i for i, v in tape.items() if v), default=-1):
            lo = min((i for i, v in tape.items() if v), default=0)
            hi = max((i for i, v in tape.items() if v), default=-1)
            if pos == hi + 1:
                e = parse(''.join(str(tape.get(i, 0)) for i in range(lo, hi + 1)))
                if e is not None:
                    events.append((steps, e))
                    if stop_on_family: return ('FAM', e, steps, events)
    return ('TIMEOUT', steps, events)

def runfrom_blank(maxsteps):
    tape, pos, q, steps, ev = {}, 0, 0, 0, []
    while steps < maxsteps:
        s = tape.get(pos, 0); tr = TM[(q, s)]
        if tr is None: return ev, ('HALT', steps)
        w, d, nq = tr; tape[pos] = w; pos += d; q = nq; steps += 1
        if q == G:
            ones = [i for i, v in tape.items() if v]
            if ones and pos == max(ones) + 1:
                e = parse(''.join(str(tape.get(i, 0)) for i in range(min(ones), max(ones) + 1)))
                if e is not None: ev.append((steps, e))
    return ev, None

bad = 0
# 1. start-up
ev, h = runfrom_blank(5000)
print('blank-tape family configurations (first 8):', [(s, e if len(e) < 8 else f'{e[:3]}..len{len(e)}') for s, e in ev[:8]])
hit = [s for s, e in ev if e == [5] + [1] * 26 + [1]]
print('C([2,0^26]|0) = entries [5]+[1]*26+[1] reached at step(s):', hit, '(agent: 3890)')
if hit != [3890]: bad += 1
# 2. rules on random configurations (top entry may be even; digits odd = 2d+1; accumulator 2b+1)
random.seed(1)
nr1 = nr23 = 0
for trial in range(1500):
    k = random.randint(1, 8)
    top = random.randint(0, 9)
    digits = [2 * random.randint(0, 6) + 1 for _ in range(k)]
    b = random.randint(0, 12)
    ent = [top] + digits + [2 * b + 1]
    r = run(ent, 3_000_000)
    # prediction
    ds = [top] + digits                    # list entries, nearest last
    if ds[-1] >= 2 and (ds[-1] % 2 == 1 or len(ds) == 1):    # R1 on the nearest entry (value d+1 >= 1)
        pred = ds[:-1] + [ds[-1] - 2] + [2 * (b + 2) + 1]; kind = 'R1'
    else:
        # nearest entries are zeros (n=1, or n=0 for an even top): find the nearest nonzero entry
        j = len(ds) - 1
        while j >= 0 and ds[j] in (0, 1): j -= 1
        if j < 0: continue                 # exhausted list: rebuild/halt, checked separately
        x1 = ds[j]
        zeros = len(ds) - 1 - j            # k+1 zero digits after it
        pred = ds[:j] + [x1 - 2] + [2 * (b + 2) + 1] + [1] * (zeros - 1) + [1]; kind = 'R23'
    ok = r[0] == 'FAM' and r[1] == pred
    if kind == 'R1': nr1 += 1
    else: nr23 += 1
    if not ok:
        bad += 1
        if bad < 6: print('MISMATCH', kind, ent, '->', r[:2], 'pred', pred)
print(f'rule checks: R1 {nr1}, R23 {nr23}, mismatches so far {bad}')
# 3. rebuild C(0^m|b) -> N(6, 1^(4b+m+6), 1)
nreb = 0
for m in range(1, 13):
    for b in range(0, 15):
        r = run([1] * m + [2 * b + 1], 50_000_000)
        pred = [6] + [1] * (4 * b + m + 6) + [1]
        nreb += 1
        if not (r[0] == 'FAM' and r[1] == pred):
            bad += 1
            if bad < 10: print('REBUILD MISMATCH m', m, 'b', b, '->', r[0], (r[1] if r[0] == 'FAM' else r[1:4]))
print(f'rebuild checks: {nreb}, mismatches so far {bad}')
# 4. halt N(0, 1^L, 2b+1) -> J reads 0, ones 2b+2L+5
nh = 0
for L in range(1, 25):
    for b in range(0, 25):
        r = run([0] + [1] * L + [2 * b + 1], 20_000_000)
        nh += 1
        if not (r[0] == 'HALT' and r[1] == 'J' and r[2] == 0 and r[3] == 2 * b + 2 * L + 5):
            bad += 1
            if bad < 14: print('HALT MISMATCH L', L, 'b', b, '->', r[:5])
print(f'halt checks: {nh}, mismatches so far {bad}')
# 5. whole end-game for L = 1: N(6, 1^1, 1) -> ... -> halt with b2 = F_1^3(0) = 28, ones 2*28 + 2 + 5 = 63
r = run([6, 1, 1], 100_000_000, stop_on_family=False)
print('end-game L=1 from N(6,1,1):', r[0], r[1:4] if r[0] == 'HALT' else r[1])
if not (r[0] == 'HALT' and r[3] == 63): bad += 1
print('TOTAL MISMATCHES:', bad)
