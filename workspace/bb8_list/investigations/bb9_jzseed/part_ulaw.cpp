// ------------------------------------------------------------------ U residue law (Jacobzheng's digit cascade)
// U_0(x) = 3x+7, U_(j+1)(x) = iter (x - 2j) U_j X_j, X_0 = 7, X_(j+1) = U_j(U_j(X_j))     (Coq UX, BB9_fw2_1RB0RD.v)
// CDPx: Kd (0^j ++ v :: Us) 0 B -->* Kd (0^(j+1) ++ Us) 0 (iter v (U j) B) when 2j <= B;  Ugrow: U_j(x) >= x + 2j + 5.
// Value classes: exact v (<= VT) or huge (value >= HUGEMIN, residue mod MG known).
struct VC { bool huge; i128 v; ll r; };
static i128 VT = (i128)1 << 100;
static i128 REPBASE = 0;   // --rep B: huge cascade values replaced by the representative >= B with the right residue (NOT sound; screening)   // --vt (validation: smaller VT turns more values into classes)
static const i128 HUGEMIN = (i128)1 << 64;
static VC vexact(i128 v) { if (v > VT) return VC{true, 0, (ll)pmod(v, MG)}; return VC{false, v, 0}; }
static bool vcEq(const VC &a, const VC &b) { return a.huge == b.huge && (a.huge ? a.r == b.r : a.v == b.v); }
struct UTab { int h = 0; vector<i128> pre; int mu = 0, lam = 1; vector<ll> res; };
static vector<UTab> UT;      // UT[j], j >= 2: s_t = U_(j-1)^t (X_(j-1));  U_j(x) = s_(max(0, x - 2(j-1)))
static vector<VC> XC;        // classes of X_j
static int JINF = -1, JMAX = 48;
static const int INFJ = 1 << 30;   // "symbolic depth >= JINF": U_j = U_JINF on huge arguments
static ll LAM2; static int A3;
static ll powmod(ll b, i128 e, ll m) { i128 r = 1 % m, x = b % m; while (e > 0) { if (e & 1) r = r * x % m; x = x * x % m; e >>= 1; } return (ll)r; }
static VC U1res(i128 e) { ll m2 = 2 * MG; ll t = powmod(3, e, m2); ll u = (ll)pmod((i128)21 * t - 7, m2); return VC{true, 0, (u / 2) % MG}; }
static VC UV(int j, const VC &x);
static VC tabAt(const UTab &T, i128 t) {
    if (t < T.h) return VC{false, T.pre[(size_t)t], 0};
    i128 u = t - T.h; if (u < T.mu) return VC{true, 0, T.res[(size_t)u]};
    return VC{true, 0, T.res[(size_t)(T.mu + pmod(u - T.mu, T.lam))]};
}
static VC tabHuge(const UTab &T, int j, ll xr) {   // x huge, x == xr mod MG, t = x - 2(j-1) in the periodic part
    return VC{true, 0, T.res[(size_t)(T.mu + pmod((i128)xr - 2 * (j - 1) - T.h - T.mu, T.lam))]};
}
static VC UV(int j, const VC &x) {
    if (j == 0) { if (!x.huge) return vexact(3 * x.v + 7); return VC{true, 0, (ll)((3 * (i128)x.r + 7) % MG)}; }
    if (j == 1) {
        if (!x.huge) { if (x.v <= 60) { i128 p = 1; for (int i = 0; i < x.v; ++i) p *= 3; return vexact((21 * p - 7) / 2); } return U1res(x.v); }
        return U1res(A3 + pmod((i128)x.r - A3, LAM2));
    }
    if (j == INFJ || j > JMAX) {
        if (x.huge) return tabHuge(UT[JINF], JINF, x.r);
        // exact x at depth j > JMAX: U_j(x) = s_t, t = x - 2(j-1), with the same orbit s_t = G^t(xi) as table JMAX
        // (all X_j == xi and U_j == G on huge arguments for j >= JINF); for symbolic j the caller guarantees x >= 2j
        // (t >= 2), and table JMAX is purely periodic, so only the parity of t (= parity of x) matters
        const UTab &T = UT[JMAX];
        if (T.h != 0 || T.mu != 0 || JMAX < JINF + 2) UD("U: exact argument at deep j");
        if (j == INFJ) return tabAt(T, 2 + (x.v & 1));
        i128 t = x.v - 2 * ((i128)j - 1); if (t < 0) t = 0; return tabAt(T, t);
    }
    const UTab &T = UT[j];
    if (!x.huge) { i128 t = x.v - 2 * (j - 1); if (t < 0) t = 0; return tabAt(T, t); }
    return tabHuge(T, j, x.r);
}
static bool ftabEq(int a, int b) {   // U_a and U_b agree on huge arguments
    for (ll r = 0; r < MG; ++r) if (!vcEq(tabHuge(UT[a], a, r), tabHuge(UT[b], b, r))) return false;
    return true;
}
static bool ftabParity(int a) { for (ll r = 0; r + 2 < MG; ++r) if (!vcEq(tabHuge(UT[a], a, r), tabHuge(UT[a], a, r + 2))) return false; return true; }
static void buildU() {
    ll m2 = 2 * MG; A3 = 0; ll mm = m2; while (mm % 3 == 0) { mm /= 3; ++A3; }
    LAM2 = 1; { ll x = 3 % mm; while (x != 1 % mm) { x = x * 3 % mm; ++LAM2; } if (mm == 1) LAM2 = 1; }
    if (MG % LAM2 != 0) { fprintf(stderr, "MG=%lld: ord of 3 (%lld) does not divide MG\n", MG, LAM2); exit(2); }
    UT.assign(JMAX + 1, UTab{}); XC.assign(JMAX + 1, VC{});
    XC[0] = vexact(7); XC[1] = vexact(91);
    for (int j = 2; j <= JMAX; ++j) {
        UTab T; VC v = XC[j - 1]; T.h = -1; map<ll, int> seen;
        for (int t = 0;; ++t) {
            if (!v.huge) T.pre.push_back(v.v);
            else {
                if (T.h < 0) T.h = t;
                auto it = seen.find(v.r);
                if (it != seen.end()) { T.mu = it->second - T.h; T.lam = t - it->second; break; }
                seen[v.r] = t; T.res.push_back(v.r);
            }
            v = UV(j - 1, v);
            if (t > 3000000) { fprintf(stderr, "U table j=%d does not cycle\n", j); exit(2); }
        }
        if (MG % T.lam != 0) { fprintf(stderr, "U table j=%d: period %d does not divide MG\n", j, T.lam); exit(2); }
        UT[j] = T; XC[j] = tabAt(T, 2);
    }
    JINF = -1;
    for (int J = 3; J + 1 <= JMAX && JINF < 0; ++J)
        if (XC[J].huge && vcEq(XC[J], XC[J + 1]) && ftabParity(J) && ftabEq(J, J + 1)) JINF = J;
    if (JINF < 0) { fprintf(stderr, "U tables do not stabilise\n"); exit(2); }
}
// exact U with cap: -1 if the value exceeds cap (cap <= SYMCAP < 2^140 < U_1(91) <= U_j(x) for j >= 3 or j = 2, x >= 3)
static i128 Uex(i128 j, i128 x, i128 cap) {
    if (j == 0) { if (x > (cap - 7) / 3) return -1; return 3 * x + 7; }
    if (j == 1) { if (x > 60) return -1; i128 p = 1; for (int i = 0; i < x; ++i) p *= 3; i128 v = (21 * p - 7) / 2; return v <= cap ? v : -1; }
    if (j == 2 && x <= 2) return 91 <= cap ? 91 : -1;
    return -1;
}
static i128 Uiterex(i128 j, i128 v, i128 x, i128 cap) { for (i128 t = 0; t < v; ++t) { x = Uex(j, x, cap); if (x < 0) return -1; } return x; }
struct Orbit { vector<VC> seq; int mu = -1, lam = -1; };   // seq[t] = x_(t+1)
static Orbit orbitU(int jj, const VC &b) {
    Orbit o; VC x = UV(jj, b); map<ll, int> seen;
    for (int t = 0; t < 3000000; ++t) {
        if (x.huge) { auto it = seen.find(x.r); if (it != seen.end()) { o.mu = it->second; o.lam = t - it->second; return o; } seen[x.r] = t; }
        o.seq.push_back(x);
        x = UV(jj, x);
    }
    UD("orbit does not cycle");
}
static VC orbitAt(const Orbit &o, i128 a) {   // x_a, a >= 1
    i128 t = a - 1;
    if (t < (i128)o.seq.size()) return o.seq[(size_t)t];
    return o.seq[(size_t)(o.mu + pmod(t - o.mu, o.lam))];
}
static VC orbitAtRes(const Orbit &o, ll ares) { return o.seq[(size_t)(o.mu + pmod((i128)ares - 1 - o.mu, o.lam))]; }   // a - 1 >= seq.size()
static VC Uiter(int jj, i128 v, const VC &b) {
    if (v <= 0) return b;
    if (v <= 4096) { VC x = b; for (i128 t = 0; t < v; ++t) x = UV(jj, x); return x; }
    return orbitAt(orbitU(jj, b), v);
}

// ------------------------------------------------------------------ cascade value
// KStruct: the operations of one accelerated cascade, in order, from the counter B0 = b + 3a:
//   digit op: one digit of value v at depth j (iter v (U j) B);  bulk op: m copies of a digit block at depths >= JINF
//   (all applications use U_JINF, so the block acts as iter (D*m) U_JINF with D its digit sum).
template <class P> static VC kValue(const KStruct &K, P &prov) {
    VC cur; bool started = false;
    for (const KOp &op : K.ops) {
        if (!started) {
            i128 v; if (prov.exact(K.B0, v)) cur = vexact(v); else { prov.ge(K.B0, HUGEMIN); cur = VC{true, 0, prov.res(K.B0, MG)}; }
            started = true;
        }
        if (!op.bulk) {
            int jj; i128 dj;
            if (prov.exact(op.depth, dj)) { jj = dj <= JMAX ? (int)dj : (dj < INFJ ? (int)dj : INFJ); }
            else { prov.ge(op.depth, JINF); jj = INFJ; }
            i128 vv;
            if (prov.exact(op.v, vv)) cur = Uiter(jj, vv, cur);
            else {
                Orbit o = orbitU(jj, cur); prov.ge(op.v, (i128)o.seq.size() + 1);
                if (MG % o.lam != 0) UD("K: orbit period");
                cur = orbitAtRes(o, prov.res(op.v, o.lam));
            }
        } else {
            ll D = 0; for (int d : op.digs) D += d;
            if (D == 0) continue;
            if (!cur.huge) UD("K: bulk on exact B");
            prov.ge(op.depth, JINF);
            Orbit o = orbitU(INFJ, cur); i128 mm;
            if (MG % o.lam != 0) UD("K: orbit period");
            if (prov.exact(op.m, mm)) { if (mm > 0) cur = orbitAt(o, mm * D); }
            else {
                prov.ge(op.m, ((i128)o.seq.size() + 1 + D - 1) / D);
                ll rm = prov.res(op.m, o.lam);
                cur = orbitAtRes(o, (ll)(((i128)rm * D) % o.lam));
            }
        }
    }
    if (!started) { i128 v; if (prov.exact(K.B0, v)) return vexact(v); prov.ge(K.B0, HUGEMIN); return VC{true, 0, prov.res(K.B0, MG)}; }
    return cur;
}
struct ProvMain {   // global forms (no proof symbols)
    bool exact(const Lin &e, i128 &v) { if (e.isExact()) { v = e.c; return true; } return false; }
    ll res(const Lin &e, ll m) { return resG(e, m); }
    void ge(const Lin &e, i128 c) { if (sgnG(laddc(e, -c)) < 0) UD("K: ge"); }
};
// lower bound of the cascade value from lower bounds of the arguments (U monotone in x, iterates increase,
// any application at depth >= 3 gives >= X_2 > SYMCAP); LB: a callable Lin -> i128 lower bound
template <class F> static i128 kLower(const KStruct &K, F LB) {
    i128 B = LB(K.B0); if (B < 0) B = 0;
    for (const KOp &op : K.ops) {
        if (!op.bulk) {
            i128 d = LB(op.v); if (d <= 0) continue;
            i128 j; if (op.depth.isExact()) j = op.depth.c; else j = JINF;
            if (j >= 3) return SYMCAP;
            i128 r = Uiterex(j, min<i128>(d, 4096), B, SYMCAP); if (r < 0) return SYMCAP; B = r;
        } else {
            ll D = 0; for (int x : op.digs) D += x;
            if (D > 0 && LB(op.m) >= 1) return SYMCAP;   // depth >= JINF >= 3
        }
    }
    return B;
}
