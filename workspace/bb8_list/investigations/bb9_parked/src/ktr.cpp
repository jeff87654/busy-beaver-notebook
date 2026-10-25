// ktr.cpp: fully literal K-moment tracer (no jumps).  Prints every canonical moment
//   Kt ds m r t = 0^inf <farw> D(d_n)..D(d_1) D(m) (10)^r 11 (11111100)^t 1001 B> 0^inf     (D(x) = (10)^x 1)
// as "K# step tokens(farw->near) | m r t" plus the transitions used since the previous moment.
//   ktr MACHINE [--kt "d_n,..,d_1;m;r;t" (a token may be x*k = k copies; zN = N blank cells) | --start W:H:Q] [--nk N] [--maxs S] [--Q B] [--far W] [--quiet]
//   --far W : cells written left of the tokens (default "11", the record family's 0^inf 11 prefix)
// Without --kt/--start the run starts from the blank tape in state A.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <windows.h>
typedef long long ll;
struct Tr { int w, d, nx; bool def; };
static std::vector<unsigned char> t; static ll off, lo, hi, pos;
static void grow() { ll add = t.size(); std::vector<unsigned char> n(t.size() + 2 * add, 0); memcpy(&n[add], t.data(), t.size()); t.swap(n); off += add; lo += add; hi += add; pos += add; }
static bool at(ll p, const char *s) { ll L = strlen(s); if (p - L + 1 < lo) return false; for (ll i = 0; i < L; ++i) if (t[p - L + 1 + i] != s[i] - '0') return false; return true; }
int main(int argc, char **argv) {
    SetPriorityClass(GetCurrentProcess(), IDLE_PRIORITY_CLASS);
    std::string m = argv[1]; int n = (m.size() + 1) / 7; std::vector<Tr> tr(2 * n);
    for (int s = 0; s < n; ++s) for (int c = 0; c < 2; ++c) { const char *x = m.c_str() + 7 * s + 3 * c;
        if (x[0] == '-' || x[2] - 'A' >= n || x[2] < 'A') tr[2 * s + c] = {0, 0, 0, false}; else tr[2 * s + c] = {x[0] - '0', x[1] == 'R' ? 1 : -1, x[2] - 'A', true}; }
    std::string kt, start, farw = "11"; ll NK = 50, MAXS = (ll)1e10; int QS = 1; bool quiet = false;
    for (int i = 2; i < argc; ++i) { std::string a = argv[i];
        if (a == "--kt") kt = argv[++i]; else if (a == "--start") start = argv[++i]; else if (a == "--nk") NK = atoll(argv[++i]);
        else if (a == "--maxs") MAXS = (ll)atof(argv[++i]); else if (a == "--Q") QS = argv[++i][0] - 'A'; else if (a == "--far") farw = argv[++i];
        else if (a == "--quiet") quiet = true; else { fprintf(stderr, "bad opt %s\n", a.c_str()); return 2; } }
    std::string w; ll head = 0; int q = 0;
    if (!kt.empty()) {
        std::vector<std::string> f; size_t p0 = 0; while (true) { size_t p1 = kt.find(';', p0); f.push_back(kt.substr(p0, p1 == std::string::npos ? std::string::npos : p1 - p0)); if (p1 == std::string::npos) break; p0 = p1 + 1; }
        w = farw == "-" ? "" : farw;
        if (!f[0].empty()) { size_t a = 0; while (true) { size_t b = f[0].find(',', a); std::string it = f[0].substr(a, b == std::string::npos ? std::string::npos : b - a); size_t st = it.find('*'); ll d = atoll(it.c_str()), rep = st == std::string::npos ? 1 : atoll(it.c_str() + st + 1); if (it[0] == 'z') { ll g = atoll(it.c_str() + 1); for (ll j = 0; j < rep * g; ++j) w += "0"; } else for (ll j = 0; j < rep; ++j) { for (ll i = 0; i < d; ++i) w += "10"; w += "1"; } if (b == std::string::npos) break; a = b + 1; } }
        ll mm = atoll(f[1].c_str()), r = atoll(f[2].c_str()), tt = atoll(f[3].c_str());
        for (ll i = 0; i < mm; ++i) w += "10"; w += "1"; for (ll i = 0; i < r; ++i) w += "10"; w += "11";
        for (ll i = 0; i < tt; ++i) w += "11111100"; w += "1001"; head = w.size(); q = QS;
    } else if (!start.empty()) { size_t a = start.find(':'), b = start.rfind(':'); w = start.substr(0, a); if (w == "-") w = ""; head = atoll(start.substr(a + 1, b - a - 1).c_str()); q = start[b + 1] - 'A'; }
    ll sz = std::max<ll>(1 << 22, 4 * (ll)w.size() + 64); t.assign(sz, 0); off = sz / 2;
    for (size_t i = 0; i < w.size(); ++i) t[off + i] = w[i] == '1';
    pos = off + head; lo = std::min(off, pos); hi = std::max(off + (ll)w.size() - 1, pos);
    ll r1 = lo - 1; for (ll i = lo; i <= hi; ++i) if (t[i]) r1 = i;
    ll step = 0, nk = 0; unsigned used = 0;
    while (true) {
        if (pos <= 8 || pos >= (ll)t.size() - 8) { ll o = off; grow(); r1 += off - o; }
        int c = t[pos];
        if (q == QS && c == 0 && pos > r1 && step > 0 && at(pos - 1, "1001")) {
            ll p = pos - 5, tt = 0;
            while (at(p, "11111100")) { ++tt; p -= 8; }
            if (at(p, "11")) {
                p -= 2; ll r = 0; while (p - 1 >= lo && t[p] == 0 && t[p - 1] == 1) { ++r; p -= 2; }
                std::vector<ll> tok;
                while (p >= lo && t[p] == 1) { ll x = 0; ll pp = p - 1; while (pp - 1 >= lo && t[pp] == 0 && t[pp - 1] == 1) { ++x; pp -= 2; } tok.push_back(x); p = pp; }
                if (!tok.empty()) {
                    ll a0 = lo; while (a0 <= p && !t[a0]) ++a0; std::string junk; for (ll i = a0; i <= p; ++i) junk += char('0' + t[i]);
                    std::string s; size_t k = tok.size() - 1;     // farw -> near, run-length; tok[0] = m
                    for (ll i = (ll)tok.size() - 1; i >= 1; ) { ll j = i; while (j >= 1 && tok[j] == tok[i]) --j; s += std::to_string(tok[i]); if (i - j > 1) s += "*" + std::to_string(i - j); s += ' '; i = j; }
                    std::string us; for (int i = 0; i < 2 * n; ++i) if (used >> i & 1) { us += char('A' + i / 2); us += char('0' + i % 2); }
                    ++nk; (void)k;
                    if (!quiet || nk == NK) printf("K%lld step=%lld farw=%s | %s| m=%lld r=%lld t=%lld used=%s\n", nk, step, junk.size() > 60 ? (junk.substr(0, 60) + "..").c_str() : junk.c_str(), s.c_str(), tok[0], r, tt, us.c_str());
                    fflush(stdout); used = 0;
                    if (nk >= NK) return 0;
                }
            }
        }
        const Tr &x = tr[2 * q + c];
        if (!x.def) { printf("HALT %c%d step %lld\n", 'A' + q, c, step); return 0; }
        used |= 1u << (2 * q + c);
        t[pos] = x.w; if (x.w && pos > r1) r1 = pos; else if (!x.w && pos == r1) { while (r1 >= lo && !t[r1]) --r1; }
        pos += x.d; q = x.nx; ++step;
        if (pos < lo) lo = pos; if (pos > hi) hi = pos;
        if (step >= MAXS) { printf("STOP step %lld nk %lld\n", step, nk); return 0; }
    }
}
