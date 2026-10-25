"""Run the stage follower (follow2.py) from an arbitrary symbolic configuration written in its own notation.
  python fstart.py MACHINE "CONFIG" "R2=tau,R3=8492273358844,k=3" [--stages 8] [--canon B] [--start B]
                   [--budget 150000000] [--log FILE] [--verbose]
CONFIG: the follower's printed notation (D(expr)^{expr}, (10)^k, 0^k, <junk>, ( ... )^{expr} blocks).
Parameter values: 'tau' = the universal huge residue numres.tau(e) (e from --e, default 2); a plain integer N
<= 20000 = exact; 'H:N' = huge with residue N mod QBIG.  Parameters named R* get unit 3 in the period search.
The first stage starts with the head on the blank right of the word in state --start (default = --canon)."""
import argparse
import re
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'bb10_bb7_descendants'))
import follow2 as F  # noqa: E402
from numres import Num, tau  # noqa: E402

Aff = F.Aff


def aff(expr):
    e = re.sub(r'(?<![A-Za-z_\d])(\d+)', r'_F(\1)', expr.strip())
    names = set(re.findall(r'[A-Za-z_][A-Za-z_0-9]*', e)) - {'_F'}
    env = {n: Aff(0, {n: 1}) for n in names}
    env['_F'] = Fraction
    x = eval(e, {'__builtins__': {}}, env)
    return x if isinstance(x, Aff) else Aff(x)


def parse(s):
    s = s.replace('|', ' ').replace('tail', ' ')
    pos = 0

    def count():
        nonlocal pos
        if s.startswith('^{', pos):
            j = s.index('}', pos)
            c = aff(s[pos + 2:j]); pos = j + 1
            return c
        return Aff(1)

    def seq(end):
        nonlocal pos
        out = []
        while True:
            while pos < len(s) and s[pos] == ' ':
                pos += 1
            if pos >= len(s):
                if end:
                    raise ValueError('unclosed (')
                return out
            if s[pos] == ')':
                if not end:
                    raise ValueError(f'stray ) at {pos}')
                pos += 1
                return out
            m = re.compile(r'D\(([^)]*)\)').match(s, pos)
            if m:
                pos = m.end(); v = aff(m.group(1)); out.append(('D', v, count())); continue
            m = re.compile(r'\((10|01)\)\^(\{[^}]*\}|\d+)').match(s, pos)
            if m:
                pos = m.end(); k = m.group(2)
                out.append(('R', (m.group(1), aff(k[1:-1]) if k.startswith('{') else Aff(int(k))), Aff(1))); continue
            m = re.compile(r'([01])\^(\{[^}]*\}|\d+)').match(s, pos)
            if m:
                pos = m.end(); k = m.group(2)
                out.append(('R', (m.group(1), aff(k[1:-1]) if k.startswith('{') else Aff(int(k))), Aff(1))); continue
            if s[pos] == '<':
                j = s.index('>', pos)
                ent = F.parse_items(s[pos:j + 1]); pos = j + 1
                out += F.symc(ent)
                continue
            if s[pos] == '(':
                pos += 1
                inner = seq(True)
                out.append(('B', tuple(inner), count()))
                continue
            raise ValueError(f'cannot parse at {pos}: {s[pos:pos + 40]!r}')
    return seq(False)


def accelerate(sym, params, past, log, m):
    """Loop acceleration.  If an earlier stage input (within the last 12) has the same shape and the same fields
    except (i) exactly one field that is huge and smaller by a positive constant now, and (ii) fields that are bare
    accumulator parameters (fresh R's), then the stage cycle is a loop that decrements that field.  Its value is
    replaced by the small exact value (v mod 12) + 12*m, so the follower runs only the last m*12/drop rounds
    literally-abstractly.  Returns the (possibly) modified sym."""
    sh, fl = F.shape_of(sym), F.fields_of(sym)

    def bare(x):
        x = F.A(x)
        return x.c == 0 and len(x.co) == 1 and list(x.co.values())[0] == 1

    for psh, pfl in reversed(past[-400:]):
        if psh != sh or len(pfl) != len(fl):
            continue
        cand = []
        ok = True
        for i, (x, y) in enumerate(zip(pfl, fl)):
            x, y = F.A(x), F.A(y)
            if x == y:
                continue
            if bare(x) and bare(y):
                continue
            d = y - x
            if d.is_const() and d.c < 0 and y.co and any(not params[p].exact or params[p].x > 20000 for p in y.co):
                cand.append((i, -d.c))
                continue
            ok = False
            break
        if not ok or len(cand) != 1:
            continue
        i, drop = cand[0]
        v = F.A(fl[i]).num(params)
        new = v.m(12) + 12 * m
        fl2 = list(fl)
        fl2[i] = F.Aff(new)
        sym2 = F.rebuild(sh, fl2)[0]
        log(f'  ACCEL: field {i} = {F.A(fl[i])} drops by {drop} per loop; set to {new} (same residue mod 12)')
        log(f'  accelerated config: {F.fmt_sym(sym2)}')
        return sym2
    return sym


def patch_retry(factor):
    """samples that time out (T) are retried once with factor x the budget"""
    orig = F.Stage.run_at

    def run_at(self, vals, budget=None):
        o = orig(self, vals, budget)
        if o['kind'] == 'T':
            key = (self.q,) + tuple(sorted(vals.items()))
            self.cache.pop(key, None)
            o = orig(self, vals, (budget or self.budget) * factor)
        return o
    F.Stage.run_at = run_at


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('machine')
    ap.add_argument('config')
    ap.add_argument('params')
    ap.add_argument('--stages', type=int, default=8)
    ap.add_argument('--canon', default='B')
    ap.add_argument('--start')
    ap.add_argument('--e', type=int, default=2)
    ap.add_argument('--budget', type=int, default=150_000_000)
    ap.add_argument('--log')
    ap.add_argument('--verbose', action='store_true')
    ap.add_argument('--lb', type=int, help='lower bound of representative values for R* parameters (default 200)')
    ap.add_argument('--verify', type=int, default=0, help='hyb10 -v: verified transitions needed for a champion phase (default 4)')
    ap.add_argument('--retry', type=int, default=0, help='retry timed-out samples with RETRY x budget')
    ap.add_argument('--ks', type=int, help='samples per parameter in the period search (follow2 default 22)')
    ap.add_argument('--accel', type=int, default=0,
                    help='loop acceleration: a token that drops by a constant between two equal-shape stage inputs '
                         'is set to (value mod 12) + 12*ACCEL (its huge parameter dropped); 0 = off')
    a = ap.parse_args()
    F.CANON = a.canon
    if a.verify:
        orig_rh = F.run_hyb
        F.run_hyb = lambda machine, word, maxsteps, extra=(), start=None, canon=None: orig_rh(machine, word, maxsteps, tuple(extra) + ('-v', str(a.verify)), start, canon)
    if a.retry:
        patch_retry(a.retry)
    if a.ks:
        F.KS = a.ks
    if a.lb:
        F.RANK_LB[2] = F.RANK_LB[3] = F.RANK_LB[4] = a.lb
    lf = open(a.log, 'w') if a.log else None

    def log(x):
        print(x, flush=True)
        if lf:
            lf.write(x + '\n'); lf.flush()

    params, ranks = {}, {}
    for kv in [p for p in a.params.split(',') if p]:
        k, v = kv.split('=')
        if v == 'tau':
            params[k] = tau(a.e)
        elif v.startswith('H:'):
            params[k] = Num.huge(int(v[2:]))
        else:
            params[k] = Num(int(v))
        ranks[k] = 2 if k.startswith('R') else 1
    sym = parse(a.config)
    missing = F.params_in(sym) - set(params)
    if missing:
        raise SystemExit(f'missing parameter values: {missing}')
    log(f'machine {a.machine} from {F.fmt_sym(sym)} with {params}')
    for p in params:
        F.LEVEL.setdefault(p, 0)
    stage_start = a.start or a.canon
    history = []
    past = [(F.shape_of(sym), F.fields_of(sym))]
    try:
        for s in range(a.stages):
            st = F.Stage(a.machine, sym, params, ranks, a.budget, log, a.verbose, start=stage_start)
            log(f'stage {s}: input {F.fmt_sym(sym)}')
            res = st.run()
            if res['kind'] == 'H':
                log(f'  HALT (period {res["period"]}): ones = {res["ones"]}, state {res["halt_state"]}')
                history.append(('H', str(res['ones'])))
                break
            if res['kind'] != 'J':
                log(f'  outcome {res["kind"]} at {res["vals"]}: {res["out"]["raw"][:400]}')
                history.append((res['kind'],))
                break
            e = res['e']
            log(f'  champion phase (period {res["period"]}, e={e}): {F.fmt_sym(res["left"])} | tail {F.fmt_sym(res["tail"])}')
            ok, seq = F.rule_check(a.machine, res['out']['tail_c'], e, st.q)
            log(f'  rule check: {"PASS" if ok else "FAIL"} ({seq})')
            if not ok:
                history.append(('RULES-FAIL',))
                break
            ev_sym, params2, info = F.jump(res['left'], res['tail'], params, e)
            for p in params2:
                if p not in ranks:
                    ranks[p] = 2
            newp = {k: str(v) for k, v in params2.items() if k not in params}
            params = params2
            log(f'  jump -> event {info["event"]}, huge-length list cleared: {info["huge_depth"]}; level {info.get("level", 0)}; new {newp}')
            log(f'  event config: {F.fmt_sym(ev_sym)}')
            history.append(('J', info['event'], info['huge_depth']))
            if a.accel:
                ev_sym = accelerate(ev_sym, params, past, log, a.accel)
            past.append((F.shape_of(ev_sym), F.fields_of(ev_sym)))
            sym = ev_sym
            stage_start = st.q
    except F.Fail as ex:
        log(f'RESULT FAIL {ex}')
        return
    log(f'RESULT {history}')


if __name__ == '__main__':
    main()
