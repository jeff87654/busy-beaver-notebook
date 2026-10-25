import sys
fn = sys.argv[1]; s = open(fn).read()
def rep(a, b, c=1):
    global s
    assert s.count(a) == c, (a[:70], s.count(a))
    s = s.replace(a, b)
# iterConsOK with a shared evaluator
rep('''static bool iterConsOK(const Rule &R, const Lin &y) {
    vector<Lin> cv(R.nv); for (auto &l : cv) l.D = 0;
    for (int u = 0; u < R.nv; ++u) if (R.isF[u] && u != R.fvar) cv[u] = R.iterF[u];
    for (auto &cn : R.zcons) {
        FEval E; E.zs = &R.zs; E.var = R.fvar; E.xval = y; E.consts = &cv;
        Lin N = E.lin(cn.N);''', '''static bool iterConsOK(const Rule &R, const Lin &y, FEval *EP = nullptr) {
    vector<Lin> cv(R.nv); for (auto &l : cv) l.D = 0;
    for (int u = 0; u < R.nv; ++u) if (R.isF[u] && u != R.fvar) cv[u] = R.iterF[u];
    FEval E0; E0.zs = &R.zs; E0.var = R.fvar; E0.xval = y;
    FEval &E = EP ? *EP : E0; E.consts = &cv;
    for (auto &cn : R.zcons) {
        Lin N = E.lin(cn.N);''')
rep('''            if (!iterConsOK(R, y)) UD("iter: constraint");
            y = step(y);
        }
    } catch (...) { GS.resize(g0); throw; }''', '''            FEval E; E.zs = &R.zs; E.var = v; E.xval = y;
            if (!iterConsOK(R, y, &E)) UD("iter: constraint");
            E.consts = nullptr; y = E.lin(F);
        }
    } catch (...) { GS.resize(g0); throw; }''')
# result cache in iterPow's orbit path
rep('''    if (!k.isExact() && !R.grows) UD("iter: symbolic count without growth witness");
    IterOrbit O = iterOrbit(R, x0);''', '''    if (!k.isExact() && !R.grows) UD("iter: symbolic count without growth witness");
    // result cache: (rule, x0 abstraction, k abstraction) -> (residue, lower bound)
    static map<string, pair<ll, i128>> PC2;
    auto lkey = [](const Lin &e, string &out) -> bool {
        if (e.isExact()) { out += "e" + s128(e.c) + ";"; return true; }
        if (e.n != 1 || GS[e.id[0]].mod != MG) return false;
        out += "s" + s128(e.a[0]) + "," + s128(e.c) + "," + s128(e.D) + "," + s128(GS[e.id[0]].lb) + "," + to_string(GS[e.id[0]].res) + ";";
        return true;
    };
    string ck = to_string(R.uid) + ":"; bool cOK = lkey(x0, ck) && lkey(k, ck);
    if (cOK) { auto it = PC2.find(ck); if (it != PC2.end()) { ++ITERHIT; ++wSymCount; return LV(newG(max(it->second.second, (i128)1), it->second.first, "T(" + linstr(k) + "," + linstr(x0) + ")")); } }
    IterOrbit O = iterOrbit(R, x0);''')
rep('''    // growing F: F^k(x0) >= x0 + k, so the bound also covers k
    if (R.grows) { i128 kl = k.isExact() ? k.c : lbG(k); i128 l0 = x0.isExact() ? x0.c : lbG(x0); i128 s2; if (!__builtin_add_overflow(l0, kl, &s2)) lb = max(lb, min(s2, SYMCAP)); }
    ++wSymCount;''', '''    // growing F: F^k(x0) >= x0 + k, so the bound also covers k
    if (R.grows) { i128 kl = k.isExact() ? k.c : lbG(k); i128 l0 = x0.isExact() ? x0.c : lbG(x0); i128 s2; if (!__builtin_add_overflow(l0, kl, &s2)) lb = max(lb, min(s2, SYMCAP)); }
    if (cOK) { if (PC2.size() > 500000) PC2.clear(); PC2[ck] = {rr, lb}; }
    ++wSymCount;''')
open(fn, 'w').write(s)
