# disp2cells.py "DISPLAY" : symsim show() string (exact counts) -> "cells head state", trimmed to start at the first 1
import sys, re
t = sys.argv[1]; toks = t.split(); L = []; R = []; side = L; d = q = None
for tok in toks:
    if re.fullmatch(r'[A-P]>', tok): d, q = '>', tok[0]; side = R; continue
    if re.fullmatch(r'<[A-P]', tok): d, q = '<', tok[1]; side = R; continue
    w, _, c = tok.partition('^'); side.append(w * (int(c) if c else 1))
Ls, Rs = ''.join(L), ''.join(R); cells = Ls + Rs; head = len(Ls) if d == '>' else len(Ls) - 1
if head >= len(cells): cells += '0' * (head - len(cells) + 1)
first = cells.find('1'); first = 0 if first < 0 or first > head else first
print(cells[first:], head - first, q)
