// symsim.cpp: symbolic macro simulator for 2-symbol TMs, with sound HUGE counts, a Ligocki-style rule prover
// (linear acceleration rules + inductive CYCLE certificates) and the exact M9 Ch-jump (Coq CH_CA) when the
// 13 core slots of Argon's M9 engine are intact.          bb9_symsim, 2026-10-17
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
struct GSym { i128 lb; ll mod, res; string desc; };
static vector<GSym> GS;
struct PSym { char kind; Lin shadow; Lin J, B; char sub = 'W'; Lin A, K; };   // kind 'P' variable, 'Z' = W(J,B) (sub W) or iter A (W J) B (sub I)
struct Cons { char k; Lin N; i128 q = 0, r = 0; };   // 'G': N>=0  'E': N==0  'C': N == r mod q   (N.D == 1)
struct PCtx { vector<PSym> s; vector<Cons> cons; set<string> seen; };
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

// ------------------------------------------------------------------ W residue law
// value classes: exact v (< VT) or huge (>= VT) with residue mod MG
struct VC { bool huge; i128 v; ll r; };
static const i128 VT = (i128)1 << 62;
static VC vexact(i128 v) { if (v >= VT) return VC{true, 0, (ll)pmod(v, MG)}; return VC{false, v, 0}; }
struct WTab { int h; vector<i128> pre; int mu, lam; vector<ll> res; };
static vector<WTab> WT;   // WT[j], j >= 3
static int JINF = -1, JMAX = 40;
static ll LAM2; static int A3;   // 3^k mod 2MG: 0 mod 3^A3 for k >= A3, period LAM2 on the 3-free part
static ll powmod(ll b, i128 e, ll m) { i128 r = 1 % m, x = b % m; while (e > 0) { if (e & 1) r = r * x % m; x = x * x % m; e >>= 1; } return (ll)r; }
static ll w2res_exp(i128 e) {   // (3^e - 5)/2 mod MG, e = b+3
    ll m2 = 2 * MG; ll t = powmod(3, e, m2); ll u = pmod((i128)t - 5, m2); return (u / 2) % MG;
}
static VC WV(int j, const VC &b);
static const WTab &wtab(int j) { if (j >= JINF && JINF > 0) return WT[JINF]; return WT[j]; }
static VC WV(int j, const VC &b) {
    if (j == 0) { if (!b.huge) return vexact(b.v + 3); return VC{true, 0, (b.r + 3) % MG}; }
    if (j == 1) { if (!b.huge) return vexact(3 * b.v + 5); return VC{true, 0, (3 * b.r + 5) % MG}; }
    if (j == 2) {
        if (!b.huge) {
            if (b.v + 3 <= 39) { i128 p = 1; for (int i = 0; i < b.v + 3; ++i) p *= 3; return vexact((p - 5) / 2); }
            return VC{true, 0, w2res_exp(b.v + 3)};
        }
        // b >= VT: exponent class
        i128 e = A3 + pmod((i128)b.r + 3 - A3, LAM2);
        return VC{true, 0, w2res_exp(e)};
    }
    const WTab &T = wtab(j);
    if (!b.huge) {
        i128 t = b.v + 1;
        if (t < T.h) return VC{false, T.pre[(size_t)t], 0};
        if (t < T.h + T.mu) return VC{true, 0, T.res[(size_t)(t - T.h)]};
        return VC{true, 0, T.res[(size_t)(T.mu + pmod(t - T.h - T.mu, T.lam))]};
    }
    return VC{true, 0, T.res[(size_t)(T.mu + pmod((i128)b.r + 1 - T.h - T.mu, T.lam))]};
}
static bool wtabEq(const WTab &a, const WTab &b) { return a.h == b.h && a.pre == b.pre && a.mu == b.mu && a.lam == b.lam && a.res == b.res; }
static void buildW() {
    // j = 2 constants
    ll m2 = 2 * MG; A3 = 0; ll mm = m2; while (mm % 3 == 0) { mm /= 3; ++A3; }
    LAM2 = 1; { ll x = 3 % mm; while (x != 1 % mm) { x = x * 3 % mm; ++LAM2; } if (mm == 1) LAM2 = 1; }
    if (MG % LAM2 != 0) { fprintf(stderr, "MG=%lld: ord of 3 (%lld) does not divide MG\n", MG, LAM2); exit(2); }
    WT.assign(JMAX + 2, WTab{});
    JINF = -1;
    for (int j = 3; j <= JMAX + 1; ++j) {
        WTab T; vector<VC> seq; VC v = vexact(2);
        T.h = -1;
        map<ll, int> seen;
        for (int t = 0;; ++t) {
            if (!v.huge) { T.pre.push_back(v.v); }
            else {
                if (T.h < 0) T.h = t;
                auto it = seen.find(v.r);
                if (it != seen.end()) { T.mu = it->second - T.h; T.lam = t - it->second; break; }
                seen[v.r] = t; T.res.push_back(v.r);
            }
            v = WV(j - 1, v);
            if (t > 100000) { fprintf(stderr, "W table j=%d does not cycle\n", j); exit(2); }
        }
        if (MG % T.lam != 0) { fprintf(stderr, "W table j=%d: period %d does not divide MG\n", j, T.lam); exit(2); }
        WT[j] = T;
        if (j >= 4 && JINF < 0 && wtabEq(WT[j], WT[j - 1])) JINF = j - 1;
    }
    if (JINF < 0) { fprintf(stderr, "W tables do not stabilise\n"); exit(2); }
}
// exact W with cap: returns -1 if > cap
static i128 Wexact(i128 j, i128 b, i128 cap) {
    if (b < 0 || j < 0) return -1;
    if (j == 0) return b + 3 <= cap ? b + 3 : -1;
    if (j == 1) return b <= (cap - 5) / 3 ? 3 * b + 5 : -1;
    if (j == 2) { i128 p = 1; for (i128 i = 0; i < b + 3; ++i) { if (p > (2 * cap + 5) / 3) return -1; p *= 3; } i128 v = (p - 5) / 2; return v <= cap ? v : -1; }
    // j = 3: W(3,0) = 119, W(3,1) = W(2,119) > 10^57; j >= 4: W(j,b) >= W(4,0) = W(2,W(2,119)).  cap < 2^127.
    if (j == 3) return (b == 0 && 119 <= cap) ? 119 : -1;
    return -1;
}
static int bthresh(int j) { if (j == 2) return 40; const WTab &T = wtab(j); return T.h + T.mu + 1; }
static ll bmodulus(int j) { if (j == 2) return LAM2; return wtab(j).lam; }
// W(j,b) for global forms j, b (j >= 1)
static int wSymCount = 0;
static Lin Wglobal(const Lin &j, const Lin &b) {
    if (j.isExact() && j.c == 0) return laddc(b, 3);
    if (j.isExact() && j.c == 1) return laddc(lscale(b, 3), 5);
    int jj; // table index
    if (j.isExact()) jj = (int)min<i128>(j.c, (i128)JMAX);
    else { if (sgnG(laddc(j, -JINF)) < 0) UD("W: symbolic j below JINF"); jj = JINF; }
    if (jj < 2) UD("W: j<2");
    i128 lj = lbG(j);
    if (j.isExact() && b.isExact()) {
        i128 w = Wexact(j.c, b.c, EXMAX);
        if (w >= 0) return LC(w);
        VC r = WV(jj, VC{false, b.c, 0});
        if (!r.huge) { if (r.v <= EXMAX) UD("W: inconsistent class"); r = VC{true, 0, (ll)pmod(r.v, MG)}; }
        ++wSymCount;
        int id = newG(EXMAX + 1, r.r, "W(" + s128(j.c) + "," + s128(b.c) + ")");
        return LV(id);
    }
    VC bc;
    if (b.isExact()) bc = VC{false, b.c, 0};
    else {
        if (sgnG(laddc(b, -bthresh(jj))) < 0) UD("W: b below threshold");
        bc = VC{true, 0, resG(b, bmodulus(jj))};
    }
    VC r = WV(jj, bc);
    if (!r.huge) UD("W: small value from symbolic args");
    i128 lb = Wexact(lj, lbG(b), SYMCAP); if (lb < 0) lb = SYMCAP; lb = max(lb, EXMAX + 1);
    ++wSymCount;
    int id = newG(lb, r.r, "W(" + linstr(j) + "," + linstr(b) + ")");
    return LV(id);
}

// ------------------------------------------------------------------ iterated W:  I(j,a,b) = iter a (W j) b
// (BLK_iter_aux + CH_CA:  Ca j b (blk a z) -->+ Ca (j+1) (iter a (W j) b) z)
// orbit of value classes x_0 = b, x_{t+1} = W_j(x_t); returns the class of x_a.
// a exact: aEx >= 0.  a huge: aEx < 0, then needLam/needMu are set and aRes must be a mod needLam (call twice).
struct Orbit { vector<VC> seq; int mu = -1, lam = -1; };   // seq[t] = x_(t+1), t = 0.. until the first repeat of a huge residue
static Orbit orbitV(int jj, const VC &b) {   // starts at x_1 = W_j(b): every later class carries a full residue mod MG
    Orbit o; VC x = WV(jj, b); map<ll, int> seen;
    for (int t = 0; t < 100000; ++t) {
        if (x.huge) { auto it = seen.find(x.r); if (it != seen.end()) { o.mu = it->second; o.lam = t - it->second; return o; } seen[x.r] = t; }
        o.seq.push_back(x);
        x = WV(jj, x);
    }
    UD("orbit does not cycle");
}
static VC orbitAt(const Orbit &o, i128 a) {   // x_a for exact a >= 1
    i128 t = a - 1;
    if (t < (i128)o.seq.size()) return o.seq[(size_t)t];
    return o.seq[(size_t)(o.mu + pmod(t - o.mu, o.lam))];
}
static VC orbitAtRes(const Orbit &o, ll ares) {   // x_a for a - 1 >= seq.size(), a == ares mod lam
    return o.seq[(size_t)(o.mu + pmod((i128)ares - 1 - o.mu, o.lam))];
}
static i128 Iexact(i128 j, i128 a, i128 b, i128 cap) {   // exact iter a (W j) b, -1 if > cap
    if (j == 0) { if (a > (cap - b) / 3) return -1; return b + 3 * a; }
    i128 x = b;
    for (i128 t = 0; t < a; ++t) { x = Wexact(j, x, cap); if (x < 0) return -1; }
    return x;
}
static Lin Iglobal(const Lin &j, const Lin &a, const Lin &b) {
    if (j.isExact() && j.c == 0) return ladd(b, lscale(a, 3));
    if (a.isExact() && a.c == 0) return b;
    if (a.isExact() && a.c == 1) return Wglobal(j, b);
    int jj;
    if (j.isExact()) jj = (int)min<i128>(j.c, (i128)JMAX);
    else { if (sgnG(laddc(j, -JINF)) < 0) UD("I: symbolic j below JINF"); jj = JINF; }
    if (j.isExact() && a.isExact() && b.isExact()) { i128 v = Iexact(j.c, a.c, b.c, EXMAX); if (v >= 0) return LC(v); }
    VC bc;
    if (b.isExact()) bc = VC{false, b.c, 0};
    else {
        if (jj >= 2 && sgnG(laddc(b, -bthresh(jj))) < 0) UD("I: b below threshold");
        bc = VC{true, 0, resG(b, jj == 1 ? MG : bmodulus(jj))};
    }
    Orbit o = orbitV(jj, bc);
    VC r;
    if (a.isExact()) r = orbitAt(o, a.c);
    else {
        if (sgnG(laddc(a, -(i128)o.seq.size() - 1)) < 0) UD("I: a below orbit length");
        if (MG % o.lam != 0) UD("I: orbit period");
        r = orbitAtRes(o, resG(a, o.lam));
    }
    if (!r.huge) { if (r.v <= EXMAX) return LC(r.v); r = VC{true, 0, (ll)pmod(r.v, MG)}; }
    i128 lb = -1;
    try { i128 la = lbG(a); i128 lbb = lbG(b); i128 lj = lbG(j); lb = Iexact(lj, min<i128>(la, 64), lbb, SYMCAP); } catch (Undec &) {}
    if (lb < 0) lb = SYMCAP; lb = max(lb, EXMAX + 1);
    ++wSymCount;
    return LV(newG(lb, r.r, "I(" + linstr(j) + "," + linstr(a) + "," + linstr(b) + ")"));
}

// ------------------------------------------------------------------ k BLK jumps in a row:
// Ca j b ((0 1^(a+1))^k ... ) with a cell 0 after the run: x_0 = b, x_(t+1) = iter a (W (j+t)) x_t,
// result Ca (j+k) x_k.   M(j,a,k,b) = x_k  (a exact).
static VC IclassV(int jj, i128 a, const VC &x) {   // class of iter a (W jj) x, a >= 1 exact
    Orbit o = orbitV(jj, x); return orbitAt(o, a);
}
static Lin MBglobal(const Lin &j, i128 a, const Lin &k, const Lin &b) {
    if (a == 0) return b;
    if (k.isExact() && k.c <= 64) { Lin x = b; for (i128 t = 0; t < k.c; ++t) x = Iglobal(laddc(j, t), LC(a), x); return x; }
    // peel steps until j >= JINF
    Lin x = b, jj = j, kk = k;
    for (int t = 0; t < 8 && jj.isExact() && jj.c < JINF; ++t) {
        if (sgnG(laddc(kk, -1)) <= 0) UD("M: k too small");
        x = Iglobal(jj, LC(a), x); jj = laddc(jj, 1); kk = laddc(kk, -1);
    }
    if (sgnG(laddc(jj, -JINF)) < 0) UD("M: j below JINF");
    VC y0;
    if (x.isExact()) y0 = VC{false, x.c, 0};
    else { if (sgnG(laddc(x, -bthresh(JINF))) < 0) UD("M: b below threshold"); y0 = VC{true, 0, resG(x, bmodulus(JINF))}; }
    // orbit of y_(t+1) = class of iter a (W JINF) y_t, starting at y_1 (full residues mod MG)
    vector<VC> seq; map<ll, int> seen; int mu = -1, lam = -1; VC y = IclassV(JINF, a, y0);
    for (int t = 0; t < 100000; ++t) {
        if (y.huge) { auto it = seen.find(y.r); if (it != seen.end()) { mu = it->second; lam = t - it->second; break; } seen[y.r] = t; }
        seq.push_back(y); y = IclassV(JINF, a, y);
    }
    if (lam < 0) UD("M: orbit does not cycle");
    VC r;
    if (kk.isExact()) { i128 t = kk.c - 1; r = t < (i128)seq.size() ? seq[(size_t)t] : seq[(size_t)(mu + pmod(t - mu, lam))]; }
    else {
        if (sgnG(laddc(kk, -(i128)seq.size() - 1)) < 0) UD("M: k below orbit length");
        if (MG % lam != 0) UD("M: orbit period");
        r = seq[(size_t)(mu + pmod((i128)resG(kk, lam) - 1 - mu, lam))];
    }
    if (!r.huge) UD("M: small value");
    i128 lb = -1;
    try { lb = Iexact(lbG(jj), a, lbG(x), SYMCAP); } catch (Undec &) {}
    if (lb < 0) lb = SYMCAP; lb = max(lb, EXMAX + 1);
    ++wSymCount;
    return LV(newG(lb, r.r, "M(" + linstr(jj) + "," + s128(a) + "," + linstr(kk) + "," + linstr(x) + ")"));
}

// ------------------------------------------------------------------ machine
static int NS = 0;
struct Tr { int w, d, nx; bool halt; };   // d: 0 = L, 1 = R
static Tr TT[16][2];
static const char *M9 = "1RB1RA_0LI1RC_0LD1LG_0RE1LD_1RF1RF_0RB0RA_1RA0LH_1LG1LH_---0LD";
static const int CORE[13] = {0, 1, 3, 4, 5, 6, 7, 9, 11, 12, 13, 14, 15};
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
    Tr B[16][2]; int ns; parseMachine(M9, B, ns);
    if (NS != 9) return false;
    for (int i = 0; i < 13; ++i) {
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
    ll macro = 0, jumps = 0, ruleApps = 0;
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
        if (t.halt) { pushRaw(f, Run{"1", LC(1)}); addSteps(LC(1)); return S_HALT; }
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
    Lin computeW(const Lin &j, const Lin &b) {
        if (!hasProof(j) && !hasProof(b)) return Wglobal(j, b);
        if (j.isExact() && j.c == 1) return laddc(lscale(b, 3), 5);
        if (j.isExact() && j.c == 0) return laddc(b, 3);
        Lin sh = Wglobal(shadowOf(j), shadowOf(b));
        PC->s.push_back(PSym{'Z', sh, j, b});
        return LV(PBASE + (int)PC->s.size() - 1);
    }
    // Ch j b z = 0^inf (10)^j [H on the last 0] 1^(b+1) 0 z  -->  Ca j (W j b) z = 0^inf (10)^j 1^W [A on 0] z
    bool tryCh() {
        auto &L = c.st[0], &R = c.st[1];
        struct Piece { string w; Lin n; };
        vector<Piece> lp;
        if (c.f == 0) {
            if (L.empty()) { touchBottom(0); return false; }
            touch(0, L.back());
            const Run &t = L.back(); if (t.w[0] != '0') return false;
            if (t.w.size() > 1) lp.push_back({t.w.substr(1), LC(1)});
            if (!isOne(t.n)) lp.push_back({t.w, laddc(t.n, -1)});
            for (int i = (int)L.size() - 2; i >= 0; --i) lp.push_back({L[i].w, L[i].n});
        } else {
            if (R.empty()) { touchBottom(1); return false; }
            touch(1, R.back()); if (R.back().w[0] != '0') return false;
            for (int i = (int)L.size() - 1; i >= 0; --i) lp.push_back({L[i].w, L[i].n});
        }
        // right of head: 1^(b+1) then 0
        Lin bones = LC(0);
        {
            int skipTop = (c.f == 1);
            bool done = false;
            for (int i = (int)R.size() - 1; i >= 0 && !done; --i) {
                const Run &t = R[i]; touch(1, t);
                vector<Piece> ps;
                if (skipTop && i == (int)R.size() - 1) {
                    if (t.w.size() > 1) ps.push_back({t.w.substr(1), LC(1)});
                    if (!isOne(t.n)) ps.push_back({t.w, laddc(t.n, -1)});
                } else ps.push_back({t.w, t.n});
                for (auto &p : ps) {
                    if (allOne(p.w)) { bones = ladd(bones, lscale(p.n, (i128)p.w.size())); continue; }
                    size_t k = 0; while (p.w[k] == '1') ++k;
                    bones = laddc(bones, (i128)k); done = true; break;
                }
            }
            if (!done) touchBottom(1);
            if (bones.isExact() && bones.c < 1) return false;
        }
        // left of head: 1 (01)^(j-1) then zeros
        Lin ones = LC(0); char expect = '1';
        for (size_t i = 0; i < lp.size(); ++i) {
            Piece &p = lp[i];
            auto restZero = [&](size_t from) { for (size_t k = from; k < lp.size(); ++k) if (!allZero(lp[k].w)) return false; return true; };
            if (allZero(p.w)) { if (!restZero(i + 1)) return false; break; }
            if (alternating(p.w) && p.w[0] == expect) {
                if (p.w.size() % 2 == 0) { ones = ladd(ones, lscale(p.n, (i128)(p.w.size() / 2))); continue; }
                if (!isOne(p.n)) return false;
                ones = laddc(ones, count1(p.w)); expect = p.w.back() == '1' ? '0' : '1'; continue;
            }
            if (!isOne(p.n)) return false;
            size_t k = 0;
            for (; k < p.w.size() && p.w[k] == expect; ++k) { if (expect == '1') ones = laddc(ones, 1); expect = expect == '1' ? '0' : '1'; }
            if (expect == '0') return false;
            for (; k < p.w.size(); ++k) if (p.w[k] != '0') return false;
            if (!restZero(i + 1)) return false;
            break;
        }
        touchBottom(0);
        if (ones.isExact() && ones.c < 1) return false;
        // jump
        Lin j = ones, b = laddc(bones, -1);
        Lin W = computeW(j, b);
        if (c.f == 1) popCell(1);
        while (!R.empty()) {
            Run &t = R.back(); touch(1, t);
            if (allOne(t.w)) { R.pop_back(); continue; }
            string w = t.w; size_t k = 0; while (w[k] == '1') ++k;
            popCopy(1); pushRaw(1, Run{w.substr(k), LC(1)});
            break;
        }
        L.clear();
        pushRaw(0, Run{"01", j}); pushRaw(0, Run{"1", W});
        c.q = 0; c.f = 1; stepsKnown = false; ++jumps;
        if (!proof) {
            try { if (cmpL(j, maxJ) > 0) maxJ = j; } catch (Undec &) {}
            jlog.push_back(linstr(j) + ":" + linstr(b) + (W.isExact() ? "" : "*"));
            if (jlog.size() > 8) jlog.erase(jlog.begin());
        }
        return true;
    }
    Lin computeIter(const Lin &j, const Lin &a, const Lin &b) {
        if (!hasProof(j) && !hasProof(a) && !hasProof(b)) return Iglobal(j, a, b);
        if (j.isExact() && j.c == 0) return ladd(b, lscale(a, 3));
        if (a.isExact() && a.c == 0) return b;
        if (a.isExact() && a.c == 1) return computeW(j, b);
        Lin sh = Iglobal(shadowOf(j), shadowOf(a), shadowOf(b));
        PSym z{'Z', sh, j, b}; z.sub = 'I'; z.A = a; PC->s.push_back(z);
        return LV(PBASE + (int)PC->s.size() - 1);
    }
    Lin computeMB(const Lin &j, i128 a, const Lin &k, const Lin &b) {
        if (!hasProof(j) && !hasProof(k) && !hasProof(b)) return MBglobal(j, a, k, b);
        if (a == 0) return b;
        if (k.isExact() && k.c <= 64) { Lin x = b; for (i128 t = 0; t < k.c; ++t) x = computeIter(laddc(j, t), LC(a), x); return x; }
        Lin sh = MBglobal(shadowOf(j), a, shadowOf(k), shadowOf(b));
        PSym z{'Z', sh, j, b}; z.sub = 'M'; z.A = LC(a); z.K = k; PC->s.push_back(z);
        return LV(PBASE + (int)PC->s.size() - 1);
    }
    // count the 1s of an alternation (starting with cell `expect`) that is followed only by zeros
    bool altOnes(vector<pair<string, Lin>> &lp, size_t from, char expect, Lin &ones) {
        auto restZero = [&](size_t k0) { for (size_t k = k0; k < lp.size(); ++k) if (!allZero(lp[k].first)) return false; return true; };
        for (size_t i = from; i < lp.size(); ++i) {
            const string w = lp[i].first; const Lin n = lp[i].second;
            if (w.empty()) continue;
            if (allZero(w)) return restZero(i + 1);
            if (alternating(w) && w[0] == expect && w.size() % 2 == 0) { ones = ladd(ones, lscale(n, (i128)(w.size() / 2))); continue; }
            if (!n.isExact() || n.c > 32) return false;
            for (i128 t = 0; t < n.c; ++t)
                for (size_t k = 0; k < w.size(); ++k) {
                    if (w[k] == expect) { if (expect == '1') ones = laddc(ones, 1); expect = expect == '1' ? '0' : '1'; continue; }
                    if (expect == '0') return false;          // a 1 where the alternation needs a 0
                    // a 0 where a 1 was expected: everything from here on must be blank
                    for (size_t kk = k; kk < w.size(); ++kk) if (w[kk] != '0') return false;
                    if (t + 1 < n.c) return false;
                    return restZero(i + 1);
                }
        }
        return true;
    }
    // Ca j b (blk a z) = 0^inf (10)^j 1^b [A on 0] 1^(a+1) 0 z  -->  Ca (j+1) (iter a (W j) b) z    (BLK_iter_aux, CH_CA)
    ll blks = 0;
    bool tryBlk() {
        auto &L = c.st[0], &R = c.st[1];
        if (R.empty()) { touchBottom(1); return false; }
        touch(1, R.back()); if (R.back().w[0] != '0') return false;
        Lin ones = LC(0); bool done = false;
        for (int i = (int)R.size() - 1; i >= 0 && !done; --i) {
            const Run &t = R[i]; touch(1, t);
            vector<pair<string, Lin>> ps;
            if (i == (int)R.size() - 1) { if (t.w.size() > 1) ps.push_back({t.w.substr(1), LC(1)}); if (!isOne(t.n)) ps.push_back({t.w, laddc(t.n, -1)}); }
            else ps.push_back({t.w, t.n});
            for (auto &p : ps) {
                if (allOne(p.first)) { ones = ladd(ones, lscale(p.second, (i128)p.first.size())); continue; }
                size_t k = 0; while (p.first[k] == '1') ++k;
                ones = laddc(ones, (i128)k); done = true; break;
            }
        }
        if (!done) touchBottom(1);
        if (ones.isExact() && ones.c < 1) return false;
        bool multi = false; Lin kcnt;
        if (ones.isExact() && ones.c <= 64) {   // the head copy starts a run (0 1^(a+1))^k followed by a 0: k BLKs at once
            string w0 = "0" + string((size_t)ones.c, '1');
            if (R.size() >= 2 && R.back().n.isExact() && R.back().n.c == 1 && R.back().w != w0) {
                // rephase u v^n = w0^n u when u v == w0 u (representation change)
                const string u = R.back().w, v = R[R.size() - 2].w;
                touch(1, R[R.size() - 2]);
                if (u + v == w0 + u) { Lin n = R[R.size() - 2].n; R.pop_back(); R.pop_back(); pushRaw(1, Run{u, LC(1)}); pushRaw(1, Run{w0, n}); }
            }
            const Run &t = R.back();
            if (t.w == w0 && !isOne(t.n) && (R.size() == 1 || R[R.size() - 2].w[0] == '0')) {
                multi = true; kcnt = t.n;
                if (R.size() > 1) touch(1, R[R.size() - 2]); else touchBottom(1);
            }
        }
        touchBottom(0);
        vector<pair<string, Lin>> lp; for (int k = (int)L.size() - 1; k >= 0; --k) lp.push_back({L[k].w, L[k].n});
        Lin b = LC(0), j = LC(0); size_t pi = 0;
        while (pi < lp.size() && allOne(lp[pi].first)) { b = ladd(b, lscale(lp[pi].second, (i128)lp[pi].first.size())); ++pi; }
        if (pi < lp.size() && lp[pi].first[0] == '1') {
            if (!isOne(lp[pi].second)) return false;
            string w = lp[pi].first; size_t k = 0; while (k < w.size() && w[k] == '1') ++k;
            b = laddc(b, (i128)k); lp[pi].first = w.substr(k);
        }
        if (!altOnes(lp, pi, '0', j)) return false;
        Lin a = laddc(ones, -1);
        Lin V;
        if (multi) {
            V = computeMB(j, a.c, kcnt, b);
            R.pop_back();
        } else {
            V = computeIter(j, a, b);
            popCell(1);
            while (!R.empty()) {
                Run &t = R.back(); touch(1, t);
                if (allOne(t.w)) { R.pop_back(); continue; }
                string w = t.w; size_t k = 0; while (w[k] == '1') ++k;
                popCopy(1); pushRaw(1, Run{w.substr(k), LC(1)});
                break;
            }
        }
        L.clear();
        pushRaw(0, Run{"01", multi ? ladd(j, kcnt) : laddc(j, 1)});
        if (!(V.isExact() && V.c == 0)) pushRaw(0, Run{"1", V});
        c.q = 0; c.f = 1; stepsKnown = false; ++blks;
        if (!proof && multi) { jlog.push_back("M" + linstr(j) + "," + linstr(a) + "," + linstr(kcnt) + "," + linstr(b) + (V.isExact() ? "" : "*")); if (jlog.size() > 8) jlog.erase(jlog.begin()); }
        else if (!proof) { jlog.push_back("B" + linstr(j) + "," + linstr(a) + "," + linstr(b) + (V.isExact() ? "" : "*")); if (jlog.size() > 8) jlog.erase(jlog.begin()); }
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
        if (chOK && c.q == 7 && tryCh()) return S_OK;
        if (chOK && c.q == 0 && c.f == 1 && tryBlk()) return S_OK;
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
        i128 w = z.sub == 'I' ? Iexact(LBe(z.J), min<i128>(LBe(z.A), 64), LBe(z.B), SYMCAP)
               : z.sub == 'M' ? Iexact(LBe(z.J), z.A.c, LBe(z.B), SYMCAP) : Wexact(LBe(z.J), LBe(z.B), SYMCAP);
        if (w < 0) w = SYMCAP;
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
        const PSym &z = PC->s[v]; int jj;
        if (z.J.isExact()) jj = (int)min<i128>(z.J.c, JMAX);
        else { requireLB(z.J, JINF); jj = JINF; }
        if (jj < 2) UD("Z: j<2");
        VC bc; VC r;
        if (z.sub == 'M') {   // y_(t+1) = class of iter a (W JINF) y_t, j >= JINF throughout
            if (jj != JINF && !(z.J.isExact() && z.J.c >= JINF)) UD("Z-M: j");
            i128 a = z.A.c;
            if (z.B.isExact()) bc = VC{false, z.B.c, 0};
            else { requireLB(z.B, bthresh(JINF)); bc = VC{true, 0, resAbs(z.B, bmodulus(JINF))}; }
            vector<VC> seq; map<ll, int> seen; int mu = -1, lam = -1; VC y = IclassV(JINF, a, bc);
            for (int t = 0; t < 100000; ++t) {
                if (y.huge) { auto it = seen.find(y.r); if (it != seen.end()) { mu = it->second; lam = t - it->second; break; } seen[y.r] = t; }
                seq.push_back(y); y = IclassV(JINF, a, y);
            }
            if (lam < 0 || MG % lam != 0) UD("Z-M: orbit");
            if (z.K.isExact()) { i128 t = z.K.c - 1; r = t < (i128)seq.size() ? seq[(size_t)t] : seq[(size_t)(mu + pmod(t - mu, lam))]; }
            else { requireLB(z.K, (i128)seq.size() + 1); r = seq[(size_t)(mu + pmod((i128)resAbs(z.K, lam) - 1 - mu, lam))]; }
            if (!r.huge) UD("Z: small");
            return r.r % m;
        }
        if (z.sub == 'I') {
            if (z.B.isExact()) bc = VC{false, z.B.c, 0};
            else { if (jj >= 2) requireLB(z.B, bthresh(jj)); bc = VC{true, 0, resAbs(z.B, jj == 1 ? MG : bmodulus(jj))}; }
            Orbit o = orbitV(jj, bc);
            if (z.A.isExact()) r = orbitAt(o, z.A.c);
            else { requireLB(z.A, (i128)o.seq.size() + 1); if (MG % o.lam != 0) UD("Z: orbit period"); r = orbitAtRes(o, resAbs(z.A, o.lam)); }
            if (!r.huge) UD("Z: small");
            return r.r % m;
        }
        if (z.B.isExact()) bc = VC{false, z.B.c, 0};
        else { requireLB(z.B, bthresh(jj)); bc = VC{true, 0, resAbs(z.B, bmodulus(jj))}; }
        r = WV(jj, bc); if (!r.huge) UD("Z: small");
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
static ll PROOFS = 0, PROOFOK = 0;
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
            if (o.st == 2) { M.cyc = o.kind + (mult > 1 ? "x" + to_string(mult) : ""); ++PROOFOK; return 2; }
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
static void runOne(const string &mach, int start, const vector<string> &tok) {
    GS.clear(); MINI.clear(); wSymCount = 0;
    if (!parseMachine(mach, TT, NS)) { printf("R %s %c BAD\n", mach.c_str(), 'A' + start); return; }
    RuleSet RS; Sim M; M.rules = &RS; M.chOK = !OPT.noch && coreIntact(); M.trace = OPT.trace;
    if (!initTape(M, start, tok)) { printf("R %s %c BADTAPE\n", mach.c_str(), 'A' + start); return; }
    unordered_map<ull, array<ll, 3>> past;   // last, delta, fails
    string verdict = "BUDGET", detail = "-";
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
    string sig = "?", sd;
    try { Lin s = M.sigma(); sig = linstr(s); if (verdict == "HALT") sd = symDescs(s); } catch (Undec &) {}
    string jl; for (auto &x : M.jlog) jl += " " + x;
    printf("R %s %c %s %s macro=%lld steps=%s sigma=%s jumps=%lld maxj=%s rules=%zu apps=%lld syms=%zu |%s |%s\n", mach.c_str(), 'A' + start,
           verdict.c_str(), detail.c_str(), M.macro, M.stepsKnown ? s128(M.steps.c).c_str() : "?", sig.c_str(), M.jumps, linstr(M.maxJ).c_str(),
           RS.R.size(), M.ruleApps, GS.size(), jl.c_str(), sd.c_str());
    if (OPT.tape) printf("%s\n", verdict == "HALT" ? tapeDump(M).c_str() : "TAPE notshown");
    if (M.trace) fprintf(stderr, "END %s\n", M.show().c_str());
    fflush(stdout);
}
int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: symsim run|wtab [opts] < input\n"); return 1; }
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
        else { fprintf(stderr, "bad option %s\n", a.c_str()); return 1; }
    }
    buildW();
    if (mode == "wtab") {
        printf("MG=%lld LAM2=%lld A3=%d JINF=%d\n", MG, LAM2, A3, JINF);
        for (int j = 3; j <= JINF + 1; ++j) {
            const WTab &T = WT[j]; printf("j=%d h=%d pre=", j, T.h); for (auto v : T.pre) printf("%s,", s128(v).c_str());
            printf(" mu=%d lam=%d res=", T.mu, T.lam); for (auto v : T.res) printf("%lld,", v); printf("\n");
        }
        // residues of W(j,b) for exact small arguments
        string line;
        while (getline(cin, line)) {
            if (line[0] == 'I') {   // I j a b : residue of iter a (W j) b via the orbit machinery (Iglobal with EXMAX huge)
                istringstream is(line.substr(1)); string js, as, bs; is >> js >> as >> bs;
                Lin v; try { v = Iglobal(LC(p128(js.c_str())), LC(p128(as.c_str())), LC(p128(bs.c_str()))); } catch (Undec &u) { printf("I %s %s %s UNDEC %s\n", js.c_str(), as.c_str(), bs.c_str(), u.why.c_str()); continue; }
                if (v.isExact()) printf("I %s %s %s exact %s %lld\n", js.c_str(), as.c_str(), bs.c_str(), s128(v.c).c_str(), (ll)pmod(v.c, MG));
                else printf("I %s %s %s huge %lld\n", js.c_str(), as.c_str(), bs.c_str(), GS[v.id[0]].res);
                continue;
            }
            istringstream is(line); string js, bs; if (!(is >> js >> bs)) continue;
            i128 j = p128(js.c_str()), b = p128(bs.c_str());
            i128 w = Wexact(j, b, EXMAX);
            VC r = WV((int)min<i128>(j, JMAX), VC{false, b, 0});
            printf("W %s %s exact=%s class=%s %lld\n", js.c_str(), bs.c_str(), w >= 0 ? s128(w).c_str() : "-", r.huge ? "huge" : "exact", r.huge ? r.r : (ll)pmod(r.v, MG));
        }
        return 0;
    }
    string line;
    while (getline(cin, line)) {
        if (!line.empty() && line.back() == '\r') line.pop_back();
        istringstream is(line); string mach, st; if (!(is >> mach >> st)) continue;
        vector<string> tok; string t; while (is >> t) tok.push_back(t);
        runOne(mach, st[0] - 'A', tok);
    }
    return 0;
}
