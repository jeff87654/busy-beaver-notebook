"""mfx.py: two-representative mini-follower screen (wraps halt_redirect/mf/mf35g.py, read-only).
follow(): copy of mf35g.follow with the representative floor LB as a parameter.
screen(fam, machine): run A (M=2520, LB=19) and run B (M=36, LB=60) from the same start (b0); a stage whose cleared
list length (zeros=) differs between A and B cleared a list built from a huge value = a full (omega-level) cycle.
Returns dict(kind, stages, cycles, grow, histA, histB)."""
from __future__ import annotations
import sys
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/halt_redirect/mf')
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/bb9_engines1')
import mf35, mf35g
from follow2 import Aff, Fail, jump


def follow(fam, machine, stages, maxs, b0, M, LB, ordered=False, verbose=False, start=None, gtop0=0):
    F = mf35g.FAMILIES[fam]
    E = F['E']
    word, head, state = start if start else mf35g.xstart(fam, b0)
    hist, sigs = [], []
    gtop = gtop0
    for s in range(stages):
        out = mf35g.run_stage(fam, machine, word, head, state, maxs)
        if not out:
            return 'FAIL', hist + ['no output']
        f = out.split()
        if f[0] == 'H':
            hist.append(f'H {f[2]}{f[3]} ones={f[4]}')
            return 'HALT', hist
        if f[0] in ('T', 'W'):
            hist.append(f[0])
            return {'T': 'TIME', 'W': 'WIDE'}[f[0]], hist
        if f[0] != 'J':
            return 'FAIL', hist + [out[:100]]
        parts = out.split('|')
        toks = [int(x) for x in parts[1].split()]
        far = parts[2].strip() if len(parts) > 2 else ''
        digits = toks[2:][::-1]
        ent = []
        for m in digits:
            if ent and ent[-1][1] == m:
                ent[-1][2] += 1
            else:
                ent.append(['D', m, 1])
        left = [('D', Aff(m), Aff(c)) for _, m, c in ent] + [('D', Aff(toks[1]), Aff(1)), ('D', Aff(toks[0]), Aff(1))]
        try:
            items, newp, info = jump(left, [], {}, E)
        except (Fail, AssertionError, RuntimeError, RecursionError) as ex:
            hist.append(f'J k={len(digits)} JUMPFAIL {ex}')
            return 'FAIL', hist
        if ordered:
            # every new huge value gets a representative above twice every number on the tape (real runs: R1 << R2 << ...)
            top = max([LB, gtop, len(far)] + toks)
            vals = {}
            for p, v in newp.items():
                lb = 2 * top + 40
                vals[p] = mf35.rep(v, M, lb) if not (v.exact and v.x <= 2000) else v.x
                top = max(top, vals[p])
            gtop = top
        else:
            vals = {p: mf35.rep(v, M, LB) for p, v in newp.items()}
        new = []
        for e in items:
            m = e[1].at(vals) if isinstance(e[1], Aff) else int(e[1])
            c = e[2].at(vals) if isinstance(e[2], Aff) else int(e[2])
            new += [m] * c
        if len(new) >= 2 and new[-1] > 2000 and not ordered:
            new[-1] = LB + ((new[-1] - LB) % M)
        nz = 0
        for m in new[:-2][::-1]:
            if m != 1:
                break
            nz += 1
        hist.append(f'J k={len(digits)} far={"junk" if far else "clean"} ev={info.get("event")} zeros={nz} '
                    f'r={",".join(str(v) for v in vals.values())}')
        if verbose:
            from eng import tokens, tokstr
            print(s, hist[-1], '\n    list:', mf35.rle(new), '\n    far:', tokstr(tokens(far))[:300], flush=True)
        word = far + mf35.word_of_tokens(new) + F['SUF']
        head, state = len(word), F['Q']
        blocks = []
        for m in new:
            if blocks and blocks[-1][0] == m:
                blocks[-1][1] += 1
            else:
                blocks.append([m, 1])
        sigs.append((tuple(x[0] for x in blocks), tuple(x[1] for x in blocks) + (len(far),)))
        p = mf35.affine_period(sigs)
        if p:
            hist.append(f'LOOP p={p}')
            return 'LOOP', hist
    return 'MAXSTAGES', hist


def zs(h):
    return [mf35.zeros_of(x) for x in h if x.startswith('J')]


def screen(fam, machine, stages=16, maxs=3_000_000, b0=6):
    m10 = machine + '_------' * (9 - machine.count('_'))
    try:
        ka, ha = follow(fam, m10, stages, maxs, b0, 2520, 19)
        kb, hb = follow(fam, m10, stages, maxs, b0, 36, 60)
    except Exception as ex:
        return dict(kind='CRASH', stages=0, cycles=0, grow=0, histA=[repr(ex)[:200]], histB=[])
    za, zb = zs(ha), zs(hb)
    cyc = sum(1 for x, y in zip(za, zb) if x != y)
    # growing periods: stages where the run-A cleared length exceeds every earlier one and depends on a huge value
    grow, best = 0, -1
    for x, y in zip(za, zb):
        if x is None:
            continue
        if x != y and x > best:
            grow += 1
        best = max(best, x)
    return dict(kind=ka, kindB=kb, stages=len(za), cycles=cyc, grow=grow, histA=ha, histB=hb)
