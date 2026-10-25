"""towercls.py MACHINE TEMPLATE : refit the base's K-rules (reb7 fit7) and compute the residues of deep clearing
results with the eng7 residue engine.  Prints JSON {tmpl, rules, vals:[[cfg, value]], cls720: sorted set of residues
mod 720 of Huge values, const: bool}."""
import sys, json, time
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7')
import fit7, eng7
import reb7
def towercls(m, tmpl, Q=80640, M=720):
    out = {'machine': m, 'tmpl_in': tmpl}
    cands = list(fit7.variants(tmpl))
    for rc in fit7.recodings(tmpl):
        cands += [x for x in fit7.variants(rc) if x not in cands]
    R = None
    for tv, absorbed in cands[:12]:
        P = fit7.Prober(m, tv)
        try:
            R = fit7.fit_rules(P); out['tmpl'] = tv; out['absorbed'] = absorbed; break
        except Exception as e:
            R = None
    if R is None:
        out['err'] = 'NOFIT'; return out, None
    out['rules'] = reb7.rules_str(R)
    eng = eng7.Eng(R, Q=Q, JMAX=3000)
    eng.deadline = time.time() + 300
    vals = []; res = set()
    cfgs = []
    for j in (4, 6, 9, 12, 15, 20):
        for d in (1, 2, 5):
            for b in (0, 1, 2, 3, 7):
                cfgs.append(([d] + [0] * j, 0, b))
    cfgs += [([1, 0, 0, 3], 2, 5), ([3, 1, 4, 1, 5, 9, 2, 6], 5, 3), ([7] + [1] * 10, 1, 2)]
    for ds, a, b in cfgs:
        try:
            v = eng.value(ds, a, b)
        except Exception as e:
            vals.append([[len(ds), ds[0], a, b], 'ERR %s' % e]); continue
        if isinstance(v, eng7.Huge):
            md = v.mod or Q
            vals.append([[len(ds), ds[0], a, b], 'H%d/%d' % (v.r, md)])
            if md % M == 0: res.add(v.r % M)
        else:
            vals.append([[len(ds), ds[0], a, b], 'E' + (str(v) if v < 10**12 else '>1e12')])
    out['vals'] = vals; out['cls'] = sorted(res); out['M'] = M; out['flags'] = eng.flags[:4]
    out['const'] = len(res) == 1
    return out, R
if __name__ == '__main__':
    o, R = towercls(sys.argv[1], sys.argv[2])
    print(json.dumps(o))
