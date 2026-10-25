"""Exact literal verification of the X/Y family rules of
   1RB0LG_0LC0RH_---1LD_0RD1LE_1RF0LC_1RG1LG_1LA1LF_1RA1RH
Families (head in state A on the blank cell just left of the word, blank tape elsewhere):
   X(a,b,c) = 0^inf A> 0 1^a 0 1^b 0 1 (011)^c 0^inf
   Y(n)     = 0^inf A> 0 1^n 0^inf
Each start configuration is simulated with no acceleration until the first later configuration
of the form 0^inf A> 0 w 0^inf with w in X u Y (or a halt); the result is compared to the prediction.
"""
import re, sys, json, time
TM = "1RB0LG_0LC0RH_---1LD_0RD1LE_1RF0LC_1RG1LG_1LA1LF_1RA1RH"

def parse(tm):
    t = []
    for ch in tm.split('_'):
        row = []
        for i in (0, 3):
            e = ch[i:i+3]
            row.append(None if e == '---' else (int(e[0]), 1 if e[1] == 'R' else -1, 'ABCDEFGH'.index(e[2])))
        t.append(row)
    return t
T = parse(TM)

def Xw(a, b, c): return '1' * a + '0' + '1' * b + '0' + '1' + '011' * c
def Yw(n): return '1' * n

RX = re.compile(r'(1+)0(1*)01((?:011)*)')
RY = re.compile(r'1*')
def classify(w):
    m = RX.fullmatch(w)
    if m: return ('X', len(m.group(1)), len(m.group(2)), len(m.group(3)) // 3)
    if RY.fullmatch(w): return ('Y', len(w))
    return None

def run(word, maxsteps=2*10**6):
    """Simulate from 0^inf A> 0 word 0^inf. Returns (status, steps, result, final_tape_info)."""
    n = len(word)
    pad = 8 * n + 4000
    tape = bytearray(pad) + bytearray(int(c) for c in word) + bytearray(pad)
    pos = pad - 1; st = 0; steps = 0
    lo = pos; hi = pad + n
    while steps < maxsteps:
        s = tape[pos]
        e = T[st][s]
        if e is None:
            # halted: report tape
            l = tape.find(1, lo, hi + 1)
            r = tape.rfind(1, lo, hi + 1)
            ones = tape.count(1, lo, hi + 1)
            left = tape[l:pos] if l < pos else b''
            right = tape[pos + 1:r + 1] if r > pos else b''
            return ('halt', steps, (('ABCDEFGH'[st], s), ''.join(map(str, left)), ''.join(map(str, right)), ones))
        w, d, q = e
        tape[pos] = w; pos += d; st = q; steps += 1
        if pos < lo:
            lo = pos
            if pos <= 1:
                ext = len(tape); tape = bytearray(ext) + tape; pos += ext; lo += ext; hi += ext
        elif pos > hi:
            hi = pos
            if pos >= len(tape) - 2:
                tape += bytearray(len(tape))
        if st == 0 and tape[pos] == 0 and tape.find(1, lo, pos) < 0:
            r = tape.rfind(1, pos, hi + 1)
            wd = ''.join(map(str, tape[pos + 1:r + 1]))
            c = classify(wd)
            if c:
                return ('ok', steps, c)
    return ('limit', steps, None)

def check(cases):
    res = []; bad = 0
    for name, word, pred in cases:
        t0 = time.time()
        st, steps, got = run(word)
        if pred[0] == 'HALT':
            ok = st == 'halt' and got[0] == ('C', 0) and got[1] == pred[1] and got[2] == pred[2]
            gshow = (got[0], got[1], got[2][:30] + '..', got[3]) if st == 'halt' else got
        else:
            ok = st == 'ok' and got == pred
            gshow = got
        if not ok:
            bad += 1
            print('MISMATCH', name, st, steps, gshow, 'pred', pred[:2])
        res.append(dict(case=name, status=st, steps=steps, got=str(gshow), pred=str(pred[:3]), ok=ok))
    return res, bad

def cases(A, B, C, K):
    out = []
    for a in range(1, A + 1, 2):          # a odd (the reachable X configs have a = 1 mod 4)
        for b in range(0, B + 1):
            for c in range(0, C + 1):
                w = Xw(a, b + 1, c)
                out.append(('R1 X(%d,%d,%d)' % (a, b + 1, c), w, ('X', a + 4, b, c)))
    for a in range(1, A + 1, 2):
        for c in range(0, C + 1):
            out.append(('R2 X(%d,0,%d)' % (a, c + 1), Xw(a, 0, c + 1), ('X', 1, a + 4, c)))
        out.append(('R3 X(%d,0,0)' % a, Xw(a, 0, 0), ('Y', a + 8)))
    for k in range(1, K + 1):
        out.append(('R4 Y(%d)' % (3 * k), Yw(3 * k), ('X', 1, 5, k - 1)))
    for k in range(3, K + 1):
        out.append(('R5 Y(%d)' % (3 * k + 1), Yw(3 * k + 1), ('X', 17, 3, k - 3)))
    out.append(('R5s Y(1)', Yw(1), ('Y', 5)))
    out.append(('R5s Y(4)', Yw(4), ('Y', 13)))
    out.append(('R5h Y(7)', Yw(7), ('HALT', '10' + '1' * 14, '011')))
    for k in range(0, K + 1):
        out.append(('R6 Y(%d)' % (3 * k + 2), Yw(3 * k + 2), ('HALT', '1', '011' * (k + 1))))
    return out

if __name__ == '__main__':
    A, B, C, K = (int(x) for x in sys.argv[1:5])
    cs = cases(A, B, C, K)
    res, bad = check(cs)
    by = {}
    for r in res:
        k = r['case'].split()[0]
        by.setdefault(k, [0, 0, 0]); by[k][0] += 1; by[k][1] += (not r['ok']); by[k][2] = max(by[k][2], r['steps'])
    for k in sorted(by):
        print('%-4s %5d cases, %d mismatches, max steps %d' % (k, by[k][0], by[k][1], by[k][2]))
    print('TOTAL %d cases, %d mismatches' % (len(res), bad))
    json.dump(res, open('check_rules.json', 'w'), indent=0)
