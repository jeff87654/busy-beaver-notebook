// msim.cpp (bb9_c04_sib): B-form macro simulator for n1-engine machines (rows A-H of n1), e.g. X1.
// B-form (n1 notation, bb10_n1_coq/NOTES.md): tape = ... D(t_1) .. D(t_n) D0 D(A), state H on the blank right end, D(x) = (10)^x 1.
// CLR (n1 engine rule): [L, c+3d, 1^n | A] -> [L, c, 1^n | iter d (U n) A]  -- applied as a JUMP, new A = representative:
//   --pol lin  : A' = 3*(C + F*(n+1)) + 1          (zfg-like, depth-monotone)
//   --pol depthd: A' = 3*(C + F*(n+1) + G*d) + 1   (also monotone in the cleared digit d)
//   always A' >= A + 3 and A' = 1 mod 3.  n = 0 (R1 doubling, exact 2A+8 per unit) is exact while 2^d*A < --exact.
// Every other B-form-to-B-form segment is an EVENT, simulated literally; one line per event (before -> after, RLE tokens).
//   msim TM [--C c] [--F f] [--G g] [--events N] [--maxseg S] [--maxtot S] [--view N] [--clrlog] [--start "toks|A"]
#include <cstdio>
#include <cmath>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <algorithm>
#include <windows.h>
typedef long long ll;
struct Tr { int w, d, nx; bool def; };
static std::vector<unsigned char> t; static ll pos, lo, hi, r1; static int q;
static void grow() { ll add = std::max<ll>(t.size(), 1 << 20); std::vector<unsigned char> n(t.size() + 2 * add, 0); memcpy(&n[add], t.data(), t.size()); t.swap(n); lo += add; hi += add; pos += add; r1 += add; }
// parse tokens leftwards from cell p (inclusive): token = 1 (01)^m read right-to-left as "1" then pairs "0 1"
static bool tokL(ll &p, ll &m) { if (p < lo || t[p] != 1) return false; m = 0; ll pp = p - 1; while (pp - 1 >= lo && t[pp] == 0 && t[pp - 1] == 1) { ++m; pp -= 2; } p = pp; return true; }
static std::string rle(const std::vector<ll> &v, size_t maxc) {
    std::string out; size_t i = 0;
    while (i < v.size()) { size_t j = i; while (j < v.size() && v[j] == v[i]) ++j; char b[64];
        if (j - i == 1) snprintf(b, sizeof b, "%lld", v[i]); else snprintf(b, sizeof b, "%lld^%zu", v[i], j - i);
        if (!out.empty()) out += ' '; out += b; i = j; }
    if (out.size() > maxc) out = out.substr(0, maxc / 4) + " ... " + out.substr(out.size() - 3 * maxc / 4);
    return out;
}
int main(int argc, char **argv) {
    SetPriorityClass(GetCurrentProcess(), IDLE_PRIORITY_CLASS);
    std::string m = argv[1]; int n = (m.size() + 1) / 7; std::vector<Tr> tr(2 * n);
    for (int s = 0; s < n; ++s) for (int c = 0; c < 2; ++c) { const char *x = m.c_str() + 7 * s + 3 * c;
        if (x[0] == '-') tr[2 * s + c] = {0, 0, 0, false}; else tr[2 * s + c] = {x[0] - '0', x[1] == 'R' ? 1 : -1, x[2] - 'A', true}; }
    ll C = 5, EV = 200, MAXSEG = (ll)1e11, MAXTOT = (ll)1e12, VIEW = 600, EXACT = 1000000; double F = 1, G = 0, P = 1, W = 0; bool clrlog = false; std::string start;
    for (int i = 2; i < argc; ++i) { std::string a = argv[i];
        if (a == "--C") C = atoll(argv[++i]); else if (a == "--F") F = atof(argv[++i]); else if (a == "--G") G = atof(argv[++i]);
        else if (a == "--events") EV = atoll(argv[++i]); else if (a == "--maxseg") MAXSEG = (ll)atof(argv[++i]); else if (a == "--maxtot") MAXTOT = (ll)atof(argv[++i]);
        else if (a == "--view") VIEW = atoll(argv[++i]); else if (a == "--clrlog") clrlog = true; else if (a == "--start") start = argv[++i];
        else if (a == "--P") P = atof(argv[++i]); else if (a == "--W") W = atof(argv[++i]); else if (a == "--exact") EXACT = atoll(argv[++i]);
        else { fprintf(stderr, "bad opt %s\n", a.c_str()); return 2; } }
    t.assign(1 << 22, 0); lo = hi = pos = 1 << 21; r1 = lo - 1; q = 0;
    if (!start.empty()) {   // "t1 t2^k ...|A"  far->near
        size_t bar = start.find('|'); std::string f = start.substr(0, bar); ll A = atoll(start.c_str() + bar + 1);
        std::vector<ll> ts; size_t i = 0;
        while (i < f.size()) { while (i < f.size() && f[i] == ' ') ++i; if (i >= f.size()) break; size_t j = f.find(' ', i); if (j == std::string::npos) j = f.size();
            std::string it = f.substr(i, j - i); size_t c = it.find('^'); ll v = atoll(it.c_str()), r = c == std::string::npos ? 1 : atoll(it.c_str() + c + 1);
            for (ll k = 0; k < r; ++k) ts.push_back(v); i = j; }
        ts.push_back(0); ts.push_back(A);
        ll p = pos; for (ll v : ts) { for (ll k = 0; k < v; ++k) { t[p++] = 1; t[p++] = 0; } t[p++] = 1; if (p + 8 >= (ll)t.size()) { ll o = lo; grow(); p += lo - o; } }
        lo = pos; hi = p - 1; r1 = hi; pos = p; q = 7;  // state H on the blank right end
    }
    ll step = 0, seg = 0, nev = 0, nclr = 0; bool first = true; std::string before;
    auto snapshot = [&](ll A) -> std::string {   // full token list of the B-form (far->near), A
        std::vector<ll> ts; ll p = pos - 1, mm;
        // skip A and the D0
        tokL(p, mm); tokL(p, mm);
        while (p >= lo) { if (t[p] == 0) { ll z = 0; while (p >= lo && t[p] == 0) { ++z; --p; } if (p < lo) break; ts.push_back(-z); continue; } tokL(p, mm); ts.push_back(mm); }
        std::reverse(ts.begin(), ts.end());
        std::string s = rle(ts, VIEW); char b[64]; snprintf(b, sizeof b, " | %lld]", A); return "[" + s + b;
    };
    while (true) {
        if (pos <= lo + 4) { if (pos <= 8) grow(); }
        if (pos >= (ll)t.size() - 8) grow();
        int c = t[pos];
        if (q == 7 && c == 0 && pos > r1 && (step > 0 || !start.empty())) {
            // B-form?  word ends ... D0 D(A) at pos-1
            ll p = pos - 1, A, z;
            if (tokL(p, A) && tokL(p, z) && z == 0) {
                // trailing 1^n and token x
                ll pp = p, nn = 0, x = -1, xm; ll xstart = -1, xend = -1;
                while (true) { ll q0 = pp; ll mm; if (!tokL(pp, mm)) break; if (mm == 1) { ++nn; continue; } x = mm; xend = q0; xstart = pp + 1; break; }
                std::string snap = snapshot(A);
                if (!first || !start.empty()) {
                    if (!before.empty()) { ++nev; printf("EV%lld (clr %lld) %s -> %s seg %lld\n", nev, nclr, before.c_str(), snap.c_str(), seg); fflush(stdout); before.clear(); if (nev >= EV) break; }
                }
                first = false;
                if (x >= 3) {   // CLR jump
                    ll d = x / 3, cc = x % 3, A2;
                    if (nn == 0 && 1) { // R1: A -> 2A+8 per unit, exact while small
                        double ap = (double)A; ll ex = A; bool small = true; for (ll i = 0; i < d; ++i) { ap = 2 * ap + 8; if (ap > (double)EXACT) { small = false; break; } ex = 2 * ex + 8; }
                        if (small) A2 = ex; else { A2 = 3 * (C + (ll)(F * 1) + (ll)(G * d)) + 1; if (A2 < A + 3) A2 = A + 3; while (A2 % 3 != 1) ++A2; while (A2 % 3 != ex % 3) ++A2; }
                    } else { A2 = 3 * (C + (ll)(F * pow((double)(nn + 1), P)) + (ll)(G * d) + (ll)(W * (double)(r1 - lo + 1))) + 1; if (A2 < A + 3) A2 = A + 3; while (A2 % 3 != 1) ++A2; }
                    if (clrlog) printf("  CLR n=%lld x=%lld A %lld -> %lld\n", nn, x, A, A2);
                    ++nclr;
                    // rewrite: token x -> cc, then 1^n, D0, D(A2); head after
                    std::string w; for (ll k = 0; k < cc; ++k) w += "10"; w += "1";
                    for (ll k = 0; k < nn; ++k) w += "101";
                    w += "1"; for (ll k = 0; k < A2; ++k) w += "10"; w += "1";
                    for (ll i = xstart; i <= std::max(hi, pos); ++i) t[i] = 0;
                    while (xstart + (ll)w.size() + 16 >= (ll)t.size()) { ll o = lo; grow(); xstart += lo - o; }
                    for (size_t i = 0; i < w.size(); ++i) t[xstart + i] = w[i] - '0';
                    pos = xstart + w.size(); hi = pos - 1; r1 = hi; q = 7; seg = 0;
                    continue;
                }
                before = snapshot(A); seg = 0;
            }
        }
        const Tr &x = tr[2 * q + c];
        if (!x.def) { ll ones = 0; for (ll i = lo; i <= hi; ++i) ones += t[i];
            printf("HALT %c%d step %lld seg %lld ones %lld events %lld clr %lld\n  from %s\n", 'A' + q, c, step, seg, ones, nev, nclr, before.c_str()); break; }
        t[pos] = x.w; if (x.w && pos > r1) r1 = pos; else if (!x.w && pos == r1) { while (r1 >= lo && !t[r1]) --r1; }
        pos += x.d; q = x.nx; ++step; ++seg;
        if (pos < lo) lo = pos; if (pos > hi) hi = pos;
        if (seg >= MAXSEG || step >= MAXTOT) { printf("STOP step %lld seg %lld events %lld\n  from %s\n", step, seg, nev, before.c_str()); break; }
    }
}
