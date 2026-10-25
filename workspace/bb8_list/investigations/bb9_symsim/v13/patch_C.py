import sys, re
fn = sys.argv[1]; s = open(fn).read()
def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:70], s.count(old))
    s = s.replace(old, new)
rep('bool iter = false; vector<char> isF; vector<Lin> iterF; vector<PSym> zs; vector<i128> flb; vector<Cons> fcong;',
    'bool iter = false; vector<char> isF; vector<Lin> iterF; vector<PSym> zs; vector<i128> flb; vector<Cons> zcons; int fvar = -1;')
rep('''    const vector<PSym> *zs; int var; Lin xval; map<int, Lin> memo;''', '''    const vector<PSym> *zs; int var; Lin xval; map<int, Lin> memo; const vector<Lin> *consts = nullptr;''')
rep('''                if ((*zs)[idx].kind == 'P') { if (idx != var) UD("iter: foreign variable"); t = xval; }''',
    '''                if ((*zs)[idx].kind == 'P') {
                    if (idx == var) t = xval;
                    else if (consts && idx < (int)consts->size() && (*consts)[idx].D != 0) t = (*consts)[idx];
                    else UD("iter: foreign variable");
                }''')
# replace iterPow body
i0 = s.index('static Lin iterPow(const Rule &R, int v, const Lin &x0, const Lin &k) {')
i1 = s.index('struct RuleSet {', i0)
s = s[:i0] + r'''// the constraints of the rule at an iterate's input y (t >= 1): constant variables hold their constants
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
static Lin iterPow(const Rule &R, int v, const Lin &x0, const Lin &k) {
    if (v != R.fvar) return R.iterF[v];   // constant reset (k >= 1)
    const Lin &F = R.iterF[v];
    auto step = [&](const Lin &y) { vector<Lin> cv(R.nv); for (auto &l : cv) l.D = 0; FEval E; E.zs = &R.zs; E.var = v; E.xval = y; E.consts = &cv; return E.lin(F); };
    if (k.isExact() && k.c <= 64) { Lin y = x0; for (i128 t = 0; t < k.c; ++t) { if (t > 0 && !iterConsOK(R, y)) UD("iter: constraint"); y = step(y); } return y; }
    // orbit of (residue, saturated lower bound): iterate t >= 1 is abstracted by a fresh symbol with its lower bound and
    // residue (sound: F is monotone, and every constraint check and residue depends only on these)
    Lin y = step(x0);
    vector<ll> rs; vector<i128> lbs; map<ll, int> seen; int mu = -1, lam = -1;
    for (int t = 0; t < 20000; ++t) {
        ll r = resG(y, MG); i128 lb = y.isExact() ? y.c : lbG(y);
        if (lb >= SYMCAP) { auto it = seen.find(r); if (it != seen.end()) { mu = it->second; lam = t - it->second; break; } seen[r] = t; }
        rs.push_back(r); lbs.push_back(lb);
        if (!y.isExact()) { ++ITERSYMS; y = LV(newG(lb, r, "iterfake")); }
        if (!iterConsOK(R, y)) UD("iter: constraint");
        y = step(y);
    }
    if (lam < 0) UD("iter: orbit");
    // rs[t] is the residue of F^(t+1)(x0)
    ll rr; i128 lb;
    if (k.isExact()) { i128 t = k.c - 1; size_t i = t < (i128)rs.size() ? (size_t)t : (size_t)(mu + pmod(t - mu, lam)); rr = rs[i]; lb = lbs[min(i, lbs.size() - 1)]; }
    else {
        if (sgnG(laddc(k, -(i128)rs.size() - 1)) < 0) UD("iter: k below orbit length");
        if (MG % lam != 0) UD("iter: orbit period");
        rr = rs[(size_t)(mu + pmod((i128)resG(k, lam) - 1 - mu, lam))]; lb = SYMCAP;
    }
    ++wSymCount;
    return LV(newG(max(lb, (i128)1), rr, "T(" + linstr(k) + "," + linstr(x0) + ")"));
}
''' + s[i1:]
rep('            R.isF[v] = 1; R.iterF[v] = x; anyF = true;', '            if (R.fvar >= 0) { ok = false; iwhy = "two F vars"; break; }\n            R.isF[v] = 1; R.iterF[v] = x; anyF = true; R.fvar = v;')
i0 = s.index('            Pres PR; PR.init();\n            bool okc = true, lim = false;')
i1 = s.index('            if (okc && lim) {', i0)
s = s[:i0] + r'''            bool okc = true, lim = false;
            for (auto &cn : ctx.cons) {
                bool hasF = false, hasL = false, hasZc = mentionsZ(cn.N), foreign = false;
                for (int t = 0; t < cn.N.n; ++t) if (cn.N.id[t] >= PBASE) {
                    int v = cn.N.id[t] - PBASE;
                    if (ctx.s[v].kind != 'P') continue;
                    if (!inPrefix[v]) foreign = true; else if (R.isF[v]) hasF = true; else hasL = true;
                }
                if (foreign) { if (!(cn.k == 'G' && cn.N.n == 1 && cn.N.a[0] == 1 && cn.N.c == -1)) { okc = false; iwhy = "foreign " + linstr(cn.N); } continue; }
                if (hasZc || hasF) {
                    if (hasL) { okc = false; iwhy = "mixed " + linstr(cn.N); break; }
                    // checked at every application's input (first: applyRule, later: iterConsOK)
                    R.zcons.push_back(cn);
                    if (!hasZc) { R.cons.push_back(cn); R.cskip.push_back(1); }
                    continue;
                }
                R.cons.push_back(cn); R.cskip.push_back(0);
                i128 B = 0; for (int t = 0; t < cn.N.n; ++t) if (cn.N.id[t] >= PBASE) B += cn.N.a[t] * R.delta[cn.N.id[t] - PBASE];
                if ((cn.k == 'G' && B < 0) || (cn.k == 'E' && B != 0) || (cn.k == 'C' && pmod(B, cn.q) != 0)) lim = true;
            }
''' + s[i1:]
rep('            R.cons.clear(); R.cskip.clear(); R.fcong.clear(); R.zs.clear();', '            R.cons.clear(); R.cskip.clear(); R.zcons.clear(); R.zs.clear(); R.fvar = -1;')
rep('''            // number of applications
            if (R.iter && proof) return -1;   // ITER rules: main mode only''', '''            // number of applications
            if (R.iter && proof) return -1;   // ITER rules: main mode only
            if (R.iter) {   // Z constraints at the first application (input = the bound values)
                vector<Lin> cv(R.nv); for (auto &l : cv) l.D = 0;
                for (int u = 0; u < R.nv; ++u) if (R.isF[u] && u != R.fvar && bind[u].D != 0) cv[u] = bind[u];
                for (auto &cn : R.zcons) {
                    FEval E; E.zs = &R.zs; E.var = R.fvar; E.xval = bind[R.fvar]; E.consts = &cv;
                    Lin N = E.lin(cn.N);
                    bool okz = cn.k == 'G' ? sgnG(N) >= 0 : cn.k == 'E' ? (N.isExact() && N.c == 0) : (i128)resG(N, (ll)cn.q) == cn.r;
                    if (!okz) return -1;
                }
            }''')
open(fn, 'w').write(s)
