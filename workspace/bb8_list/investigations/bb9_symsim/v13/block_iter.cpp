static Lin zIterS(const Rule &R, const Lin &x, const Lin &k, const Lin &j);
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
            case 'T': try { v = zIterS(*z.rp, lin(z.B), lin(z.K), lin(z.J)); } catch (IterStop &) { UD("iter: inner iteration stopped"); } break;
            default: {
                Lin J = lin(z.J), A = lin(z.A), B = lin(z.B), K = lin(z.K);
                if (hasProof(J) || hasProof(A) || hasProof(B) || hasProof(K)) UD("iter eval: proof W/I/M");
                v = z.sub == 'I' ? Iglobal(J, A, B) : z.sub == 'M' ? MBglobal(J, z.A.c, K, B) : Wglobal(J, B);
            }
        }
        memo[idx] = v; return v;
    }
};
static ll ITERSYMS = 0, ITERORB = 0, ITERORBST = 0, ITERHIT = 0; static bool ITERSTAT = false;
static const i128 JCAP = 64;   // the counter j of an ITER rule is abstracted to "j >= 64, residue unknown" beyond 64
// values of the other variables for an application whose input is (y, j): constant resets and the counter j
static vector<Lin> iterVals(const Rule &R, const Lin &j) {
    vector<Lin> cv(R.nv); for (auto &l : cv) l.D = 0;
    for (int u = 0; u < R.nv; ++u) if (R.isF[u] && u != R.fvar && R.iterF[u].isExact()) cv[u] = R.iterF[u];
    if (R.lvar >= 0) cv[R.lvar] = j;
    return cv;
}
static Lin jNext(const Rule &R, const Lin &j) { return R.lvar >= 0 ? laddc(j, R.delta[R.lvar]) : j; }
// abstraction of the counter: exact up to JCAP, then a fresh symbol with lower bound JCAP and no residue (mod 1)
static Lin jAbs(const Rule &R, const Lin &j) {
    if (R.lvar < 0) return LC(0);
    if (j.isExact() && j.c <= JCAP) return j;
    i128 l = j.isExact() ? j.c : lbG(j);
    return LV(newG(min(l, JCAP), 0, "jfake", 1));
}
static string jKey(const Rule &R, const Lin &j) { if (R.lvar < 0) return "-"; if (j.isExact() && j.c <= JCAP) return s128(j.c); return "J"; }
// the constraints of the rule at an iterate's input (y, j) (t >= 1)
static bool iterConsOK(const Rule &R, const Lin &y, const Lin &j, FEval *EP = nullptr) {
    vector<Lin> cv = iterVals(R, j);
    FEval E0; E0.zs = &R.zs; E0.var = R.fvar; E0.xval = y;
    FEval &E = EP ? *EP : E0; E.consts = &cv;
    for (auto &cn : R.zcons) {
        Lin N = E.lin(cn.N);
        if (cn.k == 'G') { if (sgnG(N) < 0) return false; }
        else if (cn.k == 'E') { if (!(N.isExact() && N.c == 0)) return false; }
        else if ((i128)resG(N, (ll)cn.q) != cn.r) return false;
    }
    return true;
}
static Lin iterStep(const Rule &R, const Lin &y, const Lin &j) {
    vector<Lin> cv = iterVals(R, j); FEval E; E.zs = &R.zs; E.var = R.fvar; E.xval = y; E.consts = &cv; return E.lin(R.iterF[R.fvar]);
}
// orbit of the iterates F^(t+1)(x0), t >= 0: each is abstracted (after the first) by a fresh symbol carrying its lower
// bound and residue (and the counter by jAbs); sound because F is monotone and every residue / sign / bound used depends
// only on these.
struct IterOrbit { vector<ll> rs; vector<i128> lbs; int mu = -1, lam = -1, stop = -1; };   // stop: valid applications if a constraint fails
static IterOrbit iterOrbit(const Rule &R, const Lin &x0, const Lin &j0) {
    static map<string, IterOrbit> OC;
    bool cacheable = x0.isExact() || (x0.n == 1 && x0.a[0] == 1 && x0.D == 1 && x0.c == 0 && GS[x0.id[0]].mod == MG);
    if (R.lvar >= 0 && !(j0.isExact() || (j0.n == 1 && j0.a[0] == 1 && j0.D == 1 && j0.c == 0))) cacheable = false;
    string key;
    if (cacheable) {
        key = to_string(R.uid) + ":" + (x0.isExact() ? "e" + s128(x0.c) : "s" + s128(GS[x0.id[0]].lb) + "," + to_string(GS[x0.id[0]].res)) + ":" + jKey(R, j0);
        auto it = OC.find(key); if (it != OC.end()) { ++ITERHIT; return it->second; }
    }
    IterOrbit O; size_t g0 = GS.size();   // scratch symbols are dropped afterwards
    try {
        Lin j = j0;
        Lin y = iterStep(R, x0, j); j = jAbs(R, jNext(R, j));
        map<string, int> seen; ++ITERORB;
        for (int t = 0; t < 20000; ++t) { ++ITERORBST;
            ll r = resG(y, MG); i128 lb = y.isExact() ? y.c : lbG(y);
            if (lb >= SYMCAP) { string sk = to_string(r) + "|" + jKey(R, j); auto it = seen.find(sk); if (it != seen.end()) { O.mu = it->second; O.lam = t - it->second; break; } seen[sk] = t; }
            O.rs.push_back(r); O.lbs.push_back(lb);
            if (!y.isExact()) { ++ITERSYMS; y = LV(newG(lb, r, "iterfake")); }
            FEval E; E.zs = &R.zs; E.var = R.fvar; E.xval = y;
            if (!iterConsOK(R, y, j, &E)) { O.stop = t + 1; break; }
            vector<Lin> cv = iterVals(R, j); E.consts = &cv; y = E.lin(R.iterF[R.fvar]);
            j = jAbs(R, jNext(R, j));
        }
    } catch (...) { GS.resize(g0); throw; }
    GS.resize(g0);
    if (O.lam < 0 && O.stop < 0) UD("iter: orbit");
    if (cacheable) { static size_t OCTOT = 0; OCTOT += O.rs.size(); if (OC.size() > 200000 || OCTOT > 4000000) { OC.clear(); OCTOT = O.rs.size(); } OC[key] = O; }
    return O;
}
static Lin iterPow(const Rule &R, int v, const Lin &x0, const Lin &k, bool orbitOnly, const Lin &j0) {
    if (v != R.fvar) return R.iterF[v];   // constant reset (k >= 1)
    if (k.isExact() && k.c <= 64 && !orbitOnly) {   // literal composition while the iterates are exact; then the orbit abstraction
        Lin y = x0, j = j0;
        for (i128 t = 0; t < k.c; ++t) {
            if (t > 0 && !iterConsOK(R, y, j)) throw IterStop{t};
            if (t > 0 && !y.isExact() && k.c - t > 2 && !ITERCHECK) { try { return iterPow(R, v, y, LC(k.c - t), true, j); } catch (IterStop &s2) { throw IterStop{t + s2.t}; } }
            y = iterStep(R, y, j); j = jNext(R, j);
        }
        if (ITERCHECK && !y.isExact() && k.c >= 2) {   // --itercheck: the orbit abstraction must agree with the composition
            try {
                Lin z = iterPow(R, v, x0, k, true, j0);
                ll r1 = resG(y, MG), r2 = resG(z, MG); i128 l1 = lbG(y), l2 = lbG(z);
                if (r1 != r2) { ++ICFAIL; fprintf(stderr, "ITERCHECK-FAIL k=%s res %lld vs %lld\n", s128(k.c).c_str(), r1, r2); } else ++ICPASS;
                if (l2 > l1 && l1 < SYMCAP) ++ICLBWARN;
            } catch (Undec &) { ++ICSKIP; } catch (IterStop &) { ++ICSKIP; }
        }
        return y;
    }
    if (!k.isExact() && !R.grows) UD("iter: symbolic count without growth witness");
    // result cache: (rule, x0 abstraction, k abstraction, counter abstraction) -> (residue, lower bound)
    static map<string, pair<ll, i128>> PC2;
    auto lkey = [](const Lin &e, string &out) -> bool {
        if (e.isExact()) { out += "e" + s128(e.c) + ";"; return true; }
        if (e.n != 1 || GS[e.id[0]].mod != MG) return false;
        out += "s" + s128(e.a[0]) + "," + s128(e.c) + "," + s128(e.D) + "," + s128(GS[e.id[0]].lb) + "," + to_string(GS[e.id[0]].res) + ";";
        return true;
    };
    string ck = to_string(R.uid) + ":"; bool cOK = lkey(x0, ck) && lkey(k, ck);
    if (R.lvar >= 0) { if (j0.isExact() || (j0.n == 1 && j0.a[0] == 1 && j0.D == 1 && j0.c == 0)) ck += jKey(R, j0); else cOK = false; }
    if (cOK) { auto it = PC2.find(ck); if (it != PC2.end()) { ++ITERHIT; ++wSymCount; return LV(newG(max(it->second.second, (i128)1), it->second.first, "T(" + linstr(k) + "," + linstr(x0) + ")")); } }
    IterOrbit O = iterOrbit(R, x0, j0);
    if (ITERCHECK) {   // --itercheck: the first iterates composed with real symbols must match the orbit abstraction
        size_t g1 = GS.size();
        try {
            Lin y = x0, j = j0;
            for (size_t t = 0; t < O.rs.size() && t < 6; ++t) {
                if (t > 0 && !iterConsOK(R, y, j)) break;
                y = iterStep(R, y, j); j = jNext(R, j);
                if (resG(y, MG) != O.rs[t]) { ++ICFAIL; fprintf(stderr, "ITERCHECK-FAIL orbit t=%zu res %lld vs %lld\n", t, resG(y, MG), O.rs[t]); }
                else ++ICPASS;
                i128 l = y.isExact() ? y.c : lbG(y); if (O.lbs[t] > l) ++ICLBWARN;
            }
        } catch (Undec &) { ++ICSKIP; } catch (IterStop &) { ++ICSKIP; }
        GS.resize(g1);
    }
    if (O.stop >= 0 && !(k.isExact() && k.c <= O.stop)) throw IterStop{O.stop};
    if (O.stop >= 0) cOK = false;
    ll rr; i128 lb;
    if (k.isExact()) { i128 t = k.c - 1; size_t i = t < (i128)O.rs.size() ? (size_t)t : (size_t)(O.mu + pmod(t - O.mu, O.lam)); rr = O.rs[i]; lb = O.lbs[min(i, O.lbs.size() - 1)]; }
    else {
        if (sgnG(laddc(k, -(i128)O.rs.size() - 1)) < 0) UD("iter: k below orbit length");
        if (MG % O.lam != 0) UD("iter: orbit period");
        rr = O.rs[(size_t)(O.mu + pmod((i128)resG(k, O.lam) - 1 - O.mu, O.lam))]; lb = SYMCAP;
    }
    // growing F: F^k(x0) >= x0 + k, so the bound also covers k
    if (R.grows) { i128 kl = k.isExact() ? k.c : lbG(k); i128 l0 = x0.isExact() ? x0.c : lbG(x0); i128 s2; if (!__builtin_add_overflow(l0, kl, &s2)) lb = max(lb, min(s2, SYMCAP)); }
    if (cOK) { if (PC2.size() > 500000) PC2.clear(); PC2[ck] = {rr, lb}; }
    ++wSymCount;
    return LV(newG(max(lb, (i128)1), rr, "T(" + linstr(k) + "," + linstr(x0) + ")"));
}
static Lin zIterS(const Rule &R, const Lin &x, const Lin &k, const Lin &j) {
    if (!hasProof(x) && !hasProof(k) && !hasProof(j)) return iterPow(R, R.fvar, x, k, false, j);
    if (k.isExact() && k.c == 0) return x;
    Lin sh; try { sh = iterPow(R, R.fvar, shadowOf(x), shadowOf(k), false, shadowOf(j)); } catch (IterStop &) { UD("iter: shadow iteration stopped"); }
    static map<ll, std::shared_ptr<Rule>> RP;
    auto it = RP.find(R.uid); if (it == RP.end()) it = RP.emplace(R.uid, std::make_shared<Rule>(R)).first;
    PSym z{'Z', sh, j, x}; z.sub = 'T'; z.K = k; z.rp = it->second; PC->s.push_back(z);
    return LV(PBASE + (int)PC->s.size() - 1);
}
// first application with the bound values of the constant-reset variables and the counter, then k - 1 further
// applications (proof-aware)
static Lin iterFirst(const Rule &R, const vector<Lin> &bind, const Lin &k) {
    vector<Lin> cv(R.nv); for (auto &l : cv) l.D = 0;
    for (int u = 0; u < R.nv; ++u) if (((R.isF[u] && u != R.fvar) || u == R.lvar) && u < (int)bind.size() && bind[u].D != 0) cv[u] = bind[u];
    FEval E; E.zs = &R.zs; E.var = R.fvar; E.xval = bind[R.fvar]; E.consts = &cv;
    Lin y1 = E.lin(R.iterF[R.fvar]);
    if (k.isExact() && k.c == 1) return y1;
    Lin j1 = R.lvar >= 0 ? jNext(R, bind[R.lvar]) : LC(0);
    if (!hasProof(y1) && !hasProof(k) && !hasProof(j1)) {   // the second iterate's input must satisfy the constraints too
        if (!iterConsOK(R, y1, j1)) throw IterStop{1};
        try { return zIterS(R, y1, laddc(k, -1), j1); } catch (IterStop &s2) { throw IterStop{1 + s2.t}; }
    }
    return zIterS(R, y1, laddc(k, -1), j1);
}
// lower bound of a formula over zs for var >= vlb, counter >= jlb (other proof variables: their constants)
static i128 lbForm(const Rule &R, const vector<PSym> &zs, const Lin &e, int var, i128 vlb, map<int, i128> &memo, int depth = 0, i128 jlb = 0);
static i128 lbNodeT(const Rule &R, i128 lbB, i128 lbK, i128 lbJ) {   // lower bound of F^k(B) with B >= lbB, k >= lbK >= 1
    i128 y = lbB; i128 kk = min<i128>(lbK, 64); i128 jl = lbJ;
    for (i128 t = 0; t < kk && y < SYMCAP; ++t) {
        map<int, i128> m; i128 ny = lbForm(R, R.zs, R.iterF[R.fvar], R.fvar, y, m, 0, jl);
        if (ny <= y && R.grows) ny = y + 1; y = ny;
        if (R.lvar >= 0) jl = min<i128>(jl + R.delta[R.lvar], SYMCAP);
    }
    if (R.grows) { i128 s2; if (!__builtin_add_overflow(lbB, lbK, &s2)) y = max(y, min(s2, SYMCAP)); }
    return min(y, SYMCAP);
}
static i128 lbForm(const Rule &R, const vector<PSym> &zs, const Lin &e, int var, i128 vlb, map<int, i128> &memo, int depth, i128 jlb) {
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
                else if (idx == R.lvar) l = jlb;
                else if (R.isF.size() > (size_t)idx && R.isF[idx] && R.iterF[idx].isExact()) l = R.iterF[idx].c;
                else UD("lbForm: foreign variable");
            } else {
                auto it = memo.find(idx);
                if (it != memo.end()) l = it->second;
                else {
                    auto L = [&](const Lin &x) { return lbForm(R, zs, x, var, vlb, memo, depth + 1, jlb); };
                    if (z.sub == 'A') { i128 w = L(z.B), a = z.A.c, cc = z.J.c, kk = min<i128>(L(z.K), 128);
                        for (i128 t = 0; t < kk && w < SYMCAP; ++t) { i128 u; if (__builtin_mul_overflow(w, a, &u) || __builtin_add_overflow(u, cc, &w) || w > SYMCAP) w = SYMCAP; }
                        l = min(w, SYMCAP); }
                    else if (z.sub == 'P') { i128 w = L(z.B) + 4, kk = min<i128>(L(z.A), 120); for (i128 t = 0; t < kk && w < SYMCAP; ++t) w *= 2; l = min(w - 4, SYMCAP); }
                    else if (z.sub == 'C') { i128 w = IUexact(L(z.J), min<i128>(L(z.A), 4), L(z.B), SYMCAP); l = w < 0 ? SYMCAP : w; }
                    else if (z.sub == 'T') { l = lbNodeT(*z.rp, L(z.B), max<i128>(L(z.K), 1), L(z.J)); }
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
