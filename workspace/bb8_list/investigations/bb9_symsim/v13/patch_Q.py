import sys
fn = sys.argv[1]; s = open(fn).read()
def rep(a, b, c=1):
    global s
    assert s.count(a) == c, (a[:70], s.count(a))
    s = s.replace(a, b)
# rule check status per rule
rep('    bool grows = false; ll uid = 0; int lvar = -1;', '    bool grows = false; ll uid = 0; int lvar = -1;\n    int rc = -1, rcK = 0;   // v14 --rulecheck: -1 unchecked, 0 literal FAIL, 1 literal PASS, 2 untestable; rcK: largest k checked')
# Sim: last k of a rule application, used-rule set
rep('    ll macro = 0, jumps = 0, ruleApps = 0, affApps = 0, iterApps = 0, iterStops = 0, iterSym = 0;',
    '    ll macro = 0, jumps = 0, ruleApps = 0, affApps = 0, iterApps = 0, iterStops = 0, iterSym = 0; Lin lastK; set<int> usedRules;')
rep('''            ++R.uses; ++ruleApps; if (R.affine) ++affApps;''', '''            lastK = k;
            ++R.uses; ++ruleApps; if (R.affine) ++affApps;''')
rep('''        for (int id : it->second) { int r = applyRule(rules->R[id]); if (r >= 0) return r; }''',
    '''        for (int id : it->second) { int r = applyRule(rules->R[id]); if (r >= 0) { if (!proof) usedRules.insert(id); return r; } }''')
# ruleCheck returns the status
rep('static void ruleCheck(const Rule &R0) {', 'static pair<int, int> ruleCheck(const Rule &R0) {')
rep('''    int tested = 0, passed = 0;
    for (int trial = 0; trial < 300 && tested < 4; ++trial) {''', '''    int tested = 0, passed = 0, maxK = 0;
    for (int trial = 0; trial < 300 && tested < 6; ++trial) {''')
rep('''        if (st != S_OK) continue;
        bool okA; string target = cfgCells(A.c, okA);
        if (!okA) { continue; }
        ++tested;''', '''        if (st != S_OK) continue;
        bool okA; string target = cfgCells(A.c, okA);
        if (!okA) { continue; }
        ++tested; int kk = A.lastK.isExact() ? (int)min<i128>(A.lastK.c, 1000000) : 0;''')
rep('''        if (hit) ++passed;''', '''        if (hit) { ++passed; maxK = max(maxK, kk); }''')
rep('''    if (tested == 0) ++RCSKIP; else if (passed == tested) ++RCPASS; else ++RCFAIL;
    fprintf(stderr, "RULECHECK %s tested=%d passed=%d\\n", R.iter ? "ITER" : "AFF", tested, passed);
}''', '''    if (tested == 0) ++RCSKIP; else if (passed == tested) ++RCPASS; else ++RCFAIL;
    if (SHOWPROOF) fprintf(stderr, "RULECHECK %s tested=%d passed=%d maxk=%d\\n", R.iter ? "ITER" : R.affine ? "AFF" : "LIN", tested, passed, maxK);
    return {tested == 0 ? 2 : passed == tested ? 1 : 0, maxK};
}''')
rep('''            if (o.st == 1) { addRule(M, o.rule); ++PROOFOK; if (RULECHECK && !M.proof && (o.rule.affine || o.rule.iter)) ruleCheck(o.rule); return 1; }''',
    '''            if (o.st == 1) {
                size_t before = M.rules->R.size(); addRule(M, o.rule); ++PROOFOK;
                if (RULECHECK && !M.proof && M.rules->R.size() > before) { auto pr = ruleCheck(M.rules->R.back()); M.rules->R.back().rc = pr.first; M.rules->R.back().rcK = pr.second; }
                return 1;
            }''')
# report used-rule check status in the R line
rep('''    printf("R %s %c %s %s kt=%d kj=%lld''', '''    string rcu;
    {
        int np = 0, nf = 0, nu = 0; map<string, int> unk;
        for (int id : M.usedRules) {
            const Rule &R = RS.R[id]; string kind = R.iter ? "ITER" : R.affine ? "AFF" : "LIN";
            if (R.rc == 1 && (!R.iter || R.rcK >= 2)) ++np; else if (R.rc == 0) { ++nf; unk[kind + "-FAIL"]++; } else { ++nu; unk[kind + (R.rc == 1 ? "-k1only" : R.rc == 2 ? "-untestable" : "-unchecked")]++; }
        }
        rcu = "rcu=" + to_string(np) + "/" + to_string(nf) + "/" + to_string(nu);
        for (auto &pr : unk) rcu += "," + pr.first + ":" + to_string(pr.second);
    }
    printf("R %s %c %s %s kt=%d kj=%lld''')
rep('''apps=%lld syms=%zu it=%lld bc=%lld sc=%lld its=%lld |%s |%s\\n", mach.c_str()''', '''apps=%lld syms=%zu it=%lld bc=%lld sc=%lld its=%lld %s |%s |%s\\n", mach.c_str()''')
rep('''RS.R.size(), M.ruleApps, GS.size(), M.iterApps, M.bigClears, M.symClears, M.iterSym, jl.c_str(), sd.c_str());''',
    '''RS.R.size(), M.ruleApps, GS.size(), M.iterApps, M.bigClears, M.symClears, M.iterSym, rcu.c_str(), jl.c_str(), sd.c_str());''')
open(fn, 'w').write(s)
