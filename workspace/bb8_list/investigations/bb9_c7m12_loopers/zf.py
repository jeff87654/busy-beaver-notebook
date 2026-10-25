"""zf.py: 'zeroing follower' for list engines that are NOT the BB(7) champion's (the weak-engine c7m12 rows).
Literal simulation; at every K-moment (state Q reading 0 on the rightmost visited cell, not at the stage's first step)
the tape left of the head is read nearest-first and parsed as  [r] [a] d1 .. dk  BLOCKER ...  where the digits are the
maximal run of tokens that pass the digit test.  If some digit d1..dk is not the zero digit, the engine's Ackermann
process is replaced by its outcome (a JUMP): a -> zero, every d_i -> zero digit, r -> the representative R (default 20,
same parity as configured).  Otherwise the literal simulation continues (small processes and exhaustions are literal).
Reports each jump (k = the length of the list the jump clears, the blocker, the far part), every K-moment whose shape is
new, and a halt (undefined slot read).  Screening only: R is a single representative (residues not tracked).

Machine configs (CONF): Q, nearest-first reading S = reversed(tape left of head) with tokens
  'D': (10)^m 1 in S    'U': 1 (01)^m in S (i.e. D-tokens of the forward tape read right to left)
  r: 'tok' = first token, 'pairs' = leading (01)^r pairs of S after an optional single 0 (raw accumulator run)
  lead0: S starts with this many 0 cells (template suffix), az: zero a-token, dz: zero digit token, dig: digit test.

  python zf.py NAME [--start blank|exh:R] [--maxs 3e8] [--R 20] [--jumps 40]"""
import sys, argparse, re
from tm import parse, dtoks
sys.setrecursionlimit(10000)

CONF = {
    # E0-undefined twins: K = D-tokens .. D(a) (10)^r [0 if r odd], state I (a counts by 1, digits 2d+1)
    'E0twinA': dict(M='1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_0RH0RF_0RI1RH_1RB1LG', Q='I', tok='U', r='pairs',
                    az=0, dz=1, dig=lambda m: m % 2 == 1),
    'E0twinB': dict(M='1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_0RH0RF_0RI1RH_1RB1RH', Q='I', tok='U', r='pairs',
                    az=0, dz=1, dig=lambda m: m % 2 == 1),
    # E0-undefined looper: reversed tape = 0 D(r) D(a) D(d1) ... D(blocker) ..., state H (a counts by 1, digits 2d+1)
    'E0loop': dict(M='1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_0RH0RF_1RI0LH_0LC0RH', Q='H', tok='D', r='tok',
                   lead0=1, az=0, dz=1, dig=lambda m: m % 2 == 1),
    # G11 looper (H0 undefined): K = D-tokens .. D(a) (10)^r 011100, state A
    'G11': dict(M='1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RA0LC_1RG1LD_0RH0RF_---0RI_0LF1RA', Q='A', tok='U', r='pairs',
                sfx=['011100'], az=0, dz=1, dig=lambda m: m % 2 == 1),
    # NOBOUNDARY/REBUILD different-engine row X1 (I0 undefined): reversed tape = D(0) D(r) D(a) D(d1) ..., state B
    'X1': dict(M='1RB0RA_1LC1LF_1RD0LB_1RA1LE_0RI0LC_1RG1LD_0RH0RF_0LB1RE_---1RA', Q='B', tok='D', r='tok',
               lead0=0, pre=[0], az=0, dz=1, dig=lambda m: m % 2 == 1),
    # G14 looper (H0 undefined): reversed tape = D(r) D(a) D(d1) ... D(blocker), state A
    'G14': dict(M='1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LF0LC_1RG1LD_0RH0RF_---0RI_1RH1RA', Q='A', tok='D', r='tok',
                lead0=5, az=0, dz=1, dig=lambda m: m % 2 == 1),
}


def tokens_of(S, kind):
    """parse S (nearest-first) into tokens; returns (lead zeros, [tokens], rest-string after the last token)"""
    i = 0
    while i < len(S) and S[i] == '0':
        i += 1
    lead = i
    toks = []
    n = len(S)
    while i < n:
        if kind == 'D':
            j = i; m = 0
            while j + 1 < n and S[j] == '1' and S[j + 1] == '0':
                j += 2; m += 1
            if j < n and S[j] == '1':
                toks.append(m); i = j + 1
            else:
                break
        else:   # 'U': 1 (01)^m
            if S[i] != '1':
                break
            j = i + 1; m = 0
            while j + 1 < n and S[j] == '0' and S[j + 1] == '1':
                # stop if this '01' is really the start of the next token: '0' followed by '1' that begins 1(01)^m
                # (ambiguous); tokens are separated only by their leading 1, so 1 0 1 = U(1) and 1 1 = U(0) U(..)
                j += 2; m += 1
            toks.append(m); i = j
    return lead, toks, S[i:]


def word_of_tokens(toks, kind):
    if kind == 'D':
        return ''.join('10' * m + '1' for m in toks)
    return ''.join('1' + '01' * m for m in toks)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('name'); ap.add_argument('--start', default='blank'); ap.add_argument('--maxs', type=float, default=3e8)
    ap.add_argument('--R', type=int, default=20); ap.add_argument('--jumps', type=int, default=40)
    ap.add_argument('--word', default=None, help='start word (forward), head on the blank right of it in state Q')
    a = ap.parse_args()
    C = CONF[a.name]
    T, nst = parse(C['M'])
    Q = ord(C['Q']) - 65
    N = 1 << 24
    tape = bytearray(N); off = N // 2
    if a.word:
        for i, ch in enumerate(a.word):
            tape[off + i] = ch == '1'
        pos = off + len(a.word); q = Q
    else:
        pos = off; q = 0
    lo = off; hi = max(pos, off)
    njump = 0; lastshape = None; skip_first = True
    step = 0; maxs = int(a.maxs)
    while step < maxs:
        c = tape[pos]
        if q == Q and c == 0 and pos >= hi and not skip_first:
            S = ''.join('1' if x else '0' for x in reversed(tape[lo:pos]))
            # accumulator
            body = None; r = None
            if C['r'] == 'pairs':
                sfxs = C.get('sfx', ['0', ''])
                i = None
                for sf in sfxs:
                    if S.startswith(sf[::-1]):
                        i = len(sf); break
                if i is None:
                    i = 0; S2ok = False
                else:
                    S2ok = True
                lead0 = i; r = 0
                while S.startswith('01', i):
                    i += 2; r += 1
                lz, toks, rest = tokens_of(S[i:], C['tok'])
                body = toks if (S2ok and not lz) else None
            else:
                lz, toks, rest = tokens_of(S, C['tok'])
                lead0 = lz
                if 'lead0' in C and lz != C['lead0']:
                    toks = None
                pre = C.get('pre', [])
                if toks is not None and pre:
                    if toks[:len(pre)] != pre:
                        toks = None
                    else:
                        toks = toks[len(pre):]
                r = toks[0] if toks else None
                body = toks[1:] if toks else None
            if body and r is not None and len(body) >= 2:
                aa, ds = body[0], body[1:]
                k = 0
                while k < len(ds) and C['dig'](ds[k]):
                    k += 1
                nonzero = any(d != C['dz'] for d in ds[:k])
                shape = re.sub(r'\d+', '#', dtoks(S[::-1])[-60:])
                if nonzero and k >= 1:
                    # JUMP: the Ackermann process clears d1..dk; the borrow stops at the blocker ds[k]
                    njump += 1
                    blk = ds[k] if k < len(ds) else 'END'
                    far = ds[k:]
                    print(f'J{njump} step {step}: k={k} blocker={blk} r={r} a={aa} digits={ds[:min(k, 6)]}.. far={far[:8]}'
                          f'{"..." if len(far) > 8 else ""} (+{len(far)} far tokens) rest={len(rest)}b', flush=True)
                    nb = [C['az']] + [C['dz']] * k + ds[k:]
                    R = a.R
                    if C['r'] == 'pairs':
                        sf = C['sfx'][0] if 'sfx' in C else '0' * (R % 2)
                        newS = sf[::-1] + '01' * R + word_of_tokens(nb, C['tok']) + rest
                    else:
                        newS = '0' * lead0 + word_of_tokens(C.get('pre', []) + [R] + nb, C['tok']) + rest
                    neww = newS[::-1]
                    for x in range(lo, pos):
                        tape[x] = 0
                    start = pos - len(neww)
                    for i, ch in enumerate(neww):
                        tape[start + i] = ch == '1'
                    lo = min(lo, start)
                    skip_first = True
                    if njump >= a.jumps:
                        print('MAXJUMPS', step); return
                    continue
                elif shape != lastshape:
                    lastshape = shape
                    print(f'  K step {step}: r={r} a={aa} k={k} digits0 blocker={ds[k] if k < len(ds) else "END"} '
                          f'far={ds[k:k + 8]} (+{len(ds) - k})', flush=True)
        skip_first = False
        t = T.get((q, c))
        if t is None:
            w = ''.join('1' if x else '0' for x in tape[lo:hi + 1])
            print(f'HALT step {step} {chr(65 + q)}{c} ones={w.count("1")} | {dtoks(w)[:300]}'); return
        w_, d, nq = t
        tape[pos] = w_; pos += d; q = nq; step += 1
        if pos < lo: lo = pos
        if pos > hi: hi = pos
    print('END', step)


if __name__ == '__main__':
    main()
