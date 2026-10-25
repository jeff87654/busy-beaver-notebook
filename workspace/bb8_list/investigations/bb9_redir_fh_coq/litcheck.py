"""literal check: from symbolic start (instantiated), does the machine pass through each target config (exact)?"""
from inst import word, sim
def key_of(cfg, vals):
    w, hp, q = word(cfg, vals)
    l = w.find('1'); r = w.rfind('1')
    return (w[l:r + 1], hp - l, q)
def passes(start, svals, targets, maxsteps=300000):
    s = sim(start, svals)
    want = {}
    for lab, c, v in targets:
        k = key_of(c, v); want[k] = lab
    states = {k[2] for k in want}
    lens = {len(k[0]) for k in want}
    found = {}
    for _ in range(maxsteps):
        if s.q in states:
            t = s.t
            l = t.find(1); r = t.rfind(1)
            if l >= 0 and (r - l + 1) in lens:
                k = (bytes(t[l:r + 1]).translate(bytes.maketrans(b'\x00\x01', b'01')).decode(), s.pos - l, s.q)
                if k in want and want[k] not in found:
                    found[want[k]] = s.steps
                    if len(found) == len(want): break
        if not s.step(): break
    return {lab: found.get(lab) for lab, _, _ in targets}
