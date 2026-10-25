// batt_fast: exact FSA-trace-accelerated version of batt.cpp.
// Since any child that has not failed prior to step s on config i has emitted the exact same (write, move) sequence
// as the base machine on config i, its tape and head position at step s are 100% identical to the base machine's.
// Recording the base's read symbol sym[i][s] alongside (w, d) eliminates all per-child tape allocations and copies.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <functional>
#include <windows.h>
typedef long long ll;
struct Tr { signed char w, d, nx; };
enum { UNDEF = -1, LAZY = -2 };
static int parse(const char *m, Tr *T) {
    int ns = (strlen(m) + 1) / 7;
    for (int q = 0; q < ns; ++q) for (int b = 0; b < 2; ++b) { const char *p = m + 7 * q + 3 * b;
        if (p[0] == 'z') T[2 * q + b] = {0, 0, LAZY};
        else if (p[0] == '-' || p[2] - 'A' >= ns) T[2 * q + b] = {0, 0, UNDEF};
        else T[2 * q + b] = {(signed char)(p[0] - '0'), (signed char)(p[1] == 'R' ? 1 : -1), (signed char)(p[2] - 'A')}; }
    return ns;
}
static std::string build(const std::string &spec) {
    std::vector<std::string> f; size_t p0 = 0;
    while (true) { size_t p1 = spec.find(';', p0); f.push_back(spec.substr(p0, p1 == std::string::npos ? std::string::npos : p1 - p0)); if (p1 == std::string::npos) break; p0 = p1 + 1; }
    std::string w;
    if (!f[0].empty()) { size_t a = 0; while (true) { size_t b = f[0].find(',', a); std::string it = f[0].substr(a, b == std::string::npos ? std::string::npos : b - a);
        size_t st = it.find('*'); ll rep = st == std::string::npos ? 1 : atoll(it.c_str() + st + 1);
        if (it[0] == 'z') { ll g = atoll(it.c_str() + 1); for (ll j = 0; j < rep * g; ++j) w += "0"; }
        else { ll d = atoll(it.c_str()); for (ll j = 0; j < rep; ++j) { for (ll i = 0; i < d; ++i) w += "10"; w += "1"; } }
        if (b == std::string::npos) break; a = b + 1; } }
    ll mm = atoll(f[1].c_str()), r = atoll(f[2].c_str()), tt = atoll(f[3].c_str());
    for (ll i = 0; i < mm; ++i) w += "10"; w += "1"; for (ll i = 0; i < r; ++i) w += "10"; w += "11";
    for (ll i = 0; i < tt; ++i) w += "11111100"; w += "1001";
    return w;
}
int main(int argc, char **argv) {
    SetPriorityClass(GetCurrentProcess(), IDLE_PRIORITY_CLASS);
    Tr base[32]; parse(argv[1], base); ll CAP = (ll)atof(argv[2]); bool JUMPONLY = getenv("BATT_FULL") == 0;
    bool pass_only = (argc > 5 && strcmp(argv[5], "--pass-only") == 0);
    std::vector<std::string> cfg; { FILE *f = fopen(argv[3], "r"); char b[4096]; while (fgets(b, sizeof b, f)) { std::string s = b; while (!s.empty() && (s.back() == '\n' || s.back() == '\r')) s.pop_back(); if (!s.empty() && s[0] != '#') cfg.push_back(s); } fclose(f); }
    std::vector<std::vector<unsigned char>> tr(cfg.size());
    for (size_t i = 0; i < cfg.size(); ++i) {
        std::string w = build(cfg[i]);
        ll SZ = 1 << 16; while (SZ < 4 * (ll)w.size() + 4 * CAP / 1000 + 4096) SZ <<= 1;
        std::vector<unsigned char> tp(SZ, 0); ll off = SZ / 4; for (size_t j = 0; j < w.size(); ++j) tp[off + j] = w[j] == '1';
        ll pos = off + w.size(); int q = 1; ll r1 = pos - 1; ll lo = off; int jt = -1; ll jk = 0;
        for (ll s = 0; s < CAP; ++s) { if (pos < 1 || pos >= (ll)tp.size() - 1) { size_t add = tp.size(); std::vector<unsigned char> n(3 * add, 0); memcpy(&n[add], tp.data(), add); tp.swap(n); pos += add; r1 += add; off += add; lo += add; }
            if (JUMPONLY && q == 1 && tp[pos] == 0 && pos > r1 && pos >= 5 && tp[pos-1]==1 && tp[pos-2]==0 && tp[pos-3]==0 && tp[pos-4]==1) {
                ll p = pos - 5; while (p >= 8 && tp[p]==0 && tp[p-1]==0 && tp[p-2]==1 && tp[p-3]==1 && tp[p-4]==1 && tp[p-5]==1 && tp[p-6]==1 && tp[p-7]==1) p -= 8;
                std::vector<ll> tok;
                if (p >= 2 && tp[p] == 1 && tp[p-1] == 1) { p -= 2; while (p >= 1 && tp[p] == 0 && tp[p-1] == 1) p -= 2;
                    while (p >= 1 && tp[p] == 1) { ll x = 0; ll pp = p - 1; while (pp >= 1 && tp[pp] == 0 && tp[pp-1] == 1) { ++x; pp -= 2; } tok.push_back(x); p = pp; } }
                if (s == 0) {
                    if (tok.empty()) { jt = 0; break; }
                    ll mm = tok[0];
                    if (mm % 3 == 1) { bool nz = mm > 1; jk = 0; while (jk + 1 < (ll)tok.size() && tok[jk + 1] % 3 == 1) { if (tok[jk + 1] > 1) nz = true; ++jk; } jt = nz ? 2 : 0; }
                    else jt = mm >= 3 ? 1 : 0;
                    if (!jt) break;
                } else if (!tok.empty()) {
                    if (jt == 1 && tok[0] < 3) break;
                    if (jt == 2 && (ll)tok.size() > jk) { bool all1 = true; for (ll k = 0; k <= jk; ++k) if (tok[k] != 1) all1 = false; if (all1) break; }
                }
            }
            unsigned char sym = tp[pos];
            Tr &t = base[2 * q + sym]; if (t.nx < 0) break;
            tr[i].push_back(t.w | ((t.d > 0) << 1) | (sym << 2)); tp[pos] = t.w;
            if (t.w && pos > r1) r1 = pos; else if (!t.w && pos == r1) { while (r1 > 0 && !tp[r1]) --r1; }
            pos += t.d; q = t.nx; }
    }
    fprintf(stderr, "battery %zu configs, base steps total %zu\n", cfg.size(), [&]{ size_t s = 0; for (auto &x : tr) s += x.size(); return s; }());
    char line[512];
    FILE *fin = argc > 4 ? fopen(argv[4], "r") : stdin;
    std::function<void(Tr *, int, const std::string &)> rec = [&](Tr *T, int ns, const std::string &name) {
        const Tr &bq = base[2 * 1 + 0]; std::string qs, ff; int ncand = 0;
        for (int X = 0; X < ns; ++X) {
            const Tr &x0 = T[2 * X]; if (x0.nx < 0 || x0.w != bq.w || x0.d != bq.d) continue; ++ncand;
            bool ok = true;
            for (size_t i = 0; i < cfg.size() && ok; ++i) {
                const unsigned char *trp = tr[i].data();
                size_t nsteps = tr[i].size();
                int q = X;
                for (size_t s = 0; s < nsteps; ++s) {
                    unsigned char entry = trp[s];
                    int sym = entry >> 2;
                    int bt = entry & 3;
                    Tr &t = T[2 * q + sym];
                    if (t.nx == LAZY) {
                        Tr save = t;
                        for (int nx = 0; nx < ns; ++nx) { t = {(signed char)(bt & 1), (signed char)((bt >> 1) ? 1 : -1), (signed char)nx};
                            std::string nm = name; size_t p = 7 * q + 3 * sym; nm[p] = '0' + (bt & 1); nm[p + 1] = (bt >> 1) ? 'R' : 'L'; nm[p + 2] = 'A' + nx;
                            rec(T, ns, nm); }
                        t = save; return; }
                    const char *kind = 0;
                    if (t.nx == UNDEF) kind = "HT"; else if ((t.w | ((t.d > 0) << 1)) != bt) kind = "WD";
                    if (kind) { if (!pass_only && ff.empty()) { char b[96]; snprintf(b, sizeof b, "%zu %zu %s %c%d q0=%c", i, s, kind, 'A' + q, sym, 'A' + X); ff = b; } ok = false; break; }
                    q = t.nx; }
            }
            if (ok) qs += char('A' + X);
        }
        if (!qs.empty()) printf("PASS %s qset=%s\n", name.c_str(), qs.c_str());
        else if (!pass_only) {
            if (!ncand) printf("FAIL - - NOK - %s\n", name.c_str());
            else printf("FAIL %s %s\n", ff.c_str(), name.c_str());
        }
    };
    while (fscanf(fin, "%511s", line) == 1) {
        Tr T[32]; int ns = parse(line, T);
        rec(T, ns, std::string(line));
    }
    fflush(stdout);
    return 0;
}
