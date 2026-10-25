"""Jump a canonical champion snapshot (tokens in front of the accumulator) to its next blocker event.
  python jump.py "TOKENS"   -> prints the event token list (without accumulator)
Rule (champion R1-R3 on 3d+1 digits): the rightmost token whose residue mod 3 is not 1, or a raw <...> token, is the
next blocker j; numeric j is set to value 1 in its own encoding (m mod 3 + 3, unchanged if already smaller) so the
machine itself performs its last decrement; every 3d+1 token right of j (digits and the a-digit) is set to D1 (= 0).
x*k repeats are expanded. Fails loudly on anything it cannot parse."""
import re, sys


def expand(toks):
    out = []
    for t in re.findall(r'<[^>]*>|\S+', toks):
        if t.startswith('<') or re.fullmatch(r'P\d+', t):
            out.append(t)
        elif re.fullmatch(r'\d+\*\d+', t):
            v, k = t.split('*'); out += [v] * int(k)
        elif re.fullmatch(r'\d+', t):
            out.append(t)
        else:
            raise SystemExit(f'cannot parse token {t!r}')
    return out


def jump(toks):
    v = expand(toks)
    j = None
    for i in range(len(v) - 1, -1, -1):
        t = v[i]
        if t.startswith('<') or t.startswith('P') or int(t) % 3 != 1:
            j = i; break
    if j is None:
        raise SystemExit('no blocker')
    if v[j].isdigit():
        m = int(v[j]); r = m % 3 + 3
        if m > r: v[j] = str(r)
    for i in range(j + 1, len(v)):
        v[i] = '1'
    return ' '.join(v)


if __name__ == '__main__':
    print(jump(sys.argv[1]))
