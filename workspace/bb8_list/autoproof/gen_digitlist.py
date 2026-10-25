"""End-to-end generator: a complete busycoq non-halting proof for a digit-list machine of the DigitListOnes class.

  python gen_digitlist.py SPEC.json OUT.v

SPEC (machine coordinates; the head sits at the blank cell left of the word, the blank tape is on the left):
  {"tm": "...", "q": "A",            head state of the family
   "P": [0,1,1,1],                   cells between the head and the accumulator (the head reads P[0])
   "u": [0,1],                       digit unit; digits and counters are u^n, each preceded by one separator 0
   "c1": 1,                          R1: b -> b + c1
   "c2": 2,                          R2: Kc (S y :: t) 0 (S r) -> Kc (y :: t) (r + c2) 0
   "c3": 1, "a3": 1,                 R3: refill digit S (r + c3), inner counter a3, accumulator 0
   "top": [m, c, extra], "a4": 1,    R4: Kc (0^k) 0 (S b) -> Kc (1^(m b + c) ++ extra) a4 0
   "init": n}                        literal steps from the blank tape to a family configuration (found here)
  Kc ds a b = (const 0) {{q}}> (P >> u^^b *> 0 >> u^^a *> rgt ds),  rgt (d :: t) = 0 >> u^^d *> rgt t.
The machine-level rules are found and proved by engine.py / coqgen.py (symbolic execution, automatic loop lemmas);
the invariant is the abstract theorem DigitListOnes.dl_nonhalt.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import planner8 as pl
from planner8 import BLANK, mkrun, V
import engine
import coqgen
import coqgen_util


def kc_tokens(spec, b_cnt, a_cnt, digits, rest):
    """Planner right side of Kc. b_cnt / a_cnt: (dict, const); digits: list of (dict, const), nearest first."""
    u = tuple(spec['u'])
    toks = list(spec['P']) + mkrun(u, *b_cnt) + [0] + mkrun(u, *a_cnt)
    for d in digits:
        toks += [0] + mkrun(u, *d)
    return toks + rest


def cfg(spec, toks):
    return (spec['q'], [BLANK], pl.norm_side(toks), '>')


def rules(spec):
    """(name, start, target, quantifiers in Kc terms) for R1..R4 at machine level."""
    T = [0, V('t')]
    c1, c2, c3, a3, a4 = spec['c1'], spec['c2'], spec['c3'], spec['a3'], spec['a4']
    m4, k4, extra = spec['top']
    out = []
    # R1: Kc ds (S a) b -> Kc ds a (b + c1), with rgt ds = 0 >> t
    out.append(('R1m', cfg(spec, kc_tokens(spec, ({'b': 1}, 0), ({'a': 1}, 1), [], T)),
                cfg(spec, kc_tokens(spec, ({'b': 1}, c1), ({'a': 1}, 0), [], T))))
    # R2: Kc (S y :: t') 0 (S r) -> Kc (y :: t') (r + c2) 0, with rgt t' = 0 >> t
    out.append(('R2m', cfg(spec, kc_tokens(spec, ({'r': 1}, 1), ({}, 0), [({'y': 1}, 1)], T)),
                cfg(spec, kc_tokens(spec, ({}, 0), ({'r': 1}, c2), [({'y': 1}, 0)], T))))
    # R3: Kc (0^(S k) ++ S y :: t') 0 (S k + S r) -> Kc (1^k ++ S (r + c3) :: y :: t') a3 0
    zeros = [0] + mkrun((0,), {'k': 1})      # the S k zero digits: rgt gives one 0 per zero digit
    u = tuple(spec['u'])
    start3 = list(spec['P']) + mkrun(u, {'k': 1, 'r': 1}, 2) + [0] + zeros + [0] + mkrun(u, {'y': 1}, 1) + T
    tgt3 = list(spec['P']) + [0] + mkrun(u, {}, a3) + mkrun((0,) + u, {'k': 1}) + [0] + mkrun(u, {'r': 1}, c3 + 1) \
        + [0] + mkrun(u, {'y': 1}) + T
    out.append(('R3m', cfg(spec, start3), cfg(spec, tgt3)))
    # R4: Kc (0^k) 0 (S b) -> Kc (1^(m4 b + k4) ++ extra) a4 0   (rgt of zero digits is the blank)
    start4 = list(spec['P']) + mkrun(u, {'b': 1}, 1) + [0] + [BLANK]
    assert m4 == 1, 'top must be 1^(k4 + b) ++ extra'
    tgt4 = list(spec['P']) + [0] + mkrun(u, {}, a4) + mkrun((0,) + u, {'b': 1}, k4)
    for d in extra:
        tgt4 += [0] + list(u) * d
    tgt4 += [BLANK]
    out.append(('R4m', cfg(spec, start4), cfg(spec, tgt4)))
    return out


def find_init(spec, max_steps=200000):
    """First configuration on the literal run from the blank tape that is a family configuration Kc ds a b with
    no zero digit and a + b >= 1. Returns (steps, ds, a, b)."""
    sys.path.insert(0, str(HERE.parent / 'investigations' / 'neighbors_family_tools'))
    from tmlit import Sim, ST
    P, u = list(spec['P']), list(spec['u'])
    s = Sim(spec['tm'], size=1 << 16)
    for n in range(max_steps):
        if ST[s.state] == spec['q'] and not any(s.tape[s.lo:s.pos]):
            w = list(s.tape[s.pos:s.hi + 1])
            while w and w[-1] == 0:
                w.pop()
            r = parse_word(w, P, u)
            if r and all(d > 0 for d in r[0]) and r[1] + r[2] >= 1:
                return (n,) + r
        if not s.step():
            raise SystemExit('the machine halts before reaching the family')
    raise SystemExit('no family configuration found')


def parse_word(w, P, u):
    """w = P u^b 0 u^a (0 u^d)* ; returns (ds, a, b) or None."""
    if w[:len(P)] != P:
        return None
    i, runs = len(P), []
    while True:
        n = 0
        while w[i:i + len(u)] == u:
            i += len(u); n += 1
        runs.append(n)
        if i >= len(w):
            break
        if w[i] != 0:
            return None
        i += 1
    if len(runs) < 2:
        return None
    b, a, ds = runs[0], runs[1], runs[2:]
    return ds, a, b


def main():
    spec = json.loads(Path(sys.argv[1]).read_text())
    outp = Path(sys.argv[2])
    TM = spec['tm']
    pl.set_tm(TM)
    pl.LEMMAS.clear()
    lemmas, rule_texts = [], []
    for name, start, target in rules(spec):
        tree = engine.explore(start, target)
        gen = coqgen.RuleGen(name, engine)
        rule_texts.append(coqgen.rule_lemma(name, start, target, tree, gen))
        lemmas.extend(gen.lemmas)
        print('  %s: proof tree found' % name, file=sys.stderr)
    nstates = len(TM.split('_'))
    head = (HERE / 'header.v.in').read_text().replace('@TITLE@', spec.get('title', TM + ' never halts')) \
        .replace('@N@', str(nstates)).replace('@TM@', TM).replace('@TABLE@', coqgen_util.table(TM))
    fam = (HERE / 'family_ones.v.in').read_text()
    u = spec['u']
    P = spec['P']
    m4, k4, extra = spec['top']
    sub = {
        '@Q@': spec['q'], '@U@': coqgen.cl(u), '@P@': ''.join('%d >> ' % x for x in P),
        '@ONE@': coqgen.cl([0] + u), '@C1@': str(spec['c1']), '@C2@': str(spec['c2']), '@C3@': str(spec['c3']),
        '@A3@': str(spec['a3']), '@A4@': str(spec['a4']),
        '@TOP@': '(repeat 1%%nat (%d + b) ++ %s)' % (k4, '[' + '; '.join('%d%%nat' % d for d in extra) + ']'),
    }
    n, ds, a, b = find_init(spec)
    print('  init: Kc %s %d %d after %d steps' % (ds, a, b, n), file=sys.stderr)
    dsl = '(@nil nat)' if not ds else '[%s]' % '; '.join('%d%%nat' % d for d in ds)
    sub['@INITPROOF@'] = ('exists %s, %d%%nat, %d%%nat. split; [| split; [repeat constructor; lia | lia]].\n'
                          '  unfold Kc. simpl. execute.' % (dsl, a, b))
    for k, v in sub.items():
        fam = fam.replace(k, v)
    text = head + '\n(** ** Crossing lemmas (generated) *)\n\n' + coqgen.crossing_lemmas() \
        + '\n(** ** Stage and loop lemmas (generated) *)\n\n' + '\n'.join(lemmas) \
        + '\n(** ** Machine-level rules (generated) *)\n\n' + '\n'.join(rule_texts) + '\n' + fam
    outp.write_text(text, newline='\n')
    print('wrote', outp, file=sys.stderr)


if __name__ == '__main__':
    main()
