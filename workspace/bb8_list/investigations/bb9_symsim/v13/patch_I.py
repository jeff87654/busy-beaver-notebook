import sys
fn = sys.argv[1]; s = open(fn).read()
def rep(a, b, c=1):
    global s
    assert s.count(a) == c, (a[:70], s.count(a))
    s = s.replace(a, b)
checker = r'''
// ------------------------------------------------------------------ v13 --rulecheck: literal validation of AFF / ITER rules
// For a new rule: instantiate its variables with small values satisfying its constraints, apply the rule once (k-fold) to
// get the claimed result, and step the same configuration with plain macro steps (no rules, no template jumps) until the
// claimed configuration appears exactly.  Untouched tape beyond the rule's window is a sentinel run that must not change.
static ll RCPASS = 0, RCFAIL = 0, RCSKIP = 0; static bool RULECHECK = false;
static string cfgCells(const Cfg &c, bool &ok) {
    string L, Rr; ok = true;
    for (auto &r : c.st[0]) { if (!r.n.isExact() || r.n.c > 4000) { ok = false; return ""; } for (i128 t = 0; t < r.n.c; ++t) L += r.w; }
    for (int i = (int)c.st[1].size() - 1; i >= 0; --i) { auto &r = c.st[1][i]; if (!r.n.isExact() || r.n.c > 4000) { ok = false; return ""; } string w(r.w.rbegin(), r.w.rend()); for (i128 t = 0; t < r.n.c; ++t) Rr += w; }
    // strip blank margins far from the head is not needed: both sides carry the same sentinels
    return string(1, char('A' + c.q)) + (c.f ? ">" : "<") + "|" + L + "|" + Rr;
}
static void ruleCheck(const Rule &R0) {
    Rule R = R0; std::mt19937 rng(12345 + (unsigned)R.nv * 7 + (unsigned)R.cons.size());
    size_t g0 = GS.size();
    int tested = 0, passed = 0;
    for (int trial = 0; trial < 300 && tested < 4; ++trial) {
        vector<Lin> bind(R.nv); for (auto &b : bind) b.D = 0;
        // lower bounds from single-variable constraints
        vector<i128> lb(R.nv, 1);
        for (auto &cn : R.cons) if (cn.k == 'G' && cn.N.n == 1 && cn.N.id[0] >= PBASE && cn.N.a[0] > 0) { int v = cn.N.id[0] - PBASE; if (v < R.nv) lb[v] = max(lb[v], cdiv(-cn.N.c, cn.N.a[0])); }
        for (int s2 = 0; s2 < 2; ++s2) for (size_t i = 0; i < R.g[s2].size(); ++i) { int v = R.rv[s2][i]; if (v >= 0) bind[v] = LC(lb[v] + (i128)(rng() % (trial < 100 ? 4 : 13))); }
        bool ok = true;
        try {
            for (auto &cn : R.cons) {
                Lin val = subst(cn.N, bind); if (!val.isExact()) { ok = false; break; }
                if (cn.k == 'G' && val.c < 0) ok = false;
                if (cn.k == 'E' && val.c != 0) ok = false;
                if (cn.k == 'C' && pmod(val.c, cn.q) != cn.r) ok = false;
                if (!ok) break;
            }
        } catch (Undec &) { ok = false; }
        if (!ok) continue;
        Cfg c0; c0.q = R.q; c0.f = R.f;
        for (int s2 = 0; s2 < 2; ++s2) {
            if (!R.bottom[s2]) c0.st[s2].push_back(Run{"0110", LC(1000), KT_SENT});
            for (int i = (int)R.g[s2].size() - 1; i >= 0; --i) { int v = R.rv[s2][i]; c0.st[s2].push_back(Run{R.g[s2][i].w, v >= 0 ? bind[v] : R.g[s2][i].n, -1}); }
        }
        // claimed result
        Sim A; A.c = c0; A.prover = false; A.ktOK = 0; A.chOK = false; RuleSet RS1; A.rules = &RS1;
        int st;
        try { st = A.applyRule(R); } catch (...) { st = -1; }
        if (st != S_OK) continue;
        bool okA; string target = cfgCells(A.c, okA);
        if (!okA) { continue; }
        ++tested;
        // literal stepping
        Sim P; P.c = c0; P.prover = false; P.ktOK = 0; P.chOK = false; RuleSet RS0; P.rules = &RS0; P.track = true;
        bool hit = false;
        try {
            for (ll t = 0; t < 3000000; ++t) {
                if (P.macroStep() != S_OK) break;
                if (P.maxTag[0] >= KT_SENT || P.maxTag[1] >= KT_SENT) break;
                if (P.c.q == A.c.q && P.c.f == A.c.f) { bool okP; string cur = cfgCells(P.c, okP); if (!okP) break; if (cur == target) { hit = true; break; } }
            }
        } catch (...) {}
        if (hit) ++passed;
        else if (SHOWPROOF || RULECHECK) {
            bool o1; fprintf(stderr, "RULECHECK-FAIL %s instance: start %s\n   claimed %s\n", R.iter ? "ITER" : "AFF", cfgCells(c0, o1).substr(0, 300).c_str(), target.substr(0, 300).c_str());
        }
    }
    GS.resize(g0);
    if (tested == 0) ++RCSKIP; else if (passed == tested) ++RCPASS; else ++RCFAIL;
    fprintf(stderr, "RULECHECK %s tested=%d passed=%d\n", R.iter ? "ITER" : "AFF", tested, passed);
}
'''
rep('''static int tryProve0(Sim &M, ll delta);
static ll PROOFOOM = 0;''', '''static int tryProve0(Sim &M, ll delta);
static ll PROOFOOM = 0;
static const int KT_SENT = 1000000;''' + checker)
rep('''}
static const int KT_SENT = 1000000;
// run from START''', '''}
// run from START''')
rep('''            if (o.st == 1) { addRule(M, o.rule); ++PROOFOK; return 1; }''', '''            if (o.st == 1) { addRule(M, o.rule); ++PROOFOK; if (RULECHECK && !M.proof && (o.rule.affine || o.rule.iter)) ruleCheck(o.rule); return 1; }''')
rep('''        else if (a == "--noretry") RETRY = false;''', '''        else if (a == "--noretry") RETRY = false;
        else if (a == "--rulecheck") RULECHECK = true;''')
rep('''    if (ITERSTAT) fprintf(stderr, "ITERSTAT''', '''    if (RULECHECK) fprintf(stderr, "RULECHECK-SUMMARY pass=%lld fail=%lld skip=%lld\\n", RCPASS, RCFAIL, RCSKIP);
    if (ITERSTAT) fprintf(stderr, "ITERSTAT''')
open(fn, 'w').write(s)
