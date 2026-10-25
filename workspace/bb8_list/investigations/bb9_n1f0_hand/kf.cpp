// kf.cpp: Kt jump-follower (screening).  Literal simulation; at every canonical moment
//   Kt ds m r t = <junk> D(d_n)..D(d_1) D(m) (10)^r 11 (11111100)^t 1001 B> 0^inf     (D(x) = (10)^x 1)
// two jumps replace astronomically long but rule-level-understood processes:
//   JR1 (m >= 3+MOFF):  R1 iterated, (m+3, r) -> (m, 2r+4): m := m mod 3 (+3 if needed to stay >= ...), r := representative
//                     with the same residue mod 3 as the true result, >= RMIN.
//   JCL (m = 1 mod 3, m > 1 or a nearest contiguous res-1 token > 1): Ackermann clearing of the contiguous res-1 suffix
//                     (m and the nearest tokens = 1 mod 3): all become D1, r := 3R+2.
//   kf MACHINE WORD HEAD STATE [--R R] [--rmin X] [--jumps N] [--maxs S] [--ntok N] [--nor1]
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <algorithm>
typedef long long ll;
struct Tr { int w, d, nx; bool def; };
static std::vector<unsigned char> t; static ll off, lo, hi, pos; static int q;
static void grow() { ll add = t.size(); std::vector<unsigned char> n(t.size() + 2 * add, 0); memcpy(&n[add], t.data(), t.size()); t.swap(n); off += add; lo += add; hi += add; pos += add; }
static bool at(ll p, const char *s) { ll L = strlen(s); if (p - L + 1 < lo) return false; for (ll i = 0; i < L; ++i) if (t[p - L + 1 + i] != s[i] - '0') return false; return true; }
static std::string tl(const std::vector<ll> &tok, ll ntok) {   // far -> near, compressed
    std::string s; ll N = tok.size(); std::vector<ll> v(tok.rbegin(), tok.rend()); ll st = 0;
    if (N > ntok) { s += "[" + std::to_string(N - ntok) + " more] "; st = N - ntok; }
    size_t k = st; while (k < v.size()) { size_t l = k; while (l < v.size() && v[l] == v[k]) ++l; s += std::to_string(v[k]); if (l - k > 1) s += "*" + std::to_string(l - k); s += ' '; k = l; }
    return s;
}
int main(int argc, char **argv) {
    std::string m = argv[1]; int n = (m.size() + 1) / 7; std::vector<Tr> tr(2 * n);
    for (int s = 0; s < n; ++s) for (int c = 0; c < 2; ++c) { const char *x = m.c_str() + 7 * s + 3 * c;
        if (x[0] == '-' || x[2] == 'Z') tr[2 * s + c] = {0, 0, 0, false}; else tr[2 * s + c] = {x[0] - '0', x[1] == 'R' ? 1 : -1, x[2] - 'A', true}; }
    std::string w = argv[2]; if (w == "-") w = ""; ll head = atoll(argv[3]); q = argv[4][0] - 'A';
    ll R = 2, R0 = -1, RMIN = 20, JMAX = 200, MAXS = (ll)3e8, NTOK = 30, MAXT = (ll)4e10; bool nor1 = false;
    for (int i = 5; i < argc; ++i) { std::string a = argv[i];
        if (a == "--R") R = atoll(argv[++i]); else if (a == "--R0") R0 = atoll(argv[++i]); else if (a == "--rmin") RMIN = atoll(argv[++i]); else if (a == "--jumps") JMAX = atoll(argv[++i]);
        else if (a == "--maxs") MAXS = (ll)atof(argv[++i]); else if (a == "--ntok") NTOK = atoll(argv[++i]); else if (a == "--nor1") nor1 = true;
        else if (a == "--maxt") MAXT = (ll)atof(argv[++i]); else { fprintf(stderr, "bad opt %s\n", a.c_str()); return 2; } }
    ll sz = std::max<ll>(1 << 20, 4 * (ll)w.size()); t.assign(sz, 0); off = sz / 2;
    for (size_t i = 0; i < w.size(); ++i) t[off + i] = w[i] == '1';
    pos = off + head; lo = std::min(off, pos); hi = std::max(off + (ll)w.size() - 1, pos);
    ll step = 0, seg = 0, nj = 0; std::vector<ll> zs;
    while (true) {
        if (pos <= 8 || pos >= (ll)t.size() - 2) grow();
        int c = t[pos];
        if (q == 1 && c == 0 && pos == hi && step > 0 && at(pos - 1, "1001")) {
            ll p = pos - 5, tt = 0;
            while (at(p, "11111100")) { ++tt; p -= 8; }
            if (at(p, "11")) {
                ll tailstart = p - 1; p -= 2; ll r = 0; while (p - 1 >= lo && t[p] == 0 && t[p - 1] == 1) { ++r; p -= 2; }
                std::vector<ll> tok, tpos;   // tpos = leftmost cell of each token
                while (p >= lo && t[p] == 1) { ll x = 0; ll pp = p - 1; while (pp - 1 >= lo && t[pp] == 0 && t[pp - 1] == 1) { ++x; pp -= 2; } tok.push_back(x); tpos.push_back(pp + 1); p = pp; }
                if (!tok.empty()) {
                    ll mm = tok[0]; int kind = 0; ll k = 0;
                    if (mm % 3 == 1) { k = 0; bool nz = mm > 1; while (k + 1 < (ll)tok.size() && tok[k + 1] % 3 == 1) { if (tok[k + 1] > 1) nz = true; ++k; } if (nz) kind = 2; }
                    else if (mm >= 3 && !nor1) kind = 1;
                    if (kind) {
                        ll junk; { ll a = lo; while (a <= p && !t[a]) ++a; junk = p - a + 1; if (junk < 0) junk = 0; }
                        // rewrite from the leftmost rewritten token to the tail
                        std::string nw; ll start; ll newr;
                        if (kind == 2) { start = tpos[k]; for (ll i = 0; i <= k; ++i) nw += "101"; newr = 3 * ((nj == 0 && R0 >= 0) ? R0 : R) + 2; }
                        else { start = tpos[0]; ll k3 = mm / 3; ll m2 = mm % 3; for (ll i = 0; i < m2; ++i) nw += "10"; nw += "1";
                               ll rr = r % 3; for (ll i = 0; i < k3; ++i) rr = (2 * rr + 4) % 3; newr = RMIN; while (newr % 3 != rr) ++newr; }
                        for (ll i = 0; i < newr; ++i) nw += "10";
                        nw += "11"; for (ll i = 0; i < tt; ++i) nw += "11111100"; nw += "1001";
                        ++nj; if (kind == 2) zs.push_back(k);
                        printf("J%lld %s step=%lld seg=%lld t=%lld junk=%lld ntok=%lld r=%lld | %s| %s\n", nj, kind == 2 ? "CL" : "R1", step, seg, tt, junk, (ll)tok.size(), r, tl(tok, NTOK).c_str(),
                               kind == 2 ? ("k=" + std::to_string(k)).c_str() : ("m->" + std::to_string(mm % 3)).c_str());
                        fflush(stdout);
                        for (ll i = start; i <= hi; ++i) t[i] = 0;
                        while (start + (ll)nw.size() + 4 >= (ll)t.size()) { ll o = off; grow(); start += off - o; }
                        for (size_t i = 0; i < nw.size(); ++i) t[start + i] = nw[i] - '0';
                        pos = start + nw.size(); hi = pos; q = 1; seg = 0;
                        if (nj >= JMAX) break;
                        continue;
                    }
                }
            }
        }
        const Tr &x = tr[2 * q + c];
        if (!x.def) { ll ones = 0; for (ll i = lo; i <= hi; ++i) ones += t[i]; printf("HALT %c%d step %lld seg %lld ones %lld jumps %lld\n", 'A' + q, c, step, seg, ones, nj);
            std::string s; for (ll i = std::max(lo, pos - 80); i <= std::min(hi, pos + 80); ++i) { if (i == pos) s += '['; s += char(48 + t[i]); if (i == pos) s += ']'; } printf("  near head: %s\n", s.c_str()); break; }
        t[pos] = x.w; pos += x.d; q = x.nx; ++step; ++seg;
        if (pos < lo) lo = pos; if (pos > hi) hi = pos;
        if (seg >= MAXS || step >= MAXT) { printf("STOP step %lld seg %lld jumps %lld\n", step, seg, nj); break; }
    }
    std::string s; for (ll z : zs) s += std::to_string(z) + " "; printf("zeros: %s\n", s.c_str());
}
