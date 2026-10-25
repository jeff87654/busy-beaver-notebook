"""SMFW B2 codec: abstract SM state <-> concrete tape (dict pos->0/1).

Concrete layout (orientation: D free end on the LEFT, N on the RIGHT, section 5 mirrored):

    ... 0^inf  [D]  0^10  M  <P chain>  0^GIN  [N]  0^inf

  D = A  (00)  B,   B = (params) (W?) c   with c the LAST run of D, c = 1^(c'+3).
  Right edge R of D (last cell of c) is PINNED at position 0; D grows LEFTWARD (free end).
  M (IP marker, a lone 1) is PINNED at MK = 0 + 1 + GAP_DI.  For B2 tests P and the chain
  are empty, so the entry cell (first chain-one cell) is MK+1.

  Runs: theorem separator = 1^1, param separator = 1^2, token value v = 1^v (e=3..A=7, v_i=8+i),
  counter = 1^(c'+3).  Runs are separated by a single 0; the A|B boundary is a TRIPLE 0 (000).
  INVARIANT WE ENFORCE: inside D the longest 0-run is 3 (the boundary); every other gap is a
  single 0.  (DET/COMMIT compact, see LAYOUT.md.)  This makes the 0^10 D->IP gap an unambiguous
  sentinel for the shared return scanner.
"""

E, EQ, IM, NOT, ALL, V0 = 3, 4, 5, 6, 7, 8
GAP_DI = 40      # zeros between D's right edge (R=0) and the marker
GAP_IN = 60      # zeros between marker and N
MK = GAP_DI + 1  # marker position = 11
ENTRY = MK + 1   # first chain-one cell = 12

def _runs_A(A):
    rs = []
    for t in A:
        rs.append(1)                 # theorem separator
        rs.extend(int(x) for x in t) # token runs
    return rs

def _runs_B(B, c):
    rs = []
    for kind, toks in B:
        rs.append(1 if kind == 'theorem' else 2)
        rs.extend(int(x) for x in toks)
    rs.append(c + 3)                 # counter run, always last
    return rs

def encode(A, B, c, N=None, rpos=0):
    """Return (tape dict, head) for the entry of a D-side op; N optional for RB."""
    Aruns = _runs_A(A)
    Bruns = _runs_B(B, c)
    # render D right-aligned so c's last cell = position 0
    cells = []   # list of (value) built left->right, then we shift so last index = 0
    def emit_runs(runs, sep_before_first=None):
        for i, r in enumerate(runs):
            if cells:
                cells.append(0)      # single-0 separator
            for _ in range(r):
                cells.append(1)
    # A then boundary then B
    if Aruns:
        emit_runs(Aruns)
        cells.append(0); cells.append(0); cells.append(0)   # triple-0 boundary (A|B)
        # B's first run must not get an extra leading sep; emit manually
        first = True
        for r in Bruns:
            if not first:
                cells.append(0)
            first = False
            for _ in range(r):
                cells.append(1)
    else:
        emit_runs(Bruns)
    # place: last cell at 0
    n = len(cells)
    tape = {}
    for i, v in enumerate(cells):
        pos = i - (n - 1)            # i==n-1 -> 0
        if v:
            tape[pos] = '1'
    tape[MK] = '1'
    if N is not None:
        # N region: remaining bits then 000 111 then placed bits
        base = MK + GAP_IN
        _render_N(tape, base, N, rpos)
    return tape, ENTRY

def _render_N(tape, base, N, rpos):
    # remaining = N[rpos:], placed = N[:rpos]; digit = '1 b 0', sentinel '111'
    p = base
    for b in N[rpos:]:
        tape[p] = '1'; tape[p+1] = str(b); p += 3   # '1 b 0'
    tape[p] = '1'; tape[p+1] = '1'; tape[p+2] = '1'; p += 3   # sentinel 111
    for b in N[:rpos]:
        tape[p] = '1'; tape[p+1] = str(b); p += 3

def _read_runs(tape, lo, hi):
    """Read maximal 1-runs in [lo,hi] with the 0-run length before each."""
    runs = []            # list of (run_len, gap_before)
    i = lo; gap = 0
    while i <= hi:
        if tape.get(i, '0') == '1':
            L = 0
            while i <= hi and tape.get(i, '0') == '1':
                L += 1; i += 1
            runs.append((L, gap)); gap = 0
        else:
            gap += 1; i += 1
    return runs

def decode(tape):
    """Decode D back to (A, B, c).  Finds D as everything left of the marker gap."""
    # locate marker
    mk = MK
    # D occupies cells left of mk-GAP_DI..?; find rightmost D cell = first 1 going left from mk-1
    i = mk - 1
    while tape.get(i, '0') == '0':
        i -= 1
        if i < mk - 2000:
            raise ValueError('no D')
    R = i
    # left end: scan left until a 0-run of length > 2
    L = R; zcount = 0; j = R
    while True:
        j -= 1
        if tape.get(j, '0') == '1':
            L = j; zcount = 0
        else:
            zcount += 1
            if zcount > 3:
                break
        if j < R - 5000:
            break
    runs = _read_runs(tape, L, R)
    # split at the boundary gap==2
    Aruns = []; Bruns = []; seen_b = False
    for idx, (ln, gap) in enumerate(runs):
        if idx > 0 and gap == 3 and not seen_b:
            seen_b = True
        (Bruns if seen_b else Aruns).append(ln)
    if not seen_b:   # no boundary -> A empty, all is B
        Bruns = Aruns; Aruns = []
    A = _parse_stack(Aruns)
    c = Bruns[-1] - 3
    B = _parse_B(Bruns[:-1])
    return A, B, c

def _parse_stack(runs):
    A = []; cur = None
    for ln in runs:
        if ln == 1:              # theorem separator
            if cur is not None: A.append(tuple(cur))
            cur = []
        else:
            cur.append(ln)
    if cur is not None: A.append(tuple(cur))
    return A

def _parse_B(runs):
    B = []; cur = None; kind = None
    for ln in runs:
        if ln == 1 or ln == 2:
            if cur is not None: B.append([kind, cur])
            kind = 'theorem' if ln == 1 else 'param'; cur = []
        else:
            cur.append(ln)
    if cur is not None: B.append([kind, cur])
    return B
