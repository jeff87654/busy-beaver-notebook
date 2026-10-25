"""Growth special P2 with the REAL size order (parked P >> transit R): [2^11,5,1^43,0^3,1,P,0,1^w | R]."""
import sys
from n1sim import literal, flab
from btrace import parse_list
for spec in sys.argv[1:]:
    ts, R = spec.rsplit(':', 1)
    L = parse_list(ts); R = int(R)
    kind, res, st, evs = literal('', L, R, 3 * 10 ** 10)
    print(flab('', L, R)[:120], '->', kind, (flab(*res)[:200] if kind == 'B' else str(res)[:300]), st, len(evs), flush=True)
