// pkf.cpp: parked-list follower (screening, representative accumulators) for the n1f0 BB(7)-engine family.
// Literal simulation; at every canonical moment
//   K = <far> D(d_n)..D(d_1) D(m) (10)^r 11 (11111100)^t 1001 Q> 0^inf      (D(x) = (10)^x 1, Q = --Q, default B)
// two jumps replace processes whose outcome is known at rule level:
//   JCL  m = 1 mod 3 and the contiguous suffix of tokens = 1 mod 3 (m, d_1, ..) has a token > 1:
//        Ackermann clearing; every suffix token becomes D1, r := 3R+2 with R chosen by the size policy.
//   JR1  m >= 3, m != 1 mod 3: R1 iterated k = m/3 times, (m, r) -> (m mod 3, 2^k (r+4) - 4); exact if small,
//        else a representative with the same residue mod MOD (default 2520*11*13) chosen by the size policy.
// Size policy for fresh accumulators: --rk F --rc C (R = C + F * cleared depth k, keeps the real order of the accumulators), or  --R N (fixed R, kf-like)  or  --grow F (R >= F * current tape width, plus --rmin)
// with R = --cls C (mod --mod M) when given.  --B N fixes R at the first JCL (the real first accumulator class).
// Output per jump: J# kind step seg t k | far-to-near token view (RLE, D-token values; z<k> = gap of k zeros).
//   pkf MACHINE [--start W:H:Q] [--Q B] [--R N | --grow F] [--rmin N] [--cls C --mod M] [--B N] [--jumps N] [--maxs S]
//       [--maxt S] [--view N] [--nojr1] [--quiet] [--kt "d_n,..,d_1;m;r;t"  (start at a Kt config; x*k = k copies, zN = N blank cells)]
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <algorithm>
#include <windows.h>
typedef long long ll;
typedef unsigned long long ull;
struct Tr { int w, d, nx; bool def; };
static std::vector<unsigned char> t; static ll off, lo, hi, pos, r1; static int q;
static void grow() { ll add = t.size(); std::vector<unsigned char> n(t.size() + 2 * add, 0); memcpy(&n[add], t.data(), t.size()); t.swap(n); off += add; lo += add; hi += add; pos += add; r1 += add; }
static bool at(ll p, const char *s) { ll L = strlen(s); if (p - L + 1 < lo) return false; for (ll i = 0; i < L; ++i) if (t[p - L + 1 + i] != s[i] - '0') return false; return true; }
// D-token view of cells [a, b]
static std::string dview(ll a, ll b, size_t maxc) {
    while (a <= b && !t[a]) ++a;
    std::vector<std::string> tok; ll i = a;
    while (i <= b) {
        if (t[i] == 0) { ll j = i; while (j <= b && !t[j]) ++j; if (j - i >= 2 || j > b) tok.push_back("z" + std::to_string(j - i)); else tok.push_back("z1"); i = j; continue; }
        // t[i] == 1: token (10)^m 1 starting here?
        ll j = i, m = 0;
        while (j + 2 <= b && t[j] == 1 && t[j + 1] == 0 && t[j + 2] == 1) { j += 2; ++m; }
        // now t[j] == 1 ends the token
        tok.push_back(std::to_string(m)); i = j + 1;
        // a "10" followed by 0 (gap) : the 0 after a token start is a gap
    }
    // the parse above never leaves a dangling "10": a 1 followed by 00 is a D0 then a gap
    std::string out; size_t k = 0;
    while (k < tok.size()) { size_t l = k; while (l < tok.size() && tok[l] == tok[k]) ++l;
        if (!out.empty()) out += ' '; out += tok[k]; if (l - k > 1) out += "*" + std::to_string(l - k); k = l; }
    if (out.size() > maxc) out = out.substr(0, maxc / 3) + " ... " + out.substr(out.size() - 2 * maxc / 3);
    return out;
}
static ll powmod(ll b, ll e, ll m) { ll r = 1 % m; b %= m; while (e > 0) { if (e & 1) r = (__int128)r * b % m; b = (__int128)b * b % m; e >>= 1; } return r; }
int main(int argc, char **argv) {
    SetPriorityClass(GetCurrentProcess(), IDLE_PRIORITY_CLASS);
    if (argc < 2) { fprintf(stderr, "usage: see header\n"); return 2; }
    std::string m = argv[1]; int n = (m.size() + 1) / 7; std::vector<Tr> tr(2 * n);
    for (int s = 0; s < n; ++s) for (int c = 0; c < 2; ++c) { const char *x = m.c_str() + 7 * s + 3 * c;
        if (x[0] == '-' || x[2] == 'Z' || x[2] - 'A' >= n) tr[2 * s + c] = {0, 0, 0, false}; else tr[2 * s + c] = {x[0] - '0', x[1] == 'R' ? 1 : -1, x[2] - 'A', true}; }
    std::string start, ktspec; int QS = 1; ll RF = 2, B = -1, RMIN = 20, JMAX = 200, MAXS = (ll)3e9, MAXT = (ll)1e11, VIEW = 400, MOD = 2520LL * 11 * 13, CLS = -1, EXACTCAP = 4000000;
    std::vector<ll> RL; ll RMOD = 36; double RKF = -1; ll RKC = 0; ll DUMPJ = -1; double GROW = 0; ll SNAP = 0, SNAPJ = 0; bool nojr1 = false, quiet = false;
    for (int i = 2; i < argc; ++i) { std::string a = argv[i];
        if (a == "--start") start = argv[++i]; else if (a == "--kt") ktspec = argv[++i]; else if (a == "--Q") QS = argv[++i][0] - 'A';
        else if (a == "--R") RF = atoll(argv[++i]); else if (a == "--grow") GROW = atof(argv[++i]); else if (a == "--rmin") RMIN = atoll(argv[++i]);
        else if (a == "--B") B = atoll(argv[++i]); else if (a == "--cls") CLS = atoll(argv[++i]); else if (a == "--mod") MOD = atoll(argv[++i]);
        else if (a == "--jumps") JMAX = atoll(argv[++i]); else if (a == "--maxs") MAXS = (ll)atof(argv[++i]); else if (a == "--maxt") MAXT = (ll)atof(argv[++i]);
        else if (a == "--view") VIEW = atoll(argv[++i]); else if (a == "--nojr1") nojr1 = true; else if (a == "--quiet") quiet = true;
        else if (a == "--snap") SNAP = (ll)atof(argv[++i]); else if (a == "--snapj") SNAPJ = atoll(argv[++i]);
        else if (a == "--Rlist") { std::string v = argv[++i]; size_t p0 = 0; while (p0 < v.size()) { size_t p1 = v.find(',', p0); if (p1 == std::string::npos) p1 = v.size(); RL.push_back(atoll(v.substr(p0, p1 - p0).c_str())); p0 = p1 + 1; } }
        else if (a == "--rmod") RMOD = atoll(argv[++i]); else if (a == "--rk") RKF = atof(argv[++i]); else if (a == "--rc") RKC = atoll(argv[++i]); else if (a == "--dumpj") DUMPJ = atoll(argv[++i]);
        else if (a == "--exactcap") EXACTCAP = atoll(argv[++i]);
        else { fprintf(stderr, "bad opt %s\n", a.c_str()); return 2; } }
    std::string w; ll head = 0; int q0 = 0;
    if (!ktspec.empty()) {   // --kt "d_n,..,d_1;m;r;t" (far-first tokens, x*k = k copies; no prefix): Kt config, head in Q on the blank right end
        std::vector<std::string> f; size_t p0 = 0; while (true) { size_t p1 = ktspec.find(';', p0); f.push_back(ktspec.substr(p0, p1 == std::string::npos ? std::string::npos : p1 - p0)); if (p1 == std::string::npos) break; p0 = p1 + 1; }
        if (!f[0].empty()) { size_t a = 0; while (true) { size_t b = f[0].find(',', a); std::string it = f[0].substr(a, b == std::string::npos ? std::string::npos : b - a); size_t st = it.find('*');
            ll rep = st == std::string::npos ? 1 : atoll(it.c_str() + st + 1);
            if (it[0] == 'z') { ll g = atoll(it.c_str() + 1); for (ll j = 0; j < rep * g; ++j) w += "0"; }      // zN = a gap of N blank cells
            else { ll d = atoll(it.c_str()); for (ll j = 0; j < rep; ++j) { for (ll i = 0; i < d; ++i) w += "10"; w += "1"; } } if (b == std::string::npos) break; a = b + 1; } }
        ll mm = atoll(f[1].c_str()), r = atoll(f[2].c_str()), tt = atoll(f[3].c_str());
        for (ll i = 0; i < mm; ++i) w += "10"; w += "1"; for (ll i = 0; i < r; ++i) w += "10"; w += "11";
        for (ll i = 0; i < tt; ++i) w += "11111100"; w += "1001"; start = w + ":" + std::to_string(w.size()) + ":" + char('A' + QS);
    }
    if (!start.empty()) { size_t a = start.find(':'), b = start.rfind(':'); w = start.substr(0, a); if (w == "-") w = ""; head = atoll(start.substr(a + 1, b - a - 1).c_str()); q0 = start[b + 1] - 'A'; }
    ll sz = std::max<ll>(1 << 22, 4 * (ll)w.size()); t.assign(sz, 0); off = sz / 2;
    for (size_t i = 0; i < w.size(); ++i) t[off + i] = w[i] == '1';
    pos = off + head; q = q0; lo = std::min(off, pos); hi = std::max(off + (ll)w.size() - 1, pos);
    r1 = lo - 1; for (ll i = lo; i <= hi; ++i) if (t[i]) r1 = i;
    ll step = 0, seg = 0, nj = 0, ncl = 0; std::vector<ll> zs; unsigned used = 0, segused = 0;
    auto pickR = [&](ll want_res, ll modulus) -> ll {   // fresh accumulator size per policy, with residue want_res mod modulus (or -1)
        ll base;
        if (GROW > 0) { ll wdt = r1 - lo + 1; base = std::max<ll>(RMIN, (ll)(GROW * (double)wdt)); }
        else base = RF;
        if (want_res >= 0) { ll x = base; ll rr = ((want_res % modulus) + modulus) % modulus; x += ((rr - x % modulus) % modulus + modulus) % modulus; return x; }
        return base;
    };
    bool any = !start.empty();
    while (true) {
        if (pos <= 8 || pos >= (ll)t.size() - 8) grow();
        int c = t[pos];
        if (q == QS && c == 0 && pos > r1 && (step > 0 || any) && at(pos - 1, "1001")) {
            ll p = pos - 5, tt = 0;
            while (at(p, "11111100")) { ++tt; p -= 8; }
            if (at(p, "11")) {
                p -= 2; ll r = 0; while (p - 1 >= lo && t[p] == 0 && t[p - 1] == 1) { ++r; p -= 2; }
                ll rstart = p + 1;
                std::vector<ll> tok, tpos;
                while (p >= lo && t[p] == 1) { ll x = 0; ll pp = p - 1; while (pp - 1 >= lo && t[pp] == 0 && t[pp - 1] == 1) { ++x; pp -= 2; } tok.push_back(x); tpos.push_back(pp + 1); p = pp; }
                if (!tok.empty()) {
                    ll mm = tok[0]; int kind = 0; ll k = 0;
                    if (mm % 3 == 1) { bool nz = mm > 1; while (k + 1 < (ll)tok.size() && tok[k + 1] % 3 == 1) { if (tok[k + 1] > 1) nz = true; ++k; } if (nz) kind = 2; }
                    else if (mm >= 3 && !nojr1) kind = 1;
                    if (kind) {
                        std::string nw; ll st0; ll newr; char info[160];
                        if (kind == 2) {
                            st0 = tpos[k]; for (ll i = 0; i <= k; ++i) nw += "101";
                            ll R = (ncl < (ll)RL.size()) ? RL[ncl] : (ncl == 0 && B >= 0) ? B : (RKF >= 0) ? RKC + (ll)(RKF * (double)k) : pickR(CLS, MOD);   // --rk F --rc C: R = C + F k (monotone in the cleared depth k)
                            newr = 3 * R + 2; ++ncl; zs.push_back(k);
                            snprintf(info, sizeof info, "k=%lld m=%lld R=%lld", k, mm, R);
                        } else {
                            st0 = tpos[0]; ll k3 = mm / 3, m2 = mm % 3;
                            for (ll i = 0; i < m2; ++i) nw += "10"; nw += "1";
                            // exact value if small
                            double approx = (double)(r + 4); bool small = true; ll ex = r + 4;
                            for (ll i = 0; i < k3; ++i) { approx *= 2; if (approx > (double)EXACTCAP) { small = false; break; } ex *= 2; }
                            if (small) newr = ex - 4;
                            else { ll res = ((__int128)powmod(2, k3, RMOD) * ((r + 4) % RMOD) % RMOD - 4 + RMOD) % RMOD; ll base = (GROW > 0) ? std::max<ll>(RMIN, (ll)(GROW * (double)(r1 - lo + 1))) : RMIN; newr = base + ((res - base % RMOD) % RMOD + RMOD) % RMOD; }
                            snprintf(info, sizeof info, "m=%lld->%lld r=%lld->%lld%s", mm, m2, r, newr, small ? "" : "(rep)");
                        }
                        for (ll i = 0; i < newr; ++i) nw += "10";
                        nw += "11"; for (ll i = 0; i < tt; ++i) nw += "11111100"; nw += "1001";
                        ++nj;
                        if (nj == DUMPJ || DUMPJ == 0) { ll a0 = lo; while (a0 < pos && !t[a0]) ++a0; std::string w; for (ll i = a0; i < pos; ++i) w += char('0' + t[i]); printf("DUMP %s\n", w.c_str()); }
                        std::string us; for (int i = 0; i < 2 * n; ++i) if (segused >> i & 1) { us += char('A' + i / 2); us += char('0' + i % 2); }
                        if (!quiet) { printf("J%lld %s step=%lld seg=%lld t=%lld %s used=%s | %s\n", nj, kind == 2 ? "CL" : "R1", step, seg, tt, info, us.c_str(), dview(lo, rstart - 1, VIEW).c_str()); fflush(stdout); }
                        for (ll i = st0; i <= std::max(hi, pos); ++i) t[i] = 0;
                        while (st0 + (ll)nw.size() + 16 >= (ll)t.size()) { ll o = off; grow(); st0 += off - o; }
                        for (size_t i = 0; i < nw.size(); ++i) t[st0 + i] = nw[i] - '0';
                        pos = st0 + nw.size(); hi = pos; r1 = pos - 1; q = QS; seg = 0; segused = 0;
                        if (nj == DUMPJ) { ll a0 = lo; while (a0 < pos && !t[a0]) ++a0; std::string w; for (ll i = a0; i < pos; ++i) w += char('0' + t[i]); printf("POST %s\n", w.c_str()); }
                        if (nj >= JMAX) { printf("END jumps %lld step %lld\n", nj, step); break; }
                        continue;
                    }
                }
            }
        }
        const Tr &x = tr[2 * q + c];
        if (!x.def) { ll ones = 0; for (ll i = lo; i <= hi; ++i) ones += t[i];
            printf("HALT %c%d step %lld seg %lld ones %lld jumps %lld\n", 'A' + q, c, step, seg, ones, nj);
            printf("  tape: %s\n", dview(lo, std::max(hi, pos), 4 * VIEW).c_str()); break; }
        segused |= 1u << (2 * q + c); used |= 1u << (2 * q + c);
        t[pos] = x.w; if (x.w && pos > r1) r1 = pos; else if (!x.w && pos == r1) { while (r1 >= lo && !t[r1]) --r1; }
        pos += x.d; q = x.nx; ++step; ++seg;
        if (pos < lo) lo = pos; if (pos > hi) hi = pos;
        if (SNAP && nj >= SNAPJ && seg % SNAP == 0) { printf("  SNAP step=%lld seg=%lld %c head-r1=%lld | %s\n", step, seg, 'A' + q, pos - r1, dview(lo, std::max(hi, pos), 2 * VIEW).c_str()); fflush(stdout); }
        if (seg >= MAXS || step >= MAXT) { printf("STOP step %lld seg %lld jumps %lld state %c\n  tape: %s\n", step, seg, nj, 'A' + q, dview(lo, std::max(hi, pos), 4 * VIEW).c_str()); break; }
    }
    std::string s; for (ll z : zs) s += std::to_string(z) + " "; printf("zeros: %s\n", s.c_str());
}
