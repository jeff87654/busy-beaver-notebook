// c231f: world follower for champ_231/232-engine children (8 states, A..H), literal simulation with two jumps taken from
// the Coq development bb7_c231_coq (C231_rules2.v R1ITER, C231_clear.v CDP):
//   Kc ds a b = 0^inf E> 0 1^(2b+1) 00 1^(2a) 00 [1^(2d) 00 for d in ds, nearest first] 1 0^inf
//   R1ITER : Kc ds a b       ->* Kc ds 0 (b + 3a)                       (exact)
//   CDP    : Kc (0^m ++ v :: Us) 0 B ->* Kc (0^(m+1) ++ Us) 0 (iter v (U m) B)   if m <= B, v >= 1
//            U 0 x = 3x + 9;  U (j+1) x = (U j)^(x+2-j) (W j 3);  W 0 B = B;  W (j+1) B = U j (W j B)
//            computed exactly while < EXCAP, else replaced by a representative R (world policy).
// A K-moment requires the whole tape left of the head to be blank (as in Kc); anything else runs literally.
// World policy for a non-exact CDP result: R = max(B + v, RC + RK*(m+1)) rounded up into CLS mod MOD (default 39 mod 162:
//   2R+3 = 0 mod 81, the only tower-stable residue of champ_231's accumulators; parity selectable via --cls).
// Output (pkf8-like, for wtree.py):  J# CL step=.. k=<list length> m=.. v=.. R=.. exact=0/1 | a=.. b=.. ds=<RLE>
//                                    J# R1 step=.. a=..->0 b=..->..
//   HALT Xc step S ones N jumps J  |  END ...  |  STOP ...;  final 'zeros:' line = the list length at every CDP jump.
//   c231f MACHINE [--maxt S] [--jumps J] [--rc C] [--rk F] [--cls C M] [--excap X] [--view N] [--kt "a;b;d1,d2,..."]
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <windows.h>
typedef long long ll;
struct Tr { signed char w, d, nx; };
static std::vector<unsigned char> t; static ll off, lo, hi, pos;
static void grow() { ll add = t.size(); std::vector<unsigned char> n(t.size() + 2 * add, 0); memcpy(&n[add], t.data(), t.size()); t.swap(n); off += add; lo += add; hi += add; pos += add; }
static ll EXCAP = 1000000000LL; static unsigned QMASK = 1u << 4;
// exact U/W with cap (returns -1 if >= EXCAP)
static ll Uf(int j, ll x);
static ll Wf(int j, ll B) { if (B < 0) return -1; ll v = B; for (int i = 0; i < j; ++i) { v = Uf(i, v); if (v < 0) return -1; } return v; }
static ll Uf(int j, ll x) {
    if (x < 0) return -1;
    if (j == 0) { ll r = 3 * x + 9; return r >= EXCAP ? -1 : r; }
    ll n = x + 2 - (j - 1); ll v = Wf(j - 1, 3); if (v < 0) return -1;
    for (ll i = 0; i < n; ++i) { v = Uf(j - 1, v); if (v < 0) return -1; }
    return v;
}
int main(int argc, char **argv) {
    SetPriorityClass(GetCurrentProcess(), IDLE_PRIORITY_CLASS);
    std::string m = argv[1]; int ns = (m.size() + 1) / 7; Tr T[32];
    for (int q = 0; q < ns; ++q) for (int b = 0; b < 2; ++b) { const char *p = m.c_str() + 7 * q + 3 * b;
        if (p[0] == '-' || p[0] == 'z' || p[2] - 'A' >= ns) T[2 * q + b] = {0, 0, -1};
        else T[2 * q + b] = {(signed char)(p[0] - '0'), (signed char)(p[1] == 'R' ? 1 : -1), (signed char)(p[2] - 'A')}; }
    ll MAXT = (ll)2e9, JMAX = 200, RC = 20, CLS = 39, MOD = 162, VIEW = 200; double RK = 1.0; std::string kt; bool FIXED = false;
    for (int i = 2; i < argc; ++i) { std::string a = argv[i];
        if (a == "--maxt") MAXT = (ll)atof(argv[++i]); else if (a == "--jumps") JMAX = atoll(argv[++i]);
        else if (a == "--rc") RC = atoll(argv[++i]); else if (a == "--rk") RK = atof(argv[++i]);
        else if (a == "--cls") { CLS = atoll(argv[++i]); MOD = atoll(argv[++i]); } else if (a == "--excap") EXCAP = (ll)atof(argv[++i]);
        else if (a == "--fixed") FIXED = true; else if (a == "--qset") { QMASK = 0; for (const char *z = argv[++i]; *z; ++z) QMASK |= 1u << (*z - 'A'); } else if (a == "--view") VIEW = atoll(argv[++i]); else if (a == "--kt") kt = argv[++i];
        else { fprintf(stderr, "bad opt %s\n", a.c_str()); return 2; } }
    t.assign(1 << 22, 0); off = 1 << 21; pos = off; lo = hi = pos; int q = 0;
    if (!kt.empty()) {   // start at Kc ds a b
        ll a, b; char ds[1 << 14]; ds[0] = 0; sscanf(kt.c_str(), "%lld;%lld;%16000s", &a, &b, ds);
        std::vector<ll> d; char *x = ds; while (*x) { ll v = strtoll(x, &x, 10); ll rep = 1; if (*x == '*') { ++x; rep = strtoll(x, &x, 10); } for (ll i = 0; i < rep; ++i) d.push_back(v); if (*x == ',') ++x; else break; }
        ll c = pos + 1; for (ll i = 0; i < 2 * b + 1; ++i) t[c++] = 1; c += 2; for (ll i = 0; i < 2 * a; ++i) t[c++] = 1; c += 2;
        for (ll v : d) { for (ll i = 0; i < 2 * v; ++i) t[c++] = 1; c += 2; } t[c] = 1; hi = c; q = 4;
    }
    ll step = 0, nj = 0; std::vector<ll> zs; bool any = !kt.empty();
    auto lastone = [&]() { ll r = hi; while (r > pos && !t[r]) --r; return r; };
    while (step < MAXT) {
        if (pos < 4 || pos >= (ll)t.size() - 4) grow();
        int c = t[pos];
        if ((QMASK >> q & 1) && c == 0 && (step > 0 || any)) {
            // K-moment test: left blank, right = 0 1^(2b+1) 00 1^(2a) 00 [1^(2d) 00]* 1 0^inf  (head on the first 0)
            bool leftblank = true; for (ll i = lo; i < pos; ++i) if (t[i]) { leftblank = false; break; }
            if (leftblank && t[pos + 1] == 1) {
                ll i = pos + 1, r1 = lastone(); ll ones = 0; while (i <= r1 && t[i]) { ++ones; ++i; }
                bool ok = ones % 2 == 1; ll b = (ones - 1) / 2; std::vector<ll> fld;
                if (ok && i + 1 <= r1 && t[i] == 0 && t[i + 1] == 0) { i += 2;
                    while (true) { ll o = 0; while (i <= r1 && t[i]) { ++o; ++i; }
                        if (i > r1) { if (o == 1) break; ok = false; break; }    // final single 1
                        if (o % 2 || t[i] != 0 || i + 1 > r1 || t[i + 1] != 0) { ok = false; break; }
                        fld.push_back(o / 2); i += 2; } }
                else ok = false;
                if (ok && !fld.empty()) {
                    ll a = fld[0]; std::vector<ll> ds(fld.begin() + 1, fld.end());
                    ll mz = 0; while (mz < (ll)ds.size() && ds[mz] == 0) ++mz;
                    int kind = 0; ll nb = b; bool exact = true; ll v = 0;
                    if (a > 0) { kind = 1; nb = b + 3 * a; }
                    else if (mz < (ll)ds.size() && mz <= b) {
                        kind = 2; v = ds[mz]; ll x = b;
                        for (ll it = 0; it < v && x >= 0; ++it) x = Uf((int)mz, x);
                        if (x >= 0) nb = x;
                        else { exact = false; nb = FIXED ? std::max<ll>(RC, mz + 1) : std::max<ll>(b + v, RC + (ll)(RK * (mz + 1)));
                            ll rr = ((nb - CLS) % MOD + MOD) % MOD; if (rr) nb += MOD - rr; }
                        for (ll k = 0; k <= mz; ++k) ds[k] = 0;
                    }
                    if (kind) {
                        ++nj;
                        if (kind == 1) printf("J%lld R1 step=%lld a=%lld->0 b=%lld->%lld\n", nj, step, a, b, nb);
                        else { zs.push_back((ll)ds.size());
                            std::string vw; for (size_t k = 0; k < ds.size();) { size_t j = k; while (j < ds.size() && ds[j] == ds[k]) ++j; char bf[48];
                                if (j - k > 1) snprintf(bf, sizeof bf, "%lld*%zu ", ds[k], j - k); else snprintf(bf, sizeof bf, "%lld ", ds[k]); vw += bf; k = j; if (vw.size() > (size_t)VIEW) { vw += "..."; break; } }
                            printf("J%lld CL step=%lld k=%zu m=%lld v=%lld R=%lld exact=%d | b=%lld ds=%s\n", nj, step, ds.size(), mz, v, nb, exact ? 1 : 0, nb, vw.c_str()); }
                        fflush(stdout);
                        // rewrite the tape: Kc ds 0 nb
                        ll cc = pos + 1; for (ll k = pos + 1; k <= hi; ++k) t[k] = 0;
                        ll need = cc + 2 * nb + 8; for (ll v2 : ds) need += 2 * v2 + 2;
                        while (need >= (ll)t.size() - 8) grow();
                        cc = pos + 1; for (ll k = 0; k < 2 * nb + 1; ++k) t[cc++] = 1; cc += 2; cc += 2;
                        for (ll v2 : ds) { for (ll k = 0; k < 2 * v2; ++k) t[cc++] = 1; cc += 2; } t[cc] = 1; hi = cc;
                        if (nj >= JMAX) { printf("END jumps %lld step %lld\n", nj, step); break; }
                        continue;
                    }
                }
            }
        }
        Tr &x = T[2 * q + c];
        if (x.nx < 0) { ll ones = 0; for (ll i = lo; i <= hi; ++i) ones += t[i];
            printf("HALT %c%d step %lld ones %lld jumps %lld\n", 'A' + q, c, step, ones, nj); break; }
        t[pos] = x.w; pos += x.d; if (pos < lo) lo = pos; if (pos > hi) hi = pos; q = x.nx; ++step;
    }
    if (step >= MAXT) printf("STOP step %lld jumps %lld\n", step, nj);
    printf("zeros:"); for (ll z : zs) printf(" %lld", z); printf("\n");
    return 0;
}
