"""Triage of the radius-3 directed search (dlnbr.exe): which CHECK machines could meet their halting boundary?

  python triage.py            reads all_rows.tsv (the rows of part_*.tsv), writes triage.tsv

For each machine graded CHECK:
- equivalence to a known machine (dedup.py: relabeling / start swap);
- kfit.py's full fit on the key (1,000,000-step probes), including R4 and the halting boundary;
- a literal run from the blank tape (3,000,000 steps): does it halt, does it enter the family, and do the fitted
  rules predict every literal successor;
- a rule-level run from the first family configuration (R1 applied `a` times at once) until it halts, leaves the
  fitted rules, or the numbers get too large.
Machines with the same key, rules and first family configurations are one group.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / 'investigations' / 'neighbors_family_tools'))
sys.path.insert(0, str(ROOT))
import dedup  # noqa: E402
import kfam  # noqa: E402
import kfit  # noqa: E402
from tmlit import Sim  # noqa: E402

LITERAL_STEPS = 3_000_000
MAX_ITERS = 300_000


def mirror(tm):
    return tm.translate(str.maketrans('LR', 'RL'))


def rule_run(P, ds, a, b):
    """Rule-level run. Returns (outcome, iterations, resets with k >= 1 seen, description)."""
    resets = []
    for it in range(MAX_ITERS):
        if a >= 1:
            if P['m1'] == 1:
                b += P['c1'] * a
            else:
                pw = P['m1'] ** a
                b = pw * b + P['c1'] * (pw - 1) // (P['m1'] - 1)
            a = 0
        k = kfam.trailing_zeros(ds)
        if ds and 1 <= k < len(ds) and len(resets) < 8:
            resets.append((k, b if b < 10 ** 9 else '2^%d' % b.bit_length()))
        try:
            p = kfit.predict(P, ds, 0, b)
        except KeyError as e:
            return 'no rule (%s)' % e.args[0], it, resets, kfam.show((ds, 0, b if b < 10 ** 9 else -1))
        if p is None:
            return 'k > kh (unpredicted)', it, resets, 'digits %d, k %d, b %s' % (len(ds), k, b if b < 10 ** 9 else 'huge')
        if p[0] == 'HALT':
            return 'HALT', it, resets, 'digits %d, k %d, b %s' % (len(ds), k, b if b < 10 ** 9 else '2^%d' % b.bit_length())
        ds, a, b = p[1]
        if b.bit_length() > 20000 or a.bit_length() > 20000 or len(ds) > 5000:
            return 'too large', it, resets, 'digits %d, b bits %d' % (len(ds), b.bit_length())
    return 'no halt in %d iterations' % MAX_ITERS, MAX_ITERS, resets, 'digits %d' % len(ds)


def examine(tm0, key):
    o, q, suf, u, sep = key.split(',')
    tm = mirror(tm0) if o == 'L' else tm0
    kfam.ENC = (u, sep)
    kfam.set_shape(q, suf)
    P, raw = kfit.fit(tm, 10 ** 6)
    rules = kfit.rule_text(P)
    # literal run from the blank tape
    s = Sim(tm, size=1 << 20)
    seq, lit = [], 'no halt in %d steps' % LITERAL_STEPS
    while s.steps < LITERAL_STEPS and len(seq) < 40:
        r = kfam.run_from(s, LITERAL_STEPS - s.steps)
        if r[0] == 'HALT':
            lit = 'HALTS at step %d (sigma %d)' % (r[1], s.ones())
            break
        if r[0] != 'K':
            break
        seq.append(r[2])
    bad = 0
    full = all(k in P for k in ('m1', 'm2', 'm3', 'mh'))
    if full:
        for c0, c1 in zip(seq, seq[1:]):
            try:
                p = kfit.predict(P, *c0)
            except KeyError:
                p = None
            if p is None or p[0] != 'K' or p[1] != c1:
                bad += 1
    if not seq:
        return rules, lit, 'never enters the family', '', ''
    fam = '%d family configs, %d rule mismatches; first %s' % (len(seq), bad, kfam.show(seq[0]))
    if not full:
        return rules, lit, fam, 'kfit did not confirm R1-R3-H', ''
    out, it, resets, desc = rule_run(P, *seq[0])
    return rules, lit, fam, '%s after %d iterations (%s)' % (out, it, desc), 'resets (k,b): %s' % resets


def main():
    rows = [l.split('\t') for l in (HERE / 'all_rows.tsv').read_text().splitlines() if l.strip()]
    check = [r for r in rows if r[1] == 'CHECK']
    known = dedup.check([r[0] for r in check])
    groups = {}
    with open(HERE / 'triage.tsv', 'w', newline='\n') as f:
        f.write('machine\tedits\tkey\tknown_equivalent\trules\tliteral\tfamily\trule_level\tresets\n')
        for i, r in enumerate(check):
            tm, _, key, params, edits = r[:5]
            try:
                res = examine(tm, key)
            except Exception as e:  # keep going: one odd machine must not stop the triage
                res = ('error: %r' % (e,), '', '', '', '')
            f.write('\t'.join([tm, edits, key, known[tm] or '-', *res]) + '\n')
            f.flush()
            groups.setdefault((key, res[0], res[1], res[3]), []).append(tm)
            print(i + 1, len(check), tm, res[1], '|', res[3], flush=True)
    print('\n%d CHECK machines in %d groups' % (len(check), len(groups)))
    for (key, rules, lit, rl), ms in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        print('%4d  %s  %s\n      literal: %s; rule level: %s\n      e.g. %s' % (len(ms), key, rules, lit, rl, ms[0]))


if __name__ == '__main__':
    main()
