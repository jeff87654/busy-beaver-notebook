"""engslots.py: for each champion-faithful group representative, the slots used by the pure champion engine
(literal run of K(2,2,2,2; 2; 2) for 3e6 steps, still inside the engine) versus the slots used by the follower's
literal stages (rebuild/exhaustion), from logs/<m>_b6.json.  Slots used ONLY outside the engine are the ones a
radius-1 change could redirect without disturbing the f_omega engine."""
import json, sys
from tm import parse, kword
SL = ['A0','A1','B0','B1','C0','C1','D0','D1','E0','E1','F0','F1','G0','G1','H0','H1','I0','I1']
def engine_slots(m, maxs=3_000_000):
    T, n = parse(m)
    w = kword([2, 2, 2, 2], 2, 2)
    tape = {i: 1 for i, ch in enumerate(w) if ch == '1'}
    pos = len(w); q = 1; used = set()
    for s in range(maxs):
        c = tape.get(pos, 0); used.add(SL[2 * q + c])
        t = T.get((q, c))
        if t is None: return used, f'H{s}'
        if t[0]: tape[pos] = 1
        else: tape.pop(pos, None)
        pos += t[1]; q = t[2]
    return used, 'ok'
for m in sys.argv[1:]:
    eng, st = engine_slots(m)
    d = json.load(open(f'logs/{m}_b6.json'))
    stage = set()
    for h in d['hist']:
        stage |= {SL[i] for i in range(18) if h['U'] >> i & 1}
    print(m, st, 'engine:', ','.join(s for s in SL if s in eng), '| only outside engine:', ','.join(s for s in SL if s in stage - eng) or '-')
