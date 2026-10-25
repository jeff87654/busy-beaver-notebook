import sys
fn = sys.argv[1]; s = open(fn).read()
def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:70], s.count(old))
    s = s.replace(old, new)
# 1. PSym gets a rule pointer (sub 'T')
rep('''struct PSym { char kind; Lin shadow; Lin J, B; char sub = 'W'; Lin A, K; };''',
    '''struct Rule;
struct PSym { char kind; Lin shadow; Lin J, B; char sub = 'W'; Lin A, K; std::shared_ptr<Rule> rp; };   // v13: sub 'A' (affine k-fold), 'T' (ITER rule k-fold, rp)''')
# 2. replace the Rule .. iterPow block
i0 = s.index('struct Rule {\n    int q, f;')
i1 = s.index('struct RuleSet {', i0)
s = s[:i0] + open(sys.argv[2]).read() + s[i1:]
# 3. Sim::computeAff -> zAffS
rep('''                    Lin nn = (R.iter && R.isF[v]) ? iterPow(R, v, bind[v], k) : (R.affine && R.amul[v] > 1) ? (proof ? computeAff(bind[v], R.amul[v], R.delta[v], k) : affPow(bind[v], R.amul[v], R.delta[v], k)) : lcomb(bind[v], 1, k, R.delta[v]); normCount(nn);''',
    '''                    Lin nn = (R.iter && R.isF[v]) ? (v == R.fvar ? zIterS(R, bind[v], k) : R.iterF[v]) : (R.affine && R.amul[v] > 1) ? zAffS(bind[v], R.amul[v], R.delta[v], k) : lcomb(bind[v], 1, k, R.delta[v]); normCount(nn);''')
# 4. ITER rules in proof mode; first-application checks proof-aware
rep('''            if (R.iter && proof) return -1;   // ITER rules: main mode only
            if (R.iter) {   // Z constraints at the first application (input = the bound values)''',
    '''            if (R.iter && proof && !PITER) return -1;
            if (R.iter) {   // Z constraints at the first application (input = the bound values; proof-aware)''')
rep('''                    bool okz = cn.k == 'G' ? sgnG(N) >= 0 : cn.k == 'E' ? (N.isExact() && N.c == 0) : (i128)resG(N, (ll)cn.q) == cn.r;''',
    '''                    bool okz = cn.k == 'G' ? sgn(N) >= 0 : cn.k == 'E' ? sgn(N) == 0 : (i128)res(N, (ll)cn.q) == cn.r;''')
rep('static bool NOAFF = false, KTFORCE = false, AFFC = true, PAFF = true, ITERON = true;',
    'static bool NOAFF = false, KTFORCE = false, AFFC = true, PAFF = true, ITERON = true, PITER = true;')
rep('''        else if (a == "--noiter") ITERON = false;''', '''        else if (a == "--noiter") ITERON = false;
        else if (a == "--nopiter") PITER = false;''')
# 5. Pres LBZ / resZ for 'A' (already) and 'T'
rep('''        if (z.sub == 'A') {   // a^k x + ...: iterate the lower bound min(lb k, 128) times''',
    '''        if (z.sub == 'T') { i128 w = lbNodeT(*z.rp, LBe(z.B), max<i128>(LBe(z.K), 1)); lbz[v] = w; return w; }
        if (z.sub == 'A') {   // a^k x + ...: iterate the lower bound min(lb k, 128) times''')
rep('''        if (z.sub == 'A') {   // orbit of r -> a r + c (mod MG) from the residue of x, indexed by k''',
    '''        if (z.sub == 'T') {   // orbit of the ITER rule's iterates from an abstraction of x (lower bound, residue), indexed by k
            const Rule &RR = *z.rp;
            Lin x0;
            if (!hasProof(z.B)) x0 = z.B;
            else { ll rB = resAbs(z.B, MG); i128 lbB = LBe(z.B); x0 = LV(newG(max(lbB, (i128)0), rB, "tfake")); }
            ll rr;
            if (z.K.isExact() && z.K.c <= 64) rr = resG(iterPow(RR, RR.fvar, x0, z.K), MG);
            else {
                IterOrbit O = iterOrbit(RR, x0);
                if (z.K.isExact()) { i128 t = z.K.c - 1; size_t i = t < (i128)O.rs.size() ? (size_t)t : (size_t)(O.mu + pmod(t - O.mu, O.lam)); rr = O.rs[i]; }
                else { requireLB(z.K, (i128)O.rs.size() + 1); if (MG % O.lam != 0) UD("Z-T: orbit period"); rr = O.rs[(size_t)(O.mu + pmod((i128)resAbs(z.K, O.lam) - 1 - O.mu, O.lam))]; }
            }
            return rr % m;
        }
        if (z.sub == 'A') {   // orbit of r -> a r + c (mod MG) from the residue of x, indexed by k''')
# 6. nonneg: 'T' requires the inner rule's growth witness
rep('''                if (z.sub == 'A' && (z.A.c < 2 || z.J.c < 0)) return false;''',
    '''                if (z.sub == 'A' && (z.A.c < 2 || z.J.c < 0)) return false;
                if (z.sub == 'T' && !(z.rp && z.rp->grows)) return false;   // F^k increasing in k needs F(y) > y''')
# 7. growth witness after the constraint loop
rep('''            if (okc && lim) {
                R.iter = true; R.stepsKnown = false;''', '''            if (okc && lim) {
                // growth witness F(y) >= y + 1 for y >= flb: a linear lower bound F(y) >= alpha y + beta (exact rationals)
                try { R.grows = iterGrows(R); } catch (Undec &) { R.grows = false; }
                R.iter = true; R.stepsKnown = false;''')
# linear lower bound helper (before the Pres struct)
rep('''struct ProofOut { int st = 0; string why; Rule rule; string kind; };''', r'''// v13: linear lower bound alpha*y + beta (rationals num/den, den > 0) of a monotone formula over zs in y = var, valid for
// y >= ylb.  A(a,c,K,B) >= B (1 + (a-1) K) (Bernoulli, B >= lbB >= 1 constant part used); P(k,r) >= (k+1)(r+4) - 4;
// T(K,B) >= B + K when the inner rule grows; other nodes: their constant lower bound.
struct LinLB { long double a = 0, b = 0; };   // only used for the yes/no growth decision with a safety margin
static LinLB linLB(const Rule &R, const vector<PSym> &zs, const Lin &e, int var, i128 ylb, int depth = 0) {
    if (depth > 40) UD("linLB depth");
    LinLB r; r.b = (long double)e.c;
    for (int k = 0; k < e.n; ++k) {
        if (e.a[k] < 0) UD("linLB: negative coefficient");
        long double ak = (long double)e.a[k]; LinLB t;
        if (e.id[k] < PBASE) t.b = (long double)GS[e.id[k]].lb;
        else {
            int idx = e.id[k] - PBASE; const PSym &z = zs[idx];
            if (z.kind == 'P') {
                if (idx == var) t.a = 1;
                else if (R.isF.size() > (size_t)idx && R.isF[idx] && R.iterF[idx].isExact()) t.b = (long double)R.iterF[idx].c;
                else UD("linLB: foreign variable");
            } else if (z.sub == 'A') {
                map<int, i128> m; i128 lbB = lbForm(R, zs, z.B, var, ylb, m);
                LinLB K = linLB(R, zs, z.K, var, ylb, depth + 1);
                if (lbB < 1) UD("linLB: A base");
                t.a = (long double)lbB * (long double)(z.A.c - 1) * K.a; t.b = (long double)lbB * (1.0L + (long double)(z.A.c - 1) * K.b);
            } else if (z.sub == 'P') {
                LinLB K = linLB(R, zs, z.A, var, ylb, depth + 1), Rr = linLB(R, zs, z.B, var, ylb, depth + 1);
                if (Rr.a == 0) { t.a = K.a * (Rr.b + 4); t.b = (K.b + 1) * (Rr.b + 4) - 4; } else { map<int, i128> m; t.b = (long double)lbForm(R, zs, LV(PBASE + idx), var, ylb, m); }
            } else if (z.sub == 'T') {
                if (!(z.rp && z.rp->grows)) UD("linLB: T without growth");
                LinLB K = linLB(R, zs, z.K, var, ylb, depth + 1), Bb = linLB(R, zs, z.B, var, ylb, depth + 1);
                t.a = K.a + Bb.a; t.b = K.b + Bb.b;
            } else { map<int, i128> m; t.b = (long double)lbForm(R, zs, LV(PBASE + idx), var, ylb, m); }
        }
        r.a += ak * t.a; r.b += ak * t.b;
    }
    // floor division: x / D >= (x - (D - 1)) / D
    long double D = (long double)e.D; r.a /= D; r.b = (r.b - (D - 1)) / D;
    return r;
}
static bool iterGrows(const Rule &R) {
    int v = R.fvar; i128 ylb = R.flb[v];
    LinLB L = linLB(R, R.zs, R.iterF[v], v, ylb);
    // F(y) >= a y + b >= y + 1 for y >= ylb when a >= 1 and a ylb + b >= ylb + 1 (margin 1e-6 relative for rounding)
    if (!(L.a >= 1.0L + 1e-9L)) return false;
    long double lhs = L.a * (long double)ylb + L.b, rhs = (long double)ylb + 1;
    return lhs >= rhs + 1e-6L * (fabsl(rhs) + 1);
}
struct ProofOut { int st = 0; string why; Rule rule; string kind; };''')
open(fn, 'w').write(s)
