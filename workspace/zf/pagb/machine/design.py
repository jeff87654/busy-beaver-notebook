"""The chosen PA design: formula ASTs of the AX roots (PRE = before the param2 read, ROWS, BUNDLE).

The choice (row order, labels, ...) is read from design_choice.json (written from the search).
Env var PA_VARIANT selects a variant:  'ng' (default, NG axiom)  or  'ctl' (positive control: NG
replaced by the refutable open sentence CTL, see DESIGN.md).

python design.py      writes source_pa[_ctl].py and pa[_ctl]_wade.tm and prints the state count.
"""
import os, json
HERE = os.path.dirname(os.path.abspath(__file__))
from pagen import *

DESIGN = os.environ.get('PA_DESIGN', 'A')   # 'A' (chosen: functional terms, var constructor) | 'flat' | 'nested' (UNSOUND, record only)
VARIANT = os.environ.get('PA_VARIANT', 'ng')
if DESIGN == 'A':
    import search_a as SR
    _ng = lambda ch: SR.ng_of(ch)
elif DESIGN == 'nested':
    import search_nest as SR
    _ng = lambda ch: SR.ng(ch)
else:
    import search_pa as SR
    _ng = lambda ch: SR.P.ng2(*ch['nglab'])
_path = os.path.join(HERE, f'design_choice_{DESIGN}.json')
CHOICE = json.load(open(_path)) if os.path.exists(_path) else SR.default_choice()

PRE, ROWS, BUNDLE = SR.assemble(CHOICE)
VAC = CHOICE.get('vac', 'pinned')
GATE = {'pinned': 'ab', 'b': 'abu', 'a': 'occ'}[VAC]     # gate condition, see DESIGN.md §2
NG_INDEX = None
for _i, _r in enumerate(ROWS):
    if _r == _ng(CHOICE):
        NG_INDEX = _i

# positive control: NG replaced by "x = 0 ∧ x = σy" (open; refuted by one MP with zero_succ)
if DESIGN == 'A':
    # "∀y 0 = σy" (open): refuted by one MP with zero_succ.  With pinned Q rows zero_succ is over v0.
    CTL = ('teq', 'Z0', ('S1', ('V', '0' if CHOICE.get('qpin') else 'b')))
elif DESIGN == 'nested':
    CTL = an(('eq', 'a', Z), ('eq', 'a', S('b')))
else:
    CTL = an(rel('a', Z), rel('a', S('b')))
if VARIANT == 'ctl':
    ROWS = list(ROWS); ROWS[NG_INDEX] = CTL

SUFFIX = ('' if DESIGN == 'A' else '_' + DESIGN) + ('' if VARIANT == 'ng' else '_' + VARIANT)

def build_files():
    SR.assemble(CHOICE)                                      # sets pagen.REG4 / pagen.OCC for this choice
    toks = tokens(PRE, ROWS, BUNDLE)
    gen_source('pa' + SUFFIX, toks)
    z, ns = compile_source('pa' + SUFFIX)
    tmp = os.path.join(HERE, f'pa{SUFFIX}_wade.tm')
    z.tm.save(tmp)
    raw = open(tmp, 'rb').read().replace(bytes([13, 10]), bytes([10]))     # published .tm is LF-only
    open(tmp, 'wb').write(raw)
    return ns, len(toks)

if __name__ == '__main__':
    ns, nt = build_files()
    print(f'variant {VARIANT}: tokens {nt} states {ns}; rows {len(ROWS)}; NG at row {NG_INDEX}')
