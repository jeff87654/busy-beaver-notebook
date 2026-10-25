"""literal check: from symbolic start S (instantiated), does the machine pass through each target config (exact tape+head+state)?"""
from inst import word, sim
def key_of(cfg, vals):
    w, hp, q = word(cfg, vals)
    # normalise: strip zeros, record head offset relative to first 1
    l = w.find('1'); r = w.rfind('1')
    return (w[l:r + 1], hp - l, q)
def passes(start, svals, targets, maxsteps=10**6):
    """targets: list of (label, cfg, vals); returns dict label -> step or None"""
    s = sim(start, svals)
    want = {key_of(c, v): lab for lab, c, v in targets}
    found = {}
    for _ in range(maxsteps):
        st, l, r = s.word()
        if l >= 0:
            k = (st[l:r + 1], s.pos - l, s.q)
            if k in want and want[k] not in found:
                found[want[k]] = s.steps
                if len(found) == len(want): break
        if not s.step(): break
    return {lab: found.get(lab) for lab, _, _ in targets}
