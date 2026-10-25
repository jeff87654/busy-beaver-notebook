import sys
sys.path.insert(0,'../neighbors_family_tools')
from tmlit import Sim, ST
from fam import TM, parse

def build(ds, a, b):
    """actual machine tape word right of the head cell: reverse(K); ds farthest-first as in the printed lists"""
    K = '111' + ''.join('10'*d + '11' for d in ds) + '10'*a + '11' + '10'*(2*b+1) + '11'
    # wait: K = 111 (10)^d1 11 ... : each digit followed by 11; then a, 11, then Brun, 11
    return K

def build2(ds, a, b):
    K = '111'
    for d in ds:
        K += '10'*d + '11'
    K += '10'*a + '11' + '10'*(2*b+1) + '11'
    return K

def sim_from(ds, a, b, maxsteps=2000000):
    K = build2(ds, a, b)
    w = '0' + K[::-1]       # head cell then the word
    s = Sim.from_word(TM, w, 0, 'A', size=1<<14)
    return s

def next_family(ds, a, b, maxsteps=2000000, need_odd=True):
    s = sim_from(ds, a, b)
    # skip the starting position
    while s.steps < maxsteps:
        if not s.step():
            return ('HALT', s.steps, s.show()[:80])
        if ST[s.state] == 'A' and not any(s.tape[s.lo:s.pos]) and s.tape[s.pos] == 0:
            w = ''.join(map(str, s.tape[s.pos+1:s.hi+1])).rstrip('0')
            r = parse(w[::-1])
            if r is not None and r[-1] % 2 == 1 and len(r) >= 2 and r[-1] >= 1:
                return (s.steps, r[:-2], r[-2], (r[-1]-1)//2)
    return ('TIMEOUT',)

if __name__ == '__main__':
    for k in range(0, 8):
        for b in range(1, 6):
            print('k=%d b=%d' % (k, b), next_family([0]*k, 0, b))
