"""Compare the literal run from the blank tape with the abstract model F(W,b) (absys.step) at every K event.

  python orbit_check.py [steps] [TM]
K event: state B on a blank cell, cells to the left ... 0 1 1, everything to the right blank; the tape to the left is
parsed as  (10)^d1 0 ... (10)^dn 0 (10)^a 0 (10)^(2b+1) 011  (far digits first) with the leading blank stripped.
"""
import sys, time
sys.path.insert(0, 'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/bb8_891716_1RB0LD0LC1RB')
from absys import step, norm

N = int(sys.argv[1]) if len(sys.argv) > 1 else 20_000_000
TM = sys.argv[2] if len(sys.argv) > 2 else "1RB0LD_0LC1RB_1LB1LA_1RE0LH_0RF1LE_0RA0RG_0RC0LE_1LD---"
tab = {}
for i, t in enumerate(TM.split('_')):
    for s in (0, 1):
        x = t[3 * s:3 * s + 3]
        tab[(i, s)] = None if x == '---' else (int(x[0]), 1 if x[1] == 'R' else -1, 'ABCDEFGH'.index(x[2]))
SIZE = 1 << 22
tape = bytearray(SIZE)
pos = SIZE // 2
lo = hi = pos
q = 0


def parse():
    """Parse the tape left of pos (state B, blank right) into (W nearest-first, b) or None."""
    s = bytes(tape[lo:pos]).rstrip(b'\x00')
    w = ''.join('1' if c else '0' for c in tape[lo:pos]).lstrip('0')
    if not w.endswith('011'):
        return None
    w = w[:-3]
    # b' units (10) at the end
    k = 0
    while w.endswith('10'):
        w = w[:-2]
        k += 1
    if k % 2 == 0:
        return None
    runs = []
    while True:
        if not w.endswith('0'):
            return None
        w = w[:-1]
        n = 0
        while w.endswith('10'):
            w = w[:-2]
            n += 1
        runs.append(n)
        if not w or set(w) == {'0'}:
            break
    return norm(runs), (k - 1) // 2


model = None          # (W, b) predicted
events = 0
mism = 0
t0 = time.time()
steps = 0
last_report = 0
while steps < N:
    s = tape[pos]
    tr = tab[(q, s)]
    if tr is None:
        print('HALT at step', steps)
        break
    w, d, q = tr
    tape[pos] = w
    pos += d
    steps += 1
    if pos < lo:
        lo = pos
    if pos > hi:
        hi = pos
    if q == 1 and tape[pos] == 0 and tape[pos - 1] == 1 and tape[pos - 2] == 1 and tape[pos - 3] == 0 and pos >= hi:
        r = parse()
        if r is None:
            continue
        events += 1
        if model is None:
            model = r
            continue
        # advance the model to the next visible K event (a model state with empty W is invisible)
        W, b = model
        W, b, kind = step(W, b)
        if not W:
            W, b, kind = step(W, b)
        model = (W, b)
        if r != model:
            mism += 1
            print('MISMATCH at step', steps, 'literal', r[0][:6], r[1], 'model', model[0][:6], model[1])
            break
    if steps - last_report >= 5_000_000:
        last_report = steps
        print('...', steps, 'steps,', events, 'K events, mismatches', mism, '%.0fs' % (time.time() - t0), flush=True)
print('done:', steps, 'steps,', events, 'K events,', mism, 'mismatches; digits', len(model[0]) if model else None,
      'b has', len(str(model[1])) if model else None, 'digits')
