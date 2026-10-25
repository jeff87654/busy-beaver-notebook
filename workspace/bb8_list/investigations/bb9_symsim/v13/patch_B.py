import sys
fn = sys.argv[1]; s = open(fn).read()
def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:70], s.count(old))
    s = s.replace(old, new)
# Rule fields
rep('''    bool affine = false; vector<i128> amul; vector<char> cskip;   // affine rule: x -> amul*x + delta; cskip: monotone constraints
};''', '''    bool affine = false; vector<i128> amul; vector<char> cskip;   // affine rule: x -> amul*x + delta; cskip: monotone constraints
    // v13 ITER rule: counters x -> x + delta (delta <= 0 limits k), self maps x_v -> F_v(x_v) built from proof symbols zs
    bool iter = false; vector<char> isF; vector<Lin> iterF; vector<PSym> zs; vector<i128> flb; vector<Cons> fcong;
};
// ---- v13: evaluation of a proof-symbol formula at a global value of its single variable (ITER rules)
struct FEval {
    const vector<PSym> *zs; int var; Lin xval; map<int, Lin> memo;
    Lin lin(const Lin &e) {
        Lin r = LC(e.c);
        for (int k = 0; k < e.n; ++k) {
            Lin t;
            if (e.id[k] < PBASE) t = LV(e.id[k]);
            else {
                int idx = e.id[k] - PBASE;
                if ((*zs)[idx].kind == 'P') { if (idx != var) UD("iter: foreign variable"); t = xval; }
                else t = node(idx);
            }
            r = lcomb(r, 1, t, e.a[k]);
        }
        return lscale(r, 1, e.D);
    }
    Lin node(int idx) {
        auto it = memo.find(idx); if (it != memo.end()) return it->second;
        const PSym &z = (*zs)[idx]; Lin v;
        switch (z.sub) {
            case 'A': v = affPow(lin(z.B), z.A.c, z.J.c, lin(z.K)); break;
            case 'P': v = Pglobal(lin(z.A), lin(z.B)); break;
            case 'C': v = Cglobal(lin(z.J), lin(z.A), lin(z.B)); break;
            case 'I': v = Iglobal(lin(z.J), lin(z.A), lin(z.B)); break;
            case 'M': v = MBglobal(lin(z.J), z.A.c, lin(z.K), lin(z.B)); break;
            default: v = Wglobal(lin(z.J), lin(z.B)); break;
        }
        memo[idx] = v; return v;
    }
};
static Lin iterEval(const vector<PSym> &zs, const Lin &F, int var, const Lin &x) { FEval E; E.zs = &zs; E.var = var; E.xval = x; return E.lin(F); }
// F_v iterated k times from x (global).  Exact small k: literal composition.  Otherwise: lower-bound chain and residue
// orbit of the iterates (later iterates are abstracted by fresh symbols carrying their lower bound and residue, which is
// sound because F is monotone and its value's residue depends only on the argument's residue and lower bound).
static ll ITERSYMS = 0;
static Lin iterPow(const Rule &R, int v, const Lin &x0, const Lin &k) {
    const Lin &F = R.iterF[v];
    auto congOK = [&](const Lin &y) {
        for (auto &cn : R.fcong) { Lin N = laddc(lscale(y, coefOf(cn.N, PBASE + v)), cn.N.c); if ((i128)resG(N, (ll)cn.q) != cn.r) return false; }
        return true;
    };
    if (k.isExact() && k.c <= 64) { Lin y = x0; for (i128 t = 0; t < k.c; ++t) { y = iterEval(R.zs, F, v, y); if (t + 1 < k.c && !congOK(y)) UD("iter: congruence"); } return y; }
    // orbit of (residue, saturated lower bound)
    Lin y = iterEval(R.zs, F, v, x0);
    vector<ll> rs; vector<i128> lbs; map<ll, int> seen; int mu = -1, lam = -1;
    for (int t = 0; t < 20000; ++t) {
        if (!congOK(y)) UD("iter: congruence");
        ll r = resG(y, MG); i128 lb = y.isExact() ? y.c : lbG(y);
        if (lb >= SYMCAP) { auto it = seen.find(r); if (it != seen.end()) { mu = it->second; lam = t - it->second; break; } seen[r] = t; }
        rs.push_back(r); lbs.push_back(lb);
        if (!y.isExact()) { ++ITERSYMS; y = LV(newG(lb, r, "iterfake")); }
        y = iterEval(R.zs, F, v, y);
    }
    if (lam < 0) UD("iter: orbit");
    // iterate t (0-based) is F^(t+1)(x0)
    ll rr; i128 lb;
    if (k.isExact()) { i128 t = k.c - 1; size_t i = t < (i128)rs.size() ? (size_t)t : (size_t)(mu + pmod(t - mu, lam)); rr = rs[i]; lb = lbs[min(i, lbs.size() - 1)]; }
    else {
        if (sgnG(laddc(k, -(i128)rs.size() - 1)) < 0) UD("iter: k below orbit length");
        if (MG % lam != 0) UD("iter: orbit period");
        rr = rs[(size_t)(mu + pmod((i128)resG(k, lam) - 1 - mu, lam))]; lb = SYMCAP;
    }
    ++wSymCount;
    return LV(newG(max(lb, (i128)1), rr, "T(" + linstr(k) + "," + linstr(x0) + ")"));
}''')
# applyRule: ITER application
rep('''            if (R.affine && proof && !PAFF) return -1;''', '''            if (R.iter && proof) return -1;   // ITER rules: main mode only
            if (R.affine && proof && !PAFF) return -1;''')
rep('''                if (R.affine && R.cskip[ci]) continue;   // monotone in the growing counts: never violated''',
    '''                if ((R.affine || R.iter) && R.cskip[ci]) continue;   // monotone in the growing counts: never violated''')
rep('''            if (inf) { if (R.affine) return -1; cyc = "LIN"; return S_CYCLE; }
            // apply k times
            if (R.affine) stepsKnown = false;''', '''            if (inf) { if (R.affine || R.iter) return -1; cyc = "LIN"; return S_CYCLE; }
            // apply k times
            if (R.affine || R.iter) stepsKnown = false;''')
rep('''            if (!R.affine && R.stepsKnown && stepsKnown) {''', '''            if (!R.affine && !R.iter && R.stepsKnown && stepsKnown) {''')
rep('''                    Lin nn = (R.affine && R.amul[v] > 1) ? (proof ? computeAff''', '''                    Lin nn = (R.iter && R.isF[v]) ? iterPow(R, v, bind[v], k) : (R.affine && R.amul[v] > 1) ? (proof ? computeAff''')
rep('''            ++R.uses; ++ruleApps; if (R.affine) ++affApps;''', '''            ++R.uses; ++ruleApps; if (R.affine) ++affApps; if (R.iter) ++iterApps;''')
rep('''    ll macro = 0, jumps = 0, ruleApps = 0, affApps = 0;''', '''    ll macro = 0, jumps = 0, ruleApps = 0, affApps = 0, iterApps = 0;''')
# ITER classification after the affine branch
rep('''    o.why = "nonlin: " + why; return o;
}''', '''    // v13 ITER rule: decreasing counters plus self maps x_v -> F_v(x_v) (F built from proof symbols of x_v only)
    if (hasZ && !extras && ITERON) {
        R.isF.assign(R.nv, 0); R.iterF.assign(R.nv, Lin()); R.flb.assign(R.nv, 1); R.amul.assign(R.nv, 1); R.delta.assign(R.nv, 0);
        bool ok = true, dec = false, anyF = false;
        // proof variables a formula depends on (through proof symbols)
        std::function<void(const Lin &, set<int> &, int)> deps = [&](const Lin &x, set<int> &out, int depth) {
            if (depth > 40) { ok = false; return; }
            for (int t = 0; t < x.n; ++t) if (x.id[t] >= PBASE) {
                int idx = x.id[t] - PBASE; const PSym &z = ctx.s[idx];
                if (z.kind == 'P') out.insert(idx);
                else for (const Lin *a : {&z.J, &z.A, &z.B, &z.K}) deps(*a, out, depth + 1);
            }
        };
        std::function<bool(const Lin &, int)> nonneg = [&](const Lin &x, int depth) -> bool {
            if (depth > 40 || !allNonneg(x) || x.c < 0) return false;
            for (int t = 0; t < x.n; ++t) if (x.id[t] >= PBASE && ctx.s[x.id[t] - PBASE].kind == 'Z') {
                const PSym &z = ctx.s[x.id[t] - PBASE];
                if (z.sub == 'A' && (z.A.c < 2 || z.J.c < 0)) return false;
                for (const Lin *a : {&z.J, &z.A, &z.B, &z.K}) if (a->n || a->c) if (!nonneg(*a, depth + 1)) return false;
            }
            return true;
        };
        for (int v = 0; v < R.nv && ok; ++v) if (inPrefix[v] && ctx.s[v].kind == 'P') {
            const Lin &x = e[v];
            if (x.n == 1 && x.id[0] == PBASE + v && x.a[0] == 1 && x.D == 1) { R.delta[v] = x.c; if (x.c < 0) dec = true; continue; }
            set<int> d; deps(x, d, 0);
            if (!ok || d.size() > 1 || (d.size() == 1 && *d.begin() != v)) { ok = false; break; }
            if (!mentionsZ(x) || !nonneg(x, 0)) { ok = false; break; }
            R.isF[v] = 1; R.iterF[v] = x; anyF = true;
        }
        if (ok && dec && anyF) {
            R.zs = ctx.s;
            // lower bounds of the F variables from single-variable constraints
            for (auto &cn : ctx.cons) if (cn.k == 'G' && cn.N.n == 1 && cn.N.id[0] >= PBASE && cn.N.a[0] > 0 && ctx.s[cn.N.id[0] - PBASE].kind == 'P') {
                int v = cn.N.id[0] - PBASE; if (R.isF[v]) R.flb[v] = max(R.flb[v], cdiv(-cn.N.c, cn.N.a[0]));
            }
            Pres PR; PR.init();
            bool okc = true, lim = false;
            for (auto &cn : ctx.cons) {
                bool hasF = false, hasL = false, hasZc = mentionsZ(cn.N), foreign = false;
                for (int t = 0; t < cn.N.n; ++t) if (cn.N.id[t] >= PBASE) {
                    int v = cn.N.id[t] - PBASE;
                    if (ctx.s[v].kind != 'P') continue;
                    if (!inPrefix[v]) foreign = true; else if (R.isF[v]) hasF = true; else hasL = true;
                }
                if (foreign) { if (!(cn.k == 'G' && cn.N.n == 1 && cn.N.a[0] == 1 && cn.N.c == -1)) okc = false; continue; }
                if (hasZc) {   // discharged by lower bounds (G with nonnegative coefficients), else refused
                    bool dis = false;
                    try { dis = cn.k == 'G' && allNonneg(cn.N) && PR.LBe(cn.N) >= 0; } catch (Undec &) { dis = false; }
                    if (!dis) { okc = false; break; }
                    continue;
                }
                if (hasF) {
                    if (hasL) { okc = false; break; }
                    if (cn.k == 'G' && cn.N.n == 1 && cn.N.a[0] > 0) { R.cons.push_back(cn); R.cskip.push_back(1); continue; }   // via flb
                    if (cn.k == 'C' && cn.N.n == 1) { R.cons.push_back(cn); R.cskip.push_back(1); R.fcong.push_back(cn); continue; }
                    okc = false; break;
                }
                R.cons.push_back(cn); R.cskip.push_back(0);
                i128 B = 0; for (int t = 0; t < cn.N.n; ++t) if (cn.N.id[t] >= PBASE) B += cn.N.a[t] * R.delta[cn.N.id[t] - PBASE];
                if ((cn.k == 'G' && B < 0) || (cn.k == 'E' && B != 0) || (cn.k == 'C' && pmod(B, cn.q) != 0)) lim = true;
            }
            // F maps [flb, inf) into itself: F(flb) >= flb, checked on a fresh symbol at the bound (F is monotone)
            for (int v = 0; v < R.nv && okc; ++v) if (R.isF[v]) {
                try {
                    Lin y = iterEval(R.zs, R.iterF[v], v, LV(newG(R.flb[v], 0, "iterlb", 1)));
                    if (!(y.isExact() ? y.c >= R.flb[v] : lbG(y) >= R.flb[v])) okc = false;
                } catch (Undec &) { okc = false; }
            }
            if (okc && lim) {
                R.iter = true; R.stepsKnown = false;
                if (SHOWPROOF) fprintf(stderr, "PROOF iter rule delta=%lld\\n", nsteps);
                o.st = 1; o.kind = "ITER"; return o;
            }
            R.cons.clear(); R.cskip.clear(); R.fcong.clear(); R.zs.clear();
        }
    }
    o.why = "nonlin: " + why; return o;
}''')
rep('static bool NOAFF = false, KTFORCE = false, AFFC = true, PAFF = true;', 'static bool NOAFF = false, KTFORCE = false, AFFC = true, PAFF = true, ITERON = true;')
rep('''        else if (a == "--nopaff") PAFF = false;''', '''        else if (a == "--nopaff") PAFF = false;
        else if (a == "--noiter") ITERON = false;''')
open(fn, 'w').write(s)
