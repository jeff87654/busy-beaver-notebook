"""rprobe.py NAME 'tokens nearest-first incl r and a' [N]: run the zf.py config NAME literally from the K word of the given
tokens and print the next N K-moments (nearest-first tokens, r first) -- for fitting the weak engines' rules."""
import sys
from tm import parse
import zf
C = zf.CONF[sys.argv[1]]
toks = [int(x) for x in sys.argv[2].split()]
N = int(sys.argv[3]) if len(sys.argv) > 3 else 3
if C['r'] == 'pairs':
    sf = C.get('sfx', ['0'])[0] if 'sfx' in C else '0' * (toks[0] % 2)
    S = sf[::-1] + '01' * toks[0] + zf.word_of_tokens(toks[1:], C['tok'])
else:
    S = '0' * C.get('lead0', 0) + zf.word_of_tokens(toks, C['tok'])
w = S[::-1]
T, n = parse(C['M']); Q = ord(C['Q']) - 65
tape = {i: 1 for i, ch in enumerate(w) if ch == '1'}
pos = len(w); q = Q; hi = pos; lo = 0; found = 0
for step in range(1, 50_000_000):
    c = tape.get(pos, 0)
    if step > 1 and q == Q and c == 0 and pos >= hi:
        S = ''.join('1' if tape.get(i) else '0' for i in range(pos - 1, lo - 1, -1))
        if C['r'] == 'pairs':
            sfx = C.get('sfx', ['0', ''])
            ok = [sf for sf in sfx if S.startswith(sf[::-1])]
            if ok:
                i = len(ok[0]); r = 0
                while S.startswith('01', i): i += 2; r += 1
                lz, tk, rest = zf.tokens_of(S[i:], C['tok'])
                if not lz:
                    print(step, [r] + tk[:12], len(tk)); found += 1
        else:
            lz, tk, rest = zf.tokens_of(S, C['tok'])
            if lz == C.get('lead0', 0):
                print(step, tk[:13], len(tk)); found += 1
        if found >= N: break
    t = T.get((q, c))
    if t is None: print('HALT', step, chr(65 + q), c); break
    w_, d, nq = t
    if w_: tape[pos] = 1
    else: tape.pop(pos, None)
    pos += d; q = nq
    lo = min(lo, pos); hi = max(hi, pos)
