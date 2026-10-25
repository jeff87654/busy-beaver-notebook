"""echeck.py: literal check of the exhaustion map far beyond the fitted windows, at the classes the real run uses.
  python echeck.py IN.jsonl[,IN2] OUT.tsv [--only M] [--B 2000] [--k 3]
For each row with an E map: for every class c actually visited in the residue rounds (trace), probe the exhaustion
literally at k values b = c (mod p) near B (and near 4B) and compare with the fitted class rule (H / rebuilt list
structure / a / b). Mismatch -> the E map does not extrapolate."""
import idle  # noqa: F401
import json
import os
import re
import sys

import fit7
import rounds7  # noqa: F401


def expect(rule, V, p, c):
    if rule[0] != 'K':
        return (rule[0],)
    d = rule[1]
    t = (V - c) // p
    if 'fixed' in d:
        ds = [e[0] * t + e[1] for e in d['fixed']]
    else:
        ds = d['pre'] + [d['mid']] * (d['cnt'][0] * t + d['cnt'][1]) + d['suf']
    return ('K', ds, d['a'][0] * t + d['a'][1], d['b'][0] * t + d['b'][1])


def main():
    ins = sys.argv[1].split(',')
    out = sys.argv[2]
    only = sys.argv[sys.argv.index('--only') + 1] if '--only' in sys.argv else None
    B = int(sys.argv[sys.argv.index('--B') + 1]) if '--B' in sys.argv else 2000
    K = int(sys.argv[sys.argv.index('--k') + 1]) if '--k' in sys.argv else 3
    rows = [json.loads(l) for fn in ins for l in open(fn)]
    with open(out, 'a', newline='\n') as fo:
        for r in rows:
            if only and r['machine'] != only:
                continue
            if 'rules' not in r or not r.get('rounds'):
                continue
            P = fit7.Prober(r['machine'], r['tmpl'])
            # rebuild the E map as used (marker: E0 at nE; else E at n0) from the stored rule string is lossy:
            # refit quickly with the same procedure
            R = fit7.fit_rules(P)
            import reb7
            if r.get('marker'):
                n = r.get('nE', 0)
            elif P.Pempty:
                n = 0
            else:
                n = r['last_K'][2]
            _, E = reb7.fit_E2(P, R, n, 60)
            if E is None:
                continue
            p, cls = E
            tr = r['rounds'].get('80640', ['', []])[1]
            visited = set()
            for x in tr:
                if isinstance(x, list) and len(x) == 3 and isinstance(x[2], list):
                    for b in x[2]:
                        mm = re.search(r'class (\d+)', b)
                        if mm:
                            visited.add(int(mm.group(1)))
            if not visited:
                visited = set(range(p))
            res = []
            for c in sorted(visited):
                for base in (B, 4 * B):
                    bs = [base + ((c - base) % p) + p * i for i in range(K)]
                    lit = P.probe([([0] * n if not P.Pempty else [], 0, b) for b in bs], N=400000000)
                    for b, L in zip(bs, lit):
                        e = expect(cls[c], b, p, c)
                        if L[0] != e[0]:
                            ok = False
                        elif L[0] == 'K':
                            ok = (fit7.norm(L[1], P.Pempty) == fit7.norm(e[1], P.Pempty) and L[2] == e[2] and L[3] == e[3])
                        else:
                            ok = True
                        res.append('c%d b=%d %s' % (c, b, 'ok' if ok else 'MISMATCH lit=%s exp=%s' % (
                            (L[0], len(L[1]) if L[0] == 'K' else '', L[2:4] if L[0] == 'K' else ''),
                            (e[0], len(e[1]) if e[0] == 'K' else '', e[2:4] if e[0] == 'K' else ''))))
            bad = [x for x in res if 'MISMATCH' in x]
            fo.write('%s\t%s\t%s\t%s\n' % (r['machine'], 'OK' if not bad else 'MISMATCH', len(res), '; '.join(bad[:4]) or '-'))
            fo.flush()
            print(r['machine'], 'OK' if not bad else 'MISMATCH', len(res), bad[:2], flush=True)


if __name__ == '__main__':
    main()
