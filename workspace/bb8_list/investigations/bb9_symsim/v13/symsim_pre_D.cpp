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
// global allocation cap (--memcap MB, default 3000): an allocation beyond it throws bad_alloc, which runOne reports as UNDECIDED
static size_t MEMUSED = 0, MEMCAP = (size_t)3000 << 20;
void *operator new(size_t n) {
    if (MEMUSED + n > MEMCAP) throw std::bad_alloc();
    void *p = malloc(n + 16); if (!p) throw std::bad_alloc();
    *(size_t *)p = n; MEMUSED += n; return (char *)p + 16;
}
void operator delete(void *p) noexcept { if (!p) return; char *q = (char *)p - 16; MEMUSED -= *(size_t *)q; free(q); }
void operator delete(void *p, size_t) noexcept { operator delete(p); }
void *operator new[](size_t n) { return operator new(n); }
void operator delete[](void *p) noexcept { operator delete(p); }
void operator delete[](void *p, size_t) noexcept { operator delete(p); }
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
static Lin lcomb0(const Lin &x, i128 kx, const Lin &y, i128 ky) {
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
static Lin lcomb(const Lin &x, i128 kx, const Lin &y, i128 ky);
static Lin lscale(const Lin &x, i128 num, i128 den = 1);
static Lin ladd(const Lin &x, const Lin &y) { return lcomb(x, 1, y, 1); }
static Lin lsub(const Lin &x, const Lin &y) { return lcomb(x, 1, y, -1); }
static Lin laddc(const Lin &x, i128 v) { if (x.n == 0) return LC(A_(x.c, v)); Lin r = x; r.c = A_(r.c, M_(v, r.D)); lnorm(r); return r; }
static Lin lscale0(const Lin &x, i128 num, i128 den = 1) {
    if (x.n == 0 && den == 1) return LC(M_(x.c, num));
    Lin r = x; r.c = M_(r.c, num); for (int k = 0; k < r.n; ++k) r.a[k] = M_(r.a[k], num); r.D = M_(r.D, den);
    if (num == 0) { r = LC(0); return r; }
    lnorm(r); return r;
}
static Lin overflowSym(const Lin &x, i128 kx, const Lin &y, i128 ky);
static Lin lcomb(const Lin &x, i128 kx, const Lin &y, i128 ky) {
    try { return lcomb0(x, kx, y, ky); }
    catch (Undec &u) { if (u.why != "overflow") throw; return overflowSym(x, kx, y, ky); }
}
static Lin lscale(const Lin &x, i128 num, i128 den) {
    try { return lscale0(x, num, den); }
    catch (Undec &u) { if (u.why != "overflow" || den != 1) throw; return overflowSym(x, num, LC(0), 0); }
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
// a global form whose coefficients overflow 128 bits: x*kx + y*ky as a fresh symbol (only lower bound and residue kept)
static Lin overflowSym(const Lin &x, i128 kx, const Lin &y, i128 ky) {
    if (hasProof(x) || hasProof(y) || x.D != 1 || y.D != 1 || kx < 0 || ky < 0) UD("overflow");
    for (int k = 0; k < x.n; ++k) if (x.a[k] < 0) UD("overflow");
    for (int k = 0; k < y.n; ++k) if (y.a[k] < 0) UD("overflow");
    if (x.c < 0 || y.c < 0) UD("overflow");
    auto satmul = [](i128 a, i128 b) { i128 r; if (__builtin_mul_overflow(a, b, &r) || r > SYMCAP) return SYMCAP; return r; };
    auto satadd = [](i128 a, i128 b) { i128 r; if (__builtin_add_overflow(a, b, &r) || r > SYMCAP) return SYMCAP; return r; };
    i128 lb = 0;
    auto addlb = [&](const Lin &z, i128 kz) {
        if (kz == 0) return;
        i128 s0 = z.c; for (int k = 0; k < z.n; ++k) s0 = satadd(s0, satmul(z.a[k], GS[z.id[k]].lb));
        lb = satadd(lb, satmul(s0, kz));
    };
    addlb(x, kx); addlb(y, ky);
    ll best = 1, bres = 0;
    for (ll m = MG; m >= 2; --m) {
        if (MG % m) continue;
        bool ok = true; i128 t = 0;
        auto addres = [&](const Lin &z, i128 kz) {
            if (kz == 0) return;
            i128 s0 = pmod(z.c, m);
            for (int k = 0; k < z.n && ok; ++k) { const GSym &g = GS[z.id[k]]; if (g.mod % m != 0) { ok = false; break; } s0 = pmod(s0 + pmod(z.a[k], m) * pmod(g.res, m), m); }
            t = pmod(t + s0 * pmod(kz, m), m);
        };
        addres(x, kx); addres(y, ky);
        if (ok) { best = m; bres = (ll)t; break; }
    }
    ++consolidations;
    return LV(newG(max(lb, (i128)1), bres, "O(" + linstr(x) + "*" + s128(kx) + "+" + linstr(y) + "*" + s128(ky) + ")", best));
}
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

// ------------------------------------------------------------------ U residue law (BB(7)-champion digit-list engine)
// U_0(x) = 2^(2x+3) - 2,  U_(j+1)(x) = iter (2x+2) (U_j) 0      (BB9_record_1RB0RA.v: U, U_0, U_S, U_closed)
// Same class machinery as W: exact values below VT, otherwise a residue mod MG.
static vector<WTab> UT;   // UT[j], j >= 1
static int JUINF = -1, JUMAX = 40;
static ll ORD2; static int A2;   // 2^e mod MG: 0 mod 2^A2 part for e >= A2, period ORD2 on the odd part
static VC UV(int j, const VC &x);
static const WTab &utab(int j) { if (j >= JUINF && JUINF > 0) return UT[JUINF]; return UT[j]; }
static ll pow2res(i128 e) { return powmod(2, e, MG); }                 // exact exponent
static ll pow2resHuge(ll emod) { return powmod(2, A2 + pmod((i128)emod - A2, ORD2), MG); }   // e >= A2, e == emod mod ORD2
static VC UV(int j, const VC &x) {
    if (j == 0) {
        if (!x.huge) { i128 e = 2 * x.v + 3; if (e <= 61) return vexact(((i128)1 << e) - 2); return VC{true, 0, (ll)pmod((i128)pow2res(e) - 2, MG)}; }
        return VC{true, 0, (ll)pmod((i128)pow2resHuge((ll)pmod(2 * (i128)x.r + 3, ORD2)) - 2, MG)};
    }
    const WTab &T = utab(j);
    if (!x.huge) {
        i128 t = 2 * x.v + 2;
        if (t < T.h) return VC{false, T.pre[(size_t)t], 0};
        if (t < T.h + T.mu) return VC{true, 0, T.res[(size_t)(t - T.h)]};
        return VC{true, 0, T.res[(size_t)(T.mu + pmod(t - T.h - T.mu, T.lam))]};
    }
    return VC{true, 0, T.res[(size_t)(T.mu + pmod(2 * (i128)x.r + 2 - T.h - T.mu, T.lam))]};
}
static void buildU() {
    A2 = 0; ll mm = MG; while (mm % 2 == 0) { mm /= 2; ++A2; }
    ORD2 = 1; { ll x = 2 % mm; while (x != 1 % mm) { x = x * 2 % mm; ++ORD2; } if (mm == 1) ORD2 = 1; }
    if (MG % ORD2 != 0) { fprintf(stderr, "MG=%lld: ord of 2 (%lld) does not divide MG\n", MG, ORD2); exit(2); }
    UT.assign(JUMAX + 2, WTab{});
    JUINF = -1;
    for (int j = 1; j <= JUMAX + 1; ++j) {
        WTab T; VC v = vexact(0); T.h = -1; map<ll, int> seen;
        for (int t = 0;; ++t) {
            if (!v.huge) T.pre.push_back(v.v);
            else {
                if (T.h < 0) T.h = t;
                auto it = seen.find(v.r);
                if (it != seen.end()) { T.mu = it->second - T.h; T.lam = t - it->second; break; }
                seen[v.r] = t; T.res.push_back(v.r);
            }
            v = UV(j - 1, v);
            if (t > 100000) { fprintf(stderr, "U table j=%d does not cycle\n", j); exit(2); }
        }
        if (T.h < 0) { fprintf(stderr, "U table j=%d never huge\n", j); exit(2); }
        if (MG % T.lam != 0) { fprintf(stderr, "U table j=%d: period %d does not divide MG\n", j, T.lam); exit(2); }
        UT[j] = T;
        if (j >= 2 && JUINF < 0 && wtabEq(UT[j], UT[j - 1])) JUINF = j - 1;
    }
    if (JUINF < 0) { fprintf(stderr, "U tables do not stabilise\n"); exit(2); }
}
// exact U with cap (-1 if > cap):  2 U_j(x) + 4 = 2^^(j+1) (2x+4)
static i128 Uexact(i128 j, i128 x, i128 cap) {
    if (x < 0 || j < 0) return -1;
    if (j == 0) { i128 e = 2 * x + 3; if (e > 120) return -1; i128 v = ((i128)1 << e) - 2; return v <= cap ? v : -1; }
    // j >= 1: U_j(0) = U_(j-1)^2(0); U_1(0) = 32766, U_1(x>=1) and U_(j>=2)(0) = U_1(U_1(0))... are huge
    if (j == 1 && x == 0) return 32766 <= cap ? 32766 : -1;
    return -1;
}
static int uthresh(int j) { if (j == 0) return 64; const WTab &T = utab(j); return T.h + T.mu + 1; }   // huge-input threshold
static ll umodulus(int j) { if (j == 0) return ORD2; return utab(j).lam; }
// orbit of classes under U_j starting from b, seq[t] = x_(t+1)
static Orbit orbitU(int jj, const VC &b) {
    Orbit o; VC x = UV(jj, b); map<ll, int> seen;
    for (int t = 0; t < 100000; ++t) {
        if (x.huge) { auto it = seen.find(x.r); if (it != seen.end()) { o.mu = it->second; o.lam = t - it->second; return o; } seen[x.r] = t; }
        o.seq.push_back(x); x = UV(jj, x);
    }
    UD("U orbit does not cycle");
}
static i128 IUexact(i128 j, i128 v, i128 b, i128 cap) {   // exact iter v (U j) b, -1 if > cap
    i128 x = b; for (i128 t = 0; t < v; ++t) { x = Uexact(j, x, cap); if (x < 0) return -1; } return x;
}
// C(j,v,b) = iter v (U j) b  for global forms (CDP: clearing digit v at depth j from accumulator b)
static Lin Cglobal(const Lin &j, const Lin &v, const Lin &b) {
    if (v.isExact() && v.c == 0) return b;
    int jj;
    if (j.isExact()) jj = (int)min<i128>(j.c, (i128)JUMAX);
    else { if (sgnG(laddc(j, -JUINF)) < 0) UD("C: symbolic j below JUINF"); jj = JUINF; }
    if (j.isExact() && v.isExact() && b.isExact()) { i128 e = IUexact(j.c, v.c, b.c, EXMAX); if (e >= 0) return LC(e); }
    VC bc;
    if (b.isExact()) bc = VC{false, b.c, 0};
    else { if (sgnG(laddc(b, -uthresh(jj))) < 0) UD("C: b below threshold"); bc = VC{true, 0, resG(b, umodulus(jj))}; }
    Orbit o = orbitU(jj, bc); VC r;
    if (v.isExact()) r = orbitAt(o, v.c);
    else {
        if (sgnG(laddc(v, -(i128)o.seq.size() - 1)) < 0) UD("C: v below orbit length");
        if (MG % o.lam != 0) UD("C: orbit period");
        r = orbitAtRes(o, resG(v, o.lam));
    }
    if (!r.huge) { if (r.v <= EXMAX) return LC(r.v); r = VC{true, 0, (ll)pmod(r.v, MG)}; }
    i128 lb = -1;
    try { lb = IUexact(lbG(j), min<i128>(lbG(v), 4), lbG(b), SYMCAP); } catch (Undec &) {}
    if (lb < 0) lb = SYMCAP; lb = max(lb, EXMAX + 1);
    ++wSymCount;
    return LV(newG(lb, r.r, "C(" + linstr(j) + "," + linstr(v) + "," + linstr(b) + ")"));
}
// P(k,r) = 2^k (r+4) - 4  (Kt_R1 iterated k times)
static Lin Pglobal(const Lin &k, const Lin &r) {
    if (k.isExact()) {
        if (k.c == 0) return r;
        if (r.isExact() && k.c < 100) {
            i128 v = r.c + 4; bool ok = true;
            for (i128 t = 0; t < k.c; ++t) { if (v > EXMAX / 2) { ok = false; break; } v *= 2; }
            if (ok) return LC(v - 4);
        }
        if (k.c <= 64 && !r.isExact()) return laddc(lscale(laddc(r, 4), (i128)1 << k.c), -4);
        ll p2 = pow2res(k.c);
        ll rr = r.isExact() ? (ll)pmod(r.c, MG) : resG(r, MG);
        i128 lb = lbG(r) + 4; for (i128 t = 0; t < k.c && lb < SYMCAP; ++t) lb *= 2; lb = min(lb - 4, SYMCAP);
        ++wSymCount;
        return LV(newG(max(lb, (i128)1), (ll)pmod((i128)p2 * (rr + 4) - 4, MG), "P(" + linstr(k) + "," + linstr(r) + ")"));
    }
    if (sgnG(laddc(k, -120)) < 0) UD("P: symbolic k below 120");   // then 2^k (r+4) - 4 >= 2^120 > SYMCAP
    ll p2 = pow2resHuge(resG(k, ORD2));
    ll rr = r.isExact() ? (ll)pmod(r.c, MG) : resG(r, MG);
    ++wSymCount;
    return LV(newG(SYMCAP, (ll)pmod((i128)p2 * (rr + 4) - 4, MG), "P(" + linstr(k) + "," + linstr(r) + ")"));
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

// x -> a x + c applied k times (a >= 2): a^k x + c (a^k - 1)/(a - 1), for global forms
static Lin affPow(const Lin &x, i128 a, i128 c, const Lin &k) {
    if (k.isExact()) {
        if (k.c == 0) return x;
        if (x.isExact() && k.c <= 200) {
            i128 v = x.c; bool ok = true;
            for (i128 t = 0; t < k.c && ok; ++t) { i128 w; if (__builtin_mul_overflow(v, a, &w) || __builtin_add_overflow(w, c, &v) || v > EXMAX) ok = false; }
            if (ok) return LC(v);
        }
        if (k.c <= 64) {
            i128 ak = 1; bool ok = true; for (i128 t = 0; t < k.c && ok; ++t) if (__builtin_mul_overflow(ak, a, &ak)) ok = false;
            if (ok) return laddc(lscale(x, ak), c * ((ak - 1) / (a - 1)));
        }
    }
    ll r0 = x.isExact() ? (ll)pmod(x.c, MG) : resG(x, MG);
    // v13: orbits of r -> a r + c (mod MG) are cached by (a, c, r0, MG)
    struct AffOrb { vector<ll> seq; int mu, lam; };
    static map<tuple<long long, long long, ll, ll>, AffOrb> AFFCACHE;
    auto key = make_tuple((long long)pmod(a, MG), (long long)pmod(c, MG), r0, MG);
    auto cit = AFFCACHE.find(key);
    if (cit == AFFCACHE.end()) {
        AffOrb O; map<ll, int> seen; O.mu = -1; O.lam = -1; ll r = r0;
        for (int t = 0; t < 200000; ++t) { auto it = seen.find(r); if (it != seen.end()) { O.mu = it->second; O.lam = t - it->second; break; } seen[r] = t; O.seq.push_back(r); r = (ll)pmod((i128)a * r + c, MG); }
        if (AFFCACHE.size() > 2000) AFFCACHE.clear();
        cit = AFFCACHE.emplace(key, std::move(O)).first;
    }
    const vector<ll> &seq = cit->second.seq; int mu = cit->second.mu, lam = cit->second.lam;
    if (lam < 0) UD("affPow orbit");
    ll res;
    if (k.isExact()) res = k.c < (i128)seq.size() ? seq[(size_t)k.c] : seq[(size_t)(mu + pmod(k.c - mu, lam))];
    else {
        if (sgnG(laddc(k, -(i128)seq.size())) < 0) UD("affPow: k below orbit length");
        if (MG % lam != 0) UD("affPow: orbit period");
        res = seq[(size_t)(mu + pmod((i128)resG(k, lam) - mu, lam))];
    }
    i128 lb = x.isExact() ? x.c : lbG(x); i128 kl = min<i128>(k.isExact() ? k.c : lbG(k), 128);
    for (i128 t = 0; t < kl && lb < SYMCAP; ++t) { i128 w; if (__builtin_mul_overflow(lb, a, &w) || __builtin_add_overflow(w, c, &lb)) lb = SYMCAP; }
    lb = min(lb, SYMCAP);
    ++wSymCount;
    return LV(newG(max(lb, (i128)1), res, "A(" + s128(a) + "," + s128(c) + "," + linstr(k) + "," + linstr(x) + ")"));
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

struct KTmpl { bool on = false; int Q = 1; string u = "10", S = "111001"; int beta = 2; };
static KTmpl KT;   // template of the digit-list engine of the current machine (kgrade mode)
static int KGRULED = -1;
// --kgalt: alternative right-end gadgets S' (each grid-checked once per machine, cache KGALT: key "S|beta" -> 0/1)
static bool KGALTON = false, KGALTBUSY = false; static std::map<std::string, int> KGALT; static long long KGALTUSE = 0;
static bool kgGrid(long long &ncase, std::string &fail);
// ------------------------------------------------------------------ configurations and rules
struct Run { string w; Lin n; int tag = -1; };
struct Cfg { int q = 0, f = 1; vector<Run> st[2]; };     // st[0] left, st[1] right; back() = nearest the head
static const int PMAX = 8, FOLDREG = 72, DEEPP = 64;
static int SIGWIN = 16;
static bool KTDEBUG = false, KTTRACE = false;
static ll DEEPEVERY = 512, DEEPRUNS = 24;
static bool NOAFF = false, KTFORCE = false, AFFC = true, PAFF = true, ITERON = true;   // AFFC (v13): invariant congruences allowed in affine rules (--noaffc off)   // KTFORCE: testing only (assumes R1-R3 without verification)   // runs per side in the proof-trigger signature (0 = whole tape)
enum { S_OK = 0, S_HALT, S_CYCLE };
struct Rule {
    int q, f; vector<Run> g[2]; vector<int> rv[2]; bool bottom[2];
    int nv; vector<i128> delta; vector<Cons> cons; bool stepsKnown; Lin steps; ll uses = 0;
    bool affine = false; vector<i128> amul; vector<char> cskip;   // affine rule: x -> amul*x + delta; cskip: monotone constraints
    // v13 ITER rule: counters x -> x + delta (delta <= 0 limits k), self maps x_v -> F_v(x_v) built from proof symbols zs
    bool iter = false; vector<char> isF; vector<Lin> iterF; vector<PSym> zs; vector<i128> flb; vector<Cons> zcons; int fvar = -1;
};
// ---- v13: evaluation of a proof-symbol formula at a global value of its single variable (ITER rules)
struct FEval {
    const vector<PSym> *zs; int var; Lin xval; map<int, Lin> memo; const vector<Lin> *consts = nullptr;
    Lin lin(const Lin &e) {
        Lin r = LC(e.c);
        for (int k = 0; k < e.n; ++k) {
            Lin t;
            if (e.id[k] < PBASE) t = LV(e.id[k]);
            else {
                int idx = e.id[k] - PBASE;
                if ((*zs)[idx].kind == 'P') {
                    if (idx == var) t = xval;
                    else if (consts && idx < (int)consts->size() && (*consts)[idx].D != 0) t = (*consts)[idx];
                    else UD("iter: foreign variable");
                }
                else t = node(idx);
            }
            r = lcomb(r, 1, t, e.a[k]);
        }
        return lscale(r, 1, e.D);
    }
    Lin node(int idx) {
        auto it = memo.find(idx); if (it != memo.end()) return it->second;
        const PSym &z = (*zs)[idx]; Lin v;
        switch (z.sub) {
            case 'A': v = affPow(lin(z.B), z.A.c, z.J.c, lin(z.K)); break;
            case 'P': v = Pglobal(lin(z.A), lin(z.B)); break;
            case 'C': v = Cglobal(lin(z.J), lin(z.A), lin(z.B)); break;
            case 'I': v = Iglobal(lin(z.J), lin(z.A), lin(z.B)); break;
            case 'M': v = MBglobal(lin(z.J), z.A.c, lin(z.K), lin(z.B)); break;
            default: v = Wglobal(lin(z.J), lin(z.B)); break;
        }
        memo[idx] = v; return v;
    }
};
static Lin iterEval(const vector<PSym> &zs, const Lin &F, int var, const Lin &x) { FEval E; E.zs = &zs; E.var = var; E.xval = x; return E.lin(F); }
// F_v iterated k times from x (global).  Exact small k: literal composition.  Otherwise: lower-bound chain and residue
// orbit of the iterates (later iterates are abstracted by fresh symbols carrying their lower bound and residue, which is
// sound because F is monotone and its value's residue depends only on the argument's residue and lower bound).
static ll ITERSYMS = 0;
// the constraints of the rule at an iterate's input y (t >= 1): constant variables hold their constants
static bool iterConsOK(const Rule &R, const Lin &y) {
    vector<Lin> cv(R.nv); for (auto &l : cv) l.D = 0;
    for (int u = 0; u < R.nv; ++u) if (R.isF[u] && u != R.fvar) cv[u] = R.iterF[u];
    for (auto &cn : R.zcons) {
        FEval E; E.zs = &R.zs; E.var = R.fvar; E.xval = y; E.consts = &cv;
        Lin N = E.lin(cn.N);
        if (cn.k == 'G') { if (sgnG(N) < 0) return false; }
        else if (cn.k == 'E') { if (!(N.isExact() && N.c == 0)) return false; }
        else if ((i128)resG(N, (ll)cn.q) != cn.r) return false;
    }
    return true;
}
static Lin iterPow(const Rule &R, int v, const Lin &x0, const Lin &k) {
    if (v != R.fvar) return R.iterF[v];   // constant reset (k >= 1)
    const Lin &F = R.iterF[v];
    auto step = [&](const Lin &y) { vector<Lin> cv(R.nv); for (auto &l : cv) l.D = 0; FEval E; E.zs = &R.zs; E.var = v; E.xval = y; E.consts = &cv; return E.lin(F); };
    if (k.isExact() && k.c <= 64) { Lin y = x0; for (i128 t = 0; t < k.c; ++t) { if (t > 0 && !iterConsOK(R, y)) UD("iter: constraint"); y = step(y); } return y; }
    // orbit of (residue, saturated lower bound): iterate t >= 1 is abstracted by a fresh symbol with its lower bound and
    // residue (sound: F is monotone, and every constraint check and residue depends only on these)
    size_t g0 = GS.size();   // the orbit's scratch symbols are dropped afterwards
    Lin y = step(x0);
    vector<ll> rs; vector<i128> lbs; map<ll, int> seen; int mu = -1, lam = -1;
    for (int t = 0; t < 20000; ++t) {
        ll r = resG(y, MG); i128 lb = y.isExact() ? y.c : lbG(y);
        if (lb >= SYMCAP) { auto it = seen.find(r); if (it != seen.end()) { mu = it->second; lam = t - it->second; break; } seen[r] = t; }
        rs.push_back(r); lbs.push_back(lb);
        if (!y.isExact()) { ++ITERSYMS; y = LV(newG(lb, r, "iterfake")); }
        if (!iterConsOK(R, y)) UD("iter: constraint");
        y = step(y);
    }
    GS.resize(g0);
    if (lam < 0) UD("iter: orbit");
    // rs[t] is the residue of F^(t+1)(x0)
    ll rr; i128 lb;
    if (k.isExact()) { i128 t = k.c - 1; size_t i = t < (i128)rs.size() ? (size_t)t : (size_t)(mu + pmod(t - mu, lam)); rr = rs[i]; lb = lbs[min(i, lbs.size() - 1)]; }
    else {
        if (sgnG(laddc(k, -(i128)rs.size() - 1)) < 0) UD("iter: k below orbit length");
        if (MG % lam != 0) UD("iter: orbit period");
        rr = rs[(size_t)(mu + pmod((i128)resG(k, lam) - 1 - mu, lam))]; lb = SYMCAP;
    }
    ++wSymCount;
    return LV(newG(max(lb, (i128)1), rr, "T(" + linstr(k) + "," + linstr(x0) + ")"));
}
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
    ll macro = 0, jumps = 0, ruleApps = 0, affApps = 0, iterApps = 0;
    int maxTag[2] = {-1, -1}; bool bot[2] = {false, false};
    RuleSet *rules = nullptr;
    string cyc, lastUndec;
    vector<string> jlog;   // last jumps
    Lin maxJ = LC(0);

    bool track = false;   // record touches outside proofs too (rule verification)
    void touch(int s, const Run &r) { if ((proof || track) && r.tag > maxTag[s]) maxTag[s] = r.tag; }
    void touchBottom(int s) { if (proof || track) { bot[s] = true; maxTag[s] = INT_MAX; } }
    void addSteps(const Lin &x) { if (!stepsKnown) return; try { steps = ladd(steps, x); } catch (Undec &) { stepsKnown = false; } }
    void pushRaw(int s, Run r) {
        int p = primRoot(r.w); if (p < (int)r.w.size()) { r.n = lscale(r.n, (i128)(r.w.size() / p)); r.w.resize(p); }
        normCount(r.n);
        auto &V = c.st[s];
        if (!V.empty() && V.back().w == r.w) { touch(s, V.back()); V.back().n = ladd(V.back().n, r.n); normCount(V.back().n); return; }   // touched only when merged
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
                for (i128 q = 0; q < r.n.c; ++q) t += r.w;
                ++used; --j;
            }
            if (t.size() < L || t.compare(0, L, u) != 0) return;   // nothing changed below: no touch needed
            string left = t.substr(L);   // nearest-first, left[0] adjacent to the run
            for (int q = idx - used; q < idx; ++q) touch(s, V[q]);
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
                for (ll t = 0; t < cnt; ++t) cells += r.w;
                ++k;
            }
            int bi = (int)V.size() - 1 - k;
            if (k == 0 || cells.size() < 2) return;
            if (bi >= 0) {
                const string u = V[bi].w;
                if (u.size() <= cells.size() && cells.compare(cells.size() - u.size(), u.size(), u) == 0) {
                    touch(s, V[bi]); for (int q = 0; q < k; ++q) touch(s, V[V.size() - 1 - q]);
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
                    for (int q = 0; q < k; ++q) touch(s, V[V.size() - 1 - q]);
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
    // ---------------- BB(7)-champion digit-list engine (record format), valid only when R1-R3 were verified for this machine
    //   Kt ds m r t = 0^inf 11 D(d_n)..D(d_1) D(m) (10)^r 11 (11111100)^t 1001 B> 0^inf,  D(x) = (10)^x 1
    // left stack nearest-first: 1001, (00111111)^t, 11, (01)^r, then tokens "1 (01)^x": the a-token (x = m), the digits.
    struct KPiece { string w; Lin n; int run; bool cell; };
    vector<KPiece> kflat() {
        vector<KPiece> P; auto &L = c.st[0];
        for (int i = (int)L.size() - 1; i >= 0; --i) {
            const Run &r = L[i];
            if (r.n.isExact() && r.n.c * (i128)r.w.size() <= 4096) { for (i128 t = 0; t < r.n.c; ++t) for (char ch : r.w) P.push_back(KPiece{string(1, ch), LC(1), i, true}); }
            else P.push_back(KPiece{r.w, r.n, i, false});
        }
        return P;
    }
    // consume copies of w (nearest-first) starting at piece p; returns the count (cells must form whole copies)
    Lin krep(vector<KPiece> &P, size_t &p, const string &w) {
        Lin n = LC(0);
        while (p < P.size()) {
            if (!P[p].cell) { if (P[p].w == w) { n = ladd(n, P[p].n); ++p; continue; } break; }
            if (p + w.size() > P.size()) break;
            bool ok = true; for (size_t k = 0; k < w.size() && ok; ++k) ok = P[p + k].cell && P[p + k].w[0] == w[k];
            if (!ok) break;
            p += w.size(); n = laddc(n, 1);
        }
        return n;
    }
    bool klit(vector<KPiece> &P, size_t &p, const char *s) {
        size_t L = strlen(s); if (p + L > P.size()) return false;
        for (size_t k = 0; k < L; ++k) if (!P[p + k].cell || P[p + k].w[0] != s[k]) return false;
        p += L; return true;
    }
    int ktOK = 0;      // bit 0: rules verified for t = 0, bit 1: for t >= 1
    ll kjumps = 0;
    // replace the pieces [0, p) of the left stack by NEW (nearest-first run list)
    void kreplace(vector<KPiece> &P, size_t p, const vector<Run> &NEW) {
        auto &L = c.st[0];
        int lastRun = p > 0 ? P[p - 1].run : (int)L.size();
        vector<string> rest;   // unconsumed cells of a partly consumed run, nearest-first
        for (size_t q = p; q < P.size() && P[q].run == lastRun; ++q) { if (!P[q].cell) UD("kt: split symbolic run"); rest.push_back(P[q].w); }
        for (int i = (int)L.size() - 1; i >= lastRun; --i) touch(0, L[i]);
        L.resize(lastRun);
        for (int i = (int)rest.size() - 1; i >= 0; --i) pushRaw(0, Run{rest[i], LC(1)});
        for (int i = (int)NEW.size() - 1; i >= 0; --i) if (!(NEW[i].n.isExact() && NEW[i].n.c == 0)) pushRaw(0, NEW[i]);
    }
    Lin computeC(const Lin &j, const Lin &v, const Lin &b) {
        if (!hasProof(j) && !hasProof(v) && !hasProof(b)) return Cglobal(j, v, b);
        if (v.isExact() && v.c == 0) return b;
        Lin sh = Cglobal(shadowOf(j), shadowOf(v), shadowOf(b));
        PSym z{'Z', sh, j, b}; z.sub = 'C'; z.A = v; PC->s.push_back(z);
        return LV(PBASE + (int)PC->s.size() - 1);
    }
    // v13: k-fold affine map x -> a x + c (a >= 2, c >= 0) with proof arguments: proof symbol Z sub 'A'
    //      (z.A = a, z.J = c, z.K = k, z.B = x), shadow = the global value at the shadows
    Lin computeAff(const Lin &x, i128 a, i128 c, const Lin &k) {
        if (!hasProof(x) && !hasProof(k)) return affPow(x, a, c, k);
        if (k.isExact() && k.c == 0) return x;
        if (k.isExact() && k.c <= 3) { Lin y = x; for (i128 t = 0; t < k.c; ++t) y = laddc(lscale(y, a), c); return y; }
        Lin sh = affPow(shadowOf(x), a, c, shadowOf(k));
        PSym z{'Z', sh, LC(c), x}; z.sub = 'A'; z.A = LC(a); z.K = k; PC->s.push_back(z);
        return LV(PBASE + (int)PC->s.size() - 1);
    }
    Lin computeP(const Lin &k, const Lin &r) {
        if (!hasProof(k) && !hasProof(r)) return Pglobal(k, r);
        if (k.isExact() && k.c <= 64) return laddc(lscale(laddc(r, 4), (i128)1 << k.c), -4);
        Lin sh = Pglobal(shadowOf(k), shadowOf(r));
        PSym z{'Z', sh, LC(0), r}; z.sub = 'P'; z.A = k; PC->s.push_back(z);
        return LV(PBASE + (int)PC->s.size() - 1);
    }
    bool tryKt() {
        if (!c.st[1].empty()) { touchBottom(1); return false; }
        touchBottom(1);
        vector<KPiece> P = kflat(); size_t p = 0;
        if (!klit(P, p, "1001")) return false;
        Lin t = krep(P, p, "00111111");
        bool t0 = t.isExact() && t.c == 0;
        if (!(ktOK & (t0 ? 1 : 2))) return false;
        if (!klit(P, p, "11")) return false;
        Lin r = krep(P, p, "01");
        if (r.isExact() && r.c == 0) return false;
        // tokens "1 (01)^x" follow; a run of the word "101" is a run of tokens with x = 1
        auto token = [&](Lin &x, Lin &zeros) -> bool {   // zeros: count of a "101" run (x = 1 each), else x
            zeros = LC(0);
            if (p < P.size() && !P[p].cell && P[p].w == "101") { zeros = P[p].n; ++p; return true; }
            if (!klit(P, p, "1")) return false;
            x = krep(P, p, "01"); return true;
        };
        Lin m, z0;
        if (!token(m, z0)) return false;
        Lin j = LC(0);
        if (!(z0.isExact() && z0.c == 0)) { m = LC(1); j = laddc(z0, -1); }
        // R1 iterated: Kt ds (3k + m') r t -->* Kt ds m' P(k, r) t
        if (!(m.isExact() && m.c < 3)) {
            ll mr = res(m, 3); Lin k = lscale(laddc(m, -mr), 1, 3);
            if (!k.isExact() && sgn(k) <= 0) return false;
            Lin r2 = computeP(k, r);
            vector<Run> NEW;
            NEW.push_back(Run{"1", LC(1)}); NEW.push_back(Run{"0", LC(1)}); NEW.push_back(Run{"0", LC(1)}); NEW.push_back(Run{"1", LC(1)});
            NEW.push_back(Run{"00111111", t}); NEW.push_back(Run{"1", LC(2)}); NEW.push_back(Run{"01", r2}); NEW.push_back(Run{"1", LC(1)}); NEW.push_back(Run{"01", LC(mr)});
            kreplace(P, p, NEW);
            stepsKnown = false; ++kjumps;
            if (!proof) { jlog.push_back("R1x" + linstr(k)); if (jlog.size() > 8) jlog.erase(jlog.begin()); }
            return true;
        }
        if (!(m.isExact() && m.c == 1)) return false;
        // CDP: Kg (0^j ++ v :: Us) suf 0 B t -->* Kg (0^(j+1) ++ Us) suf 0 (iter v (U j) B) t
        if (res(r, 3) != 2) return false;
        Lin B = lscale(laddc(r, -2), 1, 3);
        Lin d;
        while (true) {
            Lin x, z;
            if (!token(x, z)) return false;
            if (!(z.isExact() && z.c == 0)) { j = ladd(j, z); continue; }
            if (x.isExact() && x.c == 1) { j = laddc(j, 1); continue; }
            d = x; break;
        }
        if (d.isExact() && d.c < 4) return false;
        if (res(d, 3) != 1) return false;
        if (p >= P.size()) return false;
        touch(0, c.st[0][P[p].run]);
        if (P[p].w[0] != '1') return false;   // the next token (or the end "11") starts with 1
        Lin v = lscale(laddc(d, -1), 1, 3);
        Lin B2 = computeC(j, v, B);
        vector<Run> NEW;
        NEW.push_back(Run{"1", LC(1)}); NEW.push_back(Run{"0", LC(1)}); NEW.push_back(Run{"0", LC(1)}); NEW.push_back(Run{"1", LC(1)});
        NEW.push_back(Run{"00111111", t}); NEW.push_back(Run{"1", LC(2)}); NEW.push_back(Run{"01", laddc(lscale(B2, 3), 2)});
        NEW.push_back(Run{"101", laddc(j, 2)});   // the a-token D(1) and j+1 zero digits D(1), nearest-first "1 01"
        kreplace(P, p, NEW);
        stepsKnown = false; ++kjumps;
        if (!proof) { jlog.push_back("C" + linstr(j) + "," + linstr(v) + "," + linstr(B) + (B2.isExact() ? "" : "*")); if (jlog.size() > 8) jlog.erase(jlog.begin()); }
        return true;
    }
    // ---------------- template digit-list engine (dlscan3 template, champion rule maps), active when the machine is RULED
    //   K(ds; a; b) = P [u^(3 d_n+1) s] .. [u^(3 d_1+1) s] u^(3a+1) s u^(3b+beta) S  Q> 0^inf      (s = 1)
    //   R1  K(ds; a+1; b) -> K(ds; a; 2b+2)      R2  K(y+1::ds; 0; b) -> K(y::ds; 2b+2; 0)
    //   R3  K(0^(M+1) ++ y+1::ds; 0; b) -> K(0^M ++ (2b+2)::y::ds; 0; 0)
    // Given R1-R3 (literal grid check per machine), R1ITER: K(ds;a;b) ->* K(ds;0;dbl(a,b)), dbl(a,b) = 2^a (b+2) - 2,
    // and CDP: K(0^j ++ v::Us; 0; B) ->* K(0^(j+1) ++ Us; 0; iter v (U j) B) (BB9_record_1RB0RA.v, abstract part).
    // alternative gadget: rS' = the literal cells before the maximal run of ru-copies nearest the head, plus t = 0..2 copies of ru;
    // beta' = (r - t) mod 3.  Accepted only if the strict literal grid passes for (S', beta').  Sound in the same sense as the template.
    bool tryKgAlt(vector<KPiece> &P, const string &ru) {
        size_t U = ru.size(), q = 0; string lit;
        while (q < P.size() && P[q].cell && lit.size() < 48) lit += P[q++].w[0];
        auto isCopy = [&](size_t at) -> bool { if (at + U > P.size()) return false; for (size_t k = 0; k < U; ++k) if (!P[at + k].cell || P[at + k].w[0] != ru[k]) return false; return true; };
        for (size_t L = 1; L <= 24 && L <= lit.size(); ++L) {
            if (L >= U && lit.compare(L - U, U, ru) == 0) continue;          // S' must not end with a copy of ru
            size_t p2 = L; Lin r = krep(P, p2, ru);
            bool sym = !r.isExact(); if (!sym && r.c < 3) continue;
            if (!sym && !(p2 < P.size())) continue;
            for (int t = 0; t <= 2; ++t) {
                if (!sym && r.c - t < 0) continue;
                string rS2 = lit.substr(0, L); for (int k = 0; k < t; ++k) rS2 += ru;
                int beta2 = (int)(((res(r, 3) - t) % 3 + 3) % 3);
                string S2(rS2.rbegin(), rS2.rend()); if (S2 == KT.S) continue;
                string key = S2 + "|" + to_string(beta2);
                auto it = KGALT.find(key); int ok;
                KTmpl save = KT;
                if (it == KGALT.end()) {
                    KT.S = S2; KT.beta = beta2; long long nc; string fail;
                    KGALTBUSY = true; ok = kgGrid(nc, fail) ? 1 : 0; KGALTBUSY = false; KT = save;
                    KGALT[key] = ok;
                    fprintf(stderr, "KGALT S=%s beta=%d %s %s\n", S2.c_str(), beta2, ok ? "RULED" : "UNRULED", ok ? "" : fail.c_str());
                } else ok = it->second;
                if (!ok) continue;
                KT.S = S2; KT.beta = beta2; KGALTBUSY = true;
                bool done = tryKg();
                KGALTBUSY = false; KT = save;
                if (done) { ++KGALTUSE; if (!proof) { jlog.back() += "@" + S2; } }
                return done;
            }
            return false;   // only the maximal-run split is tried
        }
        return false;
    }
    bool tryKg() {
        if (!c.st[1].empty()) { touchBottom(1); return false; }
        touchBottom(1);
        vector<KPiece> P = kflat(); size_t p = 0;
        const string rS(KT.S.rbegin(), KT.S.rend()), ru(KT.u.rbegin(), KT.u.rend()), z0 = "1" + ru;
        if (!klit(P, p, rS.c_str())) return KGALTON && !KGALTBUSY ? tryKgAlt(P, ru) : false;
        Lin r = krep(P, p, ru);
        auto token = [&](Lin &x, Lin &zeros) -> bool {
            zeros = LC(0);
            if (p < P.size() && !P[p].cell && P[p].w == z0) { zeros = P[p].n; ++p; return true; }
            if (!klit(P, p, "1")) return false;
            x = krep(P, p, ru); return true;
        };
        Lin m, zz;
        if (!token(m, zz)) return false;
        Lin j = LC(0);
        if (!(zz.isExact() && zz.c == 0)) { m = LC(1); j = laddc(zz, -1); }
        if (hasProof(m) || hasProof(r)) return false;   // global arguments only
        if (res(m, 3) != 1) return false;
        if ((ll)res(r, 3) != KT.beta % 3) return false;
        if (!r.isExact() && sgn(laddc(r, -KT.beta)) < 0) return false;
        Lin b = lscale(laddc(r, -KT.beta), 1, 3), a = lscale(laddc(m, -1), 1, 3);
        auto head = [&](vector<Run> &NEW, const Lin &bb) {
            for (char ch : rS) NEW.push_back(Run{string(1, ch), LC(1)});
            NEW.push_back(Run{ru, laddc(lscale(bb, 3), KT.beta)});
        };
        if (!(a.isExact() && a.c == 0)) {   // R1 iterated a times
            Lin b2 = affPow(b, 2, 2, a);
            vector<Run> NEW; head(NEW, b2); NEW.push_back(Run{"1", LC(1)}); NEW.push_back(Run{ru, LC(1)});
            kreplace(P, p, NEW);
            stepsKnown = false; ++kjumps;
            if (!proof) { jlog.push_back("R1x" + linstr(a)); if (jlog.size() > 8) jlog.erase(jlog.begin()); }
            return true;
        }
        Lin d;
        while (true) {
            Lin x, z;
            if (!token(x, z)) return false;
            if (!(z.isExact() && z.c == 0)) { j = ladd(j, z); continue; }
            if (x.isExact() && x.c == 1) { j = laddc(j, 1); continue; }
            d = x; break;
        }
        if (hasProof(d) || hasProof(j)) return false;
        if (d.isExact() && d.c < 4) return false;
        if (res(d, 3) != 1) return false;
        if (p >= P.size()) return false;
        touch(0, c.st[0][P[p].run]);
        if (P[p].w[0] != '1') return false;
        Lin v = lscale(laddc(d, -1), 1, 3);
        Lin B2 = Cglobal(j, v, b);
        vector<Run> NEW; head(NEW, B2); NEW.push_back(Run{z0, laddc(j, 2)});
        kreplace(P, p, NEW);
        stepsKnown = false; ++kjumps;
        if (!proof) { jlog.push_back("C" + linstr(j) + "," + linstr(v) + "," + linstr(b) + (B2.isExact() ? "" : "*")); if (jlog.size() > 8) jlog.erase(jlog.begin()); }
        return true;
    }
    // rule application; returns -1 not applied, else status
    int applyRule(Rule &R) {
        auto &C = c;
        for (int s = 0; s < 2; ++s) {
            if (C.st[s].size() < R.g[s].size()) { if (KTDEBUG && proof) fprintf(stderr, "    rule fail line %d\n", __LINE__); return -1; }
            if (R.bottom[s] && C.st[s].size() != R.g[s].size()) { if (KTDEBUG && proof) fprintf(stderr, "    rule fail line %d\n", __LINE__); return -1; }
            size_t sz = C.st[s].size();
            for (size_t i = 0; i < R.g[s].size(); ++i) if (C.st[s][sz - 1 - i].w != R.g[s][i].w) { if (KTDEBUG && proof) fprintf(stderr, "    rule fail line %d\n", __LINE__); return -1; }
        }
        for (int s = 0; s < 2; ++s) { size_t sz = C.st[s].size(); for (size_t i = 0; i < R.g[s].size(); ++i) touch(s, C.st[s][sz - 1 - i]); if (R.bottom[s]) touchBottom(s); }
        try {
            vector<Lin> bind(R.nv); for (auto &b : bind) b.D = 0;
            for (int s = 0; s < 2; ++s) {
                size_t sz = C.st[s].size();
                for (size_t i = 0; i < R.g[s].size(); ++i) {
                    const Lin &n = C.st[s][sz - 1 - i].n; int v = R.rv[s][i];
                    if (v < 0) { if (n.isExact() ? n.c != R.g[s][i].n.c : cmpL(n, R.g[s][i].n) != 0) { if (KTDEBUG && proof) fprintf(stderr, "    rule fail line %d\n", __LINE__); return -1; } }
                    else bind[v] = n;
                }
            }
            for (auto &cn : R.cons) {
                Lin v = subst(cn.N, bind);
                if (cn.k == 'G' && sgn(v) < 0) { if (KTDEBUG && proof) fprintf(stderr, "    rule fail line %d\n", __LINE__); return -1; }
                if (cn.k == 'E' && sgn(v) != 0) { if (KTDEBUG && proof) fprintf(stderr, "    rule fail line %d\n", __LINE__); return -1; }
                if (cn.k == 'C' && (i128)res(v, (ll)cn.q) != cn.r) { if (KTDEBUG && proof) fprintf(stderr, "    rule fail line %d\n", __LINE__); return -1; }
            }
            // number of applications
            if (R.iter && proof) return -1;   // ITER rules: main mode only
            if (R.iter) {   // Z constraints at the first application (input = the bound values)
                vector<Lin> cv(R.nv); for (auto &l : cv) l.D = 0;
                for (int u = 0; u < R.nv; ++u) if (R.isF[u] && u != R.fvar && bind[u].D != 0) cv[u] = bind[u];
                for (auto &cn : R.zcons) {
                    FEval E; E.zs = &R.zs; E.var = R.fvar; E.xval = bind[R.fvar]; E.consts = &cv;
                    Lin N = E.lin(cn.N);
                    bool okz = cn.k == 'G' ? sgnG(N) >= 0 : cn.k == 'E' ? (N.isExact() && N.c == 0) : (i128)resG(N, (ll)cn.q) == cn.r;
                    if (!okz) return -1;
                }
            }
            if (R.affine && proof && !PAFF) return -1;   // affine rules in proof mode only with v13 --paff (default on)
            bool inf = true; Lin k; bool haveK = false;
            for (size_t ci = 0; ci < R.cons.size(); ++ci) {
                const Cons &cn = R.cons[ci];
                if ((R.affine || R.iter) && R.cskip[ci]) continue;   // monotone in the growing counts: never violated
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
            if (inf) { if (R.affine || R.iter) return -1; cyc = "LIN"; return S_CYCLE; }
            // apply k times
            if (R.affine || R.iter) stepsKnown = false;
            if (!R.affine && !R.iter && R.stepsKnown && stepsKnown) {
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
                    Lin nn = (R.iter && R.isF[v]) ? iterPow(R, v, bind[v], k) : (R.affine && R.amul[v] > 1) ? (proof ? computeAff(bind[v], R.amul[v], R.delta[v], k) : affPow(bind[v], R.amul[v], R.delta[v], k)) : lcomb(bind[v], 1, k, R.delta[v]); normCount(nn);
                    C.st[s][sz - 1 - i].n = nn;
                }
            }
            ++R.uses; ++ruleApps; if (R.affine) ++affApps; if (R.iter) ++iterApps;
            return S_OK;
        } catch (Undec &u) {
            if (proof) throw;
            lastUndec = "rule: " + u.why;
            { if (KTDEBUG && proof) fprintf(stderr, "    rule fail line %d\n", __LINE__); return -1; }
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
        if (ktOK && !KT.on && c.q == 1 && c.f == 1 && tryKt()) return S_OK;
        if (ktOK && KT.on && c.q == KT.Q && c.f == 1 && tryKg()) return S_OK;
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
        for (int k = 0; k < 2; ++k) { mix(0xABCD + k); int cnt = 0; for (int i = (int)c.st[k].size() - 1; i >= 0 && (SIGWIN <= 0 || cnt < SIGWIN); --i, ++cnt) { const Run &r = c.st[k][i]; mix(std::hash<string>()(r.w)); mix(r.n.isExact() && r.n.c == 1 ? 1 : 2); } }
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
        if (z.sub == 'C') { i128 w = IUexact(LBe(z.J), min<i128>(LBe(z.A), 4), LBe(z.B), SYMCAP); if (w < 0) w = SYMCAP; lbz[v] = w; return w; }
        if (z.sub == 'A') {   // a^k x + ...: iterate the lower bound min(lb k, 128) times
            i128 w = LBe(z.B), a = z.A.c, cc = z.J.c, k = min<i128>(LBe(z.K), 128);
            for (i128 t = 0; t < k && w < SYMCAP; ++t) { i128 u; if (__builtin_mul_overflow(w, a, &u) || __builtin_add_overflow(u, cc, &w) || w > SYMCAP) w = SYMCAP; }
            w = min(w, SYMCAP); lbz[v] = w; return w;
        }
        if (z.sub == 'P') { i128 w = LBe(z.B) + 4, k = min<i128>(LBe(z.A), 120); for (i128 t = 0; t < k && w < SYMCAP; ++t) w *= 2; w = min(w - 4, SYMCAP); lbz[v] = w; return w; }
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
        if (z.sub == 'A') {   // orbit of r -> a r + c (mod MG) from the residue of x, indexed by k
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
        if (z.sub == 'P') {   // 2^k (r+4) - 4
            ll p2;
            if (z.A.isExact()) p2 = pow2res(z.A.c);
            else { requireLB(z.A, 120); p2 = pow2resHuge(resAbs(z.A, ORD2)); }
            ll rr = resAbs(z.B, MG);
            return (ll)(pmod((i128)p2 * (rr + 4) - 4, MG) % m);
        }
        if (z.sub == 'C') {   // iter v (U j) b
            int ju;
            if (z.J.isExact()) ju = (int)min<i128>(z.J.c, JUMAX); else { requireLB(z.J, JUINF); ju = JUINF; }
            VC bc;
            if (z.B.isExact()) bc = VC{false, z.B.c, 0};
            else { requireLB(z.B, uthresh(ju)); bc = VC{true, 0, resAbs(z.B, umodulus(ju))}; }
            Orbit o = orbitU(ju, bc); VC r;
            if (z.A.isExact()) r = orbitAt(o, z.A.c);
            else { requireLB(z.A, (i128)o.seq.size() + 1); if (MG % o.lam != 0) UD("Z-C: orbit period"); r = orbitAtRes(o, resAbs(z.A, o.lam)); }
            if (!r.huge) UD("Z-C: small");
            return r.r % m;
        }
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
        // run until the configuration has the start's signature again (the proof's macro path may differ from the main
        // run's in representation details); give up after 4 periods
        ull sig0 = P.signature();
        for (ll t = 0;; ++t) {
            if (t >= 4 * nsteps + 64) { o.why = "no return"; return o; }
            int st = P.macroStep(); if (st != S_OK) { o.why = "stopped"; return o; }
            if (t + 1 >= nsteps && P.signature() == sig0) break;
        }
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
    // affine rule (k-fold acceleration): every prefix count maps x -> a x + c with its own variable only
    if (!hasZ && !extras && !NOAFF) {
        R.amul.assign(R.nv, 1); bool aff = true, grow = false, dec = false;
        for (int v = 0; v < R.nv && aff; ++v) if (inPrefix[v]) {
            const Lin &x = e[v];
            if (x.n == 1 && x.id[0] == PBASE + v && x.a[0] >= 1 && x.D == 1) { R.amul[v] = x.a[0]; R.delta[v] = x.c; if (x.a[0] > 1) grow = true; else if (x.c < 0) dec = true; }
            else aff = false;
        }
        if (aff && grow && dec) {
            // per-variable lower bounds from single-variable constraints
            vector<i128> lbv(R.nv, 1);
            for (auto &cn : ctx.cons) if (cn.k == 'G' && cn.N.n == 1 && cn.N.id[0] >= PBASE && cn.N.a[0] > 0) { int v = cn.N.id[0] - PBASE; lbv[v] = max(lbv[v], cdiv(-cn.N.c, cn.N.a[0])); }
            bool okc = true, lim = false;
            for (auto &cn : ctx.cons) {
                bool inP = true, hasG = false, hasL = false;
                for (int t = 0; t < cn.N.n; ++t) { if (cn.N.id[t] < PBASE) continue; int v = cn.N.id[t] - PBASE; if (!inPrefix[v]) inP = false; else if (R.amul[v] > 1) hasG = true; else hasL = true; }
                if (!inP) { if (!(cn.k == 'G' && cn.N.n == 1 && cn.N.a[0] == 1 && cn.N.c == -1)) okc = false; continue; }
                if (hasG) {
                    bool mono = cn.k == 'G' && !hasL;
                    for (int t = 0; t < cn.N.n && mono; ++t) if (cn.N.id[t] >= PBASE) { int v = cn.N.id[t] - PBASE; if (cn.N.a[t] < 0 || (R.amul[v] - 1) * lbv[v] + R.delta[v] < 0) mono = false; }
                    if (!mono && cn.k == 'C' && AFFC) {
                        // v13: a congruence N == r (mod q) is invariant under x_v -> amul_v x_v + delta_v when
                        // a_t (amul_t - 1) == 0 and sum a_t delta_t == 0 (mod q): N(f(x)) == N(x) (mod q) for every x.
                        // It is checked at the first application, so it then holds at every iteration.
                        bool inv = true; i128 sd = 0;
                        for (int t = 0; t < cn.N.n && inv; ++t) if (cn.N.id[t] >= PBASE) {
                            int v = cn.N.id[t] - PBASE;
                            if (pmod(M_(cn.N.a[t], R.amul[v] - 1), cn.q) != 0) inv = false;
                            sd = pmod(A_(sd, M_(cn.N.a[t], R.delta[v])), cn.q);
                        }
                        if (inv && sd == 0) mono = true;
                    }
                    if (!mono) { okc = false; break; }
                    R.cons.push_back(cn); R.cskip.push_back(1);
                } else {
                    R.cons.push_back(cn); R.cskip.push_back(0);
                    i128 B = 0; for (int t = 0; t < cn.N.n; ++t) if (cn.N.id[t] >= PBASE) B += cn.N.a[t] * R.delta[cn.N.id[t] - PBASE];
                    if ((cn.k == 'G' && B < 0) || (cn.k == 'E' && B != 0) || (cn.k == 'C' && pmod(B, cn.q) != 0)) lim = true;
                }
            }
            if (okc && lim) {
                R.affine = true; R.stepsKnown = false;
                if (SHOWPROOF) fprintf(stderr, "PROOF affine rule delta=%lld\n", nsteps);
                o.st = 1; o.kind = "AFF"; return o;
            }
            R.cons.clear(); R.cskip.clear();
        }
    }
    // v13 ITER rule: decreasing counters plus self maps x_v -> F_v(x_v) (F built from proof symbols of x_v only)
    if (hasZ && !extras && ITERON) {
        R.isF.assign(R.nv, 0); R.iterF.assign(R.nv, Lin()); R.flb.assign(R.nv, 1); R.amul.assign(R.nv, 1); R.delta.assign(R.nv, 0);
        bool ok = true, dec = false, anyF = false; string iwhy;
        // proof variables a formula depends on (through proof symbols)
        std::function<void(const Lin &, set<int> &, int)> deps = [&](const Lin &x, set<int> &out, int depth) {
            if (depth > 40) { ok = false; return; }
            for (int t = 0; t < x.n; ++t) if (x.id[t] >= PBASE) {
                int idx = x.id[t] - PBASE; const PSym &z = ctx.s[idx];
                if (z.kind == 'P') out.insert(idx);
                else for (const Lin *a : {&z.J, &z.A, &z.B, &z.K}) deps(*a, out, depth + 1);
            }
        };
        std::function<bool(const Lin &, int)> nonneg = [&](const Lin &x, int depth) -> bool {
            if (depth > 40 || !allNonneg(x)) return false;   // monotone: nonnegative coefficients (constants are free)
            for (int t = 0; t < x.n; ++t) if (x.id[t] >= PBASE && ctx.s[x.id[t] - PBASE].kind == 'Z') {
                const PSym &z = ctx.s[x.id[t] - PBASE];
                if (z.sub == 'A' && (z.A.c < 2 || z.J.c < 0)) return false;
                for (const Lin *a : {&z.J, &z.A, &z.B, &z.K}) if (a->n || a->c) if (!nonneg(*a, depth + 1)) return false;
            }
            return true;
        };
        for (int v = 0; v < R.nv && ok; ++v) if (inPrefix[v] && ctx.s[v].kind == 'P') {
            const Lin &x = e[v];
            if (x.n == 1 && x.id[0] == PBASE + v && x.a[0] == 1 && x.D == 1) { R.delta[v] = x.c; if (x.c < 0) dec = true; continue; }
            if (x.isExact() && x.c >= 0) { R.isF[v] = 1; R.iterF[v] = x; continue; }   // reset to a constant
            set<int> d; deps(x, d, 0);
            if (!ok || d.size() > 1 || (d.size() == 1 && *d.begin() != v)) { ok = false; iwhy = "deps x" + to_string(v); break; }
            if (!mentionsZ(x) || !nonneg(x, 0)) { ok = false; iwhy = "form x" + to_string(v); break; }
            if (R.fvar >= 0) { ok = false; iwhy = "two F vars"; break; }
            R.isF[v] = 1; R.iterF[v] = x; anyF = true; R.fvar = v;
        }
        if (ok && dec && anyF) {
            R.zs = ctx.s;
            // lower bounds of the F variables from single-variable constraints
            for (auto &cn : ctx.cons) if (cn.k == 'G' && cn.N.n == 1 && cn.N.id[0] >= PBASE && cn.N.a[0] > 0 && ctx.s[cn.N.id[0] - PBASE].kind == 'P') {
                int v = cn.N.id[0] - PBASE; if (R.isF[v]) R.flb[v] = max(R.flb[v], cdiv(-cn.N.c, cn.N.a[0]));
            }
            bool okc = true, lim = false;
            for (auto &cn : ctx.cons) {
                bool hasF = false, hasL = false, hasZc = mentionsZ(cn.N), foreign = false;
                for (int t = 0; t < cn.N.n; ++t) if (cn.N.id[t] >= PBASE) {
                    int v = cn.N.id[t] - PBASE;
                    if (ctx.s[v].kind != 'P') continue;
                    if (!inPrefix[v]) foreign = true; else if (R.isF[v]) hasF = true; else hasL = true;
                }
                if (foreign) { if (!(cn.k == 'G' && cn.N.n == 1 && cn.N.a[0] == 1 && cn.N.c == -1)) { okc = false; iwhy = "foreign " + linstr(cn.N); } continue; }
                if (hasZc || hasF) {
                    if (hasL) { okc = false; iwhy = "mixed " + linstr(cn.N); break; }
                    // checked at every application's input (first: applyRule, later: iterConsOK)
                    R.zcons.push_back(cn);
                    if (!hasZc) { R.cons.push_back(cn); R.cskip.push_back(1); }
                    continue;
                }
                R.cons.push_back(cn); R.cskip.push_back(0);
                i128 B = 0; for (int t = 0; t < cn.N.n; ++t) if (cn.N.id[t] >= PBASE) B += cn.N.a[t] * R.delta[cn.N.id[t] - PBASE];
                if ((cn.k == 'G' && B < 0) || (cn.k == 'E' && B != 0) || (cn.k == 'C' && pmod(B, cn.q) != 0)) lim = true;
            }
            if (okc && lim) {
                R.iter = true; R.stepsKnown = false;
                if (SHOWPROOF) fprintf(stderr, "PROOF iter rule delta=%lld\n", nsteps);
                o.st = 1; o.kind = "ITER"; return o;
            }
            R.cons.clear(); R.cskip.clear(); R.zcons.clear(); R.zs.clear(); R.fvar = -1;
            if (okc && !lim) iwhy = "nolim";
        } else if (ok) iwhy = dec ? "noF" : "nodec";
        if (SHOWPROOF) fprintf(stderr, "PROOF iter failed: %s\n", iwhy.c_str());
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

// ------------------------------------------------------------------ per-machine verification of the Kt rules R1-R3
// Kt_R1  Kt ds (3+m) r t -->+ Kt ds m (2r+4) t                          (r > 0)
// Kt_R2  Kt ((3+x)::ds) 1 r t -->+ Kt (x::ds) (2r+3) 2 t                (r > 0)
// Kt_R3  Kt (1^(k+1) ++ (3+x)::ds) 1 r t -->+ Kt (1^k ++ (2r+3)::x::ds) 1 2 t   (r > 0, x > 0)
// Each rule is executed symbolically from a configuration with proof variables (m, r, t, x, k) and an untouched
// sentinel run standing for the arbitrary rest of the tape; it holds for this machine if the target configuration is
// reached, the sentinel was never read, and every recorded decision follows from the hypotheses (lower bounds).
// Given R1-R3 for all ds, the abstract lemmas R1ITER, CH, CDP of BB9_record_1RB0RA.v follow (they use nothing else).
struct CItem { bool cell; char ch; string w; Lin n; };
static vector<CItem> canonRuns(const vector<Run> &runs) {   // runs nearest-first
    vector<CItem> it;
    for (const Run &r0 : runs) {
        Run r = r0; int p = primRoot(r.w); if (p < (int)r.w.size()) { r.n = lscale(r.n, (i128)(r.w.size() / p)); r.w.resize(p); }
        if (r.n.isExact() && r.n.c * (i128)r.w.size() <= 200000) { for (i128 t = 0; t < r.n.c; ++t) for (char ch : r.w) it.push_back(CItem{true, ch, "", LC(0)}); }
        else it.push_back(CItem{false, 0, r.w, r.n});
    }
    bool chg = true;
    while (chg) {
        chg = false;
        for (size_t i = 0; i < it.size() && !chg; ++i) {
            if (it[i].cell) continue;
            const string w = it[i].w; size_t L = w.size();
            if (i + 1 < it.size() && !it[i + 1].cell && it[i + 1].w == w) { it[i].n = ladd(it[i].n, it[i + 1].n); it.erase(it.begin() + i + 1); chg = true; break; }
            if (i >= L) { bool ok = true; for (size_t k = 0; k < L && ok; ++k) ok = it[i - L + k].cell && it[i - L + k].ch == w[k];
                if (ok) { it[i].n = laddc(it[i].n, 1); it.erase(it.begin() + (i - L), it.begin() + i); chg = true; break; } }
            if (i + L < it.size()) { bool ok = true; for (size_t k = 0; k < L && ok; ++k) ok = it[i + 1 + k].cell && it[i + 1 + k].ch == w[k];
                if (ok) { it[i].n = laddc(it[i].n, 1); it.erase(it.begin() + i + 1, it.begin() + i + 1 + L); chg = true; break; } }
            // rephase: a nearer cell equal to the word's last cell moves to the far side (x w^n = (x w')^n x)
            if (i >= 1 && it[i - 1].cell && it[i - 1].ch == w.back()) {
                char x = it[i - 1].ch; it[i].w = string(1, x) + w.substr(0, L - 1);
                it.erase(it.begin() + (i - 1)); it.insert(it.begin() + i, CItem{true, x, "", LC(0)});
                chg = true; break;
            }
        }
    }
    return it;
}
static bool canonEq(const vector<CItem> &a, const vector<CItem> &b) {
    if (a.size() != b.size()) return false;
    for (size_t i = 0; i < a.size(); ++i) {
        if (a[i].cell != b[i].cell) return false;
        if (a[i].cell) { if (a[i].ch != b[i].ch) return false; }
        else if (a[i].w != b[i].w || !lequal(a[i].n, b[i].n)) return false;
    }
    return true;
}
static const int KT_SENT = 1000000;
// run from START (nearest-first runs above the sentinel) to TARGET; proof mode when vars are present
static bool ktRun(const vector<Run> &start, const vector<Run> &target, ll maxm, bool proofMode, size_t nhyp, RuleSet *rules = nullptr, bool learn = false, string *why = nullptr) {
    Sim P; P.proof = proofMode; P.track = true; P.chOK = false; P.ktOK = 0; RuleSet RS0; P.rules = rules ? rules : &RS0; P.prover = false;
    unordered_map<ull, array<ll, 3>> past;
    P.c.q = KT.on ? KT.Q : 1; P.c.f = 1;
    P.c.st[0].push_back(Run{"0110", LC(1000), KT_SENT});   // count > FOLDREG: never folded
    for (int i = (int)start.size() - 1; i >= 0; --i) if (!(start[i].n.isExact() && start[i].n.c == 0)) P.c.st[0].push_back(Run{start[i].w, start[i].n, -1});
    vector<CItem> tgt = canonRuns(target);
    try {
        for (ll s = 0; s < maxm; ++s) {
            if (learn) {   // main mode with the rule prover: the learned linear rules are reused by the symbolic runs
                ull sg = P.signature(); auto it = past.find(sg);
                if (it == past.end()) past[sg] = {P.macro, -1, 0};
                else { auto &pp = it->second; ll d = P.macro - pp[0];
                    if (d == pp[1] && pp[2] < 3 && d <= MAXDELTA) { int r = tryProve(P, d); if (r == 2) { if (why) *why = "CYCLE " + P.cyc; return false; } if (r == 1) pp[2] = 0; else pp[2]++; }
                    pp[1] = d; pp[0] = P.macro; }
            }
            if (KTTRACE) fprintf(stderr, "%lld %s\n", s, P.show().c_str());
            if (!proofMode && (s & 15) == 15) for (int q = 0; q < 2; ++q) if (P.c.st[q].size() > 6) {   // representation only
                Run sent = P.c.st[0][0];
                P.deepCompress(q);
                if (q == 0 && (P.c.st[0].empty() || P.c.st[0][0].w != sent.w || !lequal(P.c.st[0][0].n, sent.n))) return false;
                if (q == 0) P.c.st[0][0].tag = KT_SENT;
            }
            int st = P.macroStep();
            if (st != S_OK) { if (KTDEBUG) fprintf(stderr, "  stopped st=%d at %lld %s\n", st, s, P.show().c_str()); return false; }
            if (P.maxTag[0] >= KT_SENT || P.bot[0]) { if (why) *why = "sentinel"; if (KTDEBUG) fprintf(stderr, "  sentinel touched at %lld\n", s); return false; }
            if (P.c.q == (KT.on ? KT.Q : 1) && P.c.f == 1 && P.c.st[1].empty()) {
                auto &L = P.c.st[0]; if (L.empty() || L[0].tag != KT_SENT) return false;
                vector<Run> cur; for (int i = (int)L.size() - 1; i >= 1; --i) cur.push_back(L[i]);
                if (KTDEBUG) {
                    auto cs = [](const vector<CItem> &v) { string s; for (auto &x : v) s += x.cell ? string(1, x.ch) : "[" + x.w + "^" + linstr(x.n) + "]"; return s; };
                    fprintf(stderr, "  B-moment %lld: %s\n     target: %s\n", s, cs(canonRuns(cur)).c_str(), cs(tgt).c_str());
                }
                if (canonEq(canonRuns(cur), tgt)) {
                    if (!proofMode) return true;
                    // every decision must follow from the hypotheses x >= lb
                    vector<i128> lb(PC->s.size(), 0);
                    for (size_t i = 0; i < nhyp; ++i) { const Cons &cn = PC->cons[i]; int v = cn.N.id[0] - PBASE; lb[v] = -cn.N.c; }
                    for (size_t i = nhyp; i < PC->cons.size(); ++i) {
                        const Cons &cn = PC->cons[i];
                        if (cn.k != 'G') return false;
                        i128 s0 = cn.N.c;
                        for (int k = 0; k < cn.N.n; ++k) {
                            if (cn.N.id[k] < PBASE || PC->s[cn.N.id[k] - PBASE].kind != 'P' || cn.N.a[k] < 0) return false;
                            s0 += cn.N.a[k] * lb[cn.N.id[k] - PBASE];
                        }
                        if (s0 < 0) return false;
                    }
                    for (auto &z : PC->s) if (z.kind != 'P') return false;
                    return true;
                }
            }
        }
    } catch (Undec &u) { if (why) *why = u.why; if (KTDEBUG) fprintf(stderr, "  undec %s\n", u.why.c_str()); return false; }
    if (why) *why = "no target";
    if (KTDEBUG) fprintf(stderr, "  no target within %lld\n", maxm);
    return false;
}
// build the start and target of rule R (1..3), tail case tc (0: t = 0, 1: t >= 1), sub (0: m/x/k at its least value)
static void ktCase(int R, int tc, int sub, const vector<Lin> &vals, vector<Run> &S, vector<Run> &T) {
    // vals: r, t, m3 (=3+m), x3 (=3+x), k1 (=k+1)
    Lin r = vals[0], t = vals[1], m3 = vals[2], x3 = vals[3], k1 = vals[4];
    auto head = [&](vector<Run> &v, const Lin &rr) {
        v.push_back(Run{"1", LC(1)}); v.push_back(Run{"0", LC(2)}); v.push_back(Run{"1", LC(1)});
        if (tc) v.push_back(Run{"00111111", t});
        v.push_back(Run{"1", LC(2)}); v.push_back(Run{"01", rr});
    };
    S.clear(); T.clear();
    if (R == 1) {
        head(S, r); S.push_back(Run{"1", LC(1)}); S.push_back(Run{"01", m3}); S.push_back(Run{"1", LC(1)});
        head(T, laddc(lscale(r, 2), 4)); T.push_back(Run{"1", LC(1)}); T.push_back(Run{"01", laddc(m3, -3)}); T.push_back(Run{"1", LC(1)});
    } else if (R == 2) {
        head(S, r); S.push_back(Run{"1", LC(1)}); S.push_back(Run{"01", LC(1)}); S.push_back(Run{"1", LC(1)}); S.push_back(Run{"01", x3}); S.push_back(Run{"1", LC(1)});
        head(T, LC(2)); T.push_back(Run{"1", LC(1)}); T.push_back(Run{"01", laddc(lscale(r, 2), 3)}); T.push_back(Run{"1", LC(1)}); T.push_back(Run{"01", laddc(x3, -3)}); T.push_back(Run{"1", LC(1)});
    } else {
        head(S, r); S.push_back(Run{"1", LC(1)}); S.push_back(Run{"01", LC(1)}); S.push_back(Run{"101", k1}); S.push_back(Run{"1", LC(1)}); S.push_back(Run{"01", x3}); S.push_back(Run{"1", LC(1)});
        head(T, LC(2)); T.push_back(Run{"1", LC(1)}); T.push_back(Run{"01", LC(1)}); T.push_back(Run{"101", laddc(k1, -1)}); T.push_back(Run{"1", LC(1)});
        T.push_back(Run{"01", laddc(lscale(r, 2), 3)}); T.push_back(Run{"1", LC(1)}); T.push_back(Run{"01", laddc(x3, -3)}); T.push_back(Run{"1", LC(1)});
    }
}
// Each parameter is either a small exact value (below KTL0) or a global symbol with lower bound KTL0 and NO residue
// information: a run that decides everything with such symbols proves the rule for every value >= KTL0.  All
// combinations of small/large parameters are run, so together they cover every parameter value.
// A worklist of parameter assignments; a "large" parameter is a symbol with lower bound L and no residue information.
// If a run needs a decision X - c (c >= L) about such a symbol, the assignment is split into the exact values
// L..c and a symbol with lower bound c+1.  When every assignment succeeds, the rule holds for every value.
static const int KTL0 = 4;
static string KTFAIL;
static int verifyKt() {
    int ok = 0;
    RuleSet RSall[4][2];
    for (int tc = 0; tc < 2; ++tc) {
        bool good = true;
        for (int R = 1; R <= 3 && good; ++R) {
            // parameters: 0 r (>=1), 1 t (tc: 0 or >=1), 2 p (m or x; R3: x>=1), 3 k (R3 only)
            int lo[4] = {1, tc ? 1 : 0, R == 3 ? 1 : 0, 0};
            bool used[4] = {true, tc == 1, true, R == 3};
            // assignment: value >= 0 exact, or -L for "symbolic with lower bound L"
            vector<array<int, 4>> work;
            {
                vector<vector<int>> vals(4);
                for (int q = 0; q < 4; ++q) {
                    if (!used[q]) { vals[q] = {lo[q]}; continue; }
                    for (int v = lo[q]; v < KTL0; ++v) vals[q].push_back(v);
                    vals[q].push_back(-KTL0);
                }
                for (int a0 : vals[0]) for (int a1 : vals[1]) for (int a2 : vals[2]) for (int a3 : vals[3]) work.push_back({a0, a1, a2, a3});
            }
            int guard = 0;
            while (!work.empty() && good) {
                if (++guard > 20000) { good = false; KTFAIL = "too many cases"; break; }
                array<int, 4> asg = work.back(); work.pop_back();
                Lin P[4]; map<int, int> symParam;
                for (int q = 0; q < 4; ++q) {
                    if (asg[q] >= 0) P[q] = LC(asg[q]);
                    else { int id = newG(-asg[q], 0, "kt-param", 1); P[q] = LV(id); symParam[id] = q; }
                }
                Lin m3 = R == 1 ? laddc(P[2], 3) : LC(3), x3 = R == 1 ? LC(3) : laddc(P[2], 3), k1 = laddc(P[3], 1);
                vector<Run> S, T; ktCase(R, tc, 0, {P[0], P[1], m3, x3, k1}, S, T);
                RuleSet &RS = RSall[R][tc]; string why;
                if (RS.R.empty()) {   // learn the inner loops on a large concrete instance first; rules are general
                    vector<Run> S2, T2; ktCase(R, tc, 0, {LC(60), LC(tc ? 7 : 0), LC(R == 1 ? 3 + 40 : 3 + 30), LC(R == 1 ? 3 : 3 + 30), LC(R == 3 ? 9 : 1)}, S2, T2);
                    ktRun(S2, T2, 200000, false, 0, &RS, true);
                }
                int res = ktRun(S, T, 200000, false, 0, &RS, true, &why);
                if (res) continue;
                // split on "sign:X<id>-<c>" for a large parameter
                int id = -1; long long cst = 0;
                if (why.rfind("sign:X", 0) == 0) {
                    const char *q = why.c_str() + 6; id = atoi(q); while (isdigit(*q)) ++q;
                    if (*q == '-') cst = atoll(q + 1); else if (*q == 0) cst = 0; else id = -1;
                }
                auto it = symParam.find(id);
                if (id >= 0 && it != symParam.end() && cst >= -asg[it->second] && cst < 64) {
                    int q = it->second, L = -asg[q];
                    for (int v = L; v <= cst; ++v) { auto a2 = asg; a2[q] = v; work.push_back(a2); }
                    auto a2 = asg; a2[q] = -(int)(cst + 1); work.push_back(a2);
                    continue;
                }
                good = false;
                KTFAIL = "R" + to_string(R) + " tc" + to_string(tc) + " asg " + to_string(asg[0]) + "," + to_string(asg[1]) + "," + to_string(asg[2]) + "," + to_string(asg[3]) + " " + why;
                if (KTDEBUG) fprintf(stderr, "kt fail %s\n", KTFAIL.c_str());
            }
        }
        if (good) ok |= 1 << tc;
    }
    return ok;
}
// ------------------------------------------------------------------ template engine: grid check of R1-R3
// nearest-first run list of K(tokens; b) for the current template: rev(S), (rev u)^(3b+beta), then tokens "1 (rev u)^x"
static void kgHead(vector<Run> &v, i128 b) {
    string rS(KT.S.rbegin(), KT.S.rend()), ru(KT.u.rbegin(), KT.u.rend());
    for (char ch : rS) v.push_back(Run{string(1, ch), LC(1)});
    v.push_back(Run{ru, LC(3 * b + KT.beta)});
}
static void kgTok(vector<Run> &v, i128 x) { string ru(KT.u.rbegin(), KT.u.rend()); v.push_back(Run{"1", LC(1)}); v.push_back(Run{ru, LC(x)}); }
static bool kgGrid(long long &ncase, string &fail) {
    ncase = 0;
    vector<int> bs = {0, 1, 2, 3, 5, 9};
    RuleSet RS[4];
    for (int extra = 0; extra < 2; ++extra) for (int R = 1; R <= 3; ++R)
        for (int b : bs) for (int a = 0; a <= (R == 1 ? 3 : 0); ++a) for (int y = 0; y <= (R == 1 ? 0 : 3); ++y) for (int M = 0; M <= (R == 3 ? 3 : 0); ++M) {
            vector<Run> S, T;
            if (R == 1) { kgHead(S, b); kgTok(S, 3 * (a + 1) + 1); kgHead(T, 2 * b + 2); kgTok(T, 3 * a + 1); }
            if (R == 2) { kgHead(S, b); kgTok(S, 1); kgTok(S, 3 * (y + 1) + 1); kgHead(T, 0); kgTok(T, 3 * (2 * b + 2) + 1); kgTok(T, 3 * y + 1); }
            if (R == 3) { kgHead(S, b); kgTok(S, 1); for (int q = 0; q <= M; ++q) kgTok(S, 1); kgTok(S, 3 * (y + 1) + 1);
                          kgHead(T, 0); kgTok(T, 1); for (int q = 0; q < M; ++q) kgTok(T, 1); kgTok(T, 3 * (2 * b + 2) + 1); kgTok(T, 3 * y + 1); }
            if (extra) { kgTok(S, 4); kgTok(T, 4); }   // one more digit beyond the rule's tokens
            S.push_back(Run{"1", LC(1)}); T.push_back(Run{"1", LC(1)});   // the next token / end of P starts with 1; the sentinel is the rest
            ++ncase; string why;
            if (!ktRun(S, T, 4000000, false, 0, nullptr, false, &why)) {   // plain macro steps, no learned rules: literal-equivalent
                fail = "R" + to_string(R) + " b=" + to_string(b) + " a=" + to_string(a) + " y=" + to_string(y) + " M=" + to_string(M) + " extra=" + to_string(extra) + " " + why;
                return false;
            }
        }
    return true;
}
// template "R,B,P=11,u=10,s=1,d=3d+1,b=3b+2,S=111001" with champion maps
static bool kgParse(const string &tmpl, const string &params, string &why) {
    KT = KTmpl();
    if (params.rfind("R1 2b+2 | R2 a=2b+2 b=0 | R3 2b+2+0k tail=0 a=0 b=0", 0) != 0) { why = "maps"; return false; }
    vector<string> f; { string x; istringstream is(tmpl); while (getline(is, x, ',')) f.push_back(x); }
    if (f.size() < 8 || f[0] != "R" || f[1].size() != 1) { why = "format"; return false; }
    KT.Q = f[1][0] - 'A';
    for (auto &x : f) {
        if (x.rfind("u=", 0) == 0) KT.u = x.substr(2);
        if (x.rfind("S=", 0) == 0) KT.S = x.substr(2);
        if (x.rfind("b=3b+", 0) == 0) KT.beta = atoi(x.c_str() + 5);
        if (x.rfind("s=", 0) == 0 && x != "s=1") { why = "s"; return false; }
        if (x.rfind("d=", 0) == 0 && x != "d=3d+1") { why = "d"; return false; }
        if (x.rfind("b=", 0) == 0 && x.rfind("b=3b+", 0) != 0) { why = "b"; return false; }
    }
    if (KT.S == "-" || KT.S.empty()) { why = "S"; return false; }
    if (KT.u != "01" && KT.u != "10") { why = "u"; return false; }
    if (KT.beta < 0 || KT.beta > 2) { why = "beta"; return false; }
    KT.on = true; return true;
}
static string cfgStr(const Cfg &c) { Sim t; t.c = c; return t.show(60); }
// ------------------------------------------------------------------ driver
struct Opts { ll budget = 1000000; bool nokt = true, noch = false, noprove = false, trace = false, tape = false; i128 hlb = 0; ll tracemax = 2000; double tlimit = 0; };
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
static int TAPEALL = 0; static bool JUMPDUMP = false, JUMPSTOP = false;
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
static string TMPLOPT, TMPLPAR = "R1 2b+2 | R2 a=2b+2 b=0 | R3 2b+2+0k tail=0 a=0 b=0", TMPLMACH; static int TMPLRULED = 0;
static void runOne(const string &mach, int start, const vector<string> &tok);
static void runOneT(const string &mach, int start, const vector<string> &tok) {   // run mode with --tmpl: grid once per machine
    if (TMPLOPT.empty()) { runOne(mach, start, tok); return; }
    if (mach != TMPLMACH) {
        string why; TMPLMACH = mach; TMPLRULED = 0;
        if (kgParse(TMPLOPT, TMPLPAR, why)) { GS.clear(); MINI.clear(); parseMachine(mach, TT, NS); long long nc; string fail; TMPLRULED = kgGrid(nc, fail) ? 1 : 0;
            fprintf(stderr, "KGRID %s %s %s\n", mach.c_str(), TMPLRULED ? "RULED" : "UNRULED", fail.c_str()); }
    }
    string why; kgParse(TMPLOPT, TMPLPAR, why); if (!TMPLRULED) KT.on = false;
    KGRULED = TMPLRULED; runOne(mach, start, tok); KT = KTmpl(); KGRULED = -1;
}
static void runOne(const string &mach, int start, const vector<string> &tok) {
    GS.clear(); MINI.clear(); wSymCount = 0;
    if (!parseMachine(mach, TT, NS)) { printf("R %s %c BAD\n", mach.c_str(), 'A' + start); return; }
    RuleSet RS; Sim M; M.rules = &RS; M.chOK = !OPT.noch && coreIntact(); M.trace = OPT.trace;
    M.ktOK = KGRULED >= 0 ? KGRULED : KTFORCE ? 3 : (OPT.nokt || NS < 2) ? 0 : verifyKt();
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
            if (M.macro % DEEPEVERY == 0) for (int s = 0; s < 2; ++s) if ((ll)M.c.st[s].size() > DEEPRUNS) M.deepCompress(s);
            ll kj0 = M.kjumps;
            int st = M.macroStep();
            if (JUMPDUMP && M.kjumps != kj0 && !M.jlog.empty() && M.jlog.back()[0] == 'C') {   // tape right after a CDP clear
                string sd; for (int s2 = 0; s2 < 2; ++s2) for (auto &r : M.c.st[s2]) if (!r.n.isExact()) sd += symDescs(r.n);
                printf("JUMPTAPE %s %s\n", M.show(4000).c_str(), sd.c_str()); fflush(stdout);
                if (JUMPSTOP) { verdict = "BUDGET"; detail = "jumpstop"; break; }
            }
            if (st == S_HALT) { verdict = "HALT"; break; }
            if (st == S_CYCLE) { verdict = "CYCLE"; detail = M.cyc; break; }
        }
    } catch (Undec &u) { verdict = "UNDECIDED"; detail = u.why; }
    catch (std::exception &ex) { verdict = "UNDECIDED"; detail = string("exception ") + ex.what(); }
    for (auto &ch : detail) if (ch == ' ') ch = '_';
    string sig = "?", sd;
    try { Lin s = M.sigma(); sig = linstr(s); if (verdict == "HALT") sd = symDescs(s); } catch (Undec &) {}
    string jl; for (auto &x : M.jlog) jl += " " + x;
    printf("R %s %c %s %s kt=%d kj=%lld aff=%lld macro=%lld steps=%s sigma=%s jumps=%lld maxj=%s rules=%zu apps=%lld syms=%zu it=%lld |%s |%s\n", mach.c_str(), 'A' + start,
           verdict.c_str(), detail.c_str(), M.ktOK, M.kjumps, M.affApps, M.macro, M.stepsKnown ? s128(M.steps.c).c_str() : "?", sig.c_str(), M.jumps, linstr(M.maxJ).c_str(),
           RS.R.size(), M.ruleApps, GS.size(), M.iterApps, jl.c_str(), sd.c_str());
    if (OPT.tape) printf("%s\n", verdict == "HALT" ? tapeDump(M).c_str() : TAPEALL ? ("TAPE " + M.show(TAPEALL)).c_str() : "TAPE notshown");
    if (OPT.tape && TAPEALL && verdict != "HALT") {   // descriptions of the symbols on the final tape
        string sd; for (int s2 = 0; s2 < 2; ++s2) for (auto &r : M.c.st[s2]) if (!r.n.isExact()) sd += symDescs(r.n);
        printf("TAPESYMS %s\n", sd.c_str());
    }
    if (M.trace) fprintf(stderr, "END %s\n", M.show().c_str());
    fflush(stdout);
}
int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: symsim run|wtab [opts] < input\n"); return 1; }
    string mode = argv[1];
    for (int i = 2; i < argc && mode != "ktone" && mode != "ktgrid"; ++i) {
        string a = argv[i];
        auto nx = [&]() { return string(argv[++i]); };
        if (a == "--budget") OPT.budget = atoll(nx().c_str());
        else if (a == "--mg") MG = atoll(nx().c_str());
        else if (a == "--exmax") EXMAX = p128(nx().c_str());
        else if (a == "--hlb") OPT.hlb = p128(nx().c_str());
        else if (a == "--maxdelta") MAXDELTA = atoll(nx().c_str());
        else if (a == "--noch") OPT.noch = true;
        else if (a == "--nokt") OPT.nokt = true;
        else if (a == "--kt") OPT.nokt = false;
        else if (a == "--noaff") NOAFF = true;
        else if (a == "--ktforce") KTFORCE = true;
        else if (a == "--tmpl") TMPLOPT = nx();
        else if (a == "--ktdebug") KTDEBUG = true;
        else if (a == "--noprove") OPT.noprove = true;
        else if (a == "--trace") OPT.trace = true;
        else if (a == "--tracemax") OPT.tracemax = atoll(nx().c_str());
        else if (a == "--tape") OPT.tape = true;
        else if (a == "--jumpdump") JUMPDUMP = true;
        else if (a == "--kgalt") KGALTON = true;
        else if (a == "--noaffc") AFFC = false;
        else if (a == "--nopaff") PAFF = false;
        else if (a == "--noiter") ITERON = false;
        else if (a == "--memcap") MEMCAP = (size_t)atoll(nx().c_str()) << 20;
        else if (a == "--jumpstop") JUMPDUMP = JUMPSTOP = true;
        else if (a == "--tapeall") { OPT.tape = true; TAPEALL = atoi(nx().c_str()); }
        else if (a == "--tlimit") OPT.tlimit = atof(nx().c_str());
        else if (a == "--sigwin") SIGWIN = atoi(nx().c_str());
        else if (a == "--deep") { DEEPEVERY = atoll(nx().c_str()); DEEPRUNS = atoll(nx().c_str()); }
        else if (a == "--showproof") SHOWPROOF = true;
        else { fprintf(stderr, "bad option %s\n", a.c_str()); return 1; }
    }
    buildW(); buildU();
    if (mode == "kgrade") {   // kgrade [opts] < "machine<TAB>slice<TAB>grade<TAB>template<TAB>params" : grid check, then exact grade
        string line;
        while (getline(cin, line)) {
            vector<string> f; { string x; istringstream is(line); while (getline(is, x, '	')) f.push_back(x); }
            if (f.size() < 5) continue;
            string why;
            if (!kgParse(f[3], f[4], why)) { printf("KGSKIP %s %s %s %s\n", f[0].c_str(), f[1].c_str(), why.c_str(), f[3].c_str()); KT = KTmpl(); KGRULED = 0; runOne(f[0], 0, {}); continue; }
            GS.clear(); MINI.clear(); parseMachine(f[0], TT, NS);
            long long nc = 0; string fail; bool ok = kgGrid(nc, fail);
            printf("KGRID %s %s %s cases=%lld %s\n", f[0].c_str(), f[1].c_str(), ok ? "RULED" : "UNRULED", nc, fail.c_str()); fflush(stdout);
            KGRULED = ok ? 1 : 0; if (!ok) KT.on = false;
            runOne(f[0], 0, {});
            KT = KTmpl(); KGRULED = -1;
        }
        return 0;
    }
    if (mode == "ktgrid") {   // ktgrid < machines : literal (exact) check of R1-R3 on a grid; prints "KG machine t0 t1 cases"
        string line; vector<int> rs = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 20, 33, 60};
        while (getline(cin, line)) {
            istringstream is(line); string mach; if (!(is >> mach)) continue;
            GS.clear(); MINI.clear(); parseMachine(mach, TT, NS);
            int okb = 0; long long ncase = 0;
            RuleSet RSg[4];   // rules are general: shared by all cases of one rule
            for (int tc = 0; tc < 2; ++tc) {
                bool good = true; vector<int> ts = tc ? vector<int>{1, 2, 3} : vector<int>{0};
                for (int R = 1; R <= 3 && good; ++R)
                    for (int t : ts) for (int r : rs) for (int p = (R == 3 ? 1 : 0); p <= 8 && good; ++p) for (int k = 0; k <= (R == 3 ? 4 : 0) && good; ++k) {
                        Lin m3 = R == 1 ? LC(p + 3) : LC(3), x3 = R == 1 ? LC(3) : LC(p + 3);
                        vector<Run> S, T; ktCase(R, tc, 0, {LC(r), LC(t), m3, x3, LC(k + 1)}, S, T);
                        RuleSet &RS = RSg[R]; ++ncase;
                        string why; if (!ktRun(S, T, 200000, false, 0, &RS, true, &why)) { good = false; fprintf(stderr, "KGFAIL R%d tc%d t=%d r=%d p=%d k=%d %s\n", R, tc, t, r, p, k, why.c_str()); }
                    }
                if (good) okb |= 1 << tc;
            }
            printf("KG %s %d %d %lld\n", mach.c_str(), okb & 1, (okb >> 1) & 1, ncase); fflush(stdout);
        }
        return 0;
    }
    if (mode == "ktone") {   // ktone MACHINE R tc r t p k  (negative value: symbolic with that lower bound)
        string mach = argv[2]; parseMachine(mach, TT, NS);
        int R = atoi(argv[3]), tc = atoi(argv[4]); int a[4]; for (int q = 0; q < 4; ++q) a[q] = atoi(argv[5 + q]);
        Lin P[4]; for (int q = 0; q < 4; ++q) P[q] = a[q] >= 0 ? LC(a[q]) : LV(newG(-a[q], 0, "kt-param", 1));
        Lin m3 = R == 1 ? laddc(P[2], 3) : LC(3), x3 = R == 1 ? LC(3) : laddc(P[2], 3), k1 = laddc(P[3], 1);
        vector<Run> S, T; ktCase(R, tc, 0, {P[0], P[1], m3, x3, k1}, S, T);
        RuleSet RS; string why; KTDEBUG = true; KTTRACE = false; SHOWPROOF = getenv("SHOWPROOF") != nullptr;
        { vector<Run> S2, T2; ktCase(R, tc, 0, {LC(60), LC(tc ? 7 : 0), LC(R == 1 ? 3 + 40 : 3 + 30), LC(R == 1 ? 3 : 3 + 30), LC(R == 3 ? 9 : 1)}, S2, T2);
          bool l = ktRun(S2, T2, 200000, false, 0, &RS, true); printf("learn %d rules %zu\n", (int)l, RS.R.size()); }
        KTTRACE = getenv("KTTRACE") != nullptr;
        bool ok = ktRun(S, T, 200000, false, 0, &RS, true, &why);
        printf("ktone %s rules=%zu why=%s\n", ok ? "OK" : "FAIL", RS.R.size(), why.c_str());
        return 0;
    }
    if (mode == "wtab") {
        printf("MG=%lld LAM2=%lld A3=%d JINF=%d\n", MG, LAM2, A3, JINF);
        for (int j = 3; j <= JINF + 1; ++j) {
            const WTab &T = WT[j]; printf("j=%d h=%d pre=", j, T.h); for (auto v : T.pre) printf("%s,", s128(v).c_str());
            printf(" mu=%d lam=%d res=", T.mu, T.lam); for (auto v : T.res) printf("%lld,", v); printf("\n");
        }
        // residues of W(j,b) for exact small arguments
        string line;
        while (getline(cin, line)) {
            if (line[0] == 'A') {   // A a c k x : k-fold x -> a x + c
                istringstream is(line.substr(1)); string a1, a2, a3, a4; is >> a1 >> a2 >> a3 >> a4;
                Lin v;
                try { v = affPow(LC(p128(a4.c_str())), p128(a1.c_str()), p128(a2.c_str()), LC(p128(a3.c_str()))); }
                catch (Undec &u) { printf("A %s %s %s %s UNDEC %s\n", a1.c_str(), a2.c_str(), a3.c_str(), a4.c_str(), u.why.c_str()); continue; }
                printf("A %s %s %s %s %s %lld\n", a1.c_str(), a2.c_str(), a3.c_str(), a4.c_str(), v.isExact() ? "exact" : "huge", v.isExact() ? (ll)pmod(v.c, MG) : resG(v, MG));
                continue;
            }
            if (line[0] == 'C' || line[0] == 'P') {   // C j v b : iter v (U j) b ;  P k r : 2^k (r+4) - 4
                istringstream is(line.substr(1)); string a1, a2, a3; is >> a1 >> a2 >> a3;
                Lin v;
                try { v = line[0] == 'C' ? Cglobal(LC(p128(a1.c_str())), LC(p128(a2.c_str())), LC(p128(a3.c_str()))) : Pglobal(LC(p128(a1.c_str())), LC(p128(a2.c_str()))); }
                catch (Undec &u) { printf("%c %s %s %s UNDEC %s\n", line[0], a1.c_str(), a2.c_str(), a3.c_str(), u.why.c_str()); continue; }
                if (v.isExact()) printf("%c %s %s %s exact %s %lld\n", line[0], a1.c_str(), a2.c_str(), a3.c_str(), s128(v.c).c_str(), (ll)pmod(v.c, MG));
                else printf("%c %s %s %s huge %lld\n", line[0], a1.c_str(), a2.c_str(), a3.c_str(), GS[v.id[0]].res);
                continue;
            }
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
        runOneT(mach, st[0] - 'A', tok);
    }
    return 0;
}
