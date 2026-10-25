import sys
fn = sys.argv[1]; s = open(fn).read()
def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:70], s.count(old))
    s = s.replace(old, new)
# computeAff next to computeP
rep('''    Lin computeP(const Lin &k, const Lin &r) {''', '''    // v13: k-fold affine map x -> a x + c (a >= 2, c >= 0) with proof arguments: proof symbol Z sub 'A'
    //      (z.A = a, z.J = c, z.K = k, z.B = x), shadow = the global value at the shadows
    Lin computeAff(const Lin &x, i128 a, i128 c, const Lin &k) {
        if (!hasProof(x) && !hasProof(k)) return affPow(x, a, c, k);
        if (k.isExact() && k.c == 0) return x;
        if (k.isExact() && k.c <= 3) { Lin y = x; for (i128 t = 0; t < k.c; ++t) y = laddc(lscale(y, a), c); return y; }
        Lin sh = affPow(shadowOf(x), a, c, shadowOf(k));
        PSym z{'Z', sh, LC(c), x}; z.sub = 'A'; z.A = LC(a); z.K = k; PC->s.push_back(z);
        return LV(PBASE + (int)PC->s.size() - 1);
    }
    Lin computeP(const Lin &k, const Lin &r) {''')
# LBZ
rep('''        if (z.sub == 'P') { i128 w = LBe(z.B) + 4, k = min<i128>(LBe(z.A), 120);''', '''        if (z.sub == 'A') {   // a^k x + ...: iterate the lower bound min(lb k, 128) times
            i128 w = LBe(z.B), a = z.A.c, cc = z.J.c, k = min<i128>(LBe(z.K), 128);
            for (i128 t = 0; t < k && w < SYMCAP; ++t) { i128 u; if (__builtin_mul_overflow(w, a, &u) || __builtin_add_overflow(u, cc, &w) || w > SYMCAP) w = SYMCAP; }
            w = min(w, SYMCAP); lbz[v] = w; return w;
        }
        if (z.sub == 'P') { i128 w = LBe(z.B) + 4, k = min<i128>(LBe(z.A), 120);''')
# resZ
rep('''        if (z.sub == 'P') {   // 2^k (r+4) - 4''', '''        if (z.sub == 'A') {   // orbit of r -> a r + c (mod MG) from the residue of x, indexed by k
            i128 a = z.A.c, cc = z.J.c;
            ll r0 = resAbs(z.B, MG);
            vector<ll> seq; map<ll, int> seen; int mu = -1, lam = -1; ll r = r0;
            for (int t = 0; t < 200000; ++t) { auto it = seen.find(r); if (it != seen.end()) { mu = it->second; lam = t - it->second; break; } seen[r] = t; seq.push_back(r); r = (ll)pmod((i128)a * r + cc, MG); }
            if (lam < 0) UD("Z-A orbit");
            ll rr;
            if (z.K.isExact()) rr = z.K.c < (i128)seq.size() ? seq[(size_t)z.K.c] : seq[(size_t)(mu + pmod(z.K.c - mu, lam))];
            else { requireLB(z.K, (i128)seq.size()); if (MG % lam != 0) UD("Z-A: orbit period"); rr = seq[(size_t)(mu + pmod((i128)resAbs(z.K, lam) - mu, lam))]; }
            return rr % m;
        }
        if (z.sub == 'P') {   // 2^k (r+4) - 4''')
# applyRule: allow affine rules in proof mode
rep('''            if (R.affine && proof) return -1;   // affine rules only in main mode''', '''            if (R.affine && proof && !PAFF) return -1;   // affine rules in proof mode only with v13 --paff (default on)''')
rep('''                    Lin nn = (R.affine && R.amul[v] > 1) ? affPow(bind[v], R.amul[v], R.delta[v], k) : lcomb(bind[v], 1, k, R.delta[v]); normCount(nn);''',
    '''                    Lin nn = (R.affine && R.amul[v] > 1) ? (proof ? computeAff(bind[v], R.amul[v], R.delta[v], k) : affPow(bind[v], R.amul[v], R.delta[v], k)) : lcomb(bind[v], 1, k, R.delta[v]); normCount(nn);''')
rep('static bool NOAFF = false, KTFORCE = false, AFFC = true;', 'static bool NOAFF = false, KTFORCE = false, AFFC = true, PAFF = true;')
rep('''        else if (a == "--noaffc") AFFC = false;''', '''        else if (a == "--noaffc") AFFC = false;
        else if (a == "--nopaff") PAFF = false;''')
open(fn, 'w').write(s)
