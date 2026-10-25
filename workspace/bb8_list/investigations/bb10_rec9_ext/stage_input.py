"""Replay a machine's cached fext stages from c_end and write the concrete tape of the stage-N input for given
parameter values (hyb10 dump format: first line "STATE HEAD").
Usage: python stage_input.py MACHINE N OUTFILE R1=v R2=v ...   (parameters not given take their exact value or
       the smallest representative >= 30 in their real residue class mod 30)"""
import pickle
import sys
from pathlib import Path

import fext
from fext import CACHE, advance, cend_input, fmt_sym
import follow3 as F
from numres import tau

HERE = Path(__file__).resolve().parent


def replay(machine, n, log=lambda s: None):
    CACHE.update(pickle.loads((HERE / 'logs' / f'cache_{machine}.pkl').read_bytes()))
    t = tau()
    params = {'R1': t, 'R2': t}
    ranks = {'R1': 2, 'R2': 3}
    F.LEVEL.clear()
    F.LEVEL.update({'R1': 0, 'R2': 1})
    sym, start = cend_input(), 'A'
    for s in range(n):
        out = advance(machine, sym, params, ranks, start, 200_000_000, log, False, quiet=True)
        if out['kind'] != 'J':
            raise SystemExit(f'stage {s}: {out["kind"]}')
        sym, params, start = out['sym'], out['params'], out['start']
    return sym, params, start


def main():
    machine, n, outf = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    given = dict(kv.split('=') for kv in sys.argv[4:])
    sym, params, start = replay(machine, n)
    vals = {}
    for p in F.params_in(sym):
        if p in given:
            vals[p] = int(given[p])
        elif params[p].exact and params[p].x <= 20000:
            vals[p] = params[p].x
        else:
            vals[p] = 30 + (params[p].m(30) - 30) % 30
    print('stage input:', fmt_sym(sym))
    print('values:', vals, 'state', start)
    w = F.word_of(F.inst(sym, vals))
    Path(outf).write_text(f'{start} {len(w)}\n{w}\n')
    print('word length', len(w))


if __name__ == '__main__':
    main()
