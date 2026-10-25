import sys
fn = sys.argv[1]; s = open(fn).read()
def rep(a, b, c=1):
    global s
    assert s.count(a) == c, (a[:70], s.count(a))
    s = s.replace(a, b)
# splice the new ITER block
i0 = s.index('static Lin zIterS(const Rule &R, const Lin &x, const Lin &k);')
i1 = s.index('struct RuleSet {', i0)
s = s[:i0] + open(sys.argv[2]).read() + s[i1:]
rep('static Lin iterPow(const Rule &R, int v, const Lin &x0, const Lin &k, bool orbitOnly = false);',
    'static Lin iterPow(const Rule &R, int v, const Lin &x0, const Lin &k, bool orbitOnly, const Lin &j0);')
rep('    bool grows = false; ll uid = 0;', '    bool grows = false; ll uid = 0; int lvar = -1;   // lvar: a counter (delta > 0) that F may read')
# Pres LBZ / resZ
rep('''        if (z.sub == 'T') { i128 w = lbNodeT(*z.rp, LBe(z.B), max<i128>(LBe(z.K), 1)); lbz[v] = w; return w; }''',
    '''        if (z.sub == 'T') { i128 w = lbNodeT(*z.rp, LBe(z.B), max<i128>(LBe(z.K), 1), LBe(z.J)); lbz[v] = w; return w; }''')
rep('''            Lin x0;
            if (!hasProof(z.B)) x0 = z.B;
            else { ll rB = resAbs(z.B, MG); i128 lbB = LBe(z.B); x0 = LV(newG(max(lbB, (i128)0), rB, "tfake")); }
            ll rr;
            if (z.K.isExact() && z.K.c <= 64) rr = resG(iterPow(RR, RR.fvar, x0, z.K), MG);
            else {
                IterOrbit O = iterOrbit(RR, x0);''', '''            Lin x0, j0 = LC(0);
            if (!hasProof(z.B)) x0 = z.B;
            else { ll rB = resAbs(z.B, MG); i128 lbB = LBe(z.B); x0 = LV(newG(max(lbB, (i128)0), rB, "tfake")); }
            if (RR.lvar >= 0) { if (!hasProof(z.J)) j0 = z.J; else j0 = LV(newG(max(LBe(z.J), (i128)0), 0, "tjfake", 1)); }
            ll rr;
            if (z.K.isExact() && z.K.c <= 64) rr = resG(iterPow(RR, RR.fvar, x0, z.K, false, j0), MG);
            else {
                IterOrbit O = iterOrbit(RR, x0, j0);''')
# classification: deltas first, then the F variable may read one increasing counter
rep('''        for (int v = 0; v < R.nv; ++v) if (inPrefix[v] && ctx.s[v].kind == 'P' && e[v].isExact() && e[v].c >= 0) { R.isF[v] = 1; R.iterF[v] = e[v]; }   // constant resets''',
    '''        for (int v = 0; v < R.nv; ++v) if (inPrefix[v] && ctx.s[v].kind == 'P' && e[v].isExact() && e[v].c >= 0) { R.isF[v] = 1; R.iterF[v] = e[v]; }   // constant resets
        for (int v = 0; v < R.nv; ++v) if (inPrefix[v] && ctx.s[v].kind == 'P') { const Lin &x = e[v]; if (x.n == 1 && x.id[0] == PBASE + v && x.a[0] == 1 && x.D == 1) R.delta[v] = x.c; }''')
rep('''            for (int u : d) if (u != v && !(R.isF[u] && R.iterF[u].isExact())) { ok = false; iwhy = "deps x" + to_string(v) + " on x" + to_string(u); }''',
    '''            for (int u : d) if (u != v && !(R.isF[u] && R.iterF[u].isExact())) {
                bool counter = inPrefix[u] && !R.isF[u] && e[u].n == 1 && e[u].id[0] == PBASE + u && e[u].a[0] == 1 && e[u].D == 1 && e[u].c > 0;
                if (counter && (R.lvar < 0 || R.lvar == u)) { R.lvar = u; continue; }
                ok = false; iwhy = "deps x" + to_string(v) + " on x" + to_string(u);
            }''')
rep('''            R.cons.clear(); R.cskip.clear(); R.zcons.clear(); R.zs.clear(); R.fvar = -1;''',
    '''            R.cons.clear(); R.cskip.clear(); R.zcons.clear(); R.zs.clear(); R.fvar = -1; R.lvar = -1;''')
# the counter's lower bound (for linLB / flb)
rep('''                int v = cn.N.id[0] - PBASE; if (R.isF[v]) R.flb[v] = max(R.flb[v], cdiv(-cn.N.c, cn.N.a[0]));''',
    '''                int v = cn.N.id[0] - PBASE; if (R.isF[v] || v == R.lvar) R.flb[v] = max(R.flb[v], cdiv(-cn.N.c, cn.N.a[0]));''')
rep('''                if (idx == var) t.a = 1;
                else if (R.isF.size() > (size_t)idx && R.isF[idx] && R.iterF[idx].isExact()) t.b = (long double)R.iterF[idx].c;''',
    '''                if (idx == var) t.a = 1;
                else if (idx == R.lvar) t.b = (long double)R.flb[idx];
                else if (R.isF.size() > (size_t)idx && R.isF[idx] && R.iterF[idx].isExact()) t.b = (long double)R.iterF[idx].c;''')
# lbForm calls from linLB need the counter bound
rep('''                map<int, i128> m; i128 lbB = lbForm(R, zs, z.B, var, ylb, m);''',
    '''                map<int, i128> m; i128 lbB = lbForm(R, zs, z.B, var, ylb, m, 0, R.lvar >= 0 ? R.flb[R.lvar] : 0);''')
open(fn, 'w').write(s)
