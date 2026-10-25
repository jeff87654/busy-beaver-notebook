# v-coding helpers: tape RLE (from lit/symsim) -> oriented cell string / v-list
import re
def lit_rle_to_cells(s):
    """lit RLE like '1^4 0 [D0] 1^2' -> (cells string, head index, state)"""
    cells=[];head=None;q=None
    for t in s.split():
        if t.startswith('['): q=t[1]; head=len(cells); cells.append(t[2]); continue
        if '^' in t: b,n=t.split('^'); cells.append(b*int(n))
        else: cells.append(t)
    return ''.join(cells),head,q
def vlist(cells):
    """cells string (head end = right) -> list of 1-run lengths separated by single 0s; leading/trailing 0s stripped.
    returns list of ints; consecutive 0s produce zero entries (0^k -> k-1 zeros)."""
    c=cells.strip('0')
    if not c: return []
    return [len(x) for x in c.split('0')]
