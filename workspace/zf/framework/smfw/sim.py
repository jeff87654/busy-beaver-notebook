"""Tiny TM simulator for SMFW .tm fragments, with exit detection.

.tm line: "state read write dir next".  A fragment EXITS when it transitions to one of the
framework sinks, which we do NOT execute (B2 is the data side; the IP arithmetic of
6.break/5.root is B3's job):
    6.break.0  -> outcome 'adv'     (advance)
    6.break.1  -> outcome 'zero'    (decnz-style zero branch)
    5.root     -> outcome 'end'     (RB END: restart main)
    halt       -> outcome 'halt'    (CHECK success = undefined transition / explicit 'halt')
On an undefined transition the sim returns outcome 'halt' (undefined = halt, per SM_SPEC CHECK).
"""
SINKS = {'6.break.0': 'adv', '6.break.1': 'zero', '5.root': 'end', 'halt': 'halt'}

def load(paths):
    tbl = {}
    for p in paths:
        for l in open(p, encoding='utf-8'):
            l = l.split('#', 1)[0].strip()
            if not l or l.startswith('#!'):
                continue
            s, r, w, d, n = l.split()
            tbl[(s, r)] = (w, d, n)
    return tbl

def run(tbl, tape, state, pos, maxsteps=2_000_000):
    """tape: dict pos->'0'/'1'.  Returns (outcome, tape, pos, steps)."""
    for steps in range(maxsteps):
        if state in SINKS:
            return SINKS[state], tape, pos, steps
        t = tbl.get((state, tape.get(pos, '0')))
        if t is None:
            return 'halt', tape, pos, steps
        w, d, n = t
        tape[pos] = w
        pos += 1 if d == 'R' else -1
        state = n
    raise RuntimeError('step limit from state %s' % state)
