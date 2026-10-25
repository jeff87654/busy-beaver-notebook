// jz.cpp: symbolic macro simulator for 2-symbol TMs (bb9_jzseed, 2026-10-17), derived from bb9_symsim/symsim.cpp:
// sound HUGE counts, Ligocki-style rule prover (linear rules + inductive CYCLE certificates), and the exact
// Jacobzheng digit cascade (KR1-KR3 iterated, Coq CDPx) when the 12 core slots of the BB(9) champion are intact.
//
// Counts are linear forms (c + sum a_i X_i) / D over symbols.  A global symbol X stands for one fixed unknown
// integer with a proven lower bound lb(X) and a known residue X mod MG.  Every decision is either valid for all
// values consistent with that knowledge or throws Undec (never guesses).  In a proof, proof variables carry a
// "shadow" (the current concrete/global value): each decision is taken on the shadow and recorded as a
// constraint, so the proved rule holds for every value satisfying the recorded constraints.
//
// Tape: two stacks of runs (word, count); words are stored nearest-head-first.  The head sits between the
// stacks and faces one of them (Ligocki's direction representation).  Macro steps: chain step over a whole
// run (uniform sweep), single-copy word step, literal step, Ch jump, rule application.
//
// usage: symsim run [opts] < lines "MACHINE START [TAPESPEC]"
//        opts: --budget N (macro steps)  --mg M (global modulus)  --exmax E (exact values > E become symbols)
//              --noch  --noprove  --trace  --hlb L (lower bound of ^H tape symbols)  --tape (print final tape)
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
typedef __int128 i128;
typedef unsigned long long ull;

struct Undec { string why; };
[[noreturn]] static void UD(const string &w) { throw Undec{w}; }

static i128 A_(i128 a, i128 b) { i128 r; if (__builtin_add_overflow(a, b, &r)) UD("overflow"); return r; }
static i128 S_(i128 a, i128 b) { i128 r; if (__builtin_sub_overflow(a, b, &r)) UD("overflow"); return r; }
static i128 M_(i128 a, i128 b) { i128 r; if (__builtin_mul_overflow(a, b, &r)) UD("overflow"); return r; }
static i128 gcd_(i128 a, i128 b) { if (a < 0) a = -a; if (b < 0) b = -b; while (b) { i128 t = a % b; a = b; b = t; } return a; }
static i128 pmod(i128 a, i128 m) { i128 r = a % m; return r < 0 ? r + m : r; }
static i128 fdiv(i128 a, i128 b) { i128 q = a / b; if ((a % b != 0) && ((a < 0) != (b < 0))) --q; return q; }
static i128 cdiv(i128 a, i128 b) { return -fdiv(-a, b); }
static string s128(i128 v) {
    if (v == 0) return "0";
    bool neg = v < 0; unsigned __int128 u = neg ? -(unsigned __int128)v : (unsigned __int128)v; string s;
    while (u) { s += char('0' + (int)(u % 10)); u /= 10; }
    if (neg) s += '-'; reverse(s.begin(), s.end()); return s;
}
static i128 p128(const char *s) { bool neg = false; if (*s == '-') { neg = true; ++s; } i128 v = 0; while (*s >= '0' && *s <= '9') v = v * 10 + (*s++ - '0'); return neg ? -v : v; }

// ------------------------------------------------------------------ linear forms
static const int MT = 8;
static const int PBASE = 1 << 24;   // ids >= PBASE are proof symbols
struct Lin {
    i128 c = 0, D = 1; int n = 0; int id[MT]; i128 a[MT];
    bool isExact() const { return n == 0; }
};
static Lin LC(i128 v) { Lin l; l.c = v; return l; }
static Lin LV(int id) { Lin l; l.n = 1; l.id[0] = id; l.a[0] = 1; return l; }
static void lnorm(Lin &x) {
    if (x.D < 0) { x.D = -x.D; x.c = -x.c; for (int k = 0; k < x.n; ++k) x.a[k] = -x.a[k]; }
    i128 g = gcd_(x.D, x.c); for (int k = 0; k < x.n && g != 1; ++k) g = gcd_(g, x.a[k]);
    if (g > 1) { x.D /= g; x.c /= g; for (int k = 0; k < x.n; ++k) x.a[k] /= g; }
    if (x.n == 0 && x.D != 1) UD("nonintegral");
}
// x*kx + y*ky
static Lin consolidate(i128 c, i128 D, const vector<pair<int, i128>> &T);
static Lin lcomb(const Lin &x, i128 kx, const Lin &y, i128 ky) {
    if (x.n == 0 && y.n == 0) return LC(A_(M_(x.c, kx), M_(y.c, ky)));
    i128 g = gcd_(x.D, y.D); i128 L = M_(x.D / g, y.D);
    i128 fx = M_(L / x.D, kx), fy = M_(L / y.D, ky);
    Lin r; r.D = L; r.c = A_(M_(x.c, fx), M_(y.c, fy));
    int i = 0, j = 0;
    while (i < x.n || j < y.n) {
        int idv; i128 av;
        if (j >= y.n || (i < x.n && x.id[i] < y.id[j])) { idv = x.id[i]; av = M_(x.a[i], fx); ++i; }
        else if (i >= x.n || y.id[j] < x.id[i]) { idv = y.id[j]; av = M_(y.a[j], fy); ++j; }
        else { idv = x.id[i]; av = A_(M_(x.a[i], fx), M_(y.a[j], fy)); ++i; ++j; }
        if (av != 0) {
            if (r.n >= MT) {   // too many symbols: consolidate (global forms only)
                vector<pair<int, i128>> T; for (int k = 0; k < r.n; ++k) T.push_back({r.id[k], r.a[k]}); T.push_back({idv, av});
                for (; i < x.n || j < y.n;) {
                    if (j >= y.n || (i < x.n && x.id[i] < y.id[j])) { T.push_back({x.id[i], M_(x.a[i], fx)}); ++i; }
                    else if (i >= x.n || y.id[j] < x.id[i]) { T.push_back({y.id[j], M_(y.a[j], fy)}); ++j; }
                    else { i128 v = A_(M_(x.a[i], fx), M_(y.a[j], fy)); if (v) T.push_back({x.id[i], v}); ++i; ++j; }
                }
                return consolidate(r.c, r.D, T);
            }
            r.id[r.n] = idv; r.a[r.n] = av; ++r.n;
        }
    }
    lnorm(r); return r;
}
static Lin ladd(const Lin &x, const Lin &y) { return lcomb(x, 1, y, 1); }
static Lin lsub(const Lin &x, const Lin &y) { return lcomb(x, 1, y, -1); }
static Lin laddc(const Lin &x, i128 v) { if (x.n == 0) return LC(A_(x.c, v)); Lin r = x; r.c = A_(r.c, M_(v, r.D)); lnorm(r); return r; }
static Lin lscale(const Lin &x, i128 num, i128 den = 1) {
    if (x.n == 0 && den == 1) return LC(M_(x.c, num));
    Lin r = x; r.c = M_(r.c, num); for (int k = 0; k < r.n; ++k) r.a[k] = M_(r.a[k], num); r.D = M_(r.D, den);
    if (num == 0) { r = LC(0); return r; }
    lnorm(r); return r;
}
static bool lequal(const Lin &x, const Lin &y) {
    if (x.n != y.n || x.c != y.c || x.D != y.D) return false;
    for (int k = 0; k < x.n; ++k) if (x.id[k] != y.id[k] || x.a[k] != y.a[k]) return false;
    return true;
}
static bool hasProof(const Lin &e) { return e.n > 0 && e.id[e.n - 1] >= PBASE; }
static i128 coefOf(const Lin &e, int id) { for (int k = 0; k < e.n; ++k) if (e.id[k] == id) return e.a[k]; return 0; }

// ------------------------------------------------------------------ symbols
static ll MG = 2520;                       // residues of global symbols are known mod MG
static i128 EXMAX = (i128)1 << 100;        // exact counts above this become symbols
static const i128 SYMCAP = (i128)1 << 118; // lower bounds are capped here
struct GSym { i128 lb; ll mod, res; string desc; Lin lbf; bool hasLbf = false; };   // lbf: X >= lbf (cascade symbols)
static vector<GSym> GS;
struct KOp { bool bulk = false; Lin depth; Lin v; vector<int> digs; Lin m; };   // cascade operation (see kValue)
struct KStruct { Lin B0; vector<KOp> ops; };
struct PSym { char kind; Lin shadow; Lin J, B; char sub = 'K'; Lin A, K; int kd = -1; };   // kind 'P' variable, 'Z' = cascade value PC->ks[kd]
struct Cons { char k; Lin N; i128 q = 0, r = 0; };   // 'G': N>=0  'E': N==0  'C': N == r mod q   (N.D == 1)
struct PCtx { vector<PSym> s; vector<Cons> cons; set<string> seen; vector<KStruct> ks; };
static PCtx *PC = nullptr;

static string linstr(const Lin &e) {
    string s; bool first = true;
    for (int k = 0; k < e.n; ++k) {
        i128 a = e.a[k]; if (!first) s += (a >= 0 ? "+" : "-"); else if (a < 0) s += "-";
        i128 aa = a < 0 ? -a : a; if (aa != 1) s += s128(aa) + "*";
        s += (e.id[k] >= PBASE ? (PC && e.id[k] - PBASE < (int)PC->s.size() && PC->s[e.id[k] - PBASE].kind == 'Z' ? "Z" : "x") + to_string(e.id[k] - PBASE) : "X" + to_string(e.id[k]));
        first = false;
    }
    if (e.c != 0 || first) { if (!first && e.c > 0) s += "+"; s += s128(e.c); }
    if (e.D != 1) s = "(" + s + ")/" + s128(e.D);
    return s;
}
static string consKey(const Cons &c) { return string(1, c.k) + linstr(c.N) + "|" + s128(c.q) + "|" + s128(c.r); }
static void addCons(const Cons &c) {
    if (!PC) return;
    string k = consKey(c); if (PC->seen.count(k)) return;
    PC->seen.insert(k); PC->cons.push_back(c);
}
static Lin numer(const Lin &e) { Lin N = e; N.D = 1; return N; }

static Lin shadowOf(const Lin &e) {
    if (!hasProof(e)) return e;
    Lin r = LC(e.c);
    for (int k = 0; k < e.n; ++k) {
        if (e.id[k] < PBASE) r = lcomb(r, 1, LV(e.id[k]), e.a[k]);
        else r = lcomb(r, 1, PC->s[e.id[k] - PBASE].shadow, e.a[k]);
    }
    return lscale(r, 1, e.D);
}
// sign of a global form (no proof symbols)
static int sgnG(const Lin &e) {
    if (e.n == 0) return e.c > 0 ? 1 : (e.c < 0 ? -1 : 0);
    bool allpos = true, allneg = true;
    for (int k = 0; k < e.n; ++k) { if (e.a[k] < 0) allpos = false; if (e.a[k] > 0) allneg = false; }
    if (allpos || allneg) {
        i128 s = e.c; bool ovf = false;
        for (int k = 0; k < e.n && !ovf; ++k) { i128 t; if (__builtin_mul_overflow(e.a[k], GS[e.id[k]].lb, &t) || __builtin_add_overflow(s, t, &s)) ovf = true; }
        if (allpos && (ovf || s > 0)) return 1;
        if (allneg && (ovf || s < 0)) return -1;
    }
    {   // positivity through linear lower-bound forms (X >= lbf) of positively weighted symbols
        Lin f = e;
        try {
            for (int round = 0; round < 4; ++round) {
                bool ch = false;
                for (int k = 0; k < f.n && !ch; ++k)
                    if (f.a[k] > 0 && GS[f.id[k]].hasLbf) { f = ladd(f, lscale(lsub(GS[f.id[k]].lbf, LV(f.id[k])), f.a[k], f.D)); ch = true; }
                if (!ch) break;
                bool ap = true; for (int k = 0; k < f.n; ++k) if (f.a[k] < 0) ap = false;
                if (ap) {
                    i128 s = f.c; bool ovf = false;
                    for (int k = 0; k < f.n && !ovf; ++k) { i128 t; if (__builtin_mul_overflow(f.a[k], GS[f.id[k]].lb, &t) || __builtin_add_overflow(s, t, &s)) ovf = true; }
                    if (ovf || s > 0) return 1;
                }
            }
        } catch (Undec &) {}
    }
    UD("sign:" + linstr(e));
}
// e mod m for a global form
static ll resG(const Lin &e, ll m) {
    if (m == 1) return 0;
    i128 Q = M_(m, e.D);
    i128 t = pmod(e.c, Q);
    for (int k = 0; k < e.n; ++k) {
        const GSym &g = GS[e.id[k]];
        i128 need = Q / gcd_(e.a[k], Q);
        if (need == 1) continue;
        if (g.mod % (ll)need != 0) UD("residue precision:" + linstr(e) + " mod " + to_string(m));
        t = pmod(t + pmod(e.a[k], Q) * pmod(g.res, need), Q);
    }
    if (t % e.D != 0) UD("residue nonintegral");
    return (ll)((t / e.D) % m);
}
static int sgn(const Lin &e) {
    if (!hasProof(e)) return sgnG(e);
    int s = sgnG(shadowOf(e));
    Lin N = numer(e);
    Cons c;
    if (s > 0) { c.k = 'G'; c.N = laddc(N, -e.D); }
    else if (s < 0) { c.k = 'G'; c.N = laddc(lscale(N, -1), -e.D); }
    else { c.k = 'E'; c.N = N; }
    addCons(c);
    return s;
}
static ll res(const Lin &e, ll m) {
    if (m == 1) return 0;
    if (!hasProof(e)) return resG(e, m);
    ll r = resG(shadowOf(e), m);
    Cons c; c.k = 'C'; c.N = numer(e); c.q = M_(m, e.D); c.r = pmod(M_(r, e.D), c.q);
    addCons(c);
    return r;
}
static bool isOne(const Lin &n) { if (n.n == 0) return n.c == 1; return sgn(laddc(n, -1)) == 0; }
static int cmpL(const Lin &x, const Lin &y) { return sgn(lsub(x, y)); }
// lower bound of a global form (exact value if exact); throws if not all coefficients positive
static i128 lbG(const Lin &e) {
    if (e.n == 0) return e.c;
    i128 s = e.c; bool ovf = false;
    for (int k = 0; k < e.n; ++k) { if (e.a[k] < 0) UD("lb of mixed form"); i128 t; if (__builtin_mul_overflow(e.a[k], GS[e.id[k]].lb, &t) || __builtin_add_overflow(s, t, &s)) ovf = true; }
    if (ovf) return SYMCAP;
    return min(cdiv(s, e.D), SYMCAP);
}
static int newG(i128 lb, ll res, const string &desc, ll mod = 0) {
    if (mod <= 0) mod = MG;
    GS.push_back(GSym{min(lb, SYMCAP), mod, (ll)pmod(res, mod), desc});
    return (int)GS.size() - 1;
}
static int consolidations = 0;
// replace a global form with too many terms by a fresh symbol: lower bound and the finest residue available
static Lin consolidate(i128 c, i128 D, const vector<pair<int, i128>> &T) {
    i128 g = gcd_(D, c); for (auto &t : T) g = gcd_(g, t.second);
    if (g > 1) { c /= g; D /= g; }
    string desc = "S(";
    bool allpos = true;
    for (auto &t : T) { if (t.first >= PBASE) UD("too many symbols"); if (t.second < 0) allpos = false; desc += (t.second / g >= 0 ? "+" : "") + s128(t.second / g) + "*X" + to_string(t.first); }
    desc += (c >= 0 ? "+" : "") + s128(c) + ")/" + s128(D);
    if (!allpos) UD("consolidate mixed signs");
    i128 s = c; bool ovf = false;
    for (auto &t : T) { i128 u; if (__builtin_mul_overflow(t.second / g, GS[t.first].lb, &u) || __builtin_add_overflow(s, u, &s)) ovf = true; }
    i128 lb = ovf ? SYMCAP : min(cdiv(s, D), SYMCAP);
    ll best = 1, bres = 0;
    for (ll m = MG; m >= 2; --m) {
        if (MG % m) continue;
        i128 Q = M_(m, D); i128 t = pmod(c, Q); bool ok = true;
        for (auto &tt : T) {
            i128 a = tt.second / g; i128 need = Q / gcd_(a, Q); if (need == 1) continue;
            if (GS[tt.first].mod % (ll)need != 0) { ok = false; break; }
            t = pmod(t + pmod(a, Q) * pmod(GS[tt.first].res, need), Q);
        }
        if (ok && t % D == 0) { best = m; bres = (ll)((t / D) % m); break; }
    }
    ++consolidations;
    return LV(newG(lb, bres, desc, best));
}
// exact values beyond EXMAX become symbols (main mode only)
static void normCount(Lin &n) {
    if (PC) return;
    if (n.n == 0 && (n.c > EXMAX || n.c < -EXMAX)) {
        if (n.c < 0) UD("negative huge count");
        int id = newG(EXMAX + 1, (ll)pmod(n.c, MG), "E" + s128(n.c));   // only the bound EXMAX+1 is used
        n = LV(id);
    }
}

// ------------------------------------------------------------------ U residue law (Jacobzheng's digit cascade)
// U_0(x) = 3x+7, U_(j+1)(x) = iter (x - 2j) U_j X_j, X_0 = 7, X_(j+1) = U_j(U_j(X_j))     (Coq UX, BB9_fw2_1RB0RD.v)
// CDPx: Kd (0^j ++ v :: Us) 0 B -->* Kd (0^(j+1) ++ Us) 0 (iter v (U j) B) when 2j <= B;  Ugrow: U_j(x) >= x + 2j + 5.
// Value classes: exact v (<= VT) or huge (value >= HUGEMIN, residue mod MG known).
struct VC { bool huge; i128 v; ll r; };
static i128 VT = (i128)1 << 100;   // --vt (validation: smaller VT turns more values into classes)
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

// ------------------------------------------------------------------ machine
static int NS = 0;
struct Tr { int w, d, nx; bool halt; };   // d: 0 = L, 1 = R
static Tr TT[16][2];
static const char *CHAMP = "1RB1RA_0LC0LF_0RD1LC_1RA1RG_1RZ0RA_1LB1LF_1LH1RE_0LI1LH_1LB0LH";
static const int CORE[12] = {0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 13};   // A0 A1 B0 B1 C0 C1 D0 D1 E1 F0 F1 G1
static bool parseMachine(const string &s, Tr out[16][2], int &ns) {
    ns = (int)(s.size() + 1) / 7;
    if (ns < 1 || ns > 16 || (int)s.size() != 7 * ns - 1) return false;
    for (int q = 0; q < ns; ++q) for (int c = 0; c < 2; ++c) {
        const char *x = s.c_str() + 7 * q + 3 * c; Tr &t = out[q][c];
        if (x[0] == '-' || x[2] == '-' || x[2] == 'Z' || x[2] - 'A' >= ns) { t = Tr{1, 1, -1, true}; continue; }
        t = Tr{x[0] - '0', x[1] == 'R' ? 1 : 0, x[2] - 'A', false};
    }
    return true;
}
static bool coreIntact() {
    Tr B[16][2]; int ns; parseMachine(CHAMP, B, ns);
    if (NS < 7) return false;
    for (int i = 0; i < 12; ++i) {
        int q = CORE[i] / 2, c = CORE[i] % 2; const Tr &a = TT[q][c], &b = B[q][c];
        if (a.halt || a.w != b.w || a.d != b.d || a.nx != b.nx) return false;
    }
    return true;
}
struct MiniRes { char kind; int q; string w; ll steps; };   // kind F far exit, N near exit, H halt inside, L loop
static unordered_map<string, MiniRes> MINI;
static MiniRes mini(int q, int f, const string &w) {
    string key; key += char(q); key += char(f); key += w;
    auto it = MINI.find(key); if (it != MINI.end()) return it->second;
    // inside a word of length L there are at most NS*L*2^L configurations: exceeding that proves a loop (L <= 14);
    // longer words only get a step cap and 'X' (no claim, literal stepping instead)
    string t = w; int p = 0, L = (int)w.size(); ll s = 0, lim = L <= 14 ? (ll)NS * L * (1LL << L) + 16 : 2000000;
    MiniRes r;
    while (true) {
        if (p < 0) { r = MiniRes{'N', q, t, s}; break; }
        if (p >= L) { r = MiniRes{'F', q, t, s}; break; }
        const Tr &tr = TT[q][t[p] - '0'];
        if (tr.halt) { r = MiniRes{'H', q, t, s}; break; }
        t[p] = char('0' + tr.w); p += (tr.d == f) ? 1 : -1; q = tr.nx; ++s;
        if (s > lim) { r = MiniRes{L <= 14 ? 'L' : 'X', q, t, s}; break; }
    }
    if (MINI.size() > 2000000) MINI.clear();
    MINI[key] = r; return r;
}
static string rev(const string &s) { return string(s.rbegin(), s.rend()); }
static bool allZero(const string &w) { return w.find('1') == string::npos; }
static bool allOne(const string &w) { return w.find('0') == string::npos; }
static bool alternating(const string &w) { for (size_t i = 1; i < w.size(); ++i) if (w[i] == w[i - 1]) return false; return true; }
static int count1(const string &w) { int k = 0; for (char ch : w) k += ch == '1'; return k; }
static int primRoot(const string &w) {   // length of the primitive root
    int L = (int)w.size();
    for (int p = 1; p < L; ++p) if (L % p == 0) { bool ok = true; for (int i = p; i < L && ok; ++i) ok = w[i] == w[i - p]; if (ok) return p; }
    return L;
}

// ------------------------------------------------------------------ configurations and rules
struct Run { string w; Lin n; int tag = -1; };
struct Cfg { int q = 0, f = 1; vector<Run> st[2]; };     // st[0] left, st[1] right; back() = nearest the head
static const int PMAX = 8, FOLDREG = 72, DEEPP = 64, SIGWIN = 16;
enum { S_OK = 0, S_HALT, S_CYCLE };
struct Rule {
    int q, f; vector<Run> g[2]; vector<int> rv[2]; bool bottom[2];
    int nv; vector<i128> delta; vector<Cons> cons; bool stepsKnown; Lin steps; ll uses = 0;
};
struct RuleSet { vector<Rule> R; unordered_map<string, vector<int>> idx; };
static string ruleKey(int q, int f, const string &top) { string k; k += char(q); k += char(f); k += top; return k; }

static Lin subst(const Lin &N, const vector<Lin> &bind) {
    Lin r = LC(N.c);
    for (int k = 0; k < N.n; ++k) {
        if (N.id[k] >= PBASE) { int v = N.id[k] - PBASE; if (v >= (int)bind.size() || bind[v].D == 0) UD("unbound rule var"); r = lcomb(r, 1, bind[v], N.a[k]); }
        else r = lcomb(r, 1, LV(N.id[k]), N.a[k]);
    }
    return lscale(r, 1, N.D);
}

struct Sim {
    Cfg c; bool proof = false, chOK = false, prover = true, trace = false;
    Lin steps = LC(0); bool stepsKnown = true;
    ll macro = 0, jumps = 0, ruleApps = 0; int haltQ = -1, haltS = 0;
    int maxTag[2] = {-1, -1}; bool bot[2] = {false, false};
    RuleSet *rules = nullptr;
    string cyc, lastUndec;
    vector<string> jlog;   // last jumps
    Lin maxJ = LC(0);

    void touch(int s, const Run &r) { if (proof && r.tag > maxTag[s]) maxTag[s] = r.tag; }
    void touchBottom(int s) { if (proof) { bot[s] = true; maxTag[s] = INT_MAX; } }
    void addSteps(const Lin &x) { if (!stepsKnown) return; try { steps = ladd(steps, x); } catch (Undec &) { stepsKnown = false; } }
    void pushRaw(int s, Run r) {
        int p = primRoot(r.w); if (p < (int)r.w.size()) { r.n = lscale(r.n, (i128)(r.w.size() / p)); r.w.resize(p); }
        normCount(r.n);
        auto &V = c.st[s];
        if (!V.empty()) { touch(s, V.back()); if (V.back().w == r.w) { V.back().n = ladd(V.back().n, r.n); normCount(V.back().n); return; } }
        r.tag = -1; V.push_back(r);
    }
    void rebuildCells(int s, const string &cells) { for (int i = (int)cells.size() - 1; i >= 0; --i) pushRaw(s, Run{string(1, cells[i]), LC(1)}); }
    // a run V[idx] = (u, n) absorbs further copies of u lying just below it (loose small exact runs)
    void absorbDown(int s, int idx) {
        auto &V = c.st[s];
        while (idx > 0) {
            const string u = V[idx].w; size_t L = u.size();
            string t; int j = idx - 1, used = 0;
            while (j >= 0 && t.size() < L) {
                const Run &r = V[j];
                if (!r.n.isExact() || r.n.c * (i128)r.w.size() > 2 * FOLDREG) break;
                touch(s, r); for (i128 q = 0; q < r.n.c; ++q) t += r.w;
                ++used; --j;
            }
            if (t.size() < L || t.compare(0, L, u) != 0) { if (j >= 0) touch(s, V[j]); return; }
            string left = t.substr(L);   // nearest-first, left[0] adjacent to the run
            V.erase(V.begin() + (idx - used), V.begin() + idx);
            idx -= used;
            V[idx].n = laddc(V[idx].n, 1); normCount(V[idx].n);
            vector<Run> ins;   // bottom-to-top = far-to-near = reverse(left)
            for (int q = (int)left.size() - 1; q >= 0; --q) {
                string cw(1, left[q]);
                if (!ins.empty() && ins.back().w == cw) ins.back().n = laddc(ins.back().n, 1); else ins.push_back(Run{cw, LC(1)});
            }
            if (!ins.empty() && idx > 0 && V[idx - 1].w == ins.front().w) { V[idx - 1].n = ladd(V[idx - 1].n, ins.front().n); ins.erase(ins.begin()); }
            V.insert(V.begin() + idx, ins.begin(), ins.end());
            idx += (int)ins.size();
        }
    }
    void fold(int s) {
        auto &V = c.st[s];
        for (int iter = 0; iter < 6; ++iter) {
            string cells; int k = 0;
            for (int i = (int)V.size() - 1; i >= 0; --i) {
                const Run &r = V[i];
                if (!r.n.isExact() || r.n.c > FOLDREG) break;
                ll cnt = (ll)r.n.c; if ((ll)cells.size() + cnt * (ll)r.w.size() > FOLDREG) break;
                touch(s, r);
                for (ll t = 0; t < cnt; ++t) cells += r.w;
                ++k;
            }
            int bi = (int)V.size() - 1 - k;
            if (bi >= 0) touch(s, V[bi]);
            if (k == 0 || cells.size() < 2) return;
            if (bi >= 0) {
                const string u = V[bi].w;
                if (u.size() <= cells.size() && cells.compare(cells.size() - u.size(), u.size(), u) == 0) {
                    string rest = cells.substr(0, cells.size() - u.size());
                    V.resize(V.size() - k); V.back().n = laddc(V.back().n, 1); normCount(V.back().n);
                    rebuildCells(s, rest);
                    continue;
                }
            }
            // seed a new run (u, r) at offset o: cells[0..o) stay loose on top
            for (int o = 0; o < PMAX; ++o)
                for (int p = 2; p <= PMAX && o + 2 * p <= (int)cells.size(); ++p) {
                    if (cells.compare(o, p, cells, o + p, p) != 0) continue;
                    string u = cells.substr(o, p); if (primRoot(u) != p) continue;
                    int r = 2; while (o + (r + 1) * p <= (int)cells.size() && cells.compare(o + r * p, p, u) == 0) ++r;
                    string rest = cells.substr(o + r * p);
                    V.resize(V.size() - k); rebuildCells(s, rest); pushRaw(s, Run{u, LC(r)});
                    absorbDown(s, (int)V.size() - 1);
                    rebuildCells(s, cells.substr(0, o));
                    return;
                }
            return;
        }
    }
    void push(int s, const Run &r) { pushRaw(s, r); fold(s); }
    // occasional full re-factorisation of a stack (main mode only; a representation change, always sound):
    // regions of small exact runs are flattened and greedily re-encoded with periods up to DEEPP (>= 3 repeats)
    void deepCompress(int s) {
        auto &V = c.st[s];
        vector<Run> res; string S;   // res nearest-first
        auto flushS = [&]() {
            size_t pos = 0, n = S.size();
            while (pos < n) {
                int bp = 1; size_t bcov = 0;
                for (int p = 2; p <= DEEPP && pos + 3 * (size_t)p <= n; ++p) {
                    size_t r = 1; while (pos + (r + 1) * p <= n && S.compare(pos + r * p, p, S, pos, p) == 0) ++r;
                    if (r >= 3 && r * p > bcov) { bcov = r * p; bp = p; }
                }
                size_t r1 = 1; while (pos + r1 < n && S[pos + r1] == S[pos]) ++r1;
                if (bp > 1 && bcov > r1) { string u = S.substr(pos, bp); if (primRoot(u) == bp) { res.push_back(Run{u, LC((i128)(bcov / bp))}); pos += bcov; continue; } }
                res.push_back(Run{string(1, S[pos]), LC((i128)r1)}); pos += r1;
            }
            S.clear();
        };
        for (int i = (int)V.size() - 1; i >= 0; --i) {
            const Run &r = V[i];
            if (r.n.isExact() && r.n.c * (i128)r.w.size() <= 256) { for (i128 t = 0; t < r.n.c; ++t) S += r.w; if (S.size() > 20000) flushS(); }
            else { flushS(); res.push_back(r); }
        }
        flushS();
        V.clear();
        for (int k = (int)res.size() - 1; k >= 0; --k) pushRaw(s, res[k]);
    }
    void popCopy(int s) {
        auto &V = c.st[s]; touch(s, V.back());
        if (isOne(V.back().n)) V.pop_back(); else V.back().n = laddc(V.back().n, -1);
    }
    int popCell(int s) {
        auto &V = c.st[s];
        if (V.empty()) { touchBottom(s); return 0; }
        string w = V.back().w; popCopy(s);
        if (w.size() > 1) pushRaw(s, Run{w.substr(1), LC(1)});
        return w[0] - '0';
    }
    int litStep() {
        int f = c.f, cb = popCell(f); const Tr &t = TT[c.q][cb];
        if (t.halt) { haltQ = c.q; haltS = cb; pushRaw(f, Run{string(1, char('0' + cb)), LC(1)}); return S_HALT; }   // tape as before the halting step
        if (t.d == f) push(1 - f, Run{string(1, char('0' + t.w)), LC(1)});
        else { push(f, Run{string(1, char('0' + t.w)), LC(1)}); c.f = 1 - f; }
        c.q = t.nx; addSteps(LC(1)); return S_OK;
    }
    bool tryRotate() {
        int f = c.f; Run top = c.st[f].back(); const string &w = top.w; int L = (int)w.size();
        for (int s = 1; s < L; ++s) {
            MiniRes pr = mini(c.q, f, w.substr(0, s));
            if (pr.kind != 'F') continue;
            string rot = w.substr(s) + w.substr(0, s);
            MiniRes rr = mini(pr.q, f, rot);
            if (rr.kind != 'F' || rr.q != pr.q) continue;
            Lin n1 = laddc(top.n, -1);
            c.st[f].pop_back();
            pushRaw(f, Run{w.substr(s), LC(1)});
            pushRaw(f, Run{rot, n1});
            push(1 - f, Run{rev(pr.w), LC(1)});
            c.q = pr.q; addSteps(LC(pr.steps));
            return true;
        }
        return false;
    }
    // ---- Jacobzheng's digit cascade (KR1 iterated = R1iter, then KR2/KR3 iterated = CDPx, digit by digit), used
    // when the 12 core slots A0 A1 B0 B1 C0 C1 D0 D1 E1 F0 F1 G1 (champion labels) are intact.
    //   Kd ds a b = 0^inf <D 1^(b+1) 0 1^a (0 1^d)*   -->*   Kd (0^k ++ rest) 0 B
    // The digit at depth j (j digits above it, all 0 by then) is cleared by iter v (U j) when B >= 2j.  That
    // condition is tracked as a lower-bound form SL <= B - 2*depth (exact while B is exact), using Ugrow.
    // The tail of the list after the first digit not cleared is left in place (untouched runs keep their tags).
    struct KPos { int pi = -1; Lin copy; int ch = 0; };   // cell where a digit starts (its leading 0): piece, copy, char
    struct KItem { bool pat = false; Lin v; vector<int> digs, offs; Lin n; KPos pos; };
    static string encDigs(const vector<int> &d) { string s; for (int x : d) { s += '0'; s += string((size_t)x, '1'); } return s; }
    ll kdJumps = 0, kdBig = 0;
    bool tryKd() {
        auto &L = c.st[0], &R = c.st[1];
        for (int i = (int)L.size() - 1; i >= 0; --i) if (!allZero(L[i].w)) return false;
        struct Piece { string w; Lin n; int orig; };   // orig: index in R, or -1 (derived from the head run)
        vector<Piece> rp;
        if (c.f == 0) { for (int i = (int)R.size() - 1; i >= 0; --i) rp.push_back({R[i].w, R[i].n, i}); }
        else {
            if (R.empty() || R.back().w[0] != '0') return false;
            const Run &t = R.back();
            if (t.w.size() > 1) rp.push_back({t.w.substr(1), LC(1), -1});
            if (!isOne(t.n)) rp.push_back({t.w, laddc(t.n, -1), -1});
            for (int i = (int)R.size() - 2; i >= 0; --i) rp.push_back({R[i].w, R[i].n, i});
        }
        if (getenv("KDDBG")) fprintf(stderr, "KDTRY %s\n", show().c_str());
        if (rp.empty() || rp[0].w[0] != '1') return false;
        // parse 1^(b+1) 0 1^a (0 1^d)*
        int phase = 0; Lin bones = LC(0), aL = LC(0), cur = LC(0); KPos curPos; vector<KItem> items;
        auto addOnes = [&](const Lin &k) { if (phase == 0) bones = ladd(bones, k); else if (phase == 1) aL = ladd(aL, k); else cur = ladd(cur, k); };
        auto pushDigit = [&]() { KItem it; it.v = cur; it.pos = curPos; items.push_back(it); };
        auto zeroCell = [&](int pi, const Lin &cp, int ch) {
            if (phase == 2) pushDigit();
            if (phase < 2) ++phase;
            if (phase == 2) { cur = LC(0); curPos = KPos{pi, cp, ch}; }
        };
        try {
            for (int pi = 0; pi < (int)rp.size(); ++pi) {
                const string &w = rp[pi].w; Lin n = rp[pi].n;
                if (n.isExact() && n.c * (i128)w.size() <= 512) {
                    for (i128 t = 0; t < n.c; ++t) for (size_t i = 0; i < w.size(); ++i) { if (w[i] == '1') addOnes(LC(1)); else zeroCell(pi, LC(t), (int)i); }
                    continue;
                }
                if (allOne(w)) { addOnes(lscale(n, (i128)w.size())); continue; }
                if (allZero(w)) {
                    if (w.size() != 1) return false;
                    i128 t = 0; bool done = false;
                    while (phase < 2) { zeroCell(pi, LC(t), 0); ++t; if (sgn(laddc(n, -t)) == 0) { done = true; break; } }
                    if (done) continue;
                    // zeros t .. n-1: zero #t closes cur, zeros t .. n-2 start zero digits, zero n-1 starts the open digit
                    pushDigit();
                    Lin z1 = laddc(n, -t - 1);
                    if (!(z1.isExact() && z1.c == 0)) { KItem it; it.pat = true; it.digs = {0}; it.offs = {0}; it.n = z1; it.pos = KPos{pi, LC(t), 0}; items.push_back(it); }
                    cur = LC(0); curPos = KPos{pi, laddc(n, -1), 0};
                    continue;
                }
                i128 t1 = 0; bool doneRun = false;
                while (phase < 2) {   // single copies until the digit list starts
                    for (size_t i = 0; i < w.size(); ++i) { if (w[i] == '1') addOnes(LC(1)); else zeroCell(pi, LC(t1), (int)i); }
                    ++t1;
                    if (sgn(laddc(n, -t1)) == 0) { doneRun = true; break; }
                }
                if (doneRun) continue;
                // copies t1 .. n-1:  w^n' = 1^u (0 v 1^u)^(n'-1) 0 v
                size_t u = 0; while (w[u] == '1') ++u;
                string v = w.substr(u + 1);
                string beta = "0" + v + string(u, '1');
                vector<int> bd, offs; for (size_t i = 0; i < beta.size(); ++i) { if (beta[i] == '0') { bd.push_back(0); offs.push_back((int)i); } else ++bd.back(); }
                cur = laddc(cur, (i128)u); pushDigit();
                Lin nb = laddc(n, -t1 - 1);
                if (!(nb.isExact() && nb.c == 0)) { KItem it; it.pat = true; it.digs = bd; it.offs = offs; it.n = nb; it.pos = KPos{pi, LC(t1), (int)u}; items.push_back(it); }
                Lin lastCopy = laddc(n, -1);
                for (size_t k = 0; k + 1 < bd.size(); ++k) { cur = LC(bd[k]); curPos = KPos{pi, lastCopy, (int)u + offs[k]}; pushDigit(); }
                cur = LC(bd.back() - (int)u); curPos = KPos{pi, lastCopy, (int)u + offs.back()};
            }
        } catch (Undec &u) { if (getenv("KDDBG")) fprintf(stderr, "KDPARSE %s\n", u.why.c_str()); return false; }
        if (phase == 2) pushDigit();
        if (bones.isExact() && bones.c < 1) return false;
        auto zeroItem = [&](const KItem &it) {
            if (!it.pat) return it.v.isExact() && it.v.c == 0;
            for (int d : it.digs) if (d) return false;
            return true;
        };
        while (!items.empty() && zeroItem(items.back())) items.pop_back();
        // structure pass
        Lin B0 = ladd(laddc(bones, -1), lscale(aL, 3));
        KStruct K; K.B0 = B0;
        deque<KItem> Q(items.begin(), items.end());
        Lin depth = LC(0), SL = B0; bool exTrack = B0.isExact(); i128 Bex = exTrack ? B0.c : 0; bool hugeB = false;
        auto sgnOK = [&](const Lin &e) -> int { try { return sgn(e); } catch (Undec &) { return -2; } };
        if (!B0.isExact() && sgnOK(laddc(B0, -HUGEMIN)) >= 0) hugeB = true;   // symbolic counter already huge
        auto peelBlock = [&](const KItem &it) {   // block at it.pos (copy c0) -> digits, then the pattern from copy c0+1
            KItem rest = it; rest.n = laddc(it.n, -1); rest.pos.copy = laddc(it.pos.copy, 1);
            Q.push_front(rest);
            for (int p = (int)it.digs.size() - 1; p >= 0; --p) { KItem d; d.v = LC(it.digs[p]); d.pos = KPos{it.pos.pi, it.pos.copy, it.pos.ch + it.offs[p]}; Q.push_front(d); }
        };
        int peels = 0;
        while (!Q.empty()) {
            KItem it = Q.front();
            if (it.pat) {
                int k = (int)it.digs.size(); ll D = 0; for (int d : it.digs) D += d;
                if (it.n.isExact() && it.n.c <= 0) { Q.pop_front(); continue; }
                if (D == 0) { Q.pop_front(); depth = ladd(depth, lscale(it.n, k)); SL = lsub(SL, lscale(it.n, 2 * k)); continue; }
                if (it.n.isExact() && it.n.c <= 64) { Q.pop_front(); peelBlock(it); continue; }
                bool ok = hugeB && sgnOK(laddc(depth, -JINF)) >= 0;
                if (ok) {
                    i128 cst = -2 * k; for (int p = 0; p < k; ++p) if (it.digs[p]) cst += (i128)it.digs[p] * (2 * p + 5);
                    ok = sgnOK(laddc(lscale(depth, 2 * D), cst)) >= 0;
                }
                if (ok) {
                    Lin s = SL;
                    for (int p = 0; p < k && ok; ++p) {
                        int d = it.digs[p];
                        if (d) { if (sgnOK(s) < 0) { ok = false; break; } s = ladd(s, laddc(lscale(laddc(depth, p), 2 * d), 5 * d)); }
                        s = laddc(s, -2);
                    }
                }
                if (ok) {
                    KOp op; op.bulk = true; op.depth = depth; op.digs = it.digs; op.m = it.n; K.ops.push_back(op);
                    depth = ladd(depth, lscale(it.n, k)); exTrack = false; Q.pop_front();
                    continue;
                }
                if (peels >= 64 || sgnOK(laddc(it.n, -1)) < 0) break;
                ++peels; Q.pop_front(); peelBlock(it);
                continue;
            }
            int sv = it.v.isExact() ? (it.v.c > 0 ? 1 : 0) : sgnOK(it.v);
            if (sv < 0) { if (getenv("KDDBG")) fprintf(stderr, "KDSTOP sv %s\n", linstr(it.v).c_str()); break; }
            if (sv == 0) { Q.pop_front(); depth = laddc(depth, 1); SL = laddc(SL, -2); continue; }
            if (sgnOK(SL) < 0) { if (getenv("KDDBG")) fprintf(stderr, "KDSTOP SL %s dep %s\n", linstr(SL).c_str(), linstr(depth).c_str()); break; }
            bool dex = depth.isExact();
            if (!dex && sgnOK(laddc(depth, -JINF)) < 0) { if (getenv("KDDBG")) fprintf(stderr, "KDSTOP depth %s\n", linstr(depth).c_str()); break; }
            KOp op; op.depth = depth; op.v = it.v; K.ops.push_back(op); Q.pop_front();
            i128 dlb = it.v.isExact() ? it.v.c : 1;
            if (exTrack && dex && it.v.isExact()) { i128 r = Uiterex(depth.c, dlb, Bex, VT); if (r >= 0) Bex = r; else exTrack = false; }
            else exTrack = false;
            if (!dex || depth.c >= 2) hugeB = true;
            if (exTrack) { depth = laddc(depth, 1); SL = lsub(LC(Bex), lscale(depth, 2)); }
            else { SL = ladd(SL, laddc(lscale(depth, 2 * dlb), 5 * dlb)); depth = laddc(depth, 1); SL = laddc(SL, -2); }
        }
        if (K.ops.empty() && aL.isExact() && aL.c == 0) return false;
        while (!Q.empty() && zeroItem(Q.back())) Q.pop_back();
        // value
        Lin Bres;
        try {
            if (K.ops.empty()) Bres = B0;
            else {
                bool pf = hasProof(B0);
                for (auto &op : K.ops) pf = pf || hasProof(op.depth) || hasProof(op.v) || hasProof(op.m);
                KStruct Ks = K;
                if (pf) { Ks.B0 = shadowOf(K.B0); for (auto &op : Ks.ops) { op.depth = shadowOf(op.depth); op.v = shadowOf(op.v); op.m = shadowOf(op.m); } }
                ProvMain pm; VC r = kValue(Ks, pm);
                Lin sh;
                if (r.huge) {
                    i128 lb = kLower(Ks, [](const Lin &e) -> i128 { try { return lbG(e); } catch (Undec &) { return 0; } });
                    lb = max(lb, HUGEMIN);
                    string desc = "K(B0=" + linstr(Ks.B0) + ";n=" + to_string(Ks.ops.size()) + ";dep=" + linstr(shadowOf(depth)) + ")";
                    int gid = newG(lb, r.r, desc); sh = LV(gid); ++kdBig;
                    // linear lower bound: the last application at depth J gives >= X_(J-1) >= 2^(J+1) J >= 128 J for J >= 6
                    // (Coq Xbound; U_J(x) = iter _ U_(J-1) X_(J-1) >= X_(J-1); iterates only increase)
                    try { const Lin &J = Ks.ops.back().depth; if (sgnG(laddc(J, -6)) >= 0) { GS[gid].lbf = lscale(J, 128); GS[gid].hasLbf = true; } } catch (Undec &) {}
                } else sh = LC(r.v);
                if (!pf) Bres = sh;
                else { PC->ks.push_back(K); PSym z{'Z', sh, Lin(), Lin()}; z.sub = 'K'; z.kd = (int)PC->ks.size() - 1; PC->s.push_back(z); Bres = LV(PBASE + (int)PC->s.size() - 1); }
            }
        } catch (Undec &u) { if (getenv("KDDBG")) fprintf(stderr, "KDVAL %s\n", u.why.c_str()); if (proof) throw; return false; }
        // rebuild the right side: new prefix 1^(B+1) 0 0^depth, then the list from the first digit not cleared
        for (auto &r : L) touch(0, r);
        touchBottom(0);
        vector<Run> keepFar;   // runs pushed (far to near) between the kept original runs and the new prefix
        int cutIdx = -1;       // R[0..cutIdx] stay as they are
        if (Q.empty()) { for (auto &r : R) touch(1, r); touchBottom(1); cutIdx = -1; }
        else {
            const KPos &p = Q.front().pos;
            int pi = p.pi;
            for (int k = pi + 1; k < (int)rp.size(); ++k) if (rp[k].orig >= 0) { cutIdx = rp[k].orig; break; }
            for (int k = (int)rp.size() - 1; k > pi; --k) if (rp[k].orig < 0) keepFar.push_back(Run{rp[k].w, rp[k].n});
            for (int i = (int)R.size() - 1; i > cutIdx; --i) touch(1, R[i]);
            if (cutIdx >= 0) touch(1, R[cutIdx]);   // the run just beyond the read part (its first cell bounds the digit)
            const string &w = rp[pi].w;
            Lin restCopies = lsub(laddc(rp[pi].n, -1), p.copy);
            if (!(restCopies.isExact() && restCopies.c == 0)) keepFar.push_back(Run{w, restCopies});
            keepFar.push_back(Run{w.substr((size_t)p.ch), LC(1)});
        }
        L.clear(); R.resize((size_t)(cutIdx + 1));
        for (auto &r : keepFar) pushRaw(1, r);
        if (!Q.empty()) {
            if (!(depth.isExact() && depth.c == 0)) pushRaw(1, Run{"0", depth});
            pushRaw(1, Run{"0", LC(1)});
        }
        pushRaw(1, Run{"1", laddc(Bres, 1)});
        c.q = 3; c.f = 0; stepsKnown = false; ++kdJumps;
        if (!proof) {
            jlog.push_back("K" + to_string(K.ops.size()) + (Q.empty() ? "" : "p") + ":" + linstr(B0) + ">" + linstr(Bres) + "@" + linstr(depth));
            if (jlog.size() > 12) jlog.erase(jlog.begin());
        }
        return true;
    }
    // rule application; returns -1 not applied, else status
    int applyRule(Rule &R) {
        auto &C = c;
        for (int s = 0; s < 2; ++s) {
            if (C.st[s].size() < R.g[s].size()) return -1;
            if (R.bottom[s] && C.st[s].size() != R.g[s].size()) return -1;
            size_t sz = C.st[s].size();
            for (size_t i = 0; i < R.g[s].size(); ++i) if (C.st[s][sz - 1 - i].w != R.g[s][i].w) return -1;
        }
        for (int s = 0; s < 2; ++s) { size_t sz = C.st[s].size(); for (size_t i = 0; i < R.g[s].size(); ++i) touch(s, C.st[s][sz - 1 - i]); if (R.bottom[s]) touchBottom(s); }
        try {
            vector<Lin> bind(R.nv); for (auto &b : bind) b.D = 0;
            for (int s = 0; s < 2; ++s) {
                size_t sz = C.st[s].size();
                for (size_t i = 0; i < R.g[s].size(); ++i) {
                    const Lin &n = C.st[s][sz - 1 - i].n; int v = R.rv[s][i];
                    if (v < 0) { if (n.isExact() ? n.c != R.g[s][i].n.c : cmpL(n, R.g[s][i].n) != 0) return -1; }
                    else bind[v] = n;
                }
            }
            for (auto &cn : R.cons) {
                Lin v = subst(cn.N, bind);
                if (cn.k == 'G' && sgn(v) < 0) return -1;
                if (cn.k == 'E' && sgn(v) != 0) return -1;
                if (cn.k == 'C' && (i128)res(v, (ll)cn.q) != cn.r) return -1;
            }
            // number of applications
            bool inf = true; Lin k; bool haveK = false;
            for (auto &cn : R.cons) {
                i128 B = 0;
                for (int t = 0; t < cn.N.n; ++t) if (cn.N.id[t] >= PBASE) B = A_(B, M_(cn.N.a[t], R.delta[cn.N.id[t] - PBASE]));
                Lin kc; bool lim = false;
                if (cn.k == 'G' && B < 0) {
                    Lin A = subst(cn.N, bind);
                    ll rr = res(A, (ll)(-B));
                    kc = laddc(lscale(laddc(A, -rr), 1, -B), 1); lim = true;
                } else if ((cn.k == 'E' && B != 0) || (cn.k == 'C' && pmod(B, cn.q) != 0)) { kc = LC(1); lim = true; }
                if (lim) { inf = false; if (!haveK || cmpL(kc, k) < 0) { k = kc; haveK = true; } }
            }
            if (inf) { cyc = "LIN"; return S_CYCLE; }
            // apply k times
            if (R.stepsKnown && stepsKnown) {
                // sum_{t<k} S(bind + t delta) = k S(bind) + sd k(k-1)/2
                try {
                    Lin S0 = subst(R.steps, bind); i128 sd = 0;
                    for (int t = 0; t < R.steps.n; ++t) if (R.steps.id[t] >= PBASE) sd = A_(sd, M_(R.steps.a[t], R.delta[R.steps.id[t] - PBASE]));
                    if (!k.isExact() || !S0.isExact()) UD("steps");
                    i128 kk = k.c; addSteps(LC(A_(M_(kk, S0.c), M_(sd, M_(kk, kk - 1) / 2))));
                } catch (Undec &) { stepsKnown = false; }
            } else stepsKnown = false;
            for (int s = 0; s < 2; ++s) {
                size_t sz = C.st[s].size();
                for (size_t i = 0; i < R.g[s].size(); ++i) {
                    int v = R.rv[s][i]; if (v < 0) continue;
                    Lin nn = lcomb(bind[v], 1, k, R.delta[v]); normCount(nn);
                    C.st[s][sz - 1 - i].n = nn;
                }
            }
            ++R.uses; ++ruleApps;
            return S_OK;
        } catch (Undec &u) {
            if (proof) throw;
            lastUndec = "rule: " + u.why;
            return -1;
        }
    }
    int tryRules() {
        if (!rules || rules->R.empty()) return -1;
        const auto &F = c.st[c.f];
        auto it = rules->idx.find(ruleKey(c.q, c.f, F.empty() ? string() : F.back().w));
        if (it == rules->idx.end()) return -1;
        for (int id : it->second) { int r = applyRule(rules->R[id]); if (r >= 0) return r; }
        return -1;
    }
    int macroStep() {
        ++macro;
        int r = tryRules(); if (r >= 0) return r;
        if (chOK && c.q == 3 && tryKd()) return S_OK;
        int f = c.f; auto &F = c.st[f];
        if (F.empty()) {
            touchBottom(f);
            const Tr &t = TT[c.q][0];
            if (!t.halt && t.d == f && t.nx == c.q) { cyc = "ESCAPE"; return S_CYCLE; }
            return litStep();
        }
        touch(f, F.back());
        MiniRes mr = mini(c.q, f, F.back().w);
        if (mr.kind == 'H' || mr.kind == 'X') return litStep();
        if (mr.kind == 'L') { cyc = "BOUNDED"; return S_CYCLE; }
        if (mr.kind == 'F' && mr.q == c.q) {
            Run run = F.back(); F.pop_back();
            addSteps(lscale(run.n, mr.steps));
            push(1 - f, Run{rev(mr.w), run.n});
            return S_OK;
        }
        if (F.back().w.size() >= 2 && !isOne(F.back().n) && tryRotate()) return S_OK;
        popCopy(f); addSteps(LC(mr.steps));
        if (mr.kind == 'F') push(1 - f, Run{rev(mr.w), LC(1)});
        else { push(f, Run{mr.w, LC(1)}); c.f = 1 - f; }
        c.q = mr.q;
        return S_OK;
    }
    string show(int maxRuns = 40) const {
        string s;
        auto cnt = [](const Lin &n) { return n.isExact() ? s128(n.c) : "{" + linstr(n) + "}"; };
        const auto &L = c.st[0], &R = c.st[1];
        int i0 = max(0, (int)L.size() - maxRuns); if (i0 > 0) s += "... ";
        for (int i = i0; i < (int)L.size(); ++i) { s += rev(L[i].w); if (!(L[i].n.isExact() && L[i].n.c == 1)) s += "^" + cnt(L[i].n); s += " "; }
        if (c.f == 1) s += string(1, char('A' + c.q)) + "> "; else s += "<" + string(1, char('A' + c.q)) + " ";
        for (int i = (int)R.size() - 1, k = 0; i >= 0 && k < maxRuns; --i, ++k) { s += R[i].w; if (!(R[i].n.isExact() && R[i].n.c == 1)) s += "^" + cnt(R[i].n); s += " "; }
        return s;
    }
    Lin sigma() const {
        Lin s = LC(0);
        for (int k = 0; k < 2; ++k) for (auto &r : c.st[k]) { int o = count1(r.w); if (o) s = ladd(s, lscale(r.n, o)); }
        return s;
    }
    ull signature() const {
        ull h = 1469598103934665603ULL; auto mix = [&](ull x) { h ^= x; h *= 1099511628211ULL; };
        mix(c.q); mix(c.f);
        // only the SIGWIN runs nearest the head enter the signature (it only triggers proof attempts; rules carry their own touched prefix)
        for (int k = 0; k < 2; ++k) { mix(0xABCD + k); int cnt = 0; for (int i = (int)c.st[k].size() - 1; i >= 0 && cnt < SIGWIN; --i, ++cnt) { const Run &r = c.st[k][i]; mix(std::hash<string>()(r.w)); mix(r.n.isExact() && r.n.c == 1 ? 1 : 2); } }
        return h;
    }
};

// ------------------------------------------------------------------ prover
// A proof generalises counts of the current configuration into variables x_k (shadow = current value),
// simulates DELTA macro steps symbolically, and compares the end configuration with the start.
//  LINEAR rule: every generalised count ends as x_k + d_k (d_k exact) and no W symbol was created.  Stored and
//    applied k times at once (k from the recorded constraints); if no constraint limits k it is an infinite rule.
//  GENERAL (nonlinear) loop: counts end as arbitrary forms e_k(x) (e.g. 3x+5 or a fresh W(...) symbol).  It is a
//    CYCLE certificate when every recorded constraint C satisfies  C(x) => C(e(x))  for all x satisfying the
//    constraints (checked by lower bounds, exact differences and residue arithmetic; W symbols are discharged by
//    monotonicity of W and the residue law).
struct ProofOut { int st = 0; string why; Rule rule; string kind; };   // st: 0 fail, 1 linear rule, 2 cycle, 3 k=1 rule
struct PCGuard { PCtx *old; PCGuard(PCtx *n) : old(PC) { PC = n; } ~PCGuard() { PC = old; } };

static bool allNonneg(const Lin &e) { for (int k = 0; k < e.n; ++k) if (e.a[k] < 0) return false; return true; }
static bool mentionsZ(const Lin &e) { for (int k = 0; k < e.n; ++k) if (e.id[k] >= PBASE && PC->s[e.id[k] - PBASE].kind == 'Z') return true; return false; }
struct Pres {
    vector<i128> lbv; map<int, i128> lbz;
    void init() {
        lbv.assign(PC->s.size(), 1);
        for (auto &cn : PC->cons) if (cn.k == 'G' && cn.N.n == 1 && cn.N.id[0] >= PBASE && cn.N.a[0] > 0 && PC->s[cn.N.id[0] - PBASE].kind == 'P') {
            int v = cn.N.id[0] - PBASE; lbv[v] = max(lbv[v], cdiv(-cn.N.c, cn.N.a[0]));
        }
    }
    i128 LBe(const Lin &e) {
        if (!allNonneg(e)) UD("lb: negative coefficient");
        i128 s = e.c; bool ovf = false;
        for (int k = 0; k < e.n && !ovf; ++k) {
            i128 l;
            if (e.id[k] < PBASE) l = GS[e.id[k]].lb;
            else { int v = e.id[k] - PBASE; l = PC->s[v].kind == 'P' ? lbv[v] : LBZ(v); }
            i128 t; if (__builtin_mul_overflow(e.a[k], l, &t) || __builtin_add_overflow(s, t, &s)) ovf = true;
        }
        if (ovf) return SYMCAP;
        return min(cdiv(s, e.D), SYMCAP);
    }
    i128 LBZ(int v) {
        auto it = lbz.find(v); if (it != lbz.end()) return it->second;
        const PSym &z = PC->s[v];
        i128 w = kLower(PC->ks[z.kd], [&](const Lin &e) -> i128 { try { return LBe(e); } catch (Undec &) { return (i128)0; } });
        lbz[v] = w; return w;
    }
    // make sure E >= v holds under the constraints; if not implied, add it (valid for the shadow) when E has no Z
    void requireLB(const Lin &E, i128 v) {
        try { if (allNonneg(E) && LBe(E) >= v) return; } catch (Undec &) {}
        if (mentionsZ(E)) UD("requireLB on Z form");
        if (sgnG(laddc(shadowOf(E), -v)) < 0) UD("requireLB: shadow below bound");
        Cons cn; cn.k = 'G'; cn.N = laddc(numer(E), -M_(v, E.D)); addCons(cn);
        if (E.n == 1 && E.id[0] >= PBASE && E.a[0] > 0) { int x = E.id[0] - PBASE; lbv[x] = max(lbv[x], cdiv(M_(v, E.D) - E.c, E.a[0])); }
    }
    // raise the lower bounds of the (Z-free) arguments of every Z in E to min(shadow bound, 64), recursively
    void strengthen(const Lin &E, int depth = 0) {
        if (depth > 6) return;
        for (int k = 0; k < E.n; ++k) {
            if (E.id[k] < PBASE || PC->s[E.id[k] - PBASE].kind != 'Z') continue;
            const PSym z = PC->s[E.id[k] - PBASE];
            for (const Lin *arg : {&z.J, &z.A, &z.B, &z.K}) {
                if (arg->n == 0) continue;
                if (mentionsZ(*arg)) { strengthen(*arg, depth + 1); continue; }
                try { i128 sv = lbG(shadowOf(*arg)); requireLB(*arg, min<i128>(sv, 64)); } catch (Undec &) {}
            }
        }
        lbz.clear();
    }
    ll resZ(int v, ll m) {
        if (MG % m != 0) UD("Z residue modulus");
        const PSym &z = PC->s[v];
        struct PP { Pres *P; bool exact(const Lin &e, i128 &x) { if (e.isExact()) { x = e.c; return true; } return false; }
                    ll res(const Lin &e, ll mm) { return P->resAbs(e, mm); } void ge(const Lin &e, i128 c) { P->requireLB(e, c); } } pp{this};
        KStruct K = PC->ks[z.kd];
        VC r = kValue(K, pp);
        if (!r.huge) UD("Z: small");
        return r.r % m;
    }
    ll resAbs(const Lin &e, ll m) {
        if (m == 1) return 0;
        i128 Q = M_(m, e.D); i128 t = pmod(e.c, Q);
        for (int k = 0; k < e.n; ++k) {
            i128 need = Q / gcd_(e.a[k], Q); if (need == 1) continue;
            ll rv;
            if (e.id[k] < PBASE) rv = resG(LV(e.id[k]), (ll)need);
            else {
                int v = e.id[k] - PBASE;
                if (PC->s[v].kind == 'P') { rv = resG(PC->s[v].shadow, (ll)need); Cons cn; cn.k = 'C'; cn.N = LV(e.id[k]); cn.q = need; cn.r = rv; addCons(cn); }
                else rv = resZ(v, (ll)need);
            }
            t = pmod(t + pmod(e.a[k], Q) * (i128)rv, Q);
        }
        if (t % e.D != 0) UD("resAbs nonintegral");
        return (ll)((t / e.D) % m);
    }
};
static Lin substE(const Lin &N, const vector<Lin> &e) {
    Lin r = LC(N.c);
    for (int k = 0; k < N.n; ++k) {
        if (N.id[k] >= PBASE && PC->s[N.id[k] - PBASE].kind == 'P') r = lcomb(r, 1, e[N.id[k] - PBASE], N.a[k]);
        else r = lcomb(r, 1, LV(N.id[k]), N.a[k]);
    }
    return lscale(r, 1, N.D);
}
static bool preserve(const vector<Lin> &e, string &why) {
    Pres P; P.init();
    try {
        for (size_t i = 0; i < PC->cons.size(); ++i) {
            Cons cn = PC->cons[i];
            if (mentionsZ(cn.N)) {
                if (cn.k == 'G') {
                    bool ok = allNonneg(cn.N) && P.LBe(cn.N) >= 0;
                    if (!ok && allNonneg(cn.N)) { P.strengthen(cn.N); ok = P.LBe(cn.N) >= 0; }
                    if (!ok) { why = "Z-ineq " + linstr(cn.N); return false; }
                }
                else if (cn.k == 'E') { why = "Z-eq"; return false; }
                else if ((i128)P.resAbs(cn.N, (ll)cn.q) != cn.r) { why = "Z-cong"; return false; }
                continue;
            }
            Lin Ne = substE(cn.N, e);
            if (cn.k == 'G') {
                Lin Dif = lsub(Ne, cn.N);
                bool ok = allNonneg(Dif) && P.LBe(Dif) >= 0;
                if (!ok) ok = allNonneg(Ne) && P.LBe(Ne) >= 0;
                if (!ok) { why = "ineq " + linstr(cn.N) + " -> " + linstr(Ne); return false; }
            } else if (cn.k == 'E') { if (!lequal(Ne, cn.N)) { why = "eq"; return false; } }
            else if ((i128)P.resAbs(Ne, (ll)cn.q) != cn.r) { why = "cong " + linstr(cn.N) + " mod " + s128(cn.q); return false; }
        }
    } catch (Undec &u) { why = "pres-undec " + u.why; return false; }
    return true;
}
static ll MAXDELTA = 20000;
static bool SHOWPROOF = false;
static string cfgStr(const Cfg &c);
static ProofOut proofRun(Sim &M, const vector<char> &gen, ll nsteps) {
    ProofOut o; PCtx ctx; PCGuard guard(&ctx);
    Sim P; P.proof = true; P.chOK = M.chOK; P.rules = M.rules; P.c = M.c; P.prover = false;
    int Gsz[2]; vector<Run> G[2]; size_t gi = 0;
    for (int s = 0; s < 2; ++s) {
        auto &V = P.c.st[s]; Gsz[s] = (int)V.size();
        for (int i = 0; i < (int)V.size(); ++i) {
            Run &r = V[V.size() - 1 - i]; r.tag = i;
            if (gen[gi++]) {
                int k = (int)ctx.s.size(); ctx.s.push_back(PSym{'P', r.n, Lin(), Lin()}); r.n = LV(PBASE + k);
                Cons cn; cn.k = 'G'; cn.N = laddc(LV(PBASE + k), -1); addCons(cn);
            }
            G[s].push_back(r);
        }
    }
    try {
        for (ll t = 0; t < nsteps; ++t) { int st = P.macroStep(); if (st != S_OK) { o.why = "stopped"; return o; } }
    } catch (Undec &u) { o.why = "undec " + u.why; return o; }
    if (P.c.q != M.c.q || P.c.f != M.c.f) { o.why = "state"; return o; }
    Rule &R = o.rule; R.q = M.c.q; R.f = M.c.f; bool extras = false;
    vector<Lin> e(ctx.s.size()); for (size_t k = 0; k < e.size(); ++k) e[k] = LV(PBASE + (int)k);
    vector<char> inPrefix(ctx.s.size(), 0);
    for (int s = 0; s < 2; ++s) {
        int dG = P.bot[s] ? Gsz[s] : min(Gsz[s], P.maxTag[s] + 1);
        int u = Gsz[s] - dG;
        auto &E = P.c.st[s];
        if ((int)E.size() < u) { o.why = "short"; return o; }
        for (int i = 0; i < u; ++i) if (E[i].tag != Gsz[s] - 1 - i) { o.why = "untouched block"; return o; }
        int dE = (int)E.size() - u;
        if (dE < dG) { o.why = "prefix length"; return o; }
        // runs created between the matched prefix and the untouched block are never read again (they lie below the
        // touched depth): allowed for CYCLE certificates only
        if (dE > dG && P.bot[s]) { o.why = "extras below a read bottom"; return o; }   // the blank beyond was read: extras would be read next time
        if (dE > dG) extras = true;
        for (int i = 0; i < dG; ++i) {
            const Run &gr = G[s][i]; const Run &er = E[E.size() - 1 - i];
            if (gr.w != er.w) { o.why = "word"; return o; }
            if (gr.n.isExact()) { if (!lequal(er.n, gr.n)) { o.why = "exact count"; return o; } R.rv[s].push_back(-1); }
            else { int v = gr.n.id[0] - PBASE; e[v] = er.n; R.rv[s].push_back(v); inPrefix[v] = 1; }
            R.g[s].push_back(gr);
        }
        R.bottom[s] = P.bot[s];
    }
    bool hasZ = false; for (auto &x : ctx.s) if (x.kind == 'Z') hasZ = true;
    bool linear = !hasZ;
    R.nv = (int)ctx.s.size(); R.delta.assign(R.nv, 0);
    for (int v = 0; v < R.nv && linear; ++v) if (inPrefix[v]) {
        const Lin &x = e[v];
        if (x.n == 1 && x.id[0] == PBASE + v && x.a[0] == 1 && x.D == 1) R.delta[v] = x.c; else linear = false;
    }
    if (linear) {
        for (auto &cn : ctx.cons) {
            bool ok = true;
            for (int t = 0; t < cn.N.n; ++t) if (cn.N.id[t] >= PBASE && !inPrefix[cn.N.id[t] - PBASE]) ok = false;
            if (ok) R.cons.push_back(cn);
            else if (!(cn.k == 'G' && cn.N.n == 1 && cn.N.a[0] == 1 && cn.N.c == -1)) { o.why = "constraint on untouched var"; return o; }
        }
        R.stepsKnown = P.stepsKnown; R.steps = P.steps;
        bool inf = true, onlyCE = true;
        for (auto &cn : R.cons) {
            i128 B = 0; for (int t = 0; t < cn.N.n; ++t) if (cn.N.id[t] >= PBASE) B += cn.N.a[t] * R.delta[cn.N.id[t] - PBASE];
            if (cn.k == 'G' && B < 0) { inf = false; onlyCE = false; }
            if ((cn.k == 'E' && B != 0) || (cn.k == 'C' && pmod(B, cn.q) != 0)) inf = false;
        }
        if (SHOWPROOF) {
            fprintf(stderr, "PROOF linear delta=%lld inf=%d\n  G : %s\n  G': %s\n", nsteps, inf, cfgStr(M.c).c_str(), cfgStr(P.c).c_str());
            for (int v = 0; v < R.nv; ++v) if (inPrefix[v]) fprintf(stderr, "  x%d shadow=%s delta=%s\n", v, linstr(ctx.s[v].shadow).c_str(), s128(R.delta[v]).c_str());
            for (auto &cn : R.cons) fprintf(stderr, "  cons %c %s %s %s\n", cn.k, linstr(cn.N).c_str(), cn.k == 'C' ? s128(cn.q).c_str() : "", cn.k == 'C' ? s128(cn.r).c_str() : "");
        }
        if (inf) { o.st = 2; o.kind = string("LIN") + (P.jumps ? "-CH" : "") + (extras ? "-X" : ""); return o; }
        if (extras) { o.why = "finite rule with extra runs"; return o; }
        o.st = onlyCE ? 3 : 1; return o;
    }
    // nonlinear: inductive cycle?
    string why;
    bool okp = preserve(e, why);
    if (SHOWPROOF) {
        fprintf(stderr, "PROOF nonlinear delta=%lld ok=%d why=%s\n  G : %s\n  G': %s\n", nsteps, okp, why.c_str(), cfgStr(M.c).c_str(), cfgStr(P.c).c_str());
        for (int v = 0; v < (int)ctx.s.size(); ++v) fprintf(stderr, "  %c%d shadow=%s%s%s -> %s\n", ctx.s[v].kind == 'P' ? 'x' : 'Z', v, linstr(ctx.s[v].shadow).c_str(),
            ctx.s[v].kind == 'Z' ? (ctx.s[v].sub == 'I' ? " = I(" + linstr(ctx.s[v].J) + "," + linstr(ctx.s[v].A) + "," + linstr(ctx.s[v].B) + ")" : " = W(" + linstr(ctx.s[v].J) + "," + linstr(ctx.s[v].B) + ")").c_str() : "", inPrefix[v] ? "" : " (untouched)", linstr(e[v]).c_str());
        for (auto &cn : ctx.cons) fprintf(stderr, "  cons %c %s %s %s\n", cn.k, linstr(cn.N).c_str(), cn.k == 'C' ? s128(cn.q).c_str() : "", cn.k == 'C' ? s128(cn.r).c_str() : "");
    }
    if (okp) {
        bool aff = false; for (int v = 0; v < R.nv; ++v) if (inPrefix[v] && !(e[v].n == 1 && e[v].id[0] == PBASE + v && e[v].a[0] == 1 && e[v].D == 1)) aff = true;
        o.st = 2; o.kind = string("GEN") + (hasZ ? "-W" : "") + (aff ? "-AFF" : "") + (extras ? "-X" : "");
        return o;
    }
    o.why = "nonlin: " + why; return o;
}
static void addRule(Sim &M, const Rule &R) {
    RuleSet &RS = *M.rules;
    if (RS.R.size() >= 5000) return;
    RS.R.push_back(R);
    string top = R.g[R.f].empty() ? string() : R.g[R.f][0].w;
    RS.idx[ruleKey(R.q, R.f, top)].push_back((int)RS.R.size() - 1);
}
static ll PROOFS = 0, PROOFOK = 0; static bool NOCYCLE = false;   // --nocycle: never claim CYCLE (validation)
// returns 0 nothing, 1 rule added, 2 cycle (M.cyc set)
static int tryProve(Sim &M, ll delta) {
    ++PROOFS;
    vector<char> genA;
    for (int s = 0; s < 2; ++s) for (int i = (int)M.c.st[s].size() - 1; i >= 0; --i) { const Lin &n = M.c.st[s][i].n; genA.push_back(!(n.isExact() && n.c == 1)); }
    ProofOut best; best.st = 0;
    auto attempt = [&](const vector<char> &gen) -> int {
        for (int mult = 1; mult <= 6; ++mult) {
            if (delta * mult > 6 * MAXDELTA) break;
            ProofOut o = proofRun(M, gen, delta * mult);
            if (o.st == 2) { if (NOCYCLE) return 0; M.cyc = o.kind + (mult > 1 ? "x" + to_string(mult) : ""); ++PROOFOK; return 2; }
            if (o.st == 1) { addRule(M, o.rule); ++PROOFOK; return 1; }
            bool retry = o.st == 3 || o.why.rfind("nonlin: cong", 0) == 0 || o.why.rfind("nonlin: Z-cong", 0) == 0;
            if (!retry) { if (M.trace) fprintf(stderr, "   proof fail d=%lld x%d: %s\n", delta, mult, o.why.c_str()); return 0; }
        }
        return 0;
    };
    int r = attempt(genA);
    if (r) return r;
    // strategy B: keep counts that do not change over one period exact
    Sim S = M; S.prover = false; S.trace = false;
    try { for (ll t = 0; t < delta; ++t) if (S.macroStep() != S_OK) return 0; } catch (Undec &) { return 0; }
    if (S.signature() != M.signature()) return 0;
    vector<char> genB; bool diff = false; size_t gi = 0;
    for (int s = 0; s < 2; ++s) for (int i = (int)M.c.st[s].size() - 1; i >= 0; --i) {
        const Lin &n0 = M.c.st[s][i].n, &n1 = S.c.st[s][i].n;
        bool g = !(n0.isExact() && n1.isExact() && n0.c == n1.c);
        genB.push_back(g); if (g != (bool)genA[gi]) diff = true; ++gi;
    }
    if (!diff) return 0;
    return attempt(genB);
}

static string cfgStr(const Cfg &c) { Sim t; t.c = c; return t.show(60); }
// ------------------------------------------------------------------ driver
struct Opts { ll budget = 1000000; bool noch = false, noprove = false, trace = false, tape = false, kd1 = false; i128 hlb = 0; ll tracemax = 2000; double tlimit = 0; };
static Opts OPT;
static bool initTape(Sim &M, int start, const vector<string> &tok) {
    M.c = Cfg(); M.c.q = start; M.c.f = 1;
    vector<Run> left, right; bool head = false;
    for (const string &t : tok) {
        if (t.size() == 2 && t[1] == '>' && t[0] >= 'A' && t[0] <= 'P') { head = true; M.c.q = t[0] - 'A'; continue; }
        size_t h = t.find('^'); string w = t.substr(0, h); Lin n = LC(1);
        if (h != string::npos) {
            string cs = t.substr(h + 1);
            if (cs[0] == 'H') { ll r = atoll(cs.c_str() + 1); i128 lb = OPT.hlb > 0 ? OPT.hlb : EXMAX + 1; n = LV(newG(lb, r, "H" + to_string(r))); }
            else n = LC(p128(cs.c_str()));
        }
        for (char ch : w) if (ch != '0' && ch != '1') return false;
        (head ? right : left).push_back(Run{w, n});
    }
    for (auto &r : left) M.pushRaw(0, Run{rev(r.w), r.n});
    for (int i = (int)right.size() - 1; i >= 0; --i) M.pushRaw(1, right[i]);
    return true;
}
static string symDescs(const Lin &e) {
    set<int> ids, done; for (int k = 0; k < e.n; ++k) if (e.id[k] < PBASE) ids.insert(e.id[k]);
    string s; int cnt = 0;
    while (!ids.empty() && cnt < 12) {
        int id = *ids.begin(); ids.erase(ids.begin()); if (done.count(id)) continue; done.insert(id); ++cnt;
        s += " X" + to_string(id) + "=" + GS[id].desc + "[r" + to_string(GS[id].res) + "]";
        const string &d = GS[id].desc;
        for (size_t p = 0; p < d.size(); ++p) if (d[p] == 'X') { int v = atoi(d.c_str() + p + 1); if (!done.count(v)) ids.insert(v); }
    }
    return s;
}
static string tapeDump(const Sim &M) {
    string cells; i128 tot = 0;
    for (auto &r : M.c.st[0]) { if (!r.n.isExact()) return "TAPE ?"; tot += r.n.c * r.w.size(); }
    for (auto &r : M.c.st[1]) { if (!r.n.isExact()) return "TAPE ?"; tot += r.n.c * r.w.size(); }
    if (tot > 20000000) return "TAPE big";
    for (auto &r : M.c.st[0]) { string w = rev(r.w); for (i128 t = 0; t < r.n.c; ++t) cells += w; }
    ll hp = (ll)cells.size() - (M.c.f == 0 ? 1 : 0);
    for (int i = (int)M.c.st[1].size() - 1; i >= 0; --i) { auto &r = M.c.st[1][i]; for (i128 t = 0; t < r.n.c; ++t) cells += r.w; }
    size_t a = cells.find('1'); if (a == string::npos) return "TAPE " + string(1, char('A' + M.c.q)) + " 0 -";
    size_t b = cells.rfind('1');
    return "TAPE " + string(1, char('A' + M.c.q)) + " " + to_string(hp - (ll)a) + " " + cells.substr(a, b - a + 1);
}
static bool FREE[16][2];
static string machStr() {
    string s;
    for (int q = 0; q < NS; ++q) {
        if (q) s += '_';
        for (int c = 0; c < 2; ++c) { const Tr &t = TT[q][c]; if (t.halt) s += "---"; else { s += char('0' + t.w); s += t.d ? 'R' : 'L'; s += char('A' + t.nx); } }
    }
    return s;
}
struct Runner {
    RuleSet RS; Sim M; unordered_map<ull, array<ll, 3>> past; string verdict = "BUDGET", detail = "-";
    Runner() {}
    Runner(const Runner &o) : RS(o.RS), M(o.M) { M.rules = &RS; }
    void run() {
        verdict = "BUDGET"; detail = "-";
        try {
            auto t0 = chrono::steady_clock::now();
            while (M.macro < OPT.budget) {
                if (OPT.tlimit > 0 && (M.macro & 1023) == 0 && chrono::duration<double>(chrono::steady_clock::now() - t0).count() > OPT.tlimit) { detail = "time"; break; }
                if (M.trace && M.macro < OPT.tracemax) fprintf(stderr, "%lld [%s] %s\n", M.macro, M.stepsKnown ? s128(M.steps.c).c_str() : "?", M.show().c_str());
                if (!OPT.noprove) {
                    ull sg = M.signature(); auto it = past.find(sg);
                    if (it == past.end()) past[sg] = {M.macro, -1, 0};
                    else {
                        auto &p = it->second; ll d = M.macro - p[0];
                        if (d == p[1] && p[2] < 3 && d <= MAXDELTA) {
                            int r = tryProve(M, d);
                            if (r == 2) { verdict = "CYCLE"; detail = M.cyc; break; }
                            if (r == 1) p[2] = 0; else p[2]++;
                        }
                        p[1] = d; p[0] = M.macro;
                    }
                    if (past.size() > 3000000) past.clear();
                }
                if ((M.macro & 511) == 0) for (int s = 0; s < 2; ++s) if (M.c.st[s].size() > 24) M.deepCompress(s);
                int st = M.macroStep();
                if (st == S_HALT) { verdict = "HALT"; break; }
                if (st == S_CYCLE) { verdict = "CYCLE"; detail = M.cyc; break; }
            }
        } catch (Undec &u) { verdict = "UNDECIDED"; detail = u.why; }
        catch (std::exception &ex) { verdict = "UNDECIDED"; detail = string("exception ") + ex.what(); }
        for (auto &ch : detail) if (ch == ' ') ch = '_';
    }
    string report(const string &tag, const string &mach, int start) {
        string sig = "?", sd;
        try {
            Lin s = M.sigma();
            if (verdict == "HALT" && M.haltS == 0) s = laddc(s, 1);   // the halting transition writes a 1
            sig = linstr(s); if (verdict == "HALT") sd = symDescs(s);
        } catch (Undec &) {}
        string jl; for (auto &x : M.jlog) jl += " " + x;
        char buf[600];
        snprintf(buf, sizeof buf, " macro=%lld steps=%s sigma=%s kd=%lld big=%lld hslot=%c%d rules=%zu apps=%lld syms=%zu |", M.macro,
                 M.stepsKnown ? s128(M.steps.c).c_str() : "?", sig.c_str(), M.kdJumps, M.kdBig, verdict == "HALT" ? 'A' + M.haltQ : '-',
                 verdict == "HALT" ? M.haltS : 0, RS.R.size(), M.ruleApps, GS.size());
        return tag + " " + mach + " " + string(1, char('A' + start)) + " " + verdict + " " + detail + buf + jl + " |" + sd;
    }
};
static void runOne(const string &mach, int start, const vector<string> &tok) {
    GS.clear(); MINI.clear();
    if (!parseMachine(mach, TT, NS)) { printf("R %s %c BAD\n", mach.c_str(), 'A' + start); return; }
    Runner R; R.M.rules = &R.RS; R.M.chOK = !OPT.noch && coreIntact(); R.M.trace = OPT.trace;
    if (!initTape(R.M, start, tok)) { printf("R %s %c BADTAPE\n", mach.c_str(), 'A' + start); return; }
    if (OPT.kd1) {   // one cascade jump from the start tape (validation)
        bool ok = false; try { ok = R.M.chOK && R.M.c.q == 3 && R.M.tryKd(); } catch (Undec &) {}
        printf("KD1 %s %d %s\n", mach.c_str(), ok ? 1 : 0, tapeDump(R.M).c_str()); fflush(stdout); return;
    }
    R.run();
    printf("%s\n", R.report("R", mach, start).c_str());
    if (OPT.tape) {
        if (R.verdict == "HALT") { R.M.popCell(R.M.c.f); R.M.pushRaw(R.M.c.f, Run{"1", LC(1)}); printf("%s\n", tapeDump(R.M).c_str()); }
        else printf("TAPE notshown\n");
    }
    if (R.M.trace) fprintf(stderr, "END %s\n", R.M.show().c_str());
    fflush(stdout);
}
// free-slot tree: every '---' slot of the input machine is free.  When the run reads a free slot, the halting leaf
// is reported and the 2*2*NS defined values are explored depth first, each continuing from the configuration where
// the slot was read (rules learned so far stay valid: their proofs never read an undefined slot).
static ll NODES = 0, NODECAP = 0;
static int SKIPQ = -1, SKIPS = 0; static Tr SKIPT;   // --skipval Qs:VAL  (subtree already covered elsewhere)
static void enumNode(Runner &R, int start) {
    R.run(); ++NODES;
    string mach = machStr();
    if (R.verdict == "CYCLE") printf("C %s %c %s kd=%lld big=%lld\n", mach.c_str(), 'A' + start, R.detail.c_str(), R.M.kdJumps, R.M.kdBig);
    else printf("%s\n", R.report("T", mach, start).c_str());
    fflush(stdout);
    if (!(R.verdict == "HALT" && FREE[R.M.haltQ][R.M.haltS])) return;
    if (NODECAP && NODES >= NODECAP) { printf("CAP %s %c\n", mach.c_str(), 'A' + start); return; }
    int q = R.M.haltQ, s = R.M.haltS;
    size_t gsz = GS.size();
    FREE[q][s] = false;
    for (int w = 0; w < 2; ++w) for (int d = 0; d < 2; ++d) for (int nx = 0; nx < NS; ++nx) {
        if (q == SKIPQ && s == SKIPS && w == SKIPT.w && d == SKIPT.d && nx == SKIPT.nx) continue;
        TT[q][s] = Tr{w, d, nx, false}; MINI.clear();
        { Runner C(R); enumNode(C, start); }
        GS.resize(gsz);
    }
    TT[q][s] = Tr{1, 1, -1, true}; MINI.clear(); FREE[q][s] = true;
}
static void enumRoot(const string &mach, int start) {
    GS.clear(); MINI.clear(); NODES = 0;
    if (!parseMachine(mach, TT, NS)) { printf("T %s %c BAD\n", mach.c_str(), 'A' + start); return; }
    for (int q = 0; q < NS; ++q) for (int c = 0; c < 2; ++c) FREE[q][c] = TT[q][c].halt;
    Runner R; R.M.rules = &R.RS; R.M.chOK = !OPT.noch && coreIntact(); R.M.trace = false;
    vector<string> tok; initTape(R.M, start, tok);
    enumNode(R, start);
    printf("S %s %c nodes=%lld\n", mach.c_str(), 'A' + start, NODES); fflush(stdout);
}
int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: jz run|enum|utab [opts] < input\n"); return 1; }
    string mode = argv[1];
    for (int i = 2; i < argc; ++i) {
        string a = argv[i];
        auto nx = [&]() { return string(argv[++i]); };
        if (a == "--budget") OPT.budget = atoll(nx().c_str());
        else if (a == "--mg") MG = atoll(nx().c_str());
        else if (a == "--exmax") EXMAX = p128(nx().c_str());
        else if (a == "--hlb") OPT.hlb = p128(nx().c_str());
        else if (a == "--maxdelta") MAXDELTA = atoll(nx().c_str());
        else if (a == "--noch") OPT.noch = true;
        else if (a == "--noprove") OPT.noprove = true;
        else if (a == "--trace") OPT.trace = true;
        else if (a == "--tracemax") OPT.tracemax = atoll(nx().c_str());
        else if (a == "--tape") OPT.tape = true;
        else if (a == "--tlimit") OPT.tlimit = atof(nx().c_str());
        else if (a == "--showproof") SHOWPROOF = true;
        else if (a == "--nodecap") NODECAP = atoll(nx().c_str());
        else if (a == "--jmax") JMAX = atoi(nx().c_str());
        else if (a == "--vt") VT = p128(nx().c_str());
        else if (a == "--kd1") OPT.kd1 = true;
        else if (a == "--nocycle") NOCYCLE = true;
        else if (a == "--skipval") { string v = nx(); SKIPQ = v[0] - 'A'; SKIPS = v[1] - '0'; SKIPT = Tr{v[3] - '0', v[4] == 'R' ? 1 : 0, v[5] - 'A', false}; }
        else { fprintf(stderr, "bad option %s\n", a.c_str()); return 1; }
    }
    buildU();
    if (mode == "utab") {
        printf("MG=%lld LAM2=%lld A3=%d JINF=%d\n", MG, LAM2, A3, JINF);
        for (int j = 2; j <= min(JMAX, JINF + 2); ++j) {
            const UTab &T = UT[j]; printf("j=%d h=%d pre=", j, T.h); for (auto v : T.pre) printf("%s,", s128(v).c_str());
            printf(" mu=%d lam=%d X=%s%lld\n", T.mu, T.lam, XC[j].huge ? "h" : "e", XC[j].huge ? XC[j].r : (ll)XC[j].v);
        }
        // queries:  U j x  -> class of U_j(x) (x exact);  I j v x -> class of iter v (U j) x;  H j r -> U_j(huge x == r)
        string line;
        while (getline(cin, line)) {
            istringstream is(line); string k, a1, a2, a3; if (!(is >> k >> a1 >> a2)) continue; is >> a3;
            try {
                VC r;
                if (k == "U") r = UV((int)p128(a1.c_str()), vexact(p128(a2.c_str())));
                else if (k == "I") r = Uiter((int)p128(a1.c_str()), p128(a2.c_str()), vexact(p128(a3.c_str())));
                else if (k == "H") r = UV((int)p128(a1.c_str()), VC{true, 0, (ll)(p128(a2.c_str()) % MG)});
                else continue;
                printf("%s %s %s %s %s %s\n", k.c_str(), a1.c_str(), a2.c_str(), a3.c_str(), r.huge ? "huge" : "exact", r.huge ? to_string(r.r).c_str() : s128(r.v).c_str());
            } catch (Undec &u) { printf("%s %s %s %s UNDEC %s\n", k.c_str(), a1.c_str(), a2.c_str(), a3.c_str(), u.why.c_str()); }
        }
        return 0;
    }
    string line;
    while (getline(cin, line)) {
        if (!line.empty() && line.back() == '\r') line.pop_back();
        istringstream is(line); string mach, st; if (!(is >> mach >> st)) continue;
        vector<string> tok; string t; while (is >> t) tok.push_back(t);
        if (mode == "enum") enumRoot(mach, st[0] - 'A');
        else runOne(mach, st[0] - 'A', tok);
    }
    return 0;
}
