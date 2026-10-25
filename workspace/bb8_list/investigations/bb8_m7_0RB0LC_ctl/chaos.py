"""Window-chaos model: the tape left of the last N cells (relative to the last 1) is chaos; the head may come back
from chaos into the window's leftmost cell in ANY right-moving state.  BFS over (window, head, state).
Reports whether a halt is reachable inside the window.
  python chaos.py N WORD [maxstates]"""
import sys
from collections import deque
from tailvisit import T
RIGHT_STATES = 'ABDEFGH'
N = int(sys.argv[1]); w0 = sys.argv[2]; MAXS = int(sys.argv[3]) if len(sys.argv) > 3 else 2_000_000
def norm(cells, head):
    """cells: list (window from left boundary to last 1, possibly with trailing zeros), head index (or None=chaos)
    returns canonical (string, head) with trailing zeros trimmed (head may lie beyond) and length capped to N."""
    s = ''.join(cells).rstrip('0')
    if not s: return None
    if len(s) > N:
        cut = len(s) - N; s = s[cut:]
        if head is not None:
            head -= cut
            if head < 0: head = None
    return s, head
start = norm(list(w0), None)
seen = {}; dq = deque()
def push(key, par):
    if key not in seen:
        seen[key] = par; dq.append(key)
push((start[0], None, None), None)
halt = None
while dq and len(seen) < MAXS:
    key = dq.popleft(); s, h, q = key
    if h is None:
        for q2 in RIGHT_STATES: push((s, 0, q2), key)
        continue
    cells = list(s);
    while h >= len(cells): cells.append('0')
    c = int(cells[h]); t = T[(q, c)]
    if t is None: halt = key; break
    cells[h] = str(t[0]); h2 = h + t[1]
    if h2 < 0:
        r = norm(cells, None)
        if r is None: print('window emptied', key); continue
        push((r[0], None, None), key); continue
    r = norm(cells, h2)
    if r is None: print('window emptied', key); continue
    if r[1] is None: push((r[0], None, None), key)
    else: push((r[0], r[1], t[2]), key)
print('states', len(seen), 'HALT' if halt else ('CLOSED' if not dq else 'CAP'))
if halt:
    path = []; k = halt
    while k is not None: path.append(k); k = seen[k]
    for k in reversed(path[-60:]):
        s, h, q = k
        print(('chaos ' + s) if h is None else (s[:h] + '[' + q + (s[h] if h < len(s) else '0') + ']' + s[h+1:]))
