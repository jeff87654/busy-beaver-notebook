import sys
fn = sys.argv[1]; s = open(fn).read()
def rep(a, b, c=1):
    global s
    assert s.count(a) == c, (a[:70], s.count(a))
    s = s.replace(a, b)
# two-pass classification: constant resets first, then the F variable may depend on them (first application only)
rep('''        for (int v = 0; v < R.nv && ok; ++v) if (inPrefix[v] && ctx.s[v].kind == 'P') {
            const Lin &x = e[v];
            if (x.n == 1 && x.id[0] == PBASE + v && x.a[0] == 1 && x.D == 1) { R.delta[v] = x.c; if (x.c < 0) dec = true; continue; }
            if (x.isExact() && x.c >= 0) { R.isF[v] = 1; R.iterF[v] = x; continue; }   // reset to a constant
            set<int> d; deps(x, d, 0);
            if (!ok || d.size() > 1 || (d.size() == 1 && *d.begin() != v)) { ok = false; iwhy = "deps x" + to_string(v); break; }''',
'''        for (int v = 0; v < R.nv; ++v) if (inPrefix[v] && ctx.s[v].kind == 'P' && e[v].isExact() && e[v].c >= 0) { R.isF[v] = 1; R.iterF[v] = e[v]; }   // constant resets
        for (int v = 0; v < R.nv && ok; ++v) if (inPrefix[v] && ctx.s[v].kind == 'P') {
            const Lin &x = e[v];
            if (x.n == 1 && x.id[0] == PBASE + v && x.a[0] == 1 && x.D == 1) { R.delta[v] = x.c; if (x.c < 0) dec = true; continue; }
            if (x.isExact() && x.c >= 0) continue;   // constant reset
            set<int> d; deps(x, d, 0);
            for (int u : d) if (u != v && !(R.isF[u] && R.iterF[u].isExact())) { ok = false; iwhy = "deps x" + to_string(v) + " on x" + to_string(u); }
            if (!ok) break;''')
# constants for later iterations in step lambdas
rep('''static IterOrbit iterOrbit(const Rule &R, const Lin &x0) {''', '''static vector<Lin> iterConsts(const Rule &R) {   // constant-reset variables after the first application
    vector<Lin> cv(R.nv); for (auto &l : cv) l.D = 0;
    for (int u = 0; u < R.nv; ++u) if (R.isF[u] && u != R.fvar && R.iterF[u].isExact()) cv[u] = R.iterF[u];
    return cv;
}
static IterOrbit iterOrbit(const Rule &R, const Lin &x0) {''')
rep('''    const int v = R.fvar; const Lin &F = R.iterF[v];
    auto step = [&](const Lin &y) { FEval E; E.zs = &R.zs; E.var = v; E.xval = y; return E.lin(F); };
    IterOrbit O; size_t g0 = GS.size();''', '''    const int v = R.fvar; const Lin &F = R.iterF[v]; vector<Lin> CV = iterConsts(R);
    auto step = [&](const Lin &y) { FEval E; E.zs = &R.zs; E.var = v; E.xval = y; E.consts = &CV; return E.lin(F); };
    IterOrbit O; size_t g0 = GS.size();''')
rep('''            E.consts = nullptr; y = E.lin(F);''', '''            E.consts = &CV; y = E.lin(F);''')
rep('''    const Lin &F = R.iterF[v];
    auto step = [&](const Lin &y) { FEval E; E.zs = &R.zs; E.var = v; E.xval = y; return E.lin(F); };
    if (k.isExact() && k.c <= 64 && !orbitOnly) {''', '''    const Lin &F = R.iterF[v]; vector<Lin> CV = iterConsts(R);
    auto step = [&](const Lin &y) { FEval E; E.zs = &R.zs; E.var = v; E.xval = y; E.consts = &CV; return E.lin(F); };
    if (k.isExact() && k.c <= 64 && !orbitOnly) {''')
# applyRule: first application with the bound constants, then k-1 iterations with the reset constants
rep('''                    Lin nn = (R.iter && R.isF[v]) ? (v == R.fvar ? zIterS(R, bind[v], k) : R.iterF[v]) : (R.affine && R.amul[v] > 1)''',
    '''                    Lin nn = (R.iter && R.isF[v]) ? (v == R.fvar ? iterFirst(R, bind, k) : R.iterF[v]) : (R.affine && R.amul[v] > 1)''')
rep('''static Lin zIterS(const Rule &R, const Lin &x, const Lin &k) {''', '''static Lin zIterS(const Rule &R, const Lin &x, const Lin &k);
// first application with the bound values of the constant-reset variables, then k - 1 further applications (proof-aware)
static Lin iterFirst(const Rule &R, const vector<Lin> &bind, const Lin &k) {
    vector<Lin> cv(R.nv); for (auto &l : cv) l.D = 0;
    for (int u = 0; u < R.nv; ++u) if (R.isF[u] && u != R.fvar && u < (int)bind.size() && bind[u].D != 0) cv[u] = bind[u];
    FEval E; E.zs = &R.zs; E.var = R.fvar; E.xval = bind[R.fvar]; E.consts = &cv;
    Lin y1 = E.lin(R.iterF[R.fvar]);
    if (k.isExact() && k.c == 1) return y1;
    if (!hasProof(y1) && !hasProof(k)) {   // the second iterate's input must satisfy the constraints too
        if (!iterConsOK(R, y1)) UD("iter: constraint");
    }
    return zIterS(R, y1, laddc(k, -1));
}
static Lin zIterS(const Rule &R, const Lin &x, const Lin &k) {''')
open(fn, 'w').write(s)
