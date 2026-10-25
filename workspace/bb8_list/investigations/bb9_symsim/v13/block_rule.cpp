struct Rule {
    int q, f; vector<Run> g[2]; vector<int> rv[2]; bool bottom[2];
    int nv; vector<i128> delta; vector<Cons> cons; bool stepsKnown; Lin steps; ll uses = 0;
    bool affine = false; vector<i128> amul; vector<char> cskip;   // affine rule: x -> amul*x + delta; cskip: monotone constraints
    // v13 ITER rule: counters x -> x + delta (delta <= 0 limits k), one self map x_fvar -> F(x_fvar) built from the proof
    // symbols zs, other variables reset to constants.  zcons: constraints checked at every iterate's input.
    // grows: F(y) >= y + 1 for every admissible y (so F^k is increasing in k).
    bool iter = false; vector<char> isF; vector<Lin> iterF; vector<PSym> zs; vector<i128> flb; vector<Cons> zcons; int fvar = -1;
    bool grows = false;
};
// ---- v13: proof-aware constructors (a proof symbol when an argument mentions proof symbols, else the global value)
static Lin iterPow(const Rule &R, int v, const Lin &x0, const Lin &k);
static Lin zAffS(const Lin &x, i128 a, i128 c, const Lin &k) {
    if (!hasProof(x) && !hasProof(k)) return affPow(x, a, c, k);
    if (k.isExact() && k.c == 0) return x;
    if (k.isExact() && k.c <= 3) { Lin y = x; for (i128 t = 0; t < k.c; ++t) y = laddc(lscale(y, a), c); return y; }
    Lin sh = affPow(shadowOf(x), a, c, shadowOf(k));
    PSym z{'Z', sh, LC(c), x}; z.sub = 'A'; z.A = LC(a); z.K = k; PC->s.push_back(z);
    return LV(PBASE + (int)PC->s.size() - 1);
}
static Lin zPS(const Lin &k, const Lin &r) {
    if (!hasProof(k) && !hasProof(r)) return Pglobal(k, r);
    if (k.isExact() && k.c <= 64) return laddc(lscale(laddc(r, 4), (i128)1 << k.c), -4);
    Lin sh = Pglobal(shadowOf(k), shadowOf(r));
    PSym z{'Z', sh, LC(0), r}; z.sub = 'P'; z.A = k; PC->s.push_back(z);
    return LV(PBASE + (int)PC->s.size() - 1);
}
static Lin zCS(const Lin &j, const Lin &v, const Lin &b) {
    if (!hasProof(j) && !hasProof(v) && !hasProof(b)) return Cglobal(j, v, b);
    if (v.isExact() && v.c == 0) return b;
    Lin sh = Cglobal(shadowOf(j), shadowOf(v), shadowOf(b));
    PSym z{'Z', sh, j, b}; z.sub = 'C'; z.A = v; PC->s.push_back(z);
    return LV(PBASE + (int)PC->s.size() - 1);
}
static Lin zIterS(const Rule &R, const Lin &x, const Lin &k) {
    if (!hasProof(x) && !hasProof(k)) return iterPow(R, R.fvar, x, k);
    if (k.isExact() && k.c == 0) return x;
    Lin sh = iterPow(R, R.fvar, shadowOf(x), shadowOf(k));
    PSym z{'Z', sh, LC(0), x}; z.sub = 'T'; z.K = k; z.rp = std::make_shared<Rule>(R); PC->s.push_back(z);
    return LV(PBASE + (int)PC->s.size() - 1);
}
// ---- v13: evaluation of a proof-symbol formula at a value of its variable (ITER rules); proof-aware
struct FEval {
    const vector<PSym> *zs; int var; Lin xval; map<int, Lin> memo; const vector<Lin> *consts = nullptr;
    Lin lin(const Lin &e) {
        Lin r = LC(e.c);
        for (int k = 0; k < e.n; ++k) {
            Lin t;
            if (e.id[k] < PBASE) t = LV(e.id[k]);
            else {
                int idx = e.id[k] - PBASE;
                if ((*zs)[idx].kind == 'P') {
                    if (idx == var) t = xval;
                    else if (consts && idx < (int)consts->size() && (*consts)[idx].D != 0) t = (*consts)[idx];
                    else UD("iter: foreign variable");
                }
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
            case 'A': v = zAffS(lin(z.B), z.A.c, z.J.c, lin(z.K)); break;
            case 'P': v = zPS(lin(z.A), lin(z.B)); break;
            case 'C': v = zCS(lin(z.J), lin(z.A), lin(z.B)); break;
            case 'T': v = zIterS(*z.rp, lin(z.B), lin(z.K)); break;
            default: {
                Lin J = lin(z.J), A = lin(z.A), B = lin(z.B), K = lin(z.K);
                if (hasProof(J) || hasProof(A) || hasProof(B) || hasProof(K)) UD("iter eval: proof W/I/M");
                v = z.sub == 'I' ? Iglobal(J, A, B) : z.sub == 'M' ? MBglobal(J, z.A.c, K, B) : Wglobal(J, B);
            }
        }
        memo[idx] = v; return v;
    }
};
static ll ITERSYMS = 0;
// the constraints of the rule at an iterate's input y (t >= 1): constant variables hold their constants (global values)
static bool iterConsOK(const Rule &R, const Lin &y) {
    vector<Lin> cv(R.nv); for (auto &l : cv) l.D = 0;
    for (int u = 0; u < R.nv; ++u) if (R.isF[u] && u != R.fvar) cv[u] = R.iterF[u];
    for (auto &cn : R.zcons) {
        FEval E; E.zs = &R.zs; E.var = R.fvar; E.xval = y; E.consts = &cv;
        Lin N = E.lin(cn.N);
        if (cn.k == 'G') { if (sgnG(N) < 0) return false; }
        else if (cn.k == 'E') { if (!(N.isExact() && N.c == 0)) return false; }
        else if ((i128)resG(N, (ll)cn.q) != cn.r) return false;
    }
    return true;
}
// orbit of the iterates F^(t+1)(x0), t >= 0: each is abstracted (after the first) by a fresh symbol carrying its lower
// bound and residue; sound because F is monotone and every residue / sign / bound used depends only on these.
struct IterOrbit { vector<ll> rs; vector<i128> lbs; int mu = -1, lam = -1; };
static IterOrbit iterOrbit(const Rule &R, const Lin &x0) {
    const int v = R.fvar; const Lin &F = R.iterF[v];
    auto step = [&](const Lin &y) { FEval E; E.zs = &R.zs; E.var = v; E.xval = y; return E.lin(F); };
    IterOrbit O; size_t g0 = GS.size();   // scratch symbols are dropped afterwards
    try {
        Lin y = step(x0); map<ll, int> seen;
        for (int t = 0; t < 20000; ++t) {
            ll r = resG(y, MG); i128 lb = y.isExact() ? y.c : lbG(y);
            if (lb >= SYMCAP) { auto it = seen.find(r); if (it != seen.end()) { O.mu = it->second; O.lam = t - it->second; break; } seen[r] = t; }
            O.rs.push_back(r); O.lbs.push_back(lb);
            if (!y.isExact()) { ++ITERSYMS; y = LV(newG(lb, r, "iterfake")); }
            if (!iterConsOK(R, y)) UD("iter: constraint");
            y = step(y);
        }
    } catch (...) { GS.resize(g0); throw; }
    GS.resize(g0);
    if (O.lam < 0) UD("iter: orbit");
    return O;
}
static Lin iterPow(const Rule &R, int v, const Lin &x0, const Lin &k) {
    if (v != R.fvar) return R.iterF[v];   // constant reset (k >= 1)
    const Lin &F = R.iterF[v];
    auto step = [&](const Lin &y) { FEval E; E.zs = &R.zs; E.var = v; E.xval = y; return E.lin(F); };
    if (k.isExact() && k.c <= 64) { Lin y = x0; for (i128 t = 0; t < k.c; ++t) { if (t > 0 && !iterConsOK(R, y)) UD("iter: constraint"); y = step(y); } return y; }
    if (!k.isExact() && !R.grows) UD("iter: symbolic count without growth witness");
    IterOrbit O = iterOrbit(R, x0);
    ll rr; i128 lb;
    if (k.isExact()) { i128 t = k.c - 1; size_t i = t < (i128)O.rs.size() ? (size_t)t : (size_t)(O.mu + pmod(t - O.mu, O.lam)); rr = O.rs[i]; lb = O.lbs[min(i, O.lbs.size() - 1)]; }
    else {
        if (sgnG(laddc(k, -(i128)O.rs.size() - 1)) < 0) UD("iter: k below orbit length");
        if (MG % O.lam != 0) UD("iter: orbit period");
        rr = O.rs[(size_t)(O.mu + pmod((i128)resG(k, O.lam) - 1 - O.mu, O.lam))]; lb = SYMCAP;
    }
    // growing F: F^k(x0) >= x0 + k, so the bound also covers k
    if (R.grows) { i128 kl = k.isExact() ? k.c : lbG(k); i128 l0 = x0.isExact() ? x0.c : lbG(x0); i128 s2; if (!__builtin_add_overflow(l0, kl, &s2)) lb = max(lb, min(s2, SYMCAP)); }
    ++wSymCount;
    return LV(newG(max(lb, (i128)1), rr, "T(" + linstr(k) + "," + linstr(x0) + ")"));
}
// lower bound of a formula over zs for var >= vlb (other proof variables: their constants)
static i128 lbForm(const Rule &R, const vector<PSym> &zs, const Lin &e, int var, i128 vlb, map<int, i128> &memo, int depth = 0);
static i128 lbNodeT(const Rule &R, i128 lbB, i128 lbK) {   // lower bound of F^k(B) with B >= lbB, k >= lbK >= 1
    i128 y = lbB; i128 kk = min<i128>(lbK, 64);
    for (i128 t = 0; t < kk && y < SYMCAP; ++t) { map<int, i128> m; i128 ny = lbForm(R, R.zs, R.iterF[R.fvar], R.fvar, y, m); if (ny <= y && R.grows) ny = y + 1; y = ny; }
    if (R.grows) { i128 s2; if (!__builtin_add_overflow(lbB, lbK, &s2)) y = max(y, min(s2, SYMCAP)); }
    return min(y, SYMCAP);
}
static i128 lbForm(const Rule &R, const vector<PSym> &zs, const Lin &e, int var, i128 vlb, map<int, i128> &memo, int depth) {
    if (depth > 60) UD("lbForm depth");
    i128 s = e.c; bool ovf = false;
    for (int k = 0; k < e.n && !ovf; ++k) {
        if (e.a[k] < 0) UD("lbForm: negative coefficient");
        i128 l;
        if (e.id[k] < PBASE) l = GS[e.id[k]].lb;
        else {
            int idx = e.id[k] - PBASE; const PSym &z = zs[idx];
            if (z.kind == 'P') {
                if (idx == var) l = vlb;
                else if (R.isF.size() > (size_t)idx && R.isF[idx] && R.iterF[idx].isExact()) l = R.iterF[idx].c;
                else UD("lbForm: foreign variable");
            } else {
                auto it = memo.find(idx);
                if (it != memo.end()) l = it->second;
                else {
                    auto L = [&](const Lin &x) { return lbForm(R, zs, x, var, vlb, memo, depth + 1); };
                    if (z.sub == 'A') { i128 w = L(z.B), a = z.A.c, cc = z.J.c, kk = min<i128>(L(z.K), 128);
                        for (i128 t = 0; t < kk && w < SYMCAP; ++t) { i128 u; if (__builtin_mul_overflow(w, a, &u) || __builtin_add_overflow(u, cc, &w) || w > SYMCAP) w = SYMCAP; }
                        l = min(w, SYMCAP); }
                    else if (z.sub == 'P') { i128 w = L(z.B) + 4, kk = min<i128>(L(z.A), 120); for (i128 t = 0; t < kk && w < SYMCAP; ++t) w *= 2; l = min(w - 4, SYMCAP); }
                    else if (z.sub == 'C') { i128 w = IUexact(L(z.J), min<i128>(L(z.A), 4), L(z.B), SYMCAP); l = w < 0 ? SYMCAP : w; }
                    else if (z.sub == 'T') { l = lbNodeT(*z.rp, L(z.B), max<i128>(L(z.K), 1)); }
                    else if (z.sub == 'I') { i128 w = Iexact(L(z.J), min<i128>(L(z.A), 64), L(z.B), SYMCAP); l = w < 0 ? SYMCAP : w; }
                    else if (z.sub == 'M') { i128 w = Iexact(L(z.J), z.A.c, L(z.B), SYMCAP); l = w < 0 ? SYMCAP : w; }
                    else { i128 w = Wexact(L(z.J), L(z.B), SYMCAP); l = w < 0 ? SYMCAP : w; }
                    memo[idx] = l;
                }
            }
        }
        i128 t; if (__builtin_mul_overflow(e.a[k], l, &t) || __builtin_add_overflow(s, t, &s)) ovf = true;
    }
    if (ovf) return SYMCAP;
    return min(cdiv(s, e.D), SYMCAP);
}
