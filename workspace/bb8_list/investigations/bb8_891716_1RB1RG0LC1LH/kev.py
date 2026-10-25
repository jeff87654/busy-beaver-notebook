"""K-family events: record every visit of state C on the blank cell right of the word, parse as K(ds;a;b)."""
import sys
from sim import T

def parse_K(w):
    """w = 1 (10)^x1 11 (10)^x2 11 ... (10)^xm 11 -> [x1..xm] or None"""
    if not w.startswith('1') or not w.endswith('11'): return None
    body = w[1:]
    xs = []; i = 0; n = len(body)
    while i < n:
        j = i; c = 0
        while body[j:j+2] == '10':
            c += 1; j += 2
        if body[j:j+2] != '11': return None
        xs.append(c); i = j + 2
    return xs if len(xs) >= 2 else None

def run_events(N, cb, init=None):
    """cb(steps, xs or None, word) at each C-on-right-blank visit. returns (halted?, steps, tape...)"""
    size = 1 << 16
    tape = bytearray(size); pos = size // 2; st = 0; steps = 0
    lo = pos
    if init:
        word, off, st = init
        pos = size//2; lo = pos - off
        for i, c in enumerate(word): tape[lo+i] = int(c)
    while steps < N:
        if pos <= 2 or pos >= len(tape) - 3:
            n = len(tape); tape = bytearray(n) + tape + bytearray(n); pos += n; lo += n
        sym = tape[pos]
        e = T[st][sym]
        if e is None:
            return ('HALT', steps, st, pos, tape, lo)
        if st == 2 and sym == 0:
            # is the cell the right end? check everything right is blank: assume if pos is beyond highest nonblank
            # we cheaply check tape[pos-1] != 0 and nothing to the right within window
            if tape[pos-1] == 1 and not any(tape[pos:pos+4]):
                w = ''.join(map(str, tape[lo:pos])).lstrip('0')
                if cb(steps, parse_K(w), w): return ('STOP', steps, st, pos, tape, lo)
        tape[pos], d, st = e[0], e[1], e[2]
        pos += d; steps += 1
        if pos < lo: lo = pos
    return ('N', steps, st, pos, tape, lo)

def fmt(xs):
    return 'K(%s; %d; %d)' % (','.join(map(str, xs[:-2])), xs[-2], xs[-1]) if len(xs) >= 2 else 'K?%s' % xs

if __name__ == '__main__':
    N = int(sys.argv[1]); lim = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    cnt = [0]
    def cb(steps, xs, w):
        cnt[0] += 1
        if cnt[0] <= lim:
            if xs is not None: print(steps, fmt(xs))
            else: print(steps, 'NOTK', w[:100])
    r = run_events(N, cb)
    print(r[:4], 'events', cnt[0])
